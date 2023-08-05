import base64
import enum
import io
import json
import tempfile
import webbrowser
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import pydantic
from PIL import Image

from classiq.interface.backend.backend_preferences import BackendPreferences
from classiq.interface.backend.quantum_backend_providers import ProviderVendor
from classiq.interface.executor import quantum_program
from classiq.interface.executor.quantum_instruction_set import QuantumInstructionSet
from classiq.interface.generator.generation_metadata import GenerationMetadata
from classiq.interface.generator.model.model import Model
from classiq.interface.generator.model.preferences.preferences import (
    CustomHardwareSettings,
    QuantumFormat,
)
from classiq.interface.generator.synthesis_metrics import SynthesisMetrics

from classiq.exceptions import ClassiqDefaultQuantumProgramError

_MAXIMUM_STRING_LENGTH = 250

_LOGO_HTML = '<p>\n    <img src="https://classiq-public.s3.amazonaws.com/logo/Green/classiq_RGB_Green.png" alt="Classiq logo" height="40">\n    <br>\n  </p>\n'


class LongStr(str):
    def __repr__(self):
        if len(self) > _MAXIMUM_STRING_LENGTH:
            length = len(self)
            return f'"{self[:4]}...{self[-4:]}" (length={length})'
        return super().__repr__()


class QasmVersion(str, enum.Enum):
    V2 = "2.0"
    V3 = "3.0"


class GenerationStatus(str, enum.Enum):
    NONE = "none"
    SUCCESS = "success"
    UNSAT = "unsat"
    TIMEOUT = "timeout"
    CANCELLED = "cancelled"
    ERROR = "error"


class ErrorDescription(pydantic.BaseModel):
    loc: List[str]
    msg: str


class ValidationErrorDetails(pydantic.BaseModel):
    errors: List[ErrorDescription]

    @pydantic.validator("errors", each_item=True, pre=True)
    def make_error_description(cls, v) -> ErrorDescription:
        if isinstance(v, ErrorDescription):
            return v
        return ErrorDescription(loc=v.get("loc"), msg=v.get("msg"))


class HardwareData(pydantic.BaseModel):
    _is_default: bool = pydantic.PrivateAttr(default=False)
    custom_hardware_settings: CustomHardwareSettings
    backend_preferences: Optional[BackendPreferences]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._is_default = (
            self.custom_hardware_settings.is_default
            and self.backend_preferences is None
        )

    @property
    def is_default(self) -> bool:
        return self._is_default


class TranspiledCircuitData(pydantic.BaseModel):
    qasm: str
    depth: int
    count_ops: Dict[str, int]


class GeneratedCircuit(pydantic.BaseModel):
    qubit_count: int
    transpiled_circuit: Optional[TranspiledCircuitData]
    outputs: Dict[QuantumFormat, str]
    qasm_version: QasmVersion
    image_raw: Optional[str]
    interactive_html: Optional[str]
    metadata: Optional[GenerationMetadata]
    synthesis_metrics: Optional[SynthesisMetrics]
    analyzer_data: Dict
    hardware_data: HardwareData
    model: Optional[Model] = None

    def show(self) -> None:
        self.image.show()

    def show_interactive(self, jupyter=False) -> None:
        if self.interactive_html is None:
            raise ValueError("Missing interactive html")
        if jupyter:  # show inline in jupyter
            # We assume that we're inside a jupyter-notebook
            # We cannot test it, since this is a part of the interface, while the jupyter-related code is in the SDK
            from IPython.core.display import HTML, display  # type: ignore

            h = HTML(self.interactive_html.replace(_LOGO_HTML, ""))
            display(h)

        else:  # open webbrowser
            with tempfile.NamedTemporaryFile(
                "w", delete=False, suffix="_interactive_circuit.html"
            ) as f:
                url = f"file://{f.name}"
                f.write(self.interactive_html)
            webbrowser.open(url)

    @property
    def image(self):
        if self.image_raw is None:
            raise ValueError("Missing image. Set draw_image=True to create the image.")
        return Image.open(io.BytesIO(base64.b64decode(self.image_raw)))

    def save_results(self, filename: Optional[Union[str, Path]] = None) -> None:
        """
        Saves generated circuit results as json.
            Parameters:
                filename (Union[str, Path]): Optional, path + filename of file.
                                             If filename supplied add `.json` suffix.

            Returns:
                  None
        """
        if filename:
            path = Path(filename)
        else:
            path = Path(
                f"generated_circuit_{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.json"
            )
        path.write_text(json.dumps(self.dict(), indent=4))

    def _hardware_unaware_program_code(
        self,
    ) -> Tuple[Optional[str], QuantumInstructionSet]:
        if self.qasm is not None:
            return self.qasm, QuantumInstructionSet.QASM
        elif self.qsharp is not None:
            return self.qsharp, QuantumInstructionSet.QSHARP
        elif self.ionq is not None:
            return self.ionq, QuantumInstructionSet.IONQ
        return None, QuantumInstructionSet.QASM

    def _default_program_code(self) -> Tuple[Optional[str], QuantumInstructionSet]:
        if self.hardware_data.backend_preferences is None:
            return self._hardware_unaware_program_code()

        backend_provider = (
            self.hardware_data.backend_preferences.backend_service_provider
        )
        if backend_provider == ProviderVendor.IONQ and self.ionq:
            return self.ionq, QuantumInstructionSet.IONQ
        elif backend_provider == ProviderVendor.AZURE_QUANTUM and self.qsharp:
            return self.qsharp, QuantumInstructionSet.QSHARP
        return (
            getattr(self.transpiled_circuit, "qasm", None),
            QuantumInstructionSet.QASM,
        )

    def to_program(self) -> quantum_program.QuantumProgram:
        code, syntax = self._default_program_code()
        if code is None:
            raise ClassiqDefaultQuantumProgramError
        return quantum_program.QuantumProgram(code=code, syntax=syntax)

    @pydantic.validator("image_raw", "interactive_html")
    def reformat_long_strings(cls, v):
        if v is None:
            return v
        return LongStr(v)

    @pydantic.validator("outputs")
    def reformat_long_string_output_formats(
        cls, outputs: Dict[QuantumFormat, str]
    ) -> Dict[QuantumFormat, LongStr]:
        return {key: LongStr(value) for key, value in outputs.items()}

    @property
    def qasm(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.QASM)

    @property
    def qsharp(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.QSHARP)

    @property
    def qir(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.QIR)

    @property
    def ionq(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.IONQ)

    @property
    def cirq_json(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.CIRQ_JSON)

    @property
    def qasm_cirq_compatible(self) -> Optional[str]:
        return self.outputs.get(QuantumFormat.QASM_CIRQ_COMPATIBLE)

    @property
    def output_format(self) -> List[QuantumFormat]:
        return list(self.outputs.keys())


class GenerationResult(pydantic.BaseModel):
    status: GenerationStatus
    details: Union[GeneratedCircuit, str, ValidationErrorDetails]
