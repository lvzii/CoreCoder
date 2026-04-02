# NanoCoder

[![PyPI](https://img.shields.io/pypi/v/nanocoder)](https://pypi.org/project/nanocoder/)
[![Python](https://img.shields.io/badge/python-3.10+-blue)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Tests](https://github.com/he-yufeng/NanoCoder/actions/workflows/ci.yml/badge.svg)](https://github.com/he-yufeng/NanoCoder/actions)

[English](README.md) | [中文](README_CN.md) | [Claude Code Architecture Deep Dive (7 articles)](article/)

**512,000 lines of TypeScript → 1,300 lines of Python.**

I read every line of the leaked Claude Code source. Then I threw away everything that wasn't load-bearing and rebuilt the core in Python. This is the result: a fully functional AI coding agent that fits in your head.

> *Think [nanoGPT](https://github.com/karpathy/nanoGPT) for coding agents.*

---

```
$ nanocoder -m deepseek-chat

You > read main.py and fix the broken import

  > read_file(file_path='main.py')
  > edit_file(file_path='main.py', ...)

--- a/main.py
+++ b/main.py
@@ -1 +1 @@
-from utils import halper
+from utils import helper

Fixed: halper → helper.
```

---

## Why

Claude Code only works with Anthropic's API. Its source is 512K lines you can't modify. And every other "alternative" is either a 100K-line project you can't read, or a wrapper with no real architecture.

NanoCoder is **1,300 lines** with every key design pattern from Claude Code:

- **Search-and-replace editing** — unique match required, unified diff output. No more editing the wrong line.
- **Parallel tool execution** — ThreadPool runs independent tools concurrently. Same idea as Claude Code's StreamingToolExecutor.
- **3-layer context compression** — snip tool outputs → LLM summarize → hard collapse. Mirrors HISTORY_SNIP → Microcompact → CONTEXT_COLLAPSE.
- **Sub-agent spawning** — delegate complex sub-tasks to agents with isolated context.
- **Dangerous command blocking** — `rm -rf /`, fork bombs, `curl | bash`.
- **Working directory tracking** — `cd` in bash actually works across commands.
- **API retry with backoff** — 429, timeout, 5xx handled automatically.
- **Session persistence** — save/resume conversations.

## Install

```bash
pip install nanocoder
```

```bash
# DeepSeek
export OPENAI_API_KEY=sk-... OPENAI_BASE_URL=https://api.deepseek.com
nanocoder -m deepseek-chat

# Qwen
export OPENAI_API_KEY=sk-... OPENAI_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
nanocoder -m qwen-plus

# Ollama (local)
export OPENAI_API_KEY=ollama OPENAI_BASE_URL=http://localhost:11434/v1
nanocoder -m qwen2.5-coder

# OpenAI
export OPENAI_API_KEY=sk-...
nanocoder

# One-shot
nanocoder -p "add error handling to parse_config()"
```

Works with **any OpenAI-compatible API**: OpenAI, DeepSeek, Qwen, Kimi, GLM, Ollama, vLLM, OpenRouter, Together AI.

## Architecture

```
nanocoder/
├── cli.py            REPL + commands               160 lines
├── agent.py          Agent loop + parallel tools    120 lines
├── llm.py            Streaming client + retry       150 lines
├── context.py        3-layer compression            145 lines
├── session.py        Save/resume                     65 lines
├── prompt.py         System prompt                   35 lines
├── config.py         Env config                      30 lines
└── tools/
    ├── bash.py       Shell + safety + cd tracking    95 lines
    ├── edit.py       Search-replace + diff            70 lines
    ├── read.py       File reading                     40 lines
    ├── write.py      File writing                     30 lines
    ├── glob_tool.py  File search                      35 lines
    ├── grep.py       Content search                   65 lines
    └── agent.py      Sub-agent spawning               50 lines
```

## Use as a Library

```python
from nanocoder import Agent, LLM

llm = LLM(model="deepseek-chat", api_key="sk-...", base_url="https://api.deepseek.com")
agent = Agent(llm=llm)
response = agent.chat("find all TODO comments in this project")
```

## Add Your Own Tools

```python
from nanocoder.tools.base import Tool

class HttpTool(Tool):
    name = "http"
    description = "Fetch a URL."
    parameters = {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}

    def execute(self, url: str) -> str:
        import urllib.request
        return urllib.request.urlopen(url).read().decode()[:5000]
```

## Commands

```
/model <name>    Switch model
/compact         Compress context
/tokens          Token usage
/save            Save session
/sessions        List sessions
/reset           Clear history
quit             Exit
```

## How It Compares

|  | Claude Code | Claw-Code | Aider | NanoCoder |
|---|---|---|---|---|
| Code | 512K lines (closed) | 100K+ lines | 50K+ lines | **1,300 lines** |
| Models | Anthropic only | Multi | Multi | **Any OpenAI-compatible** |
| Readable? | No | Hard | Medium | **One afternoon** |
| Purpose | Use it | Use it | Use it | **Understand it, build yours** |

## The Deep Dive

I wrote [7 articles](article/) breaking down Claude Code's architecture in detail — the agent loop, tool system, context compression, streaming executor, multi-agent, and hidden features behind 44 feature flags. If you want to understand *why* NanoCoder is built this way, start there.

## License

MIT. Fork it, learn from it, ship something better.

---

Built by **[Yufeng He](https://github.com/he-yufeng)** · Agentic AI Researcher @ Moonshot AI (Kimi)

[Claude Code Source Analysis — 170K+ reads on Zhihu](https://zhuanlan.zhihu.com/p/1898797658343862272)
