from qdrant_client.models import (
    VectorParams,
    SparseVectorParams,
    SparseIndexParams,
    Distance
) 

from config import(
    qdrantClient,
    SPARSE_VECTOR_NAME,
    COLLECTION_NAME
)

from exceptions import(
    QdrantCollectionNotFoundException
)

#check if the collection already exists
#if it exists return that collection or else create and return that
def create_collection_if_not_exists():

    collections = qdrantClient.get_collections()

    existing_collections = [ collection.name for collection in collections.collections]

    if COLLECTION_NAME in existing_collections:
        return COLLECTION_NAME

    # create the collection
    qdrantClient.create_collection(
        collection_name=COLLECTION_NAME,

        # Dense vector configuration
        vectors_config=VectorParams(
            size=384,
            distance=Distance.COSINE
        ),

        # Sparse vector configuration
        sparse_vectors_config={
            SPARSE_VECTOR_NAME: SparseVectorParams(
                index=SparseIndexParams(
                    on_disk=False
                )
            )
        }
    )

     # Create payload index for video_id
    qdrantClient.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="video_id",
        field_schema="keyword"
    )

    return COLLECTION_NAME


#fetch the collection name only if it exists or create Exception
def get_existing_collection() -> str:

    collections = qdrantClient.get_collections()

    existing_collections = [
        collection.name
        for collection in collections.collections
    ]

    if COLLECTION_NAME not in existing_collections:
        raise QdrantCollectionNotFoundException(
            f"Collection '{COLLECTION_NAME}' does not exist"
        )

    return COLLECTION_NAME


