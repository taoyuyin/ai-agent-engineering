"""Chapter 26: build a small citation-preserving RAG pipeline."""

from rag_runtime import Document, RAGPipeline


def main() -> None:
    rag = RAGPipeline(chunk_size=28, overlap=6)
    rag.index(
        [
            Document("policy-1", "差旅报销须在行程结束后 30 天内提交。", "policy://travel"),
            Document("policy-2", "采购超过五万元需要部门负责人审批。", "policy://purchase"),
        ]
    )
    result = rag.retrieve("差旅报销多久提交", top_k=2)
    print(result.context)
    print(result.citations)


if __name__ == "__main__":
    main()
