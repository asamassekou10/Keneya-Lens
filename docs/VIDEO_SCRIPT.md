# Keneya Lens — 3-Minute Demo Video Script

**Total time target: 2:50 – 3:00**
**Format: screen recording + voiceover (or talking head in corner)**
**No background music required — clean professional recording**

---

## Pre-recording Checklist

- [ ] API server running: `python run_api.py`
- [ ] Streamlit running: `streamlit run app/streamlit_app.py`
- [ ] Model loaded (click Load Model, wait for "Ready" status)
- [ ] Sample symptoms text ready to paste
- [ ] Sample image ready (chest X-ray or skin lesion JPEG)
- [ ] Browser zoom at 100%, full screen
- [ ] Screen recorder started, mic tested

---

## Script

### [0:00 – 0:20] Opening — Problem Statement

**[Show: Keneya Lens running in browser, header visible]**

> "In rural Mali, there is one doctor for every 25,000 people. Community health workers —
> frontline volunteers with just a few weeks of training — make critical triage decisions
> every day, without internet and without expert support.
>
> Keneya Lens changes that. It's an offline-first clinical decision support system built
> entirely on Google's Health AI Developer Foundations."

---

### [0:20 – 0:45] System Overview

**[Show: Sidebar — system status "Model Ready", RAM indicator, tabs visible]**

> "The application runs as a local FastAPI backend with a Streamlit interface.
> It uses three HAI-DEF models: MedGemma 4B for clinical reasoning,
> CXR Foundation for chest radiograph analysis, and Derm Foundation for skin lesions —
> all running on the device, no internet required.
>
> The sidebar shows real-time system status including available RAM.
> When memory is constrained, the interface guides the user through loading the model safely."

---

### [0:45 – 1:30] Feature 1 — Symptom Triage Analysis

**[Click "Symptom Analysis" tab]**
**[Paste into the text area:]**
```
4-year-old boy, 3-day history of cough and fever 38.8°C.
Respiratory rate 42 breaths/min, refusing food, mild subcostal indrawing.
No prior illness, no medications. Located 40 km from nearest clinic.
```

**[Click "Analyze"]**

> "The health worker types the patient's presentation. Keneya Lens routes the query through
> the RAG pipeline — retrieving the most relevant passages from ingested WHO IMCI guidelines —
> and passes both to MedGemma."

**[Wait for result — triage indicator appears]**

> "The response is structured with a triage level — here, Urgent — a clinical assessment
> grounded in evidence, and citations to the specific guideline sections used.
> The system never diagnoses. It supports the decision."

---

### [1:30 – 2:05] Feature 2 — Medical Image Analysis

**[Click "Image Analysis" tab]**
**[Select "Chest Radiograph" from dropdown]**
**[Upload sample chest X-ray image]**
**[Type in context: "Same 4-year-old, X-ray taken at district hospital"]**
**[Click "Analyze Image"]**

> "For image analysis, the system uses CXR Foundation — Google's model trained on
> millions of chest radiographs. It extracts structured findings from the image,
> then MedGemma synthesises a clinical interpretation and triage recommendation.
>
> The same pipeline applies to skin lesions via Derm Foundation."

**[Result appears]**

---

### [2:05 – 2:25] Feature 3 — Query History & Knowledge Base

**[Click "Query History" tab]**

> "Every query is logged locally — no data ever leaves the device.
> Supervisors can review CHW decision patterns, and logs feed into future
> fine-tuning of the models for local disease prevalence."

**[Briefly show sidebar expander for PDF upload]**

> "Clinical guidelines are uploaded as PDFs and indexed into the vector database.
> The system ships with WHO IMCI guidelines and supports any evidence base the
> deployment team provides."

---

### [2:25 – 2:50] Closing — Impact and HAI-DEF

**[Show: System Information tab or return to Symptom Analysis with result visible]**

> "In a Mali deployment of 10,000 community health workers, Keneya Lens is projected
> to prevent 13.8 million unnecessary referrals per year — saving $207 million in
> transport costs — and to catch an additional 780,000 serious cases that would otherwise
> be missed at first presentation.
>
> This is only possible with HAI-DEF. Open weights allow full offline deployment.
> Medical specialisation makes the output trustworthy. And the multi-model ecosystem —
> MedGemma, CXR Foundation, Derm Foundation — gives comprehensive coverage across
> the cases CHWs actually face.
>
> Keneya Lens. Health AI where it's needed most."

---

## Post-production Notes

- Trim any model loading wait time — cut to result appearing
- Add subtle lower-third text labels when switching features
- No music, but a clean fade-in/out is fine
- Export at 1080p, H.264, under 500 MB
- Upload to YouTube (unlisted) or Google Drive and paste link in submission
