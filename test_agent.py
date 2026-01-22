#!/usr/bin/env python3

from scripts.ollama_tool_agent import AgentConfig, ToolCallingAgent, build_registry
import os

# Set environment if needed
os.environ["OLLAMA_HOST"] = "http://localhost:11434"
os.environ["OLLAMA_MODEL"] = "qwen3:8b"
os.environ["DEBUG_AGENT"] = "1"

cfg = AgentConfig()
agent = ToolCallingAgent(cfg, build_registry())

# Smoke test prompt
prompt = "what is 2+2"
print(f"Testing prompt: {prompt}")
result = agent.run(prompt)
print("Result:")
print(result)