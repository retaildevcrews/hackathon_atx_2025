from typing import Any, Dict, List, Optional
from azure.cosmos import CosmosClient, PartitionKey
from app.config import get_settings
import logging
import uuid

logger = logging.getLogger(__name__)

class CosmosRepository:
    def __init__(self, client: CosmosClient, database_name: str, container_name: str, partition_key: str = "/id"):
        self.client = client
        self.database = client.create_database_if_not_exists(id=database_name)
        self.container = self.database.create_container_if_not_exists(
            id=container_name, partition_key=PartitionKey(path=partition_key)
        )

    def create(self, item: Dict[str, Any]):
        return self.container.create_item(body=item)

    def get(self, item_id: str) -> Optional[Dict[str, Any]]:
        try:
            return self.container.read_item(item=item_id, partition_key=item_id)
        except Exception:
            return None

    def query(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        return list(self.container.query_items(query=query, parameters=parameters or [], enable_cross_partition_query=True))

    def replace(self, item: Dict[str, Any]):
        return self.container.replace_item(item=item['id'], body=item)

    def delete(self, item_id: str):
        self.container.delete_item(item=item_id, partition_key=item_id)


def get_cosmos_client() -> CosmosClient:
    s = get_settings()
    if not s["cosmos_endpoint"] or not s["cosmos_key"]:
        raise RuntimeError("Cosmos configuration is missing")
    return CosmosClient(s["cosmos_endpoint"], credential=s["cosmos_key"])  # type: ignore


def get_candidate_repository() -> CosmosRepository:
    s = get_settings()
    client = get_cosmos_client()
    return CosmosRepository(client, s["cosmos_database"], s["candidates_container"], partition_key="/id")


def get_materials_repository() -> CosmosRepository:
    s = get_settings()
    client = get_cosmos_client()
    return CosmosRepository(client, s["cosmos_database"], s["materials_container"], partition_key="/candidateId")
