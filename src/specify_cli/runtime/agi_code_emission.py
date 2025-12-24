"""Code emission runtime - writes generated code to disk.

Auto-generated from: ontology/agi-agent-schema.ttl
Constitutional equation: agi_code_emission.py = μ(agi-agent-schema.ttl)
DO NOT EDIT MANUALLY - Edit the RDF source instead.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from specify_cli.core.telemetry import span, timed
from specify_cli.ops.agi_code_synthesizer import GeneratedCode


class CodeEmitter:
    """Emits generated code to files."""

    @timed
    def emit_code(
        self,
        code: GeneratedCode,
        output_dir: Path,
        overwrite: bool = False,
    ) -> dict[str, Path]:
        """Emit generated code to files.

        Parameters
        ----------
        code : GeneratedCode
            Generated code object
        output_dir : Path
            Output directory
        overwrite : bool, optional
            Whether to overwrite existing files

        Returns
        -------
        dict[str, Path]
            Paths of created files
        """
        with span(
            "agi_code_emission.emit_code", output_dir=str(output_dir), overwrite=overwrite
        ):
            files_created = {}

            # Write source code
            if code.source_code:
                src_path = output_dir / f"{code.metadata.get('module_name', 'generated')}.py"
                src_path.parent.mkdir(parents=True, exist_ok=True)
                src_path.write_text(code.source_code)
                files_created["source"] = src_path

            # Write tests
            if code.test_code:
                test_path = output_dir / f"test_{code.metadata.get('module_name', 'generated')}.py"
                test_path.parent.mkdir(parents=True, exist_ok=True)
                test_path.write_text(code.test_code)
                files_created["tests"] = test_path

            # Write documentation
            if code.documentation:
                doc_path = output_dir / f"{code.metadata.get('module_name', 'generated')}.md"
                doc_path.parent.mkdir(parents=True, exist_ok=True)
                doc_path.write_text(code.documentation)
                files_created["docs"] = doc_path

            return files_created
