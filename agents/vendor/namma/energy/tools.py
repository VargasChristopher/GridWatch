"""
tools.py – always-grounded Gemini helper. Settings come from agent_config.json.
"""

from __future__ import annotations

import json, logging, re
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, List

from google import genai

# ── load config -------------------------------------------------------------
_CFG = json.loads(Path(__file__).with_name("agent_config.json").read_text())
_MODEL_ID: str = _CFG["model_id"]
_TEMP: float = float(_CFG["temperature"])

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class GroundedGemini:
    """ask_json(prompt) → list[dict] (always Google-Search grounded)."""

    # lazy SDK
    @cached_property
    def _client(self) -> genai.Client:
        return genai.Client()

    _SEARCH_TOOL = [{"google_search": {}}]

    @staticmethod
    def _strip_fences(text: str) -> str:
        m = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
        return m.group(1) if m else text

    # ----------------------------------------------------------------------
    def ask_json(self, prompt: str) -> List[Dict[str, Any]]:
        resp = self._client.models.generate_content(
            model=_MODEL_ID,
            contents=prompt,
            config={
                "tools": self._SEARCH_TOOL,
                "temperature": _TEMP,
            },
        )

        gm = resp.candidates[0].grounding_metadata
        if gm and gm.web_search_queries:
            logger.info("🔎 Google-Search queries: %s", gm.web_search_queries)
        else:
            raise RuntimeError(
                "Google-Search grounding NOT invoked – aborting.\n"
                "Check SDK version, API key, or network."
            )

        cleaned = self._strip_fences(resp.text)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error("JSON parse error: %s\nOffending text:\n%s", e, cleaned)
            return []


# singleton
gt = GroundedGemini()
