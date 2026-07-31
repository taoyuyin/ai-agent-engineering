"""LangGraph: explicit, checkpointed sales analysis state machine."""

from __future__ import annotations

from sys import argv
from typing import Literal, TypedDict
from uuid import uuid4

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, StateGraph


SALES = {
    "east": {"net_revenue": 338_000.0, "order_count": 2},
    "north": {"net_revenue": 149_000.0, "order_count": 2},
    "south": {"net_revenue": 148_000.0, "order_count": 2},
}


class SalesState(TypedDict, total=False):
    question: str
    tenant_id: str
    scopes: list[str]
    status: str
    year: int
    rows: list[dict]
    answer: str
    error: str


def understand(state: SalesState) -> SalesState:
    question = state["question"]
    year = next((int(token) for token in question.split() if token.isdigit()), 2025)
    return {"year": year, "status": "understood"}


def authorize(state: SalesState) -> SalesState:
    if "sales:read" not in state.get("scopes", []):
        return {"status": "rejected", "error": "sales:read scope is required"}
    return {"status": "authorized"}


def route_after_authorization(state: SalesState) -> Literal["query", "reject"]:
    return "query" if state["status"] == "authorized" else "reject"


def query_sales(state: SalesState) -> SalesState:
    rows = [
        {"region": region, **metrics}
        for region, metrics in sorted(
            SALES.items(),
            key=lambda item: item[1]["net_revenue"],
            reverse=True,
        )
    ]
    return {"rows": rows, "status": "queried"}


def synthesize(state: SalesState) -> SalesState:
    lines = [
        f"{row['region']}: {row['net_revenue']:,.2f} CNY / {row['order_count']} orders"
        for row in state["rows"]
    ]
    return {
        "answer": f"{state['year']} net revenue\n" + "\n".join(lines),
        "status": "completed",
    }


def reject(state: SalesState) -> SalesState:
    return {"answer": f"Request rejected: {state['error']}", "status": "failed"}


def build_graph():
    builder = StateGraph(SalesState)
    builder.add_node("understand", understand)
    builder.add_node("authorize", authorize)
    builder.add_node("query_sales", query_sales)
    builder.add_node("synthesize", synthesize)
    builder.add_node("reject", reject)
    builder.add_edge(START, "understand")
    builder.add_edge("understand", "authorize")
    builder.add_conditional_edges(
        "authorize",
        route_after_authorization,
        {"query": "query_sales", "reject": "reject"},
    )
    builder.add_edge("query_sales", "synthesize")
    builder.add_edge("synthesize", END)
    builder.add_edge("reject", END)
    return builder.compile(checkpointer=InMemorySaver())


def main() -> None:
    question = " ".join(argv[1:]) or "查询 2025 年各区域净销售额"
    graph = build_graph()
    config = {"configurable": {"thread_id": str(uuid4())}}
    result = graph.invoke(
        {
            "question": question,
            "tenant_id": "demo",
            "scopes": ["sales:read"],
            "status": "accepted",
        },
        config=config,
    )
    print(result["answer"])
    print("\nFinal state:", result)


if __name__ == "__main__":
    main()
