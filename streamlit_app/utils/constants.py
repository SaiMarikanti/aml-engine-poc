"""Constants and enums for AML Investigation Platform."""
from enum import Enum

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class AlertStatus(str, Enum):
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER REVIEW"
    CONFIRMED = "CONFIRMED"
    FALSE_POSITIVE = "FALSE POSITIVE"
    CLOSED = "CLOSED"

class DetectionEngine(str, Enum):
    RULE = "Rule Engine"
    GRAPH = "Graph Analysis"
    ML = "ML Model (XGBoost)"

# Hex colors for risk visualization
RISK_COLORS = {
    RiskLevel.LOW: "#059669",
    RiskLevel.MEDIUM: "#D97706",
    RiskLevel.HIGH: "#DC2626",
    RiskLevel.CRITICAL: "#991B1B"
}

# Hex colors for alert statuses
STATUS_COLORS = {
    AlertStatus.OPEN: "#3B82F6",
    AlertStatus.UNDER_REVIEW: "#F59E0B",
    AlertStatus.CONFIRMED: "#EF4444",
    AlertStatus.FALSE_POSITIVE: "#6B7280",
    AlertStatus.CLOSED: "#10B981"
}

NEO_BG = "#E8ECF1"
NEO_SURFACE = "#E8ECF1"
NEO_PRIMARY = "#1E3A8A"
