import os
from azure.cosmos import CosmosClient
from dotenv import load_dotenv

load_dotenv()

COSMOS_ENDPOINT = os.getenv("COSMOSDB_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOSDB_KEY")
DATABASE_NAME = os.getenv("COSMOSDB_DATABASE", "criteria_db")
CONTAINER_NAME = os.getenv("COSMOSDB_CONTAINER", "criteria")

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.create_database_if_not_exists(id=DATABASE_NAME)
container = database.create_container_if_not_exists(id=CONTAINER_NAME, partition_key="/id")

def get_container():
    return container
