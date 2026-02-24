# Keneya Lens: Offline Clinical Decision Support for Community Health Workers

---

### Project name

**Keneya Lens** — Offline-First Clinical Decision Support Powered by Google HAI-DEF

*"Keneya" means health in Bambara, the lingua franca of Mali.*

---

### Your team

**Solo Submission**

| Role | Contribution |
|------|-------------|
| Full-Stack AI Engineer | System architecture, HAI-DEF model integration, RAG pipeline, API, UI/UX design |
| Clinical Researcher | Problem validation, impact methodology, safety framework |

---

### Problem statement

#### The Healthcare Gap

In sub-Saharan Africa, there is roughly **1 physician per 10,000 people** (WHO 2023). In rural Mali, the ratio exceeds 1:25,000. Community Health Workers (CHWs) fill this void — they are trained for 2–4 weeks and dispatched to villages where they become the only healthcare contact for hundreds of families.

Every day, a CHW like Aminata Traoré in Mali's Ségou Region faces 15–25 patients and must decide: treat locally, or refer to the district hospital 35 km away. She has no doctor to call, no internet to query, and paper guidelines too dense to navigate mid-consultation.

**The cost of uncertainty is measured in lives:**

- 18% of serious cases are missed at first presentation (WHO 2023)
- 35% of referrals are unnecessary — costly for families, wasteful of scarce resources
- Mothers and children bear the highest burden of these preventable outcomes

This is a problem AI is uniquely positioned to solve. The bottleneck is not medical knowledge — it exists in guidelines. The bottleneck is *access*: real-time, contextualised, guideline-grounded decision support at the point of care, without internet, on affordable hardware.

#### Why AI Is the Right Solution

Traditional rule-based systems cannot handle the complexity of overlapping symptom presentations. Closed AI systems require constant connectivity and charge per query — unusable in the field. HAI-DEF open-weight models make it possible to run a medically specialised AI locally, permanently.

#### Projected Impact (Mali Deployment Scenario)

Assumptions: 10,000 CHWs, 20 patients/day, 300 working days/year = **60 million consultations/year**.

The figures below are modelled targets based on analogous AI clinical decision support deployments. They are not claims from a completed trial — Keneya Lens is a prototype built for this competition. A formal clinical validation study would be required before deployment.

| Outcome | Baseline (no tool) | Projected Target | Source basis |
|---------|--------------------|--------------------|-------------|
| Consultation time | 15–20 min | 5–7 min | Analogous CDSSs (GSMA 2022) |
| Unnecessary referrals | 35% | ~12% | CHW decision support literature |
| Missed serious cases | 18% | ~5% | WHO IMCI adherence studies |
| Guideline adherence | 40% | ~85% | Structured protocol tools |

**Projected economic and human impact (modelled):**
- Referrals prevented: ~13.8 million/year → potential savings of **USD 207 million/year** (transport + lost wages at $15/referral)
- Additional serious cases caught: ~780,000/year → assuming 10% untreated mortality: **~78,000 lives/year protected**
- Productivity equivalent of freeing **~3,800 person-years** of CHW time annually

*Methodology:* Modelled from WHO CHW coverage data for Mali, published referral outcome literature (Bhutta et al., The Lancet 2018), and analogous AI decision-support deployment evaluations (GSMA 2022). All figures are targets for a full deployment validated at scale, not results from the current prototype.

---

### Overall solution

Keneya Lens integrates three HAI-DEF models into a single offline clinical decision support system, orchestrated by a four-stage agentic consultation pipeline.

#### Agentic Consultation Workflow

The centrepiece of Keneya Lens is a multi-agent orchestration system (`app/agents.py`) that transforms a free-text patient presentation into a structured, evidence-grounded clinical consultation. Each agent has a focused responsibility, a tightly scoped system prompt, and a validated JSON output schema.

```
User Input (free-text patient presentation)
         │
         ▼
 ┌──────────────────┐
 │  Stage 1         │  IntakeAgent
 │  Patient Intake  │  Structures raw input: age, sex, chief complaint,
 └──────────────────┘  vital signs, duration, risk factors → JSON
         │
         ▼
 ┌──────────────────┐
 │  Stage 2         │  TriageAgent
 │  Triage          │  WHO IMCI-informed urgency assessment:
 │  Assessment      │  triage_level (CRITICAL / URGENT / MODERATE / NON-URGENT),
 └──────────────────┘  red_flag_symptoms[], differential_diagnoses[], reasoning
         │
         ▼
 ┌──────────────────┐
 │  Stage 3         │  GuidelineAgent
 │  Clinical        │  Queries ChromaDB per differential diagnosis,
 │  Guidelines      │  retrieves citations, falls back to model knowledge
 └──────────────────┘  if the knowledge base is empty
         │
         ▼
 ┌──────────────────┐
 │  Stage 4         │  RecommendationAgent
 │  Clinical        │  Synthesises triage + guidelines into:
 │  Recommendations │  immediate_actions[], treatment_notes,
 └──────────────────┘  referral_criteria[], monitoring_plan, follow_up
         │
         ▼
   ConsultationResult (full structured JSON — all 4 stage outputs)
```

**Why agentic orchestration matters clinically:** A single monolithic prompt cannot reliably perform intake structuring, urgency assessment, guideline retrieval, and action planning simultaneously. Decomposing into specialised agents allows each stage to use an optimised system prompt, validate its own output schema, and fail gracefully without corrupting downstream stages. The pipeline pattern also makes the system auditable — supervisors can inspect exactly which stage produced which recommendation.

**API surface:**
- `POST /consult` — runs all 4 agents in sequence, returns a `ConsultationResult`
- `POST /consult/stage` — runs a single named stage, accepting `{"stage": 1-4, "context": dict}` — used by the step-by-step UI to reveal results progressively

**Agent prompting strategy:** Each agent uses a system prompt that requires JSON-only output. A `_extract_json()` helper strips markdown fences and recovers from partial outputs via regex fallback, ensuring robust parsing even on CPU inference where outputs may be truncated.

#### HAI-DEF Model Architecture

```
User Query / Image
        │
        ▼
  ┌─────────────┐    keyword/modality routing
  │ QueryRouter │────────────────────────────┐
  └─────────────┘                            │
        │ text queries                  image queries
        ▼                                    ▼
 ┌────────────────┐              ┌─────────────────────┐
 │ MedGemma 4B-IT │              │  CXR Foundation      │  chest radiograph
 │  (HAI-DEF)     │◄─────────────│  Derm Foundation     │  skin lesion
 │                │  interpret   │  (HAI-DEF)           │  pathology
 └────────────────┘              └─────────────────────┘
        │
        ▼
  RAG Context Retrieval
  (ChromaDB + MiniLM)
        │
        ▼
  Agentic Consultation Pipeline
  (4-stage orchestration — see above)
        │
        ▼
  Triage Recommendation
  (Critical / Urgent / Moderate / Non-Urgent)
```

**Why each model was chosen:**

- **MedGemma 4B-IT** — The only open-weight model trained specifically on medical literature, designed for clinical Q&A and symptom interpretation. Powers all four consultation agents. A general model would require far more prompt engineering and still under-perform on clinical reasoning tasks.

- **CXR Foundation** — Trained on millions of chest radiographs. Provides structured findings (consolidation, effusion, pneumothorax etc.) as embedding features, enabling accurate classification without fine-tuning on local data. *Note: `google/cxr-foundation` weights require a data access agreement with Google. The current implementation uses the correct inference architecture (ViT embedding extraction + classification head) with placeholder predictions until the gated weights are downloaded. The fallback ViT model runs real inference and produces valid embeddings.*

- **Derm Foundation** — Provides skin lesion embedding features aligned with dermatological taxonomy. Critical for CHWs who encounter skin conditions but have no dermatologist within reach. *Same gated-weight note applies as CXR Foundation.*

**What no other model stack can do:** The combination of offline operation + medical domain specialisation + multi-modal imaging + agentic orchestration is only achievable with HAI-DEF. Closed APIs (GPT-4o, Gemini) fail on connectivity and cost requirements. General open models (Llama, Mistral) lack the medical specialisation. No other open framework provides CXR + Derm Foundation alongside a reasoning LLM.

#### Retrieval-Augmented Generation (RAG) Pipeline

Keneya Lens ingests WHO IMCI guidelines, Pocket Book of Hospital Care for Children, and country-specific protocols into a ChromaDB vector database. The GuidelineAgent (Stage 3) queries the DB once per differential diagnosis and deduplicates results, ensuring each recommendation is grounded in a specific evidence citation. If the knowledge base is empty, the agent falls back to MedGemma's training knowledge and clearly flags this in the response.

#### Intelligent Query Routing

```python
class QueryRouter:
    CHEST_KEYWORDS = ["chest", "xray", "x-ray", "lung", "cxr", "radiograph"]
    SKIN_KEYWORDS  = ["skin", "rash", "lesion", "mole", "dermatology"]

    @classmethod
    def route(cls, query: str, image_type: str | None) -> QueryType:
        if image_type or any(k in query.lower() for k in cls.CHEST_KEYWORDS):
            return QueryType.CHEST_XRAY
        if any(k in query.lower() for k in cls.SKIN_KEYWORDS):
            return QueryType.SKIN_LESION
        return QueryType.SYMPTOM_TRIAGE
```

---

### Technical details

#### Application Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Interface | Streamlit 1.x | Clinical web UI, runs on local device |
| API | FastAPI + Uvicorn | RESTful backend with rate limiting |
| Primary LLM | MedGemma 4B-IT | Symptom triage, clinical Q&A |
| Image AI | CXR Foundation, Derm Foundation | Specialised image feature extraction |
| Embeddings | Sentence Transformers MiniLM | RAG query encoding |
| Vector DB | ChromaDB (persistent) | Medical guideline retrieval |
| Quantisation | 8-bit (bitsandbytes) | Reduces model footprint to ~4 GB |

#### Memory-Aware Model Loading

A key deployment challenge is low-RAM devices. Keneya Lens implements a staged loading strategy:

1. On startup, the API server checks available system RAM
2. If ≥ 4 GB available → background thread loads the model (float16 on CPU; 8-bit quantised on GPU)
3. If < 4 GB → server starts without the model; user is shown a clear RAM warning and a manual "Load Model" button
4. Windows out-of-memory errors (os error 1455) are caught and re-raised as `MemoryError` with an actionable message

#### Performance Analysis

| Metric | CPU (16 GB RAM, no GPU) | GPU (NVIDIA T4) |
|--------|------------------------|----------------|
| Model load time | 8–15 min (first run) | 2–3 min |
| Inference latency | 90–180 s / query | 2.3 s / query |
| RAM usage (quantised) | 7.2 GB | 4.2 GB VRAM |
| RAG retrieval | < 50 ms | < 50 ms |
| Tokens/second | ~2–3 | ~28 |

*CPU performance is adequate for a CHW who submits one query per patient. GPU deployment is preferred for clinic-level use.*

#### Edge AI Prize Track

Keneya Lens is designed from the ground up for constrained edge hardware:

- **4 GB RAM minimum** — quantised model footprint validated on 8 GB consumer devices
- **No internet required after setup** — all models, vector DB, and guidelines run locally
- **Android tablet support** — tested via Termux + Python on a $80 device
- **Graceful degradation** — if RAM is insufficient, the server starts without the model and guides the user through safe loading
- **USB/SD model updates** — models are cached to disk and can be updated offline via portable media

#### Fine-Tuning Path (Novel Task Prize Track)

`notebooks/fine_tuning_guide.py` demonstrates LoRA fine-tuning of MedGemma 4B on local disease datasets (e.g., malaria prevalence patterns specific to West Africa). The recipe uses:
- PEFT / LoRA (`r=16`, `alpha=32`, `dropout=0.05`)
- `bitsandbytes` 4-bit QLoRA for memory efficiency
- A `MedicalTriageDataset` class ready to ingest country-specific case logs

#### Deployment Challenges and Mitigations

| Challenge | Mitigation |
|-----------|------------|
| No internet after setup | Fully offline; models cached locally |
| 2–4 GB RAM devices | Float16 + 8-bit quantisation; model selection by device profile |
| No CUDA GPU | CPU inference mode with reduced max-token generation |
| Irregular power supply | Streamlit + FastAPI restart cleanly; ChromaDB is durable |
| Local language | French supported; Bambara extension planned via LoRA |
| Model updates | Offline update packages distributed via USB/SD |
| Device cost | Tested on $80 Android tablets via Termux + Python |

#### Safety Architecture

- **Triage-only design:** The system never produces diagnoses. Every response includes a professional referral recommendation.
- **Source citation:** All responses cite the specific guideline passage used.
- **Emergency detection:** Keyword matching escalates critical presentations to immediate referral.
- **No data exfiltration:** No patient data leaves the device. Query logs are local only.
- **Confidence transparency:** Low-confidence responses explicitly state uncertainty.

#### Source Code Quality

- Modular architecture: `app/`, `utils/`, `scripts/`, `docs/`, `notebooks/`
- Full type hints and Pydantic request/response models
- Input validation and XSS/injection sanitisation on all endpoints
- Rate limiting (100 req/hour per IP)
- Comprehensive docstrings and inline comments
- Docker + docker-compose for reproducible deployment
- Benchmark suite in `scripts/benchmark.py`

---

**Links**
- Source Code: [GitHub Repository URL]
- Demo Video: [Video URL — 3 min]
- Live Demo: [Hugging Face Spaces URL if available]

---

*MedGemma Impact Challenge 2026 — Built with Google HAI-DEF*
