# Deployment Challenges & Solutions

> Technical documentation for deploying Keneya Lens in resource-limited environments

## Overview

Deploying AI-powered medical tools in rural healthcare settings presents unique challenges. This document outlines the key obstacles and our solutions.

---

## 1. Hardware Constraints

### Challenge: Limited Compute Resources

Most rural health posts have access only to basic smartphones or low-end tablets with:
- 2-4 GB RAM
- ARM processors (not GPU)
- Limited storage (32-64 GB)

### Solutions

#### 1.1 Model Quantization

We use 8-bit quantization to reduce model size and memory requirements:

```python
from transformers import BitsAndBytesConfig

quantization_config = BitsAndBytesConfig(
    load_in_8bit=True,
    llm_int8_threshold=6.0
)
```

**Impact:**
| Metric | FP16 | INT8 | Reduction |
|--------|------|------|-----------|
| Model size | 8 GB | 4.2 GB | 48% |
| RAM usage | 10 GB | 5.5 GB | 45% |
| Inference speed | 1.0x | 0.9x | 10% slower |

#### 1.2 Model Selection by Device

```python
def select_model_for_device(available_ram_gb: float) -> str:
    if available_ram_gb >= 16:
        return "google/medgemma-27b-text-it"  # Best accuracy
    elif available_ram_gb >= 8:
        return "google/medgemma-4b-it"  # Balanced
    else:
        return "google/gemma-2-2b-it"  # Minimum viable
```

#### 1.3 CPU-Only Mode

Full support for CPU inference when GPU unavailable:

```python
model_kwargs = {
    "device_map": "cpu",
    "torch_dtype": torch.float32,
    "low_cpu_mem_usage": True
}
```

---

## 2. Connectivity Challenges

### Challenge: No Reliable Internet

60% of rural health posts lack consistent internet connectivity. Some have no connectivity at all.

### Solutions

#### 2.1 Offline-First Architecture

All core functionality works without internet:

```
┌─────────────────────────────────────────┐
│         FULLY OFFLINE COMPONENTS        │
├─────────────────────────────────────────┤
│ • MedGemma model (local)                │
│ • Foundation models (local)             │
│ • ChromaDB vector store (local)         │
│ • Medical guidelines (embedded)         │
│ • Query logging (local JSONL)           │
└─────────────────────────────────────────┘
```

#### 2.2 Pre-Download Package

We provide a complete offline installation package:

```bash
# Download complete offline package (one-time, with internet)
python scripts/download_offline_package.py

# Package contents:
# - MedGemma model weights (~8 GB)
# - Foundation model weights (~4 GB each)
# - Embedding model (~500 MB)
# - Medical guidelines PDFs (~200 MB)
# - Pre-built vector database
```

#### 2.3 Periodic Update Mechanism

For locations with occasional connectivity:

```python
class OfflineUpdateManager:
    def check_for_updates(self):
        """Check for updates when connectivity available."""
        pass

    def download_update_package(self):
        """Download incremental update package."""
        pass

    def apply_updates_offline(self):
        """Apply downloaded updates without internet."""
        pass
```

---

## 3. Power Constraints

### Challenge: Unreliable Electricity

Many rural health posts rely on:
- Solar power (intermittent)
- Generator power (limited hours)
- No electricity at all

### Solutions

#### 3.1 Low-Power Mode

Optimizations for battery-powered devices:

```python
class PowerAwareInference:
    def __init__(self, battery_threshold: float = 0.2):
        self.battery_threshold = battery_threshold

    def should_use_low_power_mode(self) -> bool:
        # Check battery level
        battery = psutil.sensors_battery()
        return battery and battery.percent < self.battery_threshold * 100

    def get_inference_config(self):
        if self.should_use_low_power_mode():
            return {
                "max_new_tokens": 256,  # Reduced from 512
                "num_beams": 1,  # Disable beam search
                "do_sample": False  # Greedy decoding
            }
        return {"max_new_tokens": 512, "do_sample": True}
```

#### 3.2 Response Caching

Cache frequent queries to reduce computation:

```python
class ResponseCache:
    def __init__(self, cache_size: int = 100):
        self.cache = OrderedDict()
        self.cache_size = cache_size

    def get_cached_response(self, query_hash: str):
        return self.cache.get(query_hash)

    def cache_response(self, query_hash: str, response: dict):
        if len(self.cache) >= self.cache_size:
            self.cache.popitem(last=False)
        self.cache[query_hash] = response
```

#### 3.3 Hardware Recommendations

| Use Case | Device | Power Solution | Runtime |
|----------|--------|----------------|---------|
| Basic | Android phone | USB power bank | 8-12 hours |
| Standard | Android tablet | Solar charger | Continuous |
| Advanced | Mini PC | Solar + battery | Continuous |

---

## 4. Language & Localization

### Challenge: Local Language Support

Users may not be fluent in English or French. Local languages (Bambara, Wolof, etc.) have limited NLP resources.

### Solutions

#### 4.1 Multi-Language System Prompts

```python
SYSTEM_PROMPTS = {
    "en": "You are a medical assistant helping healthcare workers...",
    "fr": "Vous êtes un assistant médical aidant les agents de santé...",
    "bm": "I ye dɔgɔtɔrɔ dɛmɛbaga ye..."  # Bambara
}

def get_system_prompt(language: str) -> str:
    return SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
```

#### 4.2 Translation Layer

For languages not natively supported:

```python
class LocalLanguageAdapter:
    def __init__(self, source_lang: str, target_lang: str = "en"):
        self.translator = load_offline_translator(source_lang, target_lang)

    def translate_input(self, text: str) -> str:
        """Translate user input to English for processing."""
        return self.translator.translate(text)

    def translate_output(self, text: str) -> str:
        """Translate response back to local language."""
        return self.translator.translate_reverse(text)
```

#### 4.3 Visual/Audio Interface (Future)

- Icon-based symptom selection
- Voice input/output support
- Pictorial guidelines

---

## 5. Model Update & Maintenance

### Challenge: Keeping Models Current

Medical knowledge evolves. Models need updates for:
- New disease outbreaks
- Updated treatment guidelines
- Bug fixes and improvements

### Solutions

#### 5.1 Modular Architecture

Guidelines are separate from model weights:

```
keneya_lens/
├── models/           # Model weights (rarely updated)
│   ├── medgemma/
│   └── foundations/
├── guidelines/       # Medical guidelines (frequently updated)
│   ├── who_imci_2024.pdf
│   └── local_protocols.pdf
└── data/
    └── chroma_db/    # Re-indexed when guidelines update
```

#### 5.2 Differential Updates

Only download changed components:

```python
class UpdateManager:
    def get_update_manifest(self) -> dict:
        """Fetch manifest of available updates."""
        pass

    def download_differential_update(self, current_version: str):
        """Download only changed files."""
        pass

    def verify_update_integrity(self, package_path: str) -> bool:
        """Verify update package checksum."""
        pass
```

#### 5.3 Version Management

```python
VERSION_INFO = {
    "app_version": "1.2.0",
    "medgemma_version": "4b-it-v1",
    "guidelines_version": "2024.02",
    "min_compatible_app": "1.0.0"
}
```

---

## 6. User Training & Support

### Challenge: Limited Technical Skills

CHWs typically have:
- Basic smartphone experience
- Limited technical training
- No IT support on-site

### Solutions

#### 6.1 Progressive Onboarding

```python
class OnboardingFlow:
    STEPS = [
        "welcome",           # Introduction
        "basic_query",       # Try a simple symptom query
        "interpret_result",  # Understand the response
        "image_upload",      # (Optional) Medical image analysis
        "emergency_alert",   # Recognize emergency indicators
        "completion"         # Certification
    ]
```

#### 6.2 In-App Guidance

Contextual help at every step:

```python
HELP_TOOLTIPS = {
    "symptom_input": "Describe the patient's symptoms in your own words. Include: duration, severity, and any other observations.",
    "triage_result": "🔴 = Urgent referral needed\n🟡 = Schedule appointment\n🟢 = Can manage locally",
    "confidence_score": "Higher confidence means the AI is more certain. Always use clinical judgment."
}
```

#### 6.3 Offline Training Materials

- Video tutorials (downloadable)
- Quick reference cards (printable)
- Case study examples

---

## 7. Data Privacy & Security

### Challenge: Patient Data Protection

Even in resource-limited settings, patient privacy must be protected.

### Solutions

#### 7.1 Local-Only Processing

```python
class PrivacyConfig:
    TELEMETRY_ENABLED = False
    CLOUD_SYNC_ENABLED = False
    LOCAL_STORAGE_ONLY = True
    ENCRYPT_LOCAL_LOGS = True
```

#### 7.2 Data Minimization

```python
class QueryLogger:
    def log_query(self, query: str, response: dict):
        # Log only essential metadata, not full content
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "query_length": len(query),
            "response_type": response.get("triage_level"),
            "model_used": response.get("model"),
            # NO patient-identifiable information
        }
        self._write_log(log_entry)
```

#### 7.3 Secure Export

For supervision/audit purposes:

```python
class SecureExporter:
    def export_aggregated_statistics(self) -> dict:
        """Export only aggregated, anonymized statistics."""
        return {
            "total_queries": self.count_queries(),
            "triage_distribution": self.get_triage_stats(),
            "common_symptoms": self.get_anonymized_symptom_categories()
        }
```

---

## 8. Integration with Health Systems

### Challenge: Interoperability

Health posts may use existing systems (paper registers, DHIS2, etc.).

### Solutions

#### 8.1 Export Formats

```python
EXPORT_FORMATS = {
    "csv": CSVExporter,
    "json": JSONExporter,
    "fhir": FHIRExporter,  # Healthcare interoperability standard
    "dhis2": DHIS2Exporter  # Common in Africa
}
```

#### 8.2 Offline Sync Queue

```python
class SyncQueue:
    def queue_for_sync(self, record: dict):
        """Queue record for sync when connectivity available."""
        self.pending_records.append(record)
        self._save_queue()

    def sync_when_online(self):
        """Batch sync pending records."""
        if self._check_connectivity():
            self._upload_batch(self.pending_records)
            self.pending_records.clear()
```

---

## 9. Deployment Checklist

### Pre-Deployment

- [ ] Hardware meets minimum requirements
- [ ] Complete offline package downloaded
- [ ] Local language support configured
- [ ] Power solution verified
- [ ] User training completed

### Deployment

- [ ] Install application
- [ ] Load model weights
- [ ] Index medical guidelines
- [ ] Configure local settings
- [ ] Run validation tests

### Post-Deployment

- [ ] Monitor usage patterns
- [ ] Collect user feedback
- [ ] Schedule update checks
- [ ] Plan supervision visits

---

## 10. Support Resources

### Technical Support

- **Documentation:** [GitHub Wiki]
- **Issue Tracker:** [GitHub Issues]
- **Community Forum:** [Discussions]

### Training Materials

- Quick Start Guide (PDF)
- Video Tutorials (offline package)
- Reference Card (printable)

### Emergency Contacts

- Technical Lead: [Contact]
- Medical Advisor: [Contact]
- Regional Coordinator: [Contact]

---

*Document Version: 1.0 | Last Updated: February 2026*
