"""A dependency-free prompt registry with strict rendering and version control."""

from dataclasses import dataclass
from hashlib import sha256
from string import Formatter
from typing import Dict, Mapping, Optional, Tuple
import json


@dataclass(frozen=True)
class PromptTemplate:
    prompt_id: str
    version: str
    system: str
    template: str
    variables: Tuple[str, ...]
    output_schema: Mapping[str, str]

    def validate(self) -> None:
        fields = {
            name for _, name, _, _ in Formatter().parse(self.template) if name is not None
        }
        expected = set(self.variables)
        if fields != expected:
            raise ValueError("template fields and declared variables must match")
        if not self.prompt_id or not self.version or not self.system:
            raise ValueError("prompt_id, version and system are required")

    @property
    def checksum(self) -> str:
        payload = json.dumps(
            {
                "system": self.system,
                "template": self.template,
                "schema": dict(self.output_schema),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
        return sha256(payload.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class RenderedPrompt:
    text: str
    metadata: Mapping[str, str]
    output_schema: Mapping[str, str]


class PromptRegistry:
    def __init__(self) -> None:
        self._versions: Dict[str, Dict[str, PromptTemplate]] = {}
        self._active: Dict[str, str] = {}

    def register(self, prompt: PromptTemplate, activate: bool = False) -> None:
        prompt.validate()
        versions = self._versions.setdefault(prompt.prompt_id, {})
        if prompt.version in versions:
            raise ValueError("prompt version is immutable")
        versions[prompt.version] = prompt
        if activate or prompt.prompt_id not in self._active:
            self._active[prompt.prompt_id] = prompt.version

    def activate(self, prompt_id: str, version: str) -> None:
        self.get(prompt_id, version)
        self._active[prompt_id] = version

    def get(self, prompt_id: str, version: Optional[str] = None) -> PromptTemplate:
        selected = version or self._active.get(prompt_id)
        if selected is None or selected not in self._versions.get(prompt_id, {}):
            raise KeyError("unknown prompt or version")
        return self._versions[prompt_id][selected]

    def render(
        self,
        prompt_id: str,
        values: Mapping[str, object],
        version: Optional[str] = None,
    ) -> RenderedPrompt:
        prompt = self.get(prompt_id, version)
        missing = set(prompt.variables) - set(values)
        extra = set(values) - set(prompt.variables)
        if missing or extra:
            raise ValueError("render variables mismatch: missing=%s extra=%s" % (missing, extra))
        body = prompt.template.format(**values)
        text = "%s\n\n%s" % (prompt.system, body)
        return RenderedPrompt(
            text=text,
            metadata={
                "prompt_id": prompt.prompt_id,
                "prompt_version": prompt.version,
                "prompt_checksum": prompt.checksum,
            },
            output_schema=dict(prompt.output_schema),
        )
