from agent.controller import Controller
from agent.worker import DummyWorker


def test_controller_runs_and_writes():
    c = Controller(worker=DummyWorker())
    out = c.run("Find 3 sources on linux tpm issues")
    assert "Answer to:" in out
    assert "Tools Used" in out or "kiwix_query" in out or "gather" in out
