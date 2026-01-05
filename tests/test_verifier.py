from agent.context import RunContext
from agent.models import Source, SourceType
from agent.router import route
from agent.verifier import verify


def test_research_requires_sources_and_inline_urls():
    dec = route("find sources on X")
    ctx = RunContext(objective="x", decision=dec)
    ctx.sources = [
        Source(
            source_id=Source.generate_id("test", "https://kernel.org/", "Kernel"),
            tool="test",
            source_type=SourceType.WEB,
            title="Kernel",
            locator="https://kernel.org/",
            snippet="Kernel documentation",
        ),
        Source(
            source_id=Source.generate_id(
                "test", "https://docs.python.org/3/", "Python"
            ),
            tool="test",
            source_type=SourceType.WEB,
            title="Python",
            locator="https://docs.python.org/3/",
            snippet="Python docs",
        ),
        Source(
            source_id=Source.generate_id(
                "test", "https://tailscale.com/kb/", "Tailscale"
            ),
            tool="test",
            source_type=SourceType.WEB,
            title="Tailscale",
            locator="https://tailscale.com/kb/",
            snippet="Tailscale knowledge base",
        ),
    ]
    out = "- ok (https://kernel.org/)\n- ok (https://docs.python.org/3/)\n- ok (https://tailscale.com/kb/)\n"
    v = verify(ctx, out)
    assert v.passed is True
