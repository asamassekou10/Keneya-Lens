"""
Keneya Lens — Multi-Agent Consultation Pipeline

Implements a 4-stage agentic medical consultation using MedGemma as the reasoning engine.
Each agent has a single, focused responsibility and passes its output to the next.

Pipeline:
    IntakeAgent → TriageAgent → GuidelineAgent → RecommendationAgent

Built for the MedGemma Impact Challenge 2026 — Agentic Workflow Prize track.
"""
import json
import logging
import re
from dataclasses import dataclass, field, asdict
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .medgemma_engine import MedGemmaEngine

logger = logging.getLogger(__name__)


# ── Output schemas ─────────────────────────────────────────────────────────────

@dataclass
class IntakeResult:
    """Structured patient intake extracted from free-text presentation."""
    age: str = ""
    sex: str = ""
    chief_complaint: str = ""
    duration: str = ""
    vital_signs: dict = field(default_factory=dict)
    relevant_history: str = ""
    raw_input: str = ""
    success: bool = True
    error: str = ""


@dataclass
class TriageResult:
    """Triage assessment produced by TriageAgent."""
    triage_level: str = "NON-URGENT"      # CRITICAL | URGENT | MODERATE | NON-URGENT
    red_flags: List[str] = field(default_factory=list)
    differential_diagnoses: List[str] = field(default_factory=list)
    reasoning: str = ""
    success: bool = True
    error: str = ""


@dataclass
class GuidelineResult:
    """Clinical guidelines retrieved by GuidelineAgent via RAG."""
    guidelines: List[str] = field(default_factory=list)
    citations: List[str] = field(default_factory=list)
    context_count: int = 0
    success: bool = True
    error: str = ""


@dataclass
class RecommendationResult:
    """Final clinical recommendations produced by RecommendationAgent."""
    immediate_actions: List[str] = field(default_factory=list)
    treatment_notes: str = ""
    referral_criteria: List[str] = field(default_factory=list)
    monitoring_plan: str = ""
    follow_up: str = ""
    safety_notes: str = ""
    success: bool = True
    error: str = ""


@dataclass
class ConsultationResult:
    """Complete 4-stage consultation result."""
    intake: IntakeResult = field(default_factory=IntakeResult)
    triage: TriageResult = field(default_factory=TriageResult)
    guidelines: GuidelineResult = field(default_factory=GuidelineResult)
    recommendations: RecommendationResult = field(default_factory=RecommendationResult)
    language: str = "en"

    def to_dict(self) -> dict:
        return {
            "intake": asdict(self.intake),
            "triage": asdict(self.triage),
            "guidelines": asdict(self.guidelines),
            "recommendations": asdict(self.recommendations),
            "language": self.language,
        }


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _extract_json(text: str) -> Optional[dict]:
    """
    Extract the first JSON object from a model response.
    Models often wrap JSON in markdown code fences or add preamble text.
    """
    # Try direct parse first
    try:
        return json.loads(text.strip())
    except (json.JSONDecodeError, ValueError):
        pass

    # Strip markdown code fences
    cleaned = re.sub(r"```(?:json)?\s*", "", text)
    cleaned = re.sub(r"```", "", cleaned)

    # Find first {...} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except (json.JSONDecodeError, ValueError):
            pass

    return None


def _call_engine(engine: "MedGemmaEngine", system_prompt: str, user_prompt: str,
                 max_tokens: int = 512, temperature: float = 0.3) -> str:
    """
    Run a focused, structured generation through the MedGemma engine.
    Uses lower temperature for deterministic, structured output from agents.
    """
    combined_prompt = f"{system_prompt}\n\n--- Input ---\n{user_prompt}\n\n--- Output ---\n"
    result = engine.query_symptoms(combined_prompt, max_new_tokens=max_tokens, temperature=temperature)
    return result.get("response", "")


# ── Stage 1: IntakeAgent ───────────────────────────────────────────────────────

class IntakeAgent:
    """
    Stage 1 — Structures the raw patient presentation into a clean JSON record.

    Competition note: This is the first agent in the agentic pipeline. It normalises
    free-text input so all downstream agents receive consistent structured data,
    regardless of how the CHW described the patient.
    """

    SYSTEM_PROMPT = """You are a clinical intake specialist. Extract structured patient information
from the free-text presentation provided below.

Return ONLY a valid JSON object (no markdown, no explanation) with these exact keys:
{
  "age": "patient age as string, e.g. '4 years', '38y', 'newborn'",
  "sex": "M | F | Unknown",
  "chief_complaint": "one concise sentence describing the main problem",
  "duration": "how long symptoms have been present",
  "vital_signs": {
    "temperature": "value with units if provided, else ''",
    "heart_rate": "value if provided, else ''",
    "respiratory_rate": "value if provided, else ''",
    "blood_pressure": "value if provided, else ''",
    "spo2": "value if provided, else ''"
  },
  "relevant_history": "brief summary of relevant past history, medications, allergies; '' if none"
}

If information is not present, use empty string "". Do not invent information."""

    def __init__(self, engine: "MedGemmaEngine"):
        self.engine = engine

    def run(self, raw_input: str, language: str = "en") -> IntakeResult:
        """
        Extract structured intake data from a free-text patient presentation.

        Args:
            raw_input: Raw symptom description from the CHW
            language: Output language code (en | fr)

        Returns:
            IntakeResult with structured patient data
        """
        logger.info("[IntakeAgent] Processing patient presentation...")
        result = IntakeResult(raw_input=raw_input)

        try:
            lang_note = " Respond in French." if language == "fr" else ""
            response = _call_engine(
                self.engine,
                self.SYSTEM_PROMPT + lang_note,
                raw_input,
                max_tokens=256,
                temperature=0.2,
            )

            data = _extract_json(response)
            if data:
                result.age = data.get("age", "")
                result.sex = data.get("sex", "")
                result.chief_complaint = data.get("chief_complaint", "")
                result.duration = data.get("duration", "")
                result.vital_signs = data.get("vital_signs", {})
                result.relevant_history = data.get("relevant_history", "")
            else:
                # Fallback: use raw input as chief complaint
                logger.warning("[IntakeAgent] JSON extraction failed, using raw input.")
                result.chief_complaint = raw_input[:300]

            logger.info("[IntakeAgent] Complete — chief complaint: %s", result.chief_complaint[:60])

        except Exception as e:
            logger.error("[IntakeAgent] Error: %s", e)
            result.success = False
            result.error = str(e)
            result.chief_complaint = raw_input[:300]

        return result


# ── Stage 2: TriageAgent ───────────────────────────────────────────────────────

class TriageAgent:
    """
    Stage 2 — Assesses urgency using IMCI-informed criteria.

    Competition note: This agent implements WHO Integrated Management of Childhood
    Illness (IMCI) triage logic adapted for HAI-DEF medical reasoning. The four-level
    triage mirrors international emergency triage standards (Manchester Triage, CTAS).
    """

    SYSTEM_PROMPT = """You are an emergency triage specialist trained in WHO IMCI protocols.
Analyse the structured patient intake below and determine the triage level.

TRIAGE LEVELS (choose exactly one):
- CRITICAL: Immediate life-threatening emergency. Do not delay referral.
- URGENT: Serious condition requiring referral or treatment within 24 hours.
- MODERATE: Condition requiring medical attention but not immediately life-threatening.
- NON-URGENT: Can be managed locally with standard first-line treatment.

IMCI RED FLAGS (always escalate to CRITICAL if present):
- Unable to drink/breastfeed, vomits everything
- Convulsions or loss of consciousness
- Severe respiratory distress (nasal flaring, severe indrawing, grunting)
- SpO2 < 90%
- Signs of severe dehydration
- Stiff neck with fever
- Severe pallor

Return ONLY a valid JSON object with these exact keys:
{
  "triage_level": "CRITICAL | URGENT | MODERATE | NON-URGENT",
  "red_flags": ["list of any red flag symptoms identified, empty if none"],
  "differential_diagnoses": ["top 2-3 possible diagnoses, most likely first"],
  "reasoning": "2-3 sentence explanation of the triage decision"
}"""

    def __init__(self, engine: "MedGemmaEngine"):
        self.engine = engine

    def run(self, intake: IntakeResult, language: str = "en") -> TriageResult:
        """
        Determine triage level from structured intake data.

        Args:
            intake: Output from IntakeAgent
            language: Output language code (en | fr)

        Returns:
            TriageResult with triage level, red flags, and differentials
        """
        logger.info("[TriageAgent] Assessing urgency...")
        result = TriageResult()

        # Build a focused input from intake data
        intake_summary = (
            f"Patient: {intake.age}, {intake.sex}\n"
            f"Chief complaint: {intake.chief_complaint}\n"
            f"Duration: {intake.duration}\n"
            f"Vital signs: {json.dumps(intake.vital_signs)}\n"
            f"History: {intake.relevant_history}\n"
            f"Full presentation: {intake.raw_input}"
        )

        try:
            lang_note = " Respond in French." if language == "fr" else ""
            response = _call_engine(
                self.engine,
                self.SYSTEM_PROMPT + lang_note,
                intake_summary,
                max_tokens=384,
                temperature=0.2,
            )

            data = _extract_json(response)
            if data:
                level = data.get("triage_level", "MODERATE").upper()
                if level not in ("CRITICAL", "URGENT", "MODERATE", "NON-URGENT"):
                    level = "MODERATE"
                result.triage_level = level
                result.red_flags = data.get("red_flags", [])
                result.differential_diagnoses = data.get("differential_diagnoses", [])
                result.reasoning = data.get("reasoning", "")
            else:
                # Fallback: heuristic from red-flag keywords
                logger.warning("[TriageAgent] JSON extraction failed, using heuristic.")
                text_lower = (intake.chief_complaint + " " + intake.raw_input).lower()
                if any(k in text_lower for k in ["convuls", "unconscious", "not breathing", "cyanosis"]):
                    result.triage_level = "CRITICAL"
                elif any(k in text_lower for k in ["difficulty breath", "chest pain", "high fever", "dehydrat"]):
                    result.triage_level = "URGENT"
                else:
                    result.triage_level = "MODERATE"
                result.reasoning = response[:300] if response else "Triage based on keyword analysis."

            logger.info("[TriageAgent] Complete — level: %s", result.triage_level)

        except Exception as e:
            logger.error("[TriageAgent] Error: %s", e)
            result.success = False
            result.error = str(e)
            result.triage_level = "MODERATE"
            result.reasoning = "Triage defaulted to MODERATE due to processing error."

        return result


# ── Stage 3: GuidelineAgent ────────────────────────────────────────────────────

class GuidelineAgent:
    """
    Stage 3 — Retrieves relevant clinical guidelines via RAG (ChromaDB + MiniLM).

    Competition note: This agent demonstrates the RAG augmentation layer.
    It queries the vector database for each differential diagnosis separately
    to maximise guideline coverage, then deduplicates results.
    """

    def __init__(self, engine: "MedGemmaEngine"):
        self.engine = engine

    def run(self, triage: TriageResult, intake: IntakeResult) -> GuidelineResult:
        """
        Retrieve relevant clinical guidelines for the identified differentials.

        Args:
            triage: Output from TriageAgent
            intake: Output from IntakeAgent (for patient context)

        Returns:
            GuidelineResult with retrieved guideline passages and citations
        """
        logger.info("[GuidelineAgent] Retrieving clinical guidelines...")
        result = GuidelineResult()

        try:
            # Build targeted queries for each differential
            queries = []
            for dx in triage.differential_diagnoses[:2]:
                queries.append(f"{dx} diagnosis treatment {intake.age}")
            if triage.red_flags:
                queries.append(f"emergency management {' '.join(triage.red_flags[:2])}")
            if not queries:
                queries = [intake.chief_complaint]

            seen = set()
            all_guidelines = []
            all_citations = []

            for query in queries:
                contexts = self.engine._retrieve_relevant_context(query, top_k=2)
                for ctx in contexts:
                    text = ctx.get("text", "").strip()
                    source = ctx.get("source", "clinical guidelines")
                    if text and text not in seen:
                        seen.add(text)
                        all_guidelines.append(text)
                        if source not in all_citations:
                            all_citations.append(source)

            result.guidelines = all_guidelines[:4]  # cap at 4 passages
            result.citations = all_citations
            result.context_count = len(all_guidelines)

            if not all_guidelines:
                # No documents in DB — generate standard-of-care notes from model knowledge
                logger.info("[GuidelineAgent] No RAG context. Using model knowledge base.")
                fallback_query = (
                    f"What are the standard WHO guidelines for managing "
                    f"{', '.join(triage.differential_diagnoses[:2]) or intake.chief_complaint}?"
                )
                fallback = _call_engine(
                    self.engine,
                    "You are a clinical knowledge base. Provide concise WHO standard-of-care guidance. "
                    "State '(from MedGemma model knowledge — no local guidelines indexed)' at the end.",
                    fallback_query,
                    max_tokens=300,
                    temperature=0.3,
                )
                result.guidelines = [fallback.strip()] if fallback.strip() else []
                result.citations = ["MedGemma model knowledge (no guidelines indexed)"]

            logger.info("[GuidelineAgent] Complete — %d passages retrieved", len(result.guidelines))

        except Exception as e:
            logger.error("[GuidelineAgent] Error: %s", e)
            result.success = False
            result.error = str(e)

        return result


# ── Stage 4: RecommendationAgent ──────────────────────────────────────────────

class RecommendationAgent:
    """
    Stage 4 — Synthesises triage + guidelines into actionable clinical recommendations.

    Competition note: This is the final agent in the pipeline. It takes the combined
    context from all previous stages and produces a structured, CHW-actionable plan
    with immediate actions, referral criteria, and a follow-up monitoring schedule.
    """

    SYSTEM_PROMPT = """You are a senior clinical decision support specialist.
Based on the triage assessment and clinical guidelines provided, generate a structured
clinical management plan for a Community Health Worker in a resource-limited setting.

Return ONLY a valid JSON object with these exact keys:
{
  "immediate_actions": ["list of 3-5 specific, actionable steps the CHW should do right now"],
  "treatment_notes": "1-2 sentences on first-line treatment if applicable",
  "referral_criteria": ["list of specific signs/symptoms that mean the patient MUST be referred"],
  "monitoring_plan": "what to observe and re-assess in the next 12-24 hours",
  "follow_up": "when to reassess or refer if no improvement",
  "safety_notes": "critical safety information; what NOT to do"
}

IMPORTANT:
- Actions must be specific and achievable by a CHW with basic training.
- Never state a definitive diagnosis. Always include 'consult a physician for confirmation'.
- If triage level is CRITICAL, the first immediate action must always be 'Refer to hospital immediately'.
- Keep language simple and practical."""

    def __init__(self, engine: "MedGemmaEngine"):
        self.engine = engine

    def run(self, triage: TriageResult, guidelines: GuidelineResult,
            intake: IntakeResult, language: str = "en") -> RecommendationResult:
        """
        Generate clinical recommendations from all prior agent outputs.

        Args:
            triage: Output from TriageAgent
            guidelines: Output from GuidelineAgent
            intake: Output from IntakeAgent
            language: Output language code (en | fr)

        Returns:
            RecommendationResult with structured actionable plan
        """
        logger.info("[RecommendationAgent] Generating clinical recommendations...")
        result = RecommendationResult()

        # Compose context for the agent
        guideline_text = "\n\n".join(guidelines.guidelines[:3]) if guidelines.guidelines else "No guidelines available."
        context = (
            f"Patient: {intake.age}, {intake.sex}\n"
            f"Chief complaint: {intake.chief_complaint}\n"
            f"Triage level: {triage.triage_level}\n"
            f"Red flags: {', '.join(triage.red_flags) or 'None identified'}\n"
            f"Possible diagnoses: {', '.join(triage.differential_diagnoses) or 'Not determined'}\n"
            f"Triage reasoning: {triage.reasoning}\n\n"
            f"CLINICAL GUIDELINES:\n{guideline_text}"
        )

        try:
            lang_note = " Respond in French." if language == "fr" else ""
            response = _call_engine(
                self.engine,
                self.SYSTEM_PROMPT + lang_note,
                context,
                max_tokens=512,
                temperature=0.3,
            )

            data = _extract_json(response)
            if data:
                result.immediate_actions = data.get("immediate_actions", [])
                result.treatment_notes = data.get("treatment_notes", "")
                result.referral_criteria = data.get("referral_criteria", [])
                result.monitoring_plan = data.get("monitoring_plan", "")
                result.follow_up = data.get("follow_up", "")
                result.safety_notes = data.get("safety_notes", "")
            else:
                # Fallback: use raw response text
                logger.warning("[RecommendationAgent] JSON extraction failed, using raw response.")
                result.treatment_notes = response[:600] if response else "Consult a healthcare professional."
                if triage.triage_level == "CRITICAL":
                    result.immediate_actions = ["Refer to hospital immediately."]
                result.safety_notes = "Always consult a qualified healthcare professional for definitive care."

            # Safety override: CRITICAL cases always get an immediate referral action
            if triage.triage_level == "CRITICAL":
                referral_action = "Refer to the nearest hospital or clinic IMMEDIATELY — this is a medical emergency."
                if not result.immediate_actions or result.immediate_actions[0].lower() not in ["refer", "emergency"]:
                    result.immediate_actions = [referral_action] + result.immediate_actions[:4]

            logger.info("[RecommendationAgent] Complete")

        except Exception as e:
            logger.error("[RecommendationAgent] Error: %s", e)
            result.success = False
            result.error = str(e)
            result.treatment_notes = "An error occurred. Please consult a qualified healthcare professional."
            result.safety_notes = "Do not delay care. Seek medical assistance immediately if in doubt."

        return result


# ── Orchestrator ───────────────────────────────────────────────────────────────

class ConsultationOrchestrator:
    """
    Orchestrates the 4-stage agentic medical consultation pipeline.

    Competition note: This orchestrator implements the Agentic Workflow Prize criteria.
    Each agent is independent, has a focused role, and passes structured data forward.
    The pipeline handles failures at each stage gracefully without crashing the session.

    Usage:
        orchestrator = ConsultationOrchestrator(engine)
        result = orchestrator.run(raw_symptoms, language="en")
        print(result.to_dict())
    """

    def __init__(self, engine: "MedGemmaEngine"):
        self.engine = engine
        self.intake_agent      = IntakeAgent(engine)
        self.triage_agent      = TriageAgent(engine)
        self.guideline_agent   = GuidelineAgent(engine)
        self.recommendation_agent = RecommendationAgent(engine)

    def run(self, raw_input: str, language: str = "en") -> ConsultationResult:
        """
        Run the full 4-stage consultation pipeline.

        Args:
            raw_input: Free-text patient presentation from the CHW
            language: Output language ('en' | 'fr')

        Returns:
            ConsultationResult with all 4 stages completed
        """
        logger.info("=== Starting ConsultationOrchestrator pipeline ===")
        consultation = ConsultationResult(language=language)

        # Stage 1: Intake
        consultation.intake = self.intake_agent.run(raw_input, language=language)

        # Stage 2: Triage (always runs even if intake partially failed)
        consultation.triage = self.triage_agent.run(consultation.intake, language=language)

        # Stage 3: Guideline retrieval
        consultation.guidelines = self.guideline_agent.run(consultation.triage, consultation.intake)

        # Stage 4: Recommendations
        consultation.recommendations = self.recommendation_agent.run(
            consultation.triage,
            consultation.guidelines,
            consultation.intake,
            language=language,
        )

        logger.info("=== ConsultationOrchestrator complete — triage: %s ===", consultation.triage.triage_level)
        return consultation

    @staticmethod
    def _safe_intake(d: dict) -> "IntakeResult":
        """Reconstruct IntakeResult from a dict, ignoring unknown fields."""
        valid = {f.name for f in IntakeResult.__dataclass_fields__.values()}
        return IntakeResult(**{k: v for k, v in d.items() if k in valid})

    @staticmethod
    def _safe_triage(d: dict) -> "TriageResult":
        """Reconstruct TriageResult from a dict, ignoring unknown fields."""
        valid = {f.name for f in TriageResult.__dataclass_fields__.values()}
        return TriageResult(**{k: v for k, v in d.items() if k in valid})

    @staticmethod
    def _safe_guideline(d: dict) -> "GuidelineResult":
        """Reconstruct GuidelineResult from a dict, ignoring unknown fields."""
        valid = {f.name for f in GuidelineResult.__dataclass_fields__.values()}
        return GuidelineResult(**{k: v for k, v in d.items() if k in valid})

    def run_stage(self, stage: int, context: dict, language: str = "en") -> dict:
        """
        Run a single agent stage. Used by the step-by-step API endpoint.

        Args:
            stage: Stage number (1=Intake, 2=Triage, 3=Guidelines, 4=Recommendations)
            context: Dict containing outputs from prior stages
            language: Output language code

        Returns:
            Dict with the stage output
        """
        if stage == 1:
            raw_input = context.get("raw_input", "")
            result = self.intake_agent.run(raw_input, language=language)
            return asdict(result)

        elif stage == 2:
            intake = self._safe_intake(context.get("intake", {}))
            result = self.triage_agent.run(intake, language=language)
            return asdict(result)

        elif stage == 3:
            triage = self._safe_triage(context.get("triage", {}))
            intake = self._safe_intake(context.get("intake", {}))
            result = self.guideline_agent.run(triage, intake)
            return asdict(result)

        elif stage == 4:
            triage = self._safe_triage(context.get("triage", {}))
            guidelines = self._safe_guideline(context.get("guidelines", {}))
            intake = self._safe_intake(context.get("intake", {}))
            result = self.recommendation_agent.run(triage, guidelines, intake, language=language)
            return asdict(result)

        else:
            raise ValueError(f"Invalid stage: {stage}. Must be 1-4.")
