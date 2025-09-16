from typing import Any, Dict, List, Optional, Sequence
from azure.cosmos import CosmosClient, PartitionKey
import os
import logging
from functools import lru_cache
import uuid

logger = logging.getLogger(__name__)

@lru_cache()
def get_cosmos_settings():
    return {
        "endpoint": os.getenv("COSMOSDB_ENDPOINT", ""),
        "key": os.getenv("COSMOSDB_KEY", ""),
        "database": os.getenv("COSMOSDB_DATABASE", "platform_db"),
    }

def get_cosmos_client() -> CosmosClient:
    s = get_cosmos_settings()
    if not s["endpoint"] or not s["key"]:
        raise RuntimeError("Cosmos configuration missing. Set COSMOSDB_ENDPOINT and COSMOSDB_KEY")
    return CosmosClient(s["endpoint"], credential=s["key"])  # type: ignore

class CosmosRepository:
    def __init__(self, container_name: str, partition_key: str = "/id"):
        settings = get_cosmos_settings()
        self.client = get_cosmos_client()
        self.database = self.client.create_database_if_not_exists(id=settings["database"])
        self.container = self.database.create_container_if_not_exists(id=container_name, partition_key=PartitionKey(path=partition_key))
        self.partition_key_path = partition_key

    def create(self, item: Dict[str, Any]):
        self.container.create_item(body=item)
        return item

    def get(self, item_id: str, partition_value: Optional[str] = None) -> Optional[Dict[str, Any]]:
        pk = partition_value or item_id
        try:
            return self.container.read_item(item=item_id, partition_key=pk)
        except Exception:
            return None

    def query(self, query: str, parameters: Optional[Sequence[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        return list(self.container.query_items(query=query, parameters=list(parameters or []), enable_cross_partition_query=True))

    def replace(self, item: Dict[str, Any]):
        pk_value = item.get(self.partition_key_path.strip('/')) or item['id']
        self.container.replace_item(item=item['id'], body=item, partition_key=pk_value)
        return item

    def delete(self, item_id: str, partition_value: Optional[str] = None):
        pk = partition_value or item_id
        self.container.delete_item(item=item_id, partition_key=pk)

# Helper factories for common containers (optional pattern)
def candidate_repository() -> CosmosRepository:
    return CosmosRepository(container_name=os.getenv("COSMOSDB_CANDIDATES_CONTAINER", "candidates"), partition_key="/id")

def material_repository() -> CosmosRepository:
    return CosmosRepository(container_name=os.getenv("COSMOSDB_MATERIALS_CONTAINER", "candidate_materials"), partition_key="/candidateId")
