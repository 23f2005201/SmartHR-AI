# app/core/graph_db.py
from neo4j import GraphDatabase, Query
import os
import logging
# FIXED: Import LiteralString to satisfy strict cryptographic string safety checks
from typing import Optional, Dict, Any, List, LiteralString

logger = logging.getLogger("uvicorn.error")

HOST = os.getenv("MEMGRAPH_HOST", "localhost")
PORT = os.getenv("MEMGRAPH_PORT", "7687")
URI = f"bolt://{HOST}:{PORT}"

class GraphDBLayer:
    def __init__(self):
        self.driver = None
        try:
            self.driver = GraphDatabase.driver(URI, auth=("", ""))
            logger.info("📊 Memgraph Local Graph Architecture Active.")
        except Exception as e:
            logger.warning(f"⚠️ Graph layer bypass active: {e}")

    def close(self):
        if self.driver:
            self.driver.close()

    # FIXED: Explicitly type parameter as LiteralString instead of basic str
    def run_query(self, query: LiteralString, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        if not self.driver:
            return []
        try:
            with self.driver.session() as session:
                query_params = parameters if parameters is not None else {}
                neo4j_query = Query(query)
                result = session.run(neo4j_query, query_params)
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"❌ Graph Query Error: {e}")
            return []

graph_db = GraphDBLayer()