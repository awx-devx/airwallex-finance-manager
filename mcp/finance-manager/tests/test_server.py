import asyncio

from finance_manager.server import mcp


def test_server_exposes_compute_tools():
    tools = asyncio.run(mcp.list_tools())
    names = {tool.name for tool in tools}
    assert names >= {
        "get_cash_runway",
        "detect_spend_anomalies",
        "calculate_budget_variance",
        "generate_cfo_summary",
    }
