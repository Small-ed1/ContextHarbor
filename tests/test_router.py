from agent.models import Mode
from agent.router import route


def test_override():
    r = route("mode=WRITE find sources")
    assert r.mode == Mode.WRITE
    assert r.override_used is True
    assert r.confidence == 1.0


def test_research_keywords():
    r = route("Find 3 credible sources on X with citations")
    assert r.mode in (Mode.RESEARCH, Mode.HYBRID)
    assert r.tool_budget.limits.get("web_search", 0) >= 3


def test_edit_keywords():
    r = route("Proofread and revise this draft")
    assert r.mode == Mode.EDIT


def test_write_keywords():
    r = route("Write a scene where the hero enters the bunker")
    assert r.mode == Mode.WRITE


def test_low_conf_fallback():
    r = route("yo")
    assert r.mode == Mode.HYBRID
    assert r.warning is not None
