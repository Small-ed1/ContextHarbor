from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, cast


class ConfigError(RuntimeError):
    pass


def _default_config_dir() -> Path:
    # Windows: prefer %APPDATA%\contextharbor; fallback to ~/.config/contextharbor
    if os.name == "nt":
        appdata = os.getenv("APPDATA")
        if appdata:
            return Path(appdata) / "contextharbor"
    return Path.home() / ".config" / "contextharbor"


def get_config_dir() -> Path:
    raw = (os.getenv("CONTEXTHARBOR_CONFIG_DIR") or "").strip()
    if raw:
        return Path(os.path.expanduser(raw))
    return _default_config_dir()


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        import tomllib  # py3.11+
    except Exception as exc:  # pragma: no cover
        raise ConfigError(f"TOML support unavailable: {exc}")

    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise ConfigError(
            f"Missing config file: {path}. Run `contextharbor run` to generate defaults."
        )
    except Exception as exc:
        raise ConfigError(f"Failed to parse TOML: {path}: {exc}")

    return data if isinstance(data, dict) else {}


def ensure_default_config_files(config_dir: Path) -> list[Path]:
    """Create default core/tools/search TOML files if missing.

    Returns list of created paths.
    """

    config_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    core_path = config_dir / "core.toml"
    tools_path = config_dir / "tools.toml"
    search_path = config_dir / "search.toml"

    if not core_path.exists():
        core_path.write_text(
            """# ContextHarbor core configuration (v1.0)\n\n[core]\nhost = \"0.0.0.0\"\nport = 8000\nreload = false\n\n[models]\nollama_url = \"http://127.0.0.1:11434\"\n# Use the exact tag name shown by `ollama list` (often ends with :latest).\nchat_model = \"llama3.1:latest\"\nembed_model = \"nomic-embed-text:latest\"\n\n[sources]\n# Optional: offline sources + local libraries\n# Leave kiwix_url blank to disable kiwix tools\nkiwix_url = \"\"\nkiwix_zim_dir = \"~/zims\"\nebooks_dir = \"~/Ebooks\"\n\n# Evidence policy for research/deep runs.\n# - strict: only cite evidence-eligible sources\n# - relaxed: allow citations from any retrieved source\ndefault_evidence_policy = \"strict\"\n\n# strict_fail_behavior: when strict mode yields zero evidence-eligible sources\n# - refuse: return a "no evidence found" message (recommended)\n# - speculative: answer with clearly-labeled speculation (no citations)\nstrict_fail_behavior = \"refuse\"\n\n[sources.evidence_allowlist]\n# Which source kinds are evidence-eligible in strict mode.\n# Note: EPUBs are handled separately (see [sources.epub]).\nstrict = [\"kiwix_zim\", \"web\", \"uploaded_doc\"]\n\n[sources.kiwix]\n# Optional: only allow these zims as evidence in strict mode (substring match, case-insensitive).\n# Leave empty to allow all zims.\nevidence_zim_allowlist = []\n\n[sources.epub]\n# EPUBs default to context-only in strict mode unless explicitly enabled by genre.\ndefault_genre = \"unknown\"  # unknown|fiction|nonfiction|reference\nnonfiction_is_evidence = false\nreference_is_evidence = false\nfiction_is_evidence = false\n\n[sources.trust_tiers]\n# Optional weights for provenance (0.0..1.0). Used for audit/UX; not required for retrieval.\nkiwix_zim = 0.8\nweb = 0.7\nuploaded_doc = 0.6\nepub_nonfiction = 0.5\nepub_reference = 0.6\nepub_fiction = 0.0\nepub_unknown = 0.0\n\n[paths]\n# data_dir controls where ContextHarbor stores its sqlite DBs\ndata_dir = \"~/.contextharbor/data\"\n\n[limits]\nmax_upload_bytes = 10485760\nmax_research_rounds = 6\nmax_pages_per_round = 12\nmax_web_queries = 6\nmax_doc_queries = 6\nmax_json_parse_size = 100000\n\n""",
            encoding="utf-8",
        )
        created.append(core_path)

    if not tools_path.exists():
        tools_path.write_text(
            """# ContextHarbor tool configuration (v1.0)\n\n[tools]\n# Enable/disable tools by name\nenabled = [\"web_search\", \"doc_search\", \"library_search\", \"kiwix_search\", \"local_file_read\"]\n# Optional: additional python modules that register tools\nplugin_modules = []\n# Example plugin:\n# plugin_modules = [\"contextharbor_example_plugin\"]\n\n[tools.local_file_read]\n# Allowed roots for local_file_read (expanduser supported)\nroots = [\"~\"]\nmax_bytes = 200000\n\n[tools.shell_exec]\n# When enabling, also add \"shell_exec\" to tools.enabled.\nenabled = false\n# When enabled, shell_exec requires an explicit confirmation token\nrequires_confirmation = true\n# Allowed commands (first argv element)\nallow = [\"git\", \"python\", \"python3\"]\n\n""",
            encoding="utf-8",
        )
        created.append(tools_path)

    if not search_path.exists():
        search_path.write_text(
            """# ContextHarbor web search configuration (v1.0)\n\n[search]\nenabled = true\nprovider = \"ddg\"\n# Optional: SearxNG instance URL. Accepts either base URL (http://host:port)\n# or full endpoint (http://host:port/search).\nsearxng_url = \"\"\n# User-Agent sent for search requests\nuser_agent = \"ContextHarbor/1.0\"\n# Minimum seconds between provider requests\nmin_interval_seconds = 2.0\n# Optional SSRF safety controls\nallowed_hosts = []\nblocked_hosts = []\n\n""",
            encoding="utf-8",
        )
        created.append(search_path)

    return created


@dataclass(frozen=True)
class Config:
    # core
    host: str
    port: int
    reload: bool

    # models
    ollama_url: str
    default_chat_model: str
    default_embed_model: str

    # sources (library)
    kiwix_url: str
    kiwix_zim_dir: str
    ebooks_dir: str

    # evidence policy (research/deep)
    default_evidence_policy: str
    strict_fail_behavior: str
    evidence_allowlist_strict: list[str]
    kiwix_evidence_zim_allowlist: list[str]
    epub_default_genre: str
    epub_nonfiction_is_evidence: bool
    epub_reference_is_evidence: bool
    epub_fiction_is_evidence: bool
    trust_tiers: dict[str, float]

    # search
    web_user_agent: str
    web_allowed_hosts: str
    web_blocked_hosts: str
    search_enabled: bool
    search_provider: str
    search_min_interval_seconds: float
    searxng_url: str

    # tools
    enabled_tools: list[str]
    tool_plugin_modules: list[str]
    local_file_roots: list[str]
    local_file_max_bytes: int
    shell_exec_enabled: bool
    shell_exec_allow: list[str]
    shell_exec_requires_confirmation: bool

    # paths
    data_dir: str
    rag_db: str
    chat_db: str
    web_db: str
    research_db: str
    tool_db: str

    # limits
    max_upload_bytes: int
    max_research_rounds: int
    max_pages_per_round: int
    max_web_queries: int
    max_doc_queries: int
    max_json_parse_size: int


def _expand_path(p: str) -> str:
    return str(Path(os.path.expanduser(p)).resolve())


def _as_dict(val: Any) -> dict[str, Any]:
    return val if isinstance(val, dict) else {}


def load_config(*, config_dir: Path | None = None) -> Config:
    cfg_dir = config_dir or get_config_dir()
    core: dict[str, Any] = _read_toml(cfg_dir / "core.toml")
    tools: dict[str, Any] = _read_toml(cfg_dir / "tools.toml")
    search: dict[str, Any] = _read_toml(cfg_dir / "search.toml")

    core_core = _as_dict(core.get("core"))
    core_models = _as_dict(core.get("models"))
    core_paths = _as_dict(core.get("paths"))
    core_sources = _as_dict(core.get("sources"))
    core_limits = _as_dict(core.get("limits"))

    tools_sec = _as_dict(tools.get("tools"))
    tools_local = _as_dict(tools_sec.get("local_file_read"))
    tools_shell = _as_dict(tools_sec.get("shell_exec"))

    search_sec = _as_dict(search.get("search"))

    host_raw = str(core_core.get("host") or "0.0.0.0").strip()
    # Always bind the server to all interfaces by default.
    # Treat common loopback values as aliases so restarts behave consistently.
    host = "0.0.0.0" if host_raw in {"", "127.0.0.1", "localhost"} else host_raw
    port = int(core_core.get("port") or 8000)
    reload = bool(core_core.get("reload") or False)

    ollama_url = str(core_models.get("ollama_url") or "http://127.0.0.1:11434").rstrip(
        "/"
    )
    chat_model = str(core_models.get("chat_model") or "llama3.1")
    embed_model = str(core_models.get("embed_model") or "nomic-embed-text")

    # Sources / library
    # Prefer config file; fallback to env for backwards compatibility.
    kiwix_url = str(
        core_sources.get("kiwix_url") or os.getenv("KIWIX_URL") or ""
    ).rstrip("/")
    kiwix_zim_dir_raw = str(
        core_sources.get("kiwix_zim_dir") or os.getenv("KIWIX_ZIM_DIR") or "~/zims"
    )
    ebooks_dir_raw = str(
        core_sources.get("ebooks_dir") or os.getenv("EBOOKS_DIR") or "~/Ebooks"
    )
    kiwix_zim_dir = _expand_path(kiwix_zim_dir_raw)
    ebooks_dir = _expand_path(ebooks_dir_raw)

    # Evidence policy (research/deep)
    default_evidence_policy = (
        str(core_sources.get("default_evidence_policy") or "strict").strip().lower()
    )
    if default_evidence_policy not in {"strict", "relaxed"}:
        default_evidence_policy = "strict"

    strict_fail_behavior = (
        str(core_sources.get("strict_fail_behavior") or "refuse").strip().lower()
    )
    if strict_fail_behavior not in {"refuse", "speculative"}:
        strict_fail_behavior = "refuse"

    allow_any = _as_dict(core_sources.get("evidence_allowlist"))
    strict_allow_raw = allow_any.get("strict")
    evidence_allowlist_strict = (
        [str(x).strip().lower() for x in strict_allow_raw]
        if isinstance(strict_allow_raw, list)
        else []
    )
    evidence_allowlist_strict = [x for x in evidence_allowlist_strict if x]
    if not evidence_allowlist_strict:
        evidence_allowlist_strict = ["kiwix_zim", "web", "uploaded_doc"]

    kiwix_sec = _as_dict(core_sources.get("kiwix"))
    zim_allow_raw = kiwix_sec.get("evidence_zim_allowlist")
    kiwix_evidence_zim_allowlist = (
        [str(x).strip().lower() for x in zim_allow_raw]
        if isinstance(zim_allow_raw, list)
        else []
    )
    kiwix_evidence_zim_allowlist = [x for x in kiwix_evidence_zim_allowlist if x]

    epub_sec = _as_dict(core_sources.get("epub"))
    epub_default_genre = str(epub_sec.get("default_genre") or "unknown").strip().lower()
    if epub_default_genre not in {"unknown", "fiction", "nonfiction", "reference"}:
        epub_default_genre = "unknown"

    epub_nonfiction_is_evidence = bool(epub_sec.get("nonfiction_is_evidence") or False)
    epub_reference_is_evidence = bool(epub_sec.get("reference_is_evidence") or False)
    epub_fiction_is_evidence = bool(epub_sec.get("fiction_is_evidence") or False)

    tiers_any = _as_dict(core_sources.get("trust_tiers"))
    trust_tiers: dict[str, float] = {}
    for k, v in tiers_any.items():
        kk = str(k).strip().lower()
        if not kk:
            continue
        try:
            trust_tiers[kk] = float(v)
        except Exception:
            continue

    data_dir_raw = str(core_paths.get("data_dir") or "~/.contextharbor/data")
    data_dir = _expand_path(data_dir_raw)
    Path(data_dir).mkdir(parents=True, exist_ok=True)

    max_upload_bytes = int(core_limits.get("max_upload_bytes") or (10 * 1024 * 1024))
    max_research_rounds = int(core_limits.get("max_research_rounds") or 6)
    max_pages_per_round = int(core_limits.get("max_pages_per_round") or 12)
    max_web_queries = int(core_limits.get("max_web_queries") or 6)
    max_doc_queries = int(core_limits.get("max_doc_queries") or 6)
    max_json_parse_size = int(core_limits.get("max_json_parse_size") or 100000)

    search_enabled = bool(
        search_sec.get("enabled") if "enabled" in search_sec else True
    )
    search_provider = str(search_sec.get("provider") or "ddg")
    web_user_agent = str(search_sec.get("user_agent") or "ContextHarbor/1.0")
    search_min_interval_seconds = float(search_sec.get("min_interval_seconds") or 2.0)

    searxng_url = (
        str(search_sec.get("searxng_url") or os.getenv("SEARXNG_URL") or "")
        .strip()
        .rstrip("/")
    )

    enabled_tools_raw = tools_sec.get("enabled")
    enabled_tools = (
        [str(x) for x in enabled_tools_raw]
        if isinstance(enabled_tools_raw, list)
        else []
    )

    plugin_raw = tools_sec.get("plugin_modules")
    tool_plugin_modules = (
        [str(x) for x in plugin_raw] if isinstance(plugin_raw, list) else []
    )

    roots_raw = tools_local.get("roots")
    local_file_roots = (
        [str(x) for x in roots_raw] if isinstance(roots_raw, list) else []
    )
    local_file_max_bytes = int(tools_local.get("max_bytes") or 200000)

    shell_exec_enabled = bool(tools_shell.get("enabled") or False)
    shell_exec_requires_confirmation = bool(
        tools_shell.get("requires_confirmation")
        if "requires_confirmation" in tools_shell
        else True
    )
    shell_allow_raw = tools_shell.get("allow")
    shell_exec_allow = (
        [str(x) for x in shell_allow_raw] if isinstance(shell_allow_raw, list) else []
    )

    # SSRF safety lists are enforced in webstore/web_fetch; keep as comma-joined for legacy callers.
    allowed_hosts = search_sec.get("allowed_hosts")
    blocked_hosts = search_sec.get("blocked_hosts")
    web_allowed_hosts = (
        ",".join([str(x) for x in allowed_hosts])
        if isinstance(allowed_hosts, list)
        else ""
    )
    web_blocked_hosts = (
        ",".join([str(x) for x in blocked_hosts])
        if isinstance(blocked_hosts, list)
        else ""
    )

    return Config(
        host=host,
        port=port,
        reload=reload,
        ollama_url=ollama_url,
        default_chat_model=chat_model,
        default_embed_model=embed_model,
        kiwix_url=kiwix_url,
        kiwix_zim_dir=kiwix_zim_dir,
        ebooks_dir=ebooks_dir,
        default_evidence_policy=default_evidence_policy,
        strict_fail_behavior=strict_fail_behavior,
        evidence_allowlist_strict=evidence_allowlist_strict,
        kiwix_evidence_zim_allowlist=kiwix_evidence_zim_allowlist,
        epub_default_genre=epub_default_genre,
        epub_nonfiction_is_evidence=epub_nonfiction_is_evidence,
        epub_reference_is_evidence=epub_reference_is_evidence,
        epub_fiction_is_evidence=epub_fiction_is_evidence,
        trust_tiers=trust_tiers,
        web_user_agent=web_user_agent,
        web_allowed_hosts=web_allowed_hosts,
        web_blocked_hosts=web_blocked_hosts,
        search_enabled=search_enabled,
        search_provider=search_provider,
        search_min_interval_seconds=search_min_interval_seconds,
        searxng_url=searxng_url,
        enabled_tools=enabled_tools,
        tool_plugin_modules=tool_plugin_modules,
        local_file_roots=local_file_roots,
        local_file_max_bytes=local_file_max_bytes,
        shell_exec_enabled=shell_exec_enabled,
        shell_exec_allow=shell_exec_allow,
        shell_exec_requires_confirmation=shell_exec_requires_confirmation,
        data_dir=data_dir,
        rag_db=str(Path(data_dir) / "rag.sqlite3"),
        chat_db=str(Path(data_dir) / "chat.sqlite3"),
        web_db=str(Path(data_dir) / "web.sqlite3"),
        research_db=str(Path(data_dir) / "research.sqlite3"),
        tool_db=str(Path(data_dir) / "tool.sqlite3"),
        max_upload_bytes=max_upload_bytes,
        max_research_rounds=max_research_rounds,
        max_pages_per_round=max_pages_per_round,
        max_web_queries=max_web_queries,
        max_doc_queries=max_doc_queries,
        max_json_parse_size=max_json_parse_size,
    )


class _ConfigHandle:
    """Lazy config loader.

    Importing `contextharbor.config` should not immediately require config files.
    The first attribute access triggers a load.
    """

    def __init__(self) -> None:
        self._cfg: Config | None = None

    def reload_from_disk(self) -> Config:
        self._cfg = load_config()
        return self._cfg

    def _ensure(self) -> Config:
        if self._cfg is None:
            self._cfg = load_config()
        return self._cfg

    def __getattr__(self, name: str) -> Any:
        return getattr(self._ensure(), name)


# Singleton used across the codebase: `from contextharbor import config; config.config.ollama_url`
config = _ConfigHandle()
