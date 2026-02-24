#!/usr/bin/env python3
"""
MedGemma Fine-Tuning Guide for Keneya Lens

This script demonstrates how to fine-tune MedGemma for local medical contexts.
It can be run as a Python script or converted to a Jupyter notebook.

IMPORTANT: Fine-tuning requires:
- GPU with at least 16GB VRAM (A100, V100, or RTX 3090+)
- HuggingFace account with model access
- Training data in the correct format
"""

# %% [markdown]
# # MedGemma Fine-Tuning for Local Medical Contexts
#
# This guide walks through fine-tuning MedGemma for:
# 1. Local disease patterns (e.g., malaria-endemic regions)
# 2. Local treatment protocols
# 3. Local language adaptation
# 4. Specific use cases (CHW support)

# %% [markdown]
# ## 1. Setup and Dependencies

# %%
# Install required packages (uncomment if needed)
# !pip install torch>=2.1.0 transformers>=4.35.0 peft>=0.7.0 datasets accelerate bitsandbytes

import os
import json
from typing import Dict, List, Optional
from dataclasses import dataclass

import torch
from torch.utils.data import Dataset
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling
)
from peft import (
    LoraConfig,
    get_peft_model,
    prepare_model_for_kbit_training,
    TaskType
)

# Check GPU availability
print(f"CUDA available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")

# %% [markdown]
# ## 2. Configuration

# %%
@dataclass
class FineTuningConfig:
    """Configuration for MedGemma fine-tuning."""

    # Model settings
    base_model: str = "google/medgemma-4b-it"
    output_dir: str = "./fine_tuned_medgemma"

    # LoRA settings (Parameter-Efficient Fine-Tuning)
    lora_r: int = 16  # Rank of the update matrices
    lora_alpha: int = 32  # Scaling factor
    lora_dropout: float = 0.05
    target_modules: List[str] = None  # Auto-detected if None

    # Training settings
    num_epochs: int = 3
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 2e-4
    warmup_ratio: float = 0.03
    max_seq_length: int = 1024

    # Quantization
    use_4bit: bool = True
    bnb_4bit_compute_dtype: str = "float16"

    def __post_init__(self):
        if self.target_modules is None:
            # Default LoRA targets for Gemma architecture
            self.target_modules = [
                "q_proj", "k_proj", "v_proj", "o_proj",
                "gate_proj", "up_proj", "down_proj"
            ]

config = FineTuningConfig()
print(f"Base model: {config.base_model}")
print(f"Output directory: {config.output_dir}")

# %% [markdown]
# ## 3. Training Data Format
#
# MedGemma expects instruction-following format. For medical triage, we use:
#
# ```json
# {
#   "instruction": "A patient presents with...",
#   "input": "Additional context (optional)",
#   "output": "Triage recommendation..."
# }
# ```

# %%
# Sample training data format
SAMPLE_TRAINING_DATA = [
    {
        "instruction": "You are a medical triage assistant. A community health worker reports: 'Child, 2 years old, with fever for 3 days, refuses to drink, very sleepy'. What is your triage recommendation?",
        "input": "",
        "output": """🔴 URGENT - IMMEDIATE REFERRAL REQUIRED

ASSESSMENT:
The combination of symptoms suggests possible severe illness:
- Prolonged fever (3 days) in a young child
- Refusal to drink (dehydration risk)
- Altered consciousness (lethargy/sleepiness)

DANGER SIGNS IDENTIFIED:
1. Unable to drink or breastfeed
2. Abnormally sleepy or difficult to wake

IMMEDIATE ACTIONS:
1. Check for emergency signs (convulsions, severe dehydration)
2. If available, give first dose of antimalarial (malaria-endemic area)
3. Give ORS if child can swallow
4. Arrange IMMEDIATE transport to health facility

This presentation requires urgent evaluation by a healthcare professional.

Sources: WHO IMCI Guidelines 2023"""
    },
    {
        "instruction": "You are a medical triage assistant. A community health worker reports: 'Adult woman, 28 years old, with headache and mild cough for 2 days, no fever, eating and drinking normally'. What is your triage recommendation?",
        "input": "",
        "output": """🟢 NON-URGENT - CAN BE MANAGED LOCALLY

ASSESSMENT:
Symptoms suggest a mild upper respiratory tract infection or common cold.

FAVORABLE SIGNS:
- No fever
- Eating and drinking normally
- Short duration (2 days)
- No danger signs

HOME MANAGEMENT RECOMMENDATIONS:
1. Rest and adequate fluid intake
2. Paracetamol for headache if needed (500mg every 6 hours)
3. Warm fluids for cough relief

WHEN TO RETURN:
- Fever develops
- Symptoms worsen or persist beyond 7 days
- Difficulty breathing
- Unable to eat or drink

Monitor and provide supportive care.

Sources: WHO Community Case Management Guidelines"""
    },
    # Add more training examples here...
]

print(f"Sample training data: {len(SAMPLE_TRAINING_DATA)} examples")

# %% [markdown]
# ## 4. Custom Dataset Class

# %%
class MedicalTriageDataset(Dataset):
    """Dataset for medical triage fine-tuning."""

    def __init__(
        self,
        data: List[Dict],
        tokenizer,
        max_length: int = 1024
    ):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]

        # Format as instruction-following prompt
        if item.get("input"):
            prompt = f"""### Instruction:
{item['instruction']}

### Input:
{item['input']}

### Response:
{item['output']}"""
        else:
            prompt = f"""### Instruction:
{item['instruction']}

### Response:
{item['output']}"""

        # Tokenize
        tokenized = self.tokenizer(
            prompt,
            truncation=True,
            max_length=self.max_length,
            padding="max_length",
            return_tensors="pt"
        )

        return {
            "input_ids": tokenized["input_ids"].squeeze(),
            "attention_mask": tokenized["attention_mask"].squeeze(),
            "labels": tokenized["input_ids"].squeeze()
        }

# %% [markdown]
# ## 5. Load Base Model with Quantization

# %%
def load_model_and_tokenizer(config: FineTuningConfig):
    """Load MedGemma with 4-bit quantization for efficient fine-tuning."""

    print(f"Loading tokenizer from {config.base_model}...")
    tokenizer = AutoTokenizer.from_pretrained(
        config.base_model,
        trust_remote_code=True
    )

    # Set padding token
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    print(f"Loading model with {'4-bit' if config.use_4bit else 'FP16'} quantization...")

    if config.use_4bit:
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_use_double_quant=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=getattr(torch, config.bnb_4bit_compute_dtype)
        )

        model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            quantization_config=bnb_config,
            device_map="auto",
            trust_remote_code=True
        )

        # Prepare model for k-bit training
        model = prepare_model_for_kbit_training(model)
    else:
        model = AutoModelForCausalLM.from_pretrained(
            config.base_model,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True
        )

    print(f"Model loaded successfully!")
    return model, tokenizer

# Uncomment to load model:
# model, tokenizer = load_model_and_tokenizer(config)

# %% [markdown]
# ## 6. Configure LoRA (Parameter-Efficient Fine-Tuning)

# %%
def setup_lora(model, config: FineTuningConfig):
    """Configure LoRA adapters for efficient fine-tuning."""

    lora_config = LoraConfig(
        r=config.lora_r,
        lora_alpha=config.lora_alpha,
        lora_dropout=config.lora_dropout,
        target_modules=config.target_modules,
        bias="none",
        task_type=TaskType.CAUSAL_LM
    )

    model = get_peft_model(model, lora_config)

    # Print trainable parameters
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())

    print(f"Trainable parameters: {trainable_params:,} ({100 * trainable_params / total_params:.2f}%)")
    print(f"Total parameters: {total_params:,}")

    return model

# %% [markdown]
# ## 7. Training Configuration

# %%
def get_training_args(config: FineTuningConfig) -> TrainingArguments:
    """Get training arguments for fine-tuning."""

    return TrainingArguments(
        output_dir=config.output_dir,
        num_train_epochs=config.num_epochs,
        per_device_train_batch_size=config.batch_size,
        gradient_accumulation_steps=config.gradient_accumulation_steps,
        learning_rate=config.learning_rate,
        warmup_ratio=config.warmup_ratio,
        logging_steps=10,
        save_steps=100,
        save_total_limit=3,
        fp16=True,
        optim="paged_adamw_8bit",
        lr_scheduler_type="cosine",
        report_to="none",  # Disable wandb/tensorboard
        gradient_checkpointing=True,
        max_grad_norm=0.3,
    )

# %% [markdown]
# ## 8. Fine-Tuning Pipeline

# %%
def fine_tune_medgemma(
    training_data: List[Dict],
    config: FineTuningConfig,
    validation_split: float = 0.1
):
    """
    Complete fine-tuning pipeline for MedGemma.

    Args:
        training_data: List of training examples
        config: Fine-tuning configuration
        validation_split: Fraction for validation
    """

    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(config)

    # Setup LoRA
    model = setup_lora(model, config)

    # Split data
    split_idx = int(len(training_data) * (1 - validation_split))
    train_data = training_data[:split_idx]
    val_data = training_data[split_idx:]

    print(f"Training examples: {len(train_data)}")
    print(f"Validation examples: {len(val_data)}")

    # Create datasets
    train_dataset = MedicalTriageDataset(train_data, tokenizer, config.max_seq_length)
    val_dataset = MedicalTriageDataset(val_data, tokenizer, config.max_seq_length)

    # Data collator
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Training arguments
    training_args = get_training_args(config)

    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        data_collator=data_collator,
    )

    # Train
    print("Starting fine-tuning...")
    trainer.train()

    # Save model
    print(f"Saving model to {config.output_dir}...")
    trainer.save_model()
    tokenizer.save_pretrained(config.output_dir)

    print("Fine-tuning complete!")
    return model, tokenizer

# %% [markdown]
# ## 9. Loading Fine-Tuned Model

# %%
def load_fine_tuned_model(model_path: str):
    """Load a fine-tuned MedGemma model."""

    from peft import PeftModel

    # Load base model
    base_model = AutoModelForCausalLM.from_pretrained(
        "google/medgemma-4b-it",
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )

    # Load LoRA weights
    model = PeftModel.from_pretrained(base_model, model_path)

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)

    return model, tokenizer

# %% [markdown]
# ## 10. Inference with Fine-Tuned Model

# %%
def generate_triage_response(
    model,
    tokenizer,
    symptoms: str,
    max_new_tokens: int = 512
) -> str:
    """Generate triage response using fine-tuned model."""

    prompt = f"""### Instruction:
You are a medical triage assistant. A community health worker reports: '{symptoms}'. What is your triage recommendation?

### Response:
"""

    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            do_sample=True,
            top_p=0.9,
            pad_token_id=tokenizer.eos_token_id
        )

    response = tokenizer.decode(outputs[0], skip_special_tokens=True)

    # Extract only the response part
    if "### Response:" in response:
        response = response.split("### Response:")[-1].strip()

    return response

# %% [markdown]
# ## 11. Evaluation Metrics

# %%
def evaluate_triage_accuracy(
    model,
    tokenizer,
    test_data: List[Dict],
    verbose: bool = True
) -> Dict:
    """
    Evaluate fine-tuned model on test data.

    Returns accuracy metrics for triage level classification.
    """

    results = {
        "total": len(test_data),
        "correct_triage": 0,
        "predictions": []
    }

    for item in test_data:
        # Generate prediction
        prediction = generate_triage_response(
            model, tokenizer,
            item["instruction"].split("reports: '")[1].split("'")[0]
        )

        # Extract triage level from prediction and ground truth
        pred_level = extract_triage_level(prediction)
        true_level = extract_triage_level(item["output"])

        is_correct = pred_level == true_level
        results["correct_triage"] += int(is_correct)

        results["predictions"].append({
            "instruction": item["instruction"],
            "predicted": pred_level,
            "actual": true_level,
            "correct": is_correct
        })

        if verbose:
            status = "✓" if is_correct else "✗"
            print(f"{status} Predicted: {pred_level}, Actual: {true_level}")

    results["accuracy"] = results["correct_triage"] / results["total"]

    print(f"\nOverall Accuracy: {results['accuracy']:.2%}")

    return results

def extract_triage_level(text: str) -> str:
    """Extract triage level from response text."""
    text_lower = text.lower()

    if "🔴" in text or "urgent" in text_lower or "immediate" in text_lower:
        return "URGENT"
    elif "🟡" in text or "moderate" in text_lower or "schedule" in text_lower:
        return "MODERATE"
    elif "🟢" in text or "non-urgent" in text_lower or "manage locally" in text_lower:
        return "NON-URGENT"
    else:
        return "UNKNOWN"

# %% [markdown]
# ## 12. Running Fine-Tuning (Example)

# %%
if __name__ == "__main__":
    print("=" * 60)
    print("MedGemma Fine-Tuning Guide")
    print("=" * 60)

    # Check prerequisites
    if not torch.cuda.is_available():
        print("\n⚠️  Warning: CUDA not available. Fine-tuning will be very slow.")
        print("Recommended: Use a GPU with at least 16GB VRAM")

    print("\nTo run fine-tuning:")
    print("1. Prepare training data in the format shown above")
    print("2. Configure FineTuningConfig with your settings")
    print("3. Call fine_tune_medgemma(training_data, config)")

    print("\nExample:")
    print("```python")
    print("config = FineTuningConfig(")
    print('    base_model="google/medgemma-4b-it",')
    print('    output_dir="./my_fine_tuned_model",')
    print("    num_epochs=3")
    print(")")
    print("model, tokenizer = fine_tune_medgemma(my_training_data, config)")
    print("```")

    # Example training data loading
    print("\n\nTo load training data from file:")
    print("```python")
    print('with open("training_data.json", "r") as f:')
    print("    training_data = json.load(f)")
    print("```")
