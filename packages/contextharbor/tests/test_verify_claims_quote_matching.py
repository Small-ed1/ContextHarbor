from __future__ import annotations

import json

import pytest


@pytest.mark.asyncio
async def test_verify_claims_accepts_whitespace_normalized_quotes(monkeypatch: pytest.MonkeyPatch) -> None:
    from contextharbor.services import research

    # Context includes line breaks + extra spaces.
    context_lines = [
        "[D1] Long-term monitoring showed species richness increased\n   over decades in the exclusion plots.",
    ]

    verifier_json = {
        "claims": [
            {
                "claim": "Species richness increased over decades in exclusion plots.",
                "status": "supported",
                "citations": ["D1"],
                "evidence": [
                    {
                        "citation": "D1",
                        # Same words, different whitespace/newlines.
                        "quote": "species richness increased over decades in the exclusion plots",
                    }
                ],
                "notes": "",
            }
        ]
    }

    async def fake_chat_once(*args, **kwargs) -> str:
        return json.dumps(verifier_json)

    monkeypatch.setattr(research, "_ollama_chat_once", fake_chat_once)

    out = await research._verify_claims(
        http=None,  # not used by fake
        base_url="http://ollama",
        verifier_model="m",
        query="q",
        context_lines=context_lines,
    )

    claims = out.get("claims")
    assert isinstance(claims, list)
    assert claims and claims[0].get("status") == "supported"
