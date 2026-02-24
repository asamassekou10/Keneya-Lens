"""
PDF Processing Utilities for Medical Guidelines Ingestion
"""
import pdfplumber
from typing import List
from pathlib import Path


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract text content from a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
        
    Returns:
        Extracted text content as a string
    """
    text_content = []
    
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    return "\n\n".join(text_content)


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for better context preservation.
    
    Args:
        text: Input text to chunk
        chunk_size: Maximum size of each chunk (in characters)
        overlap: Number of characters to overlap between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        
        # Try to break at sentence boundary
        if end < len(text):
            # Look for sentence endings
            for punct in ['. ', '.\n', '! ', '?\n', '?\n']:
                last_punct = text.rfind(punct, start, end)
                if last_punct != -1:
                    end = last_punct + 2
                    break
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap
    
    return chunks


def process_medical_pdf(pdf_path: str, chunk_size: int = 500, overlap: int = 50) -> List[dict]:
    """
    Process a medical PDF into chunks with metadata.
    
    Args:
        pdf_path: Path to the PDF file
        chunk_size: Size of each chunk
        overlap: Overlap between chunks
        
    Returns:
        List of dictionaries containing chunk text and metadata
    """
    text = extract_text_from_pdf(pdf_path)
    chunks = chunk_text(text, chunk_size, overlap)
    
    pdf_name = Path(pdf_path).stem
    
    processed_chunks = []
    for idx, chunk in enumerate(chunks):
        processed_chunks.append({
            'text': chunk,
            'source': pdf_name,
            'chunk_id': idx,
            'total_chunks': len(chunks)
        })
    
    return processed_chunks
