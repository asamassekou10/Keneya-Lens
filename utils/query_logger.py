"""
Query logging and history management
"""
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)


class QueryLogger:
    """Manages query history and logging."""
    
    def __init__(self, log_dir: str = "./data/logs"):
        """
        Initialize query logger.
        
        Args:
            log_dir: Directory to store query logs
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "queries.jsonl"
    
    def log_query(self, 
                  user_input: str,
                  response: str,
                  sources: List[str],
                  context_count: int,
                  model: str,
                  metadata: Optional[Dict] = None) -> str:
        """
        Log a query and response.
        
        Args:
            user_input: User's query
            response: Generated response
            sources: List of source documents
            context_count: Number of context chunks used
            model: Model name used
            metadata: Additional metadata
            
        Returns:
            Query ID
        """
        query_id = str(uuid.uuid4())
        
        log_entry = {
            'id': query_id,
            'timestamp': datetime.utcnow().isoformat(),
            'input': user_input,
            'response': response,
            'sources': sources,
            'context_count': context_count,
            'model': model,
            'metadata': metadata or {}
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
            logger.info(f"Query logged: {query_id}")
            return query_id
            
        except Exception as e:
            logger.error(f"Failed to log query: {e}")
            return query_id
    
    def get_recent_queries(self, limit: int = 10) -> List[Dict]:
        """
        Get recent queries.
        
        Args:
            limit: Maximum number of queries to return
            
        Returns:
            List of query dictionaries
        """
        queries = []
        
        try:
            if not self.log_file.exists():
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    try:
                        queries.append(json.loads(line.strip()))
                    except json.JSONDecodeError:
                        continue
            
            # Reverse to show most recent first
            return list(reversed(queries))
            
        except Exception as e:
            logger.error(f"Failed to read query history: {e}")
            return []
    
    def get_query_by_id(self, query_id: str) -> Optional[Dict]:
        """
        Get a specific query by ID.
        
        Args:
            query_id: Query ID
            
        Returns:
            Query dictionary or None if not found
        """
        try:
            if not self.log_file.exists():
                return None
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('id') == query_id:
                            return entry
                    except json.JSONDecodeError:
                        continue
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to find query: {e}")
            return None
    
    def get_statistics(self) -> Dict:
        """
        Get query statistics.
        
        Returns:
            Dictionary with statistics
        """
        try:
            if not self.log_file.exists():
                return {
                    'total_queries': 0,
                    'total_sources_used': 0,
                    'average_context_count': 0
                }
            
            total_queries = 0
            total_context = 0
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        total_queries += 1
                        total_context += entry.get('context_count', 0)
                    except json.JSONDecodeError:
                        continue
            
            return {
                'total_queries': total_queries,
                'average_context_count': total_context / total_queries if total_queries > 0 else 0,
                'log_file': str(self.log_file)
            }
            
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {'error': str(e)}
