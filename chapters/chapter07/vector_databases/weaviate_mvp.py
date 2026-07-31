"""Weaviate MVP: schema, idempotent write, filter, near-vector, and delete.

Start the local service first:
    docker compose -f chapters/chapter07/vector_databases/docker-compose.yml up -d weaviate
    pip install -r chapters/chapter07/vector_databases/requirements/weaviate.txt
    python chapters/chapter07/vector_databases/weaviate_mvp.py
"""

from uuid import NAMESPACE_DNS, uuid5

import weaviate
from weaviate.classes.config import Configure, DataType, Property
from weaviate.classes.query import Filter, MetadataQuery

from common import DOCUMENTS, QUERY, embed, print_hit


COLLECTION_NAME = "Chapter07Metric"


def object_uuid(document_id: str):
    return uuid5(NAMESPACE_DNS, "chapter07:{}".format(document_id))


def upsert(collection, document) -> None:
    uuid = object_uuid(document.id)
    properties = {
        "document_id": document.id,
        "text": document.text,
        **document.metadata(),
    }
    vector = embed(document.text)
    if collection.data.exists(uuid):
        collection.data.replace(uuid=uuid, properties=properties, vector=vector)
    else:
        collection.data.insert(uuid=uuid, properties=properties, vector=vector)


def main() -> None:
    client = weaviate.connect_to_local()
    try:
        if not client.collections.exists(COLLECTION_NAME):
            client.collections.create(
                name=COLLECTION_NAME,
                vector_config=Configure.Vectors.self_provided(),
                properties=[
                    Property(name="document_id", data_type=DataType.TEXT),
                    Property(name="text", data_type=DataType.TEXT),
                    Property(name="tenant_id", data_type=DataType.TEXT),
                    Property(name="doc_type", data_type=DataType.TEXT),
                ],
            )

        collection = client.collections.use(COLLECTION_NAME)
        for document in DOCUMENTS:
            upsert(collection, document)

        response = collection.query.near_vector(
            near_vector=embed(QUERY),
            filters=(
                Filter.by_property("tenant_id").equal("acme")
                & Filter.by_property("doc_type").equal("metric")
            ),
            limit=2,
            return_metadata=MetadataQuery(distance=True),
        )

        print("Query:", QUERY)
        for item in response.objects:
            distance = float(item.metadata.distance or 0.0)
            print_hit(
                str(item.properties["document_id"]),
                1.0 - distance,
                str(item.properties["text"]),
            )

        collection.data.delete_by_id(object_uuid("other-tenant-gmv"))
    finally:
        client.close()


if __name__ == "__main__":
    main()
