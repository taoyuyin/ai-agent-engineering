from pathlib import Path

from framework.config import RuntimeSettings
from sql_agent import build_application
from sql_agent.guardrails import ReadOnlySQLPolicy


def test_sql_agent_returns_grounded_regional_revenue(tmp_path: Path) -> None:
    application = build_application(
        RuntimeSettings(database_path=tmp_path / "sales.db")
    )

    response = application.ask("查询 2025 年各区域净销售额")

    assert "华东" in response.answer
    assert response.evidence[0].source == "sqlite.sales_orders"
    assert response.evidence[0].metadata["row_count"] == 3


def test_sql_policy_rejects_write_statement() -> None:
    policy = ReadOnlySQLPolicy(frozenset({"sales_orders"}))

    try:
        policy.validate("DELETE FROM sales_orders")
    except ValueError as error:
        assert "only SELECT" in str(error) or "forbidden" in str(error)
    else:
        raise AssertionError("write SQL must be rejected")
