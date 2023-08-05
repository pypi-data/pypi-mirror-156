from typing import Dict, Optional

import pydantic

from classiq.interface.backend.backend_preferences import (
    BackendPreferencesTypes,
    backend_preferences_field,
)
from classiq.interface.combinatorial_optimization.encoding_types import EncodingType
from classiq.interface.combinatorial_optimization.preferences import QSolverPreferences
from classiq.interface.executor.optimizer_preferences import CombinatorialOptimizer


class OptimizationProblem(pydantic.BaseModel):
    qsolver_preferences: Optional[QSolverPreferences] = pydantic.Field(
        default=None,
        description="preferences for the QSolver: QAOAMixer, QAOAPenalty or GAS",
    )
    optimizer_preferences: CombinatorialOptimizer = pydantic.Field(
        default_factory=CombinatorialOptimizer,
        description="preferences for the VQE execution",
    )
    serialized_model: Optional[Dict] = None
    backend_preferences: BackendPreferencesTypes = backend_preferences_field()
    encoding_type: Optional[EncodingType] = pydantic.Field(
        default=EncodingType.BINARY,
        description="encoding scheme for integer variables",
    )

    class Config:
        smart_union = True
