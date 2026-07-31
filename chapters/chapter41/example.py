"""Dify: invoke a published Workflow application through its service API."""

from __future__ import annotations

from os import environ
from sys import argv

import httpx


class DifyWorkflowClient:
    def __init__(self, base_url: str, api_key: str, timeout_seconds: float = 60) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = httpx.Timeout(timeout_seconds)

    def run_sales_workflow(self, question: str, user: str) -> dict:
        response = httpx.post(
            f"{self.base_url}/v1/workflows/run",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "inputs": {
                    "question": question,
                    "tenant_id": "demo",
                    "scopes": "sales:read",
                },
                "response_mode": "blocking",
                "user": user,
            },
            timeout=self.timeout,
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("data", {}).get("status") != "succeeded":
            raise RuntimeError(f"Dify workflow failed: {payload}")
        return payload


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    api_key = environ.get("DIFY_API_KEY")
    if not api_key:
        raise RuntimeError("DIFY_API_KEY is required")
    client = DifyWorkflowClient(
        base_url=environ.get("DIFY_BASE_URL", "https://api.dify.ai"),
        api_key=api_key,
    )
    result = client.run_sales_workflow(question, user="engineer-001")
    print(result["data"]["outputs"])


if __name__ == "__main__":
    main()
