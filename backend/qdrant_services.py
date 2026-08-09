from qdrant_client.models import (
    VectorParams,
    Distance
) 

from config import(
    qdrantClient,
    COLLECTION_NAME
)

#check if the collection already exists
#if it exists return that collection or else create and return that
def create_collection_if_not_exists():

    collections = qdrantClient.get_collections()

    existing_collections = [ collection.name for collection in collections.collections]

    if COLLECTION_NAME in existing_collections:
        return COLLECTION_NAME

    qdrantClient.create_collection(
        collection_name = COLLECTION_NAME,
        vectors_config = VectorParams(
            size = 384,
            distance = Distance.COSINE
        )
    )

    return COLLECTION_NAME


