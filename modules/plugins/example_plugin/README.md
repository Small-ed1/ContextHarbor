# Example CogniHub Tool Plugin

This is a minimal tool plugin demonstrating CogniHub's tool extension API.

## Install

From the repo root:

```bash
pip install -e modules/plugins/example_plugin
```

## Enable

Edit your `tools.toml` (usually under `%APPDATA%\\cognihub` on Windows):

```toml
[tools]
enabled = ["web_search", "doc_search", "local_file_read", "example_time"]
plugin_modules = ["cognihub_example_plugin"]
```

Restart CogniHub.

## Tools

- `example_time`: returns the server's current time.
