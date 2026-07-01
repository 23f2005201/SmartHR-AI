# app/core/graph_db.py
from neo4j import GraphDatabase, Query
import os
import logging
import re
from typing import Optional, Dict, Any, List, LiteralString

logger = logging.getLogger("uvicorn.error")

HOST = os.getenv("MEMGRAPH_HOST", "localhost")
PORT = os.getenv("MEMGRAPH_PORT", "7687")
URI = f"bolt://{HOST}:{PORT}"

# Strict alphanumeric regex pattern for parameter safety
SAFE_ALPHANUM_RE = re.compile(r"^[a-zA-Z0-9_\-\s\.@\+]+$")

def sanitize_input_value(val: Any) -> Any:
    """Recursively validates and sanitizes input scalars to neutralize injection fragments."""
    if isinstance(val, str):
        # Drop common malicious sequence terminators if they don't match safe formatting rules
        if not SAFE_ALPHANUM_RE.match(val):
            # Strip dangerous characters like semicolons, backslashes, and quote wrappers
            return re.sub(r"[;\"'\\]", "", val).strip()
        return val
    elif isinstance(val, dict):
        return {k: sanitize_input_value(v) for k, v in val.items()}
    elif isinstance(val, list):
        return [sanitize_input_value(x) for x in val]
    return val

class GraphDBLayer:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(URI, auth=("", ""))
            logger.info("📊 Secure Memgraph Graph Engine Online.")
        except Exception as e:
            logger.warning(f"⚠️ Graph database bypass active: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    def run_query(self, query: LiteralString, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.driver:
            return []
        try:
            with self.driver.session() as session:
                # 🛡️ SANITIZATION LAYER: Mitigate indirect query injection vectors
                raw_params = parameters if parameters is not None else {}
                secure_params = {k: sanitize_input_value(v) for k, v in raw_params.items()}
                
                neo4j_query = Query(query)
                result = session.run(neo4j_query, secure_params)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"❌ Secure Graph Query Blocked or Faulted: {e}")
            return []

graph_db = GraphDBLayer()