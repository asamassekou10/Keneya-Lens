"""
Download sample medical guidelines PDF for testing
Creates a sample PDF with basic medical information
"""
from pathlib import Path
import sys

def create_sample_pdf():
    """Create a sample medical guidelines PDF."""
    import subprocess
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    except ImportError:
        print("❌ reportlab not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
    
    output_dir = Path("data/samples")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_path = output_dir / "sample_medical_guidelines.pdf"
    
    c = canvas.Canvas(str(pdf_path), pagesize=letter)
    width, height = letter
    
    # Title
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 50, "Sample Medical Guidelines")
    
    # Content
    c.setFont("Helvetica", 12)
    y = height - 100
    
    guidelines = [
        "Fever Management:",
        "- Normal body temperature: 36.5-37.5°C",
        "- Fever: >38°C",
        "- Treatment: Rest, hydration, antipyretics if >38.5°C",
        "",
        "Headache Assessment:",
        "- Primary headaches: Migraine, tension, cluster",
        "- Secondary headaches: May indicate underlying condition",
        "- Red flags: Sudden onset, age >50, neurological symptoms",
        "",
        "Skin Lesion Evaluation:",
        "- ABCDE rule for suspicious lesions",
        "- A: Asymmetry",
        "- B: Border irregularity",
        "- C: Color variation",
        "- D: Diameter >6mm",
        "- E: Evolving/changing",
        "",
        "Respiratory Symptoms:",
        "- Cough: Acute (<3 weeks) vs Chronic (>3 weeks)",
        "- Shortness of breath: Assess severity and triggers",
        "- Chest pain: Evaluate for cardiac vs respiratory causes",
    ]
    
    for line in guidelines:
        if y < 100:
            c.showPage()
            y = height - 50
        c.drawString(50, y, line)
        y -= 20
    
    c.save()
    print(f"✅ Sample PDF created: {pdf_path}")
    return pdf_path

def main():
    """Create sample data."""
    print("Creating sample medical guidelines PDF...")
    try:
        pdf_path = create_sample_pdf()
        print(f"\n✅ Sample data ready!")
        print(f"📄 File: {pdf_path}")
        print(f"\nYou can now:")
        print(f"1. Upload this PDF via the Streamlit UI")
        print(f"2. Or ingest via API: POST /ingest with pdf_path='{pdf_path}'")
    except Exception as e:
        print(f"❌ Error creating sample PDF: {e}")
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main())
