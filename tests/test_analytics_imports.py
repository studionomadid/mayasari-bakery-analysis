import importlib

ANALYTICS_MODULES = [
    "src.customer_opportunity_insights",
    "src.executive_insights",
    "src.product_dashboard",
    "src.profitability_dashboard",
    "src.clv_insights",
    "src.visualization",
    "src.customer_dashboard",
    "src.revenue_dashboard",
]


def test_all_analytics_modules_import() -> None:
    for module_name in ANALYTICS_MODULES:
        importlib.import_module(module_name)
