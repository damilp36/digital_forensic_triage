"""XTriage: explainable anomaly detection for digital forensic triage.

Pipeline stages (paper Section III):
  S1 anomaly detection         -> xtriage.engine.detector
  S2 event-level attribution   -> xtriage.engine.explain
  S3 SHAP-augmented features   -> xtriage.engine.represent
  S4 rule induction            -> xtriage.engine.rules
  S5 disagreement guard        -> xtriage.engine.guard
  S6 forensic triage record    -> xtriage.engine.ledger
"""

__version__ = "0.1.0"
PRIORITIES = ("P1", "P2", "P3")
PRIORITY_ACTION = {"P1": "escalate", "P2": "review", "P3": "dismiss"}
