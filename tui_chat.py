#!/usr/bin/env python3
"""
Router Phase 1 TUI Chat Interface
A terminal-based chat interface using Textual.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any

import httpx

from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.text import Text

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (Button, Footer, Header, Input, LoadingIndicator,
                             RichLog, Select, Static)

# Add the agent module to path
sys.path.insert(0, str(Path(__file__).parent))

from agent.cli import cmd_run
from agent.controller import Controller
from agent.worker_ollama import OllamaWorker

HISTORY_LIMIT = 1000


class ChatHistory(Vertical):
    """Widget to display chat history."""

    def __init__(self):
        super().__init__()
        self.messages: List[Dict[str, Any]] = []

    def compose(self) -> ComposeResult:
        yield RichLog(id="chat_log", wrap=True, markup=True)

    def add_message(self, role: str, content: str, format_type: str = "text"):
        """Add a message to the chat history."""
        chat_log = self.query_one("#chat_log", RichLog)

        # Format the message
        if role == "user":
            prefix = "[bold blue]You:[/bold blue] "
        else:
            prefix = "[bold green]Assistant:[/bold green] "

        if format_type == "markdown":
            # Render as markdown
            markdown = Markdown(content)
            chat_log.write(markdown, shrink=False)
        elif format_type == "code":
            # Syntax highlight code
            syntax = Syntax(content, "python", theme="monokai", line_numbers=True)
            chat_log.write(syntax, shrink=False)
        else:
            # Plain text
            chat_log.write(f"{prefix}{content}", shrink=False)

        chat_log.write("")  # Empty line

        # Store message
        self.messages.append({"role": role, "content": content, "format": format_type})

        # Auto-scroll to bottom
        self.scroll_to_bottom()

    def scroll_to_bottom(self):
        """Scroll chat log to bottom."""
        chat_log = self.query_one("#chat_log", RichLog)
        chat_log.scroll_end(animate=False)


class ChatInput(Horizontal):
    """Widget for chat input."""

    def __init__(self):
        super().__init__()
        self.models = ["llama2:7b", "mistral:7b", "codellama:7b", "llama2:13b"]

    def compose(self) -> ComposeResult:
        with Vertical():
            with Horizontal():
                yield Select(
                    options=[(model, model) for model in self.models],
                    value=self.models[0],
                    id="model_select"
                )
                yield Input(placeholder="Type your message here... (Ctrl+C to quit)", id="message_input")
                yield Button("Send", id="send_button", variant="primary")
            yield Static("Use :help for commands | Ctrl+S: Save | Ctrl+O: Load", id="input_hint")

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle model selection change."""
        if event.select.id == "model_select":
            self.app.current_model = event.value
            sidebar = self.app.query_one("#sidebar_widget", Sidebar)
            sidebar.update_model(event.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "send_button":
            self.send_message()

    def send_message(self):
        """Send the current message."""
        input_widget = self.query_one("#message_input", Input)
        message = input_widget.value.strip()
        if message:
            # Clear input
            input_widget.value = ""
            # Send to app
            self.app.send_message(message)


class Sidebar(Vertical):
    """Sidebar widget with model and system info."""

    def __init__(self):
        super().__init__()
        self.model = "llama2:7b"
        self.system_info = "CPU: N/A\nRAM: N/A\nDisk: N/A"

    def compose(self) -> ComposeResult:
        yield Static("[bold]Current Model[/bold]", id="model_title")
        yield Static(self.model, id="model_info")
        yield Static("", id="spacer1")
        yield Static("[bold]System Status[/bold]", id="system_title")
        yield Static(self.system_info, id="system_info")

    def update_model(self, model: str):
        """Update model info."""
        self.model = model
        model_widget = self.query_one("#model_info", Static)
        model_widget.update(model)

    def update_system_info(self):
        """Update system info."""
        try:
            import psutil
            cpu = f"{psutil.cpu_percent()}%"
            ram = f"{psutil.virtual_memory().percent}%"
            disk = f"{psutil.disk_usage('/').percent}%"
            self.system_info = f"CPU: {cpu}\nRAM: {ram}\nDisk: {disk}"
        except ImportError:
            self.system_info = "psutil not available"
        system_widget = self.query_one("#system_info", Static)
        system_widget.update(self.system_info)


class StatusBar(Horizontal):
    """Status bar widget."""

    def __init__(self):
        super().__init__()
        self.status = "Ready"
        self.thinking = False

    def compose(self) -> ComposeResult:
        yield LoadingIndicator(id="loading", style="display: none;")
        yield Static(self.status, id="status_text")

    def update_status(self, status: str, thinking: bool = False):
        """Update the status text."""
        self.status = status
        self.thinking = thinking
        status_widget = self.query_one("#status_text", Static)
        status_widget.update(status)
        loading = self.query_one("#loading", LoadingIndicator)
        loading.styles.display = "block" if thinking else "none"


class RouterChatApp(App):
    """Main TUI chat application."""

    CSS = """
    Screen {
        layout: horizontal;
    }

    #sidebar {
        width: 25;
        border-right: solid $primary;
        background: $primary-darken-3;
        padding: 1;
    }

    #main_area {
        layout: vertical;
        width: 1fr;
    }

    Header {
        height: 3;
        background: $primary;
    }

    Footer {
        height: 3;
        background: $primary-darken-1;
    }

    #chat_container {
        height: 1fr;
        border: solid $primary;
        margin: 1;
    }

    #chat_history {
        height: 1fr;
        border: none;
    }

    #chat_log {
        height: 1fr;
        border: none;
        background: $surface;
    }

    #input_container {
        height: 5;
        border: solid $primary;
        margin: 1;
    }

    #message_input {
        width: 1fr;
        margin: 1;
    }

    #send_button {
        margin: 1;
        width: 10;
    }

    #status_bar {
        height: 2;
        background: $primary-darken-2;
        color: $text;
        text-align: center;
        padding: 0 2;
    }

    #sidebar Static {
        margin-bottom: 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("enter", "send_message", "Send Message"),
        Binding("ctrl+l", "clear_chat", "Clear Chat"),
        Binding("ctrl+h", "show_help", "Help"),
        Binding("ctrl+s", "save_session", "Save Session"),
        Binding("ctrl+o", "load_session", "Load Session"),
        Binding("f5", "refresh_sidebar", "Refresh Sidebar"),
    ]

    def __init__(self):
        super().__init__()
        self.controller = Controller(worker=OllamaWorker())
        self.project = "default"
        self.current_model = "llama2:7b"
        self.history_file = Path.home() / ".router_chat_history"
        self.history: List[str] = []
        self.load_history()

    def compose(self) -> ComposeResult:
        with Container(id="sidebar"):
            yield Sidebar(id="sidebar_widget")
        with Container(id="main_area"):
            yield Header()
            with Container(id="chat_container"):
                yield ChatHistory(id="chat_history")
            with Container(id="input_container"):
                yield ChatInput(id="chat_input")
            yield StatusBar(id="status_bar")
            with Footer():
                yield Static("Router Phase 1 TUI Chat - Press Ctrl+H for help", id="footer_text")

    def on_mount(self) -> None:
        """Called when the app is mounted."""
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.update_status("Initializing...")
        try:
            # Test controller
            self.controller.run("test", project=self.project)
            status_bar.update_status("Ready - Type your message or use Ctrl+H for help")
            # Update sidebar
            sidebar = self.query_one("#sidebar_widget", Sidebar)
            sidebar.update_model(self.current_model)
            sidebar.update_system_info()
            # Update every 30 seconds
            self.set_interval(30, self.update_sidebar)
        except Exception as e:
            status_bar.update_status(f"Error: {str(e)} - Check Ollama")
        # Focus on input
        self.query_one("#message_input", Input).focus()

    def send_message(self, message: str):
        """Send a message and get response."""
        if not message.strip():
            return

        # Check for commands
        if message.startswith(":"):
            self.handle_command(message)
            return

        # Add to history
        self.history.append(message)
        input_widget = self.query_one("#message_input", Input)
        input_widget.history = self.history

        # Add user message to history
        chat_history = self.query_one("#chat_history", ChatHistory)
        chat_history.add_message("user", message)

        # Update status
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.update_status("Thinking...", thinking=True)

        # Process message in background
        asyncio.create_task(self.process_message(message))

    async def process_message(self, message: str):
        """Process the message and get AI response."""
        try:
            # Check model loading
            status_bar = self.query_one("#status_bar", StatusBar)
            if not self.is_model_loaded(self.current_model):
                status_bar.update_status("Loading model...", thinking=True)
                await self.wait_for_model_load(self.current_model)
                status_bar.update_status("Model loaded, thinking...", thinking=True)

            # Run the agent
            response = await asyncio.get_event_loop().run_in_executor(
                None, self._run_agent, message
            )

            # Add response to history
            chat_history = self.query_one("#chat_history", ChatHistory)
            chat_history.add_message("assistant", response, format_type="markdown")

            # Update status
            status_bar.update_status("Ready", thinking=False)

        except Exception as e:
            # Error handling
            chat_history = self.query_one("#chat_history", ChatHistory)
            chat_history.add_message("assistant", f"Error: {str(e)}", format_type="text")

            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status("Error occurred", thinking=False)

    def _run_agent(self, message: str) -> str:
        """Run the agent synchronously."""
        # Check if model is loaded
        if not self.is_model_loaded(self.current_model):
            # Update status to loading
            pass  # Will be handled in process_message
        return self.controller.run(message, project=self.project)

    def is_model_loaded(self, model: str) -> bool:
        """Check if model is loaded via Ollama API."""
        try:
            with httpx.Client(timeout=5) as client:
                response = client.get("http://localhost:11434/api/ps")
                if response.status_code == 200:
                    data = response.json()
                    loaded_models = [m.get("name") for m in data.get("models", [])]
                    return model in loaded_models
        except Exception:
            pass
        return False

    async def wait_for_model_load(self, model: str):
        """Wait for model to be loaded."""
        while not self.is_model_loaded(model):
            await asyncio.sleep(1)

    def load_history(self):
        """Load chat history from file."""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except Exception:
                self.history = []

    def save_history(self):
        """Save chat history to file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history[-HISTORY_LIMIT:], f)  # Keep last 1000 messages
        except Exception:
            pass

    def on_unmount(self):
        """Called when the app is unmounted."""
        self.save_history()

    def update_sidebar(self):
        """Update sidebar system info."""
        sidebar = self.query_one("#sidebar_widget", Sidebar)
        sidebar.update_system_info()

    def handle_command(self, command: str):
        """Handle special commands."""
        parts = command[1:].split()
        cmd = parts[0].lower() if parts else ""

        if cmd in ("help", "h"):
            self.action_show_help()
        elif cmd in ("clear", "c"):
            self.action_clear_chat()
        elif cmd in ("quit", "q"):
            self.exit()
        elif cmd == "save" and len(parts) > 1:
            self.save_session(parts[1])
        elif cmd == "load" and len(parts) > 1:
            self.load_session(parts[1])
        else:
            chat_history = self.query_one("#chat_history", ChatHistory)
            chat_history.add_message("system", f"Unknown command: {command}")

    def save_session(self, name: str):
        """Save current chat session."""
        session_file = Path.home() / f".router_session_{name}.json"
        chat_history = self.query_one("#chat_history", ChatHistory)

        session_data = {
            "messages": chat_history.messages,
            "project": self.project,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }

        try:
            with open(session_file, 'w') as f:
                json.dump(session_data, f, indent=2)
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(f"Session saved: {name}", thinking=False)
        except Exception as e:
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(f"Save failed: {e}")

    def load_session(self, name: str):
        """Load a chat session."""
        session_file = Path.home() / f".router_session_{name}.json"

        if not session_file.exists():
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(f"Session not found: {name}", thinking=False)
            return

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            chat_history = self.query_one("#chat_history", ChatHistory)
            chat_log = chat_history.query_one("#chat_log", RichLog)
            chat_log.clear()

            chat_history.messages = session_data.get("messages", [])
            for msg in chat_history.messages:
                chat_history.add_message(msg["role"], msg["content"], msg.get("format", "text"))

            self.project = session_data.get("project", "default")

            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(f"Session loaded: {name}", thinking=False)

        except Exception as e:
            status_bar = self.query_one("#status_bar", StatusBar)
            status_bar.update_status(f"Load failed: {e}", thinking=False)

    def action_send_message(self):
        """Send message action."""
        input_widget = self.query_one("#message_input", Input)
        message = input_widget.value.strip()
        if message:
            input_widget.value = ""
            self.send_message(message)

    def action_clear_chat(self):
        """Clear chat history."""
        chat_history = self.query_one("#chat_history", ChatHistory)
        chat_log = chat_history.query_one("#chat_log", RichLog)
        chat_log.clear()
        chat_history.messages = []

        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.update_status("Chat cleared", thinking=False)

    def action_show_help(self):
        """Show help."""
        help_text = """
        Router Phase 1 TUI Chat

        Key Bindings:
        Enter - Send message
        Ctrl+L - Clear chat
        Ctrl+H - Show this help
        Ctrl+S - Save session
        Ctrl+O - Load session
        F5 - Refresh sidebar
        Ctrl+C - Quit

        Commands (type with :):
        :help - Show help
        :clear - Clear chat
        :quit - Quit
        :save <name> - Save current session
        :load <name> - Load a session
        """
        chat_history = self.query_one("#chat_history", ChatHistory)
        chat_history.add_message("system", help_text.strip())

    def action_save_session(self):
        """Save session with default name."""
        import datetime
        name = f"session_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.save_session(name)

    def action_load_session(self):
        """Load session (for now, just show message)."""
        chat_history = self.query_one("#chat_history", ChatHistory)
        chat_history.add_message("system", "Use :load <name> to load a session")
        status_bar = self.query_one("#status_bar", StatusBar)
        status_bar.update_status("Ready", thinking=False)

    def action_refresh_sidebar(self):
        """Refresh sidebar info."""
        self.update_sidebar()


def main():
    app = RouterChatApp()
    app.run()


if __name__ == "__main__":
    main()