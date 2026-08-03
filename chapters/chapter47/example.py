"""Chapter 47: a policy-governed customer service Agent MVP."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from sys import argv


ORDERS = {
    "A-1001": {"customer_id": "c-001", "delivered_on": "2026-07-29", "amount": 399.0, "status": "delivered"},
    "A-1002": {"customer_id": "c-002", "delivered_on": "2026-07-20", "amount": 1299.0, "status": "delivered"},
}
TICKETS: list[dict] = []


@dataclass(frozen=True)
class CustomerContext:
    customer_id: str
    authenticated: bool


def retrieve_policy(question: str) -> dict:
    if "退" in question or "refund" in question.lower():
        return {
            "policy_id": "refund-v4",
            "content": "签收后 7 天内、金额不超过 500 元且商品未使用，可进入自动退款审核；其他情况转人工。",
        }
    return {"policy_id": "service-v2", "content": "无法确定的问题应创建人工工单。"}


def read_order(order_id: str, context: CustomerContext) -> dict:
    if not context.authenticated:
        raise PermissionError("customer authentication is required")
    order = ORDERS.get(order_id)
    if not order or order["customer_id"] != context.customer_id:
        raise PermissionError("order is not visible to this customer")
    return {"order_id": order_id, **order}


def create_ticket(reason: str, order_id: str, priority: str) -> dict:
    ticket = {
        "ticket_id": f"T-{len(TICKETS) + 1:04d}",
        "reason": reason,
        "order_id": order_id,
        "priority": priority,
        "status": "open",
    }
    TICKETS.append(ticket)
    return ticket


def handle(question: str, order_id: str, context: CustomerContext) -> dict:
    policy = retrieve_policy(question)
    order = read_order(order_id, context)
    days_since_delivery = (date(2026, 8, 3) - date.fromisoformat(order["delivered_on"])).days
    eligible = days_since_delivery <= 7 and order["amount"] <= 500
    if eligible:
        action = {
            "type": "refund_review_created",
            "status": "pending_inventory_confirmation",
            "order_id": order_id,
        }
        response = "订单满足自动退款审核入口条件，已创建审核请求。"
    else:
        action = create_ticket("refund_requires_human_review", order_id, "high")
        response = "订单不满足自动处理边界，已升级人工客服。"
    return {
        "status": "resolved" if eligible else "escalated",
        "response": response,
        "order": order,
        "decision": {"days_since_delivery": days_since_delivery, "auto_review_eligible": eligible},
        "action": action,
        "citation": policy,
        "quality_checks": {"authenticated": context.authenticated, "ownership_verified": True},
    }


def main() -> None:
    question = " ".join(argv[1:]) or "订单 A-1001 可以退款吗？"
    result = handle(question, "A-1001", CustomerContext("c-001", True))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
