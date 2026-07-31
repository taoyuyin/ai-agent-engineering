import unittest

from rag_runtime import Document, RAGPipeline


class RAGPipelineTest(unittest.TestCase):
    def setUp(self):
        self.rag = RAGPipeline(chunk_size=80, overlap=10)
        self.rag.index(
            [
                Document("travel", "差旅报销需要在行程结束后三十天内提交。", "policy://travel"),
                Document("buy", "采购合同超过五万元需要审批。", "policy://purchase"),
            ]
        )

    def test_retrieval_ranks_relevant_document(self):
        result = self.rag.retrieve("差旅 报销 提交", 1)
        self.assertEqual("travel", result.chunks[0].document_id)
        self.assertEqual(("policy://travel",), result.citations)

    def test_context_contains_stable_chunk_id(self):
        result = self.rag.retrieve("采购 合同", 1)
        self.assertIn("[buy:0]", result.context)

    def test_empty_index_fails_explicitly(self):
        with self.assertRaises(RuntimeError):
            RAGPipeline().retrieve("anything")


if __name__ == "__main__":
    unittest.main()
