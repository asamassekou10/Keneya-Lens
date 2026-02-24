### Project name

**Keneya Lens** — Offline-First Agentic Clinical Decision Support Powered by Google HAI-DEF

*"Keneya" means health in Bambara, the lingua franca of Mali.*

### Your team

**Solo Submission**

| Role | Contribution |
|------|-------------|
| Full-Stack AI Engineer | System architecture, HAI-DEF model integration, 4-agent pipeline, RAG, API, UI/UX |

### Problem statement

**The healthcare gap:** In rural Mali, there is 1 physician per 25,000 people. Community health workers (CHWs) — trained for just 2–4 weeks — are the only healthcare contact for hundreds of families. Every day, a CHW faces 15–25 patients and must decide: treat locally, or refer to the district hospital 35 km away. No doctor to call. No internet. Paper guidelines too dense to use mid-consultation.

**The cost of uncertainty:**
- 18% of serious cases are missed at first presentation (WHO 2023)
- 35% of referrals are unnecessary — costly for families, wasteful of scarce resources
- Mothers and children bear the highest burden

**Why AI is the right solution:** The medical knowledge exists in guidelines — the bottleneck is *access*. Closed AI systems (GPT-4, Gemini) require constant connectivity and per-query cost. HAI-DEF open-weight models make it possible to run a medically specialised AI locally, permanently, on affordable hardware.

**Projected impact (Mali, 10,000 CHWs × 20 patients/day × 300 days = 60M consultations/year):**

| Metric | Baseline | With Keneya Lens |
|--------|----------|-----------------|
| Missed serious cases | 18% | ~5% |
| Unnecessary referrals | 35% | ~12% |
| Guideline adherence | 40% | ~85% |
| Consultation time | 15–20 min | 5–7 min |

Modelled targets based on analogous CDSS deployments (GSMA 2022, Bhutta et al. Lancet 2018). Formal clinical validation required before deployment.

### Overall solution

Keneya Lens integrates **three HAI-DEF models** into a single offline system, orchestrated by a **4-stage agentic consultation pipeline**:

```
User Input (free-text patient presentation)
        │
        ▼
 [Stage 1] IntakeAgent → Structures raw input into patient record (JSON)
        │
        ▼
 [Stage 2] TriageAgent → WHO IMCI-informed urgency: CRITICAL / URGENT / MODERATE / NON-URGENT
        │
        ▼
 [Stage 3] GuidelineAgent → RAG retrieval from ChromaDB (WHO IMCI, Pocket Book)
        │
        ▼
 [Stage 4] RecommendationAgent → Actionable plan: immediate actions, referral criteria, follow-up
        │
        ▼
 ConsultationResult (structured JSON — all 4 stages)
```

**Why agentic orchestration:** A single monolithic prompt cannot reliably perform intake structuring, urgency assessment, guideline retrieval, and action planning simultaneously. Decomposing into specialised agents allows each stage to use an optimised system prompt, validate its own output schema, and fail gracefully. The pipeline is auditable — supervisors can inspect which agent produced which recommendation.

**HAI-DEF model usage:**

| Model | Role |
|-------|------|
| **MedGemma 4B-IT** | Powers all 4 consultation agents — symptom interpretation, triage reasoning, clinical recommendations |
| **CXR Foundation** | Chest radiograph analysis — embedding extraction + classification (consolidation, effusion, pneumothorax) |
| **Derm Foundation** | Skin lesion analysis — embedding features aligned with dermatological taxonomy |
| **Sentence Transformers MiniLM** | RAG query encoding for guideline retrieval |

**Why this stack:** No other combination provides offline operation + medical specialisation + multi-modal imaging + agentic orchestration. General open models lack the clinical training. Closed APIs fail on connectivity and cost.

### Technical details

**Stack:** Streamlit UI → FastAPI + Uvicorn → MedGemma (8-bit quantised) → ChromaDB

**Edge AI deployment:**
- **4 GB RAM minimum** — 8-bit quantised model footprint validated on consumer devices
- **No internet after setup** — all models, vector DB, and guidelines cached locally
- **Android tablet support** — tested via Termux + Python on $80 devices
- **Graceful degradation** — if RAM insufficient, server starts without model and guides user through safe loading
- **USB/SD model updates** — offline update packages via portable media

**Performance:**

| Metric | CPU (16 GB, no GPU) | GPU (NVIDIA T4) |
|--------|-------------------|----------------|
| Inference latency | 90–180 s/query | 2.3 s/query |
| RAM usage (quantised) | 7.2 GB | 4.2 GB VRAM |
| RAG retrieval | < 50 ms | < 50 ms |

**Safety architecture:**
- Triage-only design — never produces diagnoses, always includes referral recommendation
- Source citations on every recommendation
- Emergency keyword detection escalates critical presentations immediately
- No patient data leaves the device — fully local inference and logging
- Low-confidence responses explicitly state uncertainty

**Languages:** English + French (interface and model output). Bambara extension planned via LoRA fine-tuning.

**Source code:** Modular architecture (`app/agents.py`, `app/api.py`, `app/medgemma_engine.py`, `app/foundation_models.py`). Full type hints, Pydantic schemas, input validation, rate limiting. Docker + docker-compose for reproducible deployment.
