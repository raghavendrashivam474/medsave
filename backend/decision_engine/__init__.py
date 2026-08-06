"""
MedSave Decision Engine
=======================
Package entry point.

Exposes the DecisionEngine class as the single entry point
for all intelligent decision making in MedSave.

Usage:
    from decision_engine import DecisionEngine
    engine = DecisionEngine()
    result = engine.process(request)
"""

from .engine import DecisionEngine

__all__ = ["DecisionEngine"]
