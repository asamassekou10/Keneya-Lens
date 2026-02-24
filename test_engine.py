"""
Simple test script to verify MedGemmaEngine functionality
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from app.medgemma_engine import MedGemmaEngine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_engine():
    """Test basic engine functionality."""
    print("=" * 60)
    print("MedLens Engine Test")
    print("=" * 60)
    
    try:
        # Initialize engine
        print("\n[1/3] Initializing MedGemma Engine...")
        engine = MedGemmaEngine()
        print("✅ Engine initialized successfully")
        
        # Test vector DB
        print("\n[2/3] Testing vector database...")
        collection_count = engine.collection.count()
        print(f"✅ Vector database accessible ({collection_count} documents)")
        
        # Test query (without context if DB is empty)
        print("\n[3/3] Testing symptom query...")
        test_query = "Patient has fever and headache for 2 days"
        print(f"Query: {test_query}")
        
        result = engine.query_symptoms(test_query, max_new_tokens=256)
        
        print("\n✅ Query successful!")
        print("\nResponse:")
        print("-" * 60)
        print(result['response'])
        print("-" * 60)
        print(f"\nSources: {result.get('sources', [])}")
        print(f"Context chunks used: {result.get('context_count', 0)}")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = test_engine()
    sys.exit(0 if success else 1)
