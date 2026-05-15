"""Clinical engineering metrics and criticality helpers."""


def calculate_equipment_criticality(
    *, status: str, recurrent_failures: int = 0, base_criticality: str = "Média"
) -> str:
    """Calculate displayed equipment criticality from base risk and failure pattern."""
    normalized = (base_criticality or "Média").strip().lower()
    if status == "offline" or recurrent_failures >= 3 or normalized == "alta":
        return "Alta"
    if status == "warning" or recurrent_failures >= 1 or normalized in {"média", "media"}:
        return "Média"
    return "Baixa"
