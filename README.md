# ai-pdb

The Python Debugger (PDb) augmented with AI.

## Description

`ai-pdb` is an enhanced version of the Python Debugger (PDb) that integrates AI capabilities to assist with debugging tasks. This tool leverages the power of [Claude](https://claude.ai) to provide more insightful debugging information and suggestions.

Use Claude directly from your debugging environment to avoid copying and pasting back and forth.

## Features

- AI-assisted debugging prompts
- Enhanced context-aware debugging
- Integration with the Anthropic API for AI responses

## Installation

Install using `pip`:

```sh
pip install ai-pdb
```

## Usage

You should have `ANTHROPIC_API_KEY` available in your ENV to be able to use this tool.

To use `ai-pdb`, simply import it in your Python script and start the debugger as you normally would:

```python
from ai_pdb.ai_pdb import AIPdb

debugger = AIPdB()

debugger.set_trace()
```

Once you’re in a debugging session, you can use the `ai` command to assist you with debugging.

There are three sub-commands available:

### `debug`

```sh
ai
ai debug
```

This is the default and is equivalent you just invoking `ai` from the debugging shell.

This will provide Claude with your current execution context and it will help you understand what’s going on, help you fix errors, etc.

### `docs`

```sh
ai docs
```

This will provide documentation relevant to the execution context.

### `query`

```sh
ai query <custom query>
```

You can ask Claude anything. Your question is automatically enriched with the execution context, providing all necessary information.
