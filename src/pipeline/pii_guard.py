from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PIIMatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1)
    path: str = Field(min_length=1)
    mask: str = Field(min_length=1)


class PIIReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    pii_detected: bool
    total_matches: int = Field(ge=0)
    matches: list[PIIMatch]


class PIIGuard:
    """Detect and mask PII before data is passed to an LLM."""

    EMAIL_PATTERN = re.compile(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"
    )
    PHONE_PATTERN = re.compile(
        r"(?<!\w)(?:\+?\d[\d\s().-]{7,}\d)(?!\w)"
    )

    SENSITIVE_FIELDS = {  # noqa: RUF012
        "password": "PASSWORD",
        "passwd": "PASSWORD",
        "passcode": "PASSWORD",
        "secret": "SECRET",
        "token": "TOKEN",
        "api_key": "API_KEY",
        "apikey": "API_KEY",
    }

    def scan_and_mask(self, data: Any) -> tuple[Any, PIIReport]:
        """Return a masked copy of data and a PII detection report."""
        matches: list[PIIMatch] = []

        masked_data = self._process(deepcopy(data),path="",matches=matches)

        return masked_data, self._build_report(matches)

    def _process(self,value: Any,path: str,matches: list[PIIMatch]) -> Any:
        if isinstance(value, dict):
            return self._process_dict(value, path, matches)

        if isinstance(value, list):
            return self._process_list(value, path, matches)

        if isinstance(value, str):
            return self._mask_string(value, path, matches)

        return value

    def _process_dict(self,data: dict[Any, Any],path: str,matches: list[PIIMatch]) -> dict[Any, Any]:
        result: dict[Any, Any] = {}

        for key, value in data.items():
            current_path = self._build_path(path, str(key))
            pii_type = self._get_sensitive_field_type(key)

            if pii_type and value is not None:
                result[key] = self._mask_field(pii_type,current_path,matches)
                continue

            result[key] = self._process(value,current_path,matches)

        return result

    def _process_list( self,data: list[Any],path: str, matches: list[PIIMatch]) -> list[Any]:
        return [self._process(value,f"{path}[{index}]",matches)
            for index, value in enumerate(data)]

    def _mask_string(self,value: str,path: str,matches: list[PIIMatch]) -> str:
        value = self._replace_pattern(value,self.EMAIL_PATTERN,"EMAIL",path,matches)

        return self._replace_pattern( value,self.PHONE_PATTERN,"PHONE",path,matches)

    @staticmethod
    def _replace_pattern(value: str,pattern: re.Pattern[str], pii_type: str,path: str,matches: list[PIIMatch]) -> str:
        mask = f"<{pii_type}>"

        def replace(_: re.Match[str]) -> str:
            matches.append(PIIMatch(type=pii_type,path=path,mask=mask))
            return mask

        return pattern.sub(replace, value)

    def _mask_field(self,pii_type: str,path: str,matches: list[PIIMatch],) -> str:
        mask = f"<{pii_type}>"

        matches.append(PIIMatch(type=pii_type,path=path,mask=mask))

        return mask

    def _get_sensitive_field_type(self, key: Any) -> str | None:
        return self.SENSITIVE_FIELDS.get(str(key).lower())

    @staticmethod
    def _build_path(parent: str, key: str) -> str:
        return f"{parent}.{key}" if parent else key

    @staticmethod
    def _build_report(matches: list[PIIMatch]) -> PIIReport:
        return PIIReport(pii_detected=bool(matches),total_matches=len(matches),matches=matches)