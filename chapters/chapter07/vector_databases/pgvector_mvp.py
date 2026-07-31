"""pgvector MVP: SQL schema, ACID upsert, WHERE filter, ANN, and delete.

Start PostgreSQL with pgvector first:
    docker compose -f chapters/chapter07/vector_databases/docker-compose.yml up -d postgres
    pip install -r chapters/chapter07/vector_databases/requirements/pgvector.txt
    python chapters/chapter07/vector_databases/pgvector_mvp.py
"""

import os

import psycopg
from pgvector import Vector
from pgvector.psycopg import register_vector

from common import DIMENSION, DOCUMENTS, QUERY, embed, print_hit


DSN = os.getenv(
    "PGVECTOR_DSN",
    "postgresql://chapter07:chapter07@localhost:5432/chapter07",
)


def main() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        register_vector(connection)
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chapter07_documents (
                id text PRIMARY KEY,
                tenant_id text NOT NULL,
                doc_type text NOT NULL,
                content text NOT NULL,
                embedding vector({}) NOT NULL
            )
            """.format(DIMENSION)
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS chapter07_documents_filter_idx
            ON chapter07_documents (tenant_id, doc_type)
            """
        )
        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS chapter07_documents_embedding_hnsw_idx
            ON chapter07_documents
            USING hnsw (embedding vector_cosine_ops)
            """
        )

        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO chapter07_documents
                    (id, tenant_id, doc_type, content, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    tenant_id = EXCLUDED.tenant_id,
                    doc_type = EXCLUDED.doc_type,
                    content = EXCLUDED.content,
                    embedding = EXCLUDED.embedding
                """,
                [
                    (
                        document.id,
                        document.tenant_id,
                        document.doc_type,
                        document.text,
                        Vector(embed(document.text)),
                    )
                    for document in DOCUMENTS
                ],
            )

            query_vector = Vector(embed(QUERY))
            cursor.execute(
                """
                SELECT
                    id,
                    content,
                    1 - (embedding <=> %s) AS similarity
                FROM chapter07_documents
                WHERE tenant_id = %s AND doc_type = %s
                ORDER BY embedding <=> %s
                LIMIT %s
                """,
                (query_vector, "acme", "metric", query_vector, 2),
            )

            print("Query:", QUERY)
            for doc_id, content, similarity in cursor.fetchall():
                print_hit(doc_id, float(similarity), content)

            cursor.execute(
                "DELETE FROM chapter07_documents WHERE id = %s",
                ("other-tenant-gmv",),
            )


if __name__ == "__main__":
    main()
