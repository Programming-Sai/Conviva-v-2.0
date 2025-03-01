---
# Conviva – CLI AI Assistant

Conviva is a command-line AI assistant designed to provide an interactive, conversational experience. Whether you're asking for calculations, system information, media analysis, or simply engaging in a chat, Conviva integrates a variety of tools and utilities to make your interaction seamless.

> **Note:** This version focuses on the CLI interface. A GUI version is in the works but is not part of this branch.
---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture & Modules](#architecture--modules)
  - [CLI Colors (`cli_colors.py`)](#cli-colors)
  - [Conversation Management (`conversations.py`)](#conversation-management)
  - [LLM & Tools Integration (`llm_processing.py`)](#llm--tools-integration)
  - [Main CLI Interface (`CLI.py`)](#main-cli-interface)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Arguments](#command-line-arguments)
- [Future Improvements](#future-improvements)

---

## Overview

Conviva is a personal assistant that leverages AI tools to engage in conversations, process multimedia inputs (images, audio), and execute various utility functions (like taking screenshots, controlling system volume, opening websites, etc.). The application is designed to store conversation histories in JSON files, allowing you to manage (create, open, edit, delete, and search) multiple conversation sessions easily.

---

## Features

- **Conversational Interface:** Engage in interactive chats using text (and eventually, speech).
- **Conversation Management:** Create new conversations, list, open, edit (rename), delete, and search through saved conversations.
- **Media Analysis:** Use integrated functions to analyze images and audio files.
- **System Tools:** Perform calculations, retrieve system info, open websites, take screenshots, control volume, lock the screen, and more.
- **Dynamic CLI Output:** Enhanced CLI output with color and formatting using ANSI escape codes.

---

## Architecture & Modules

### CLI Colors

The module **`cli_colors.py`** contains the `AsciiColors` class which provides:

- ANSI escape codes for various text and background colors.
- Text styles like bold, underline, italic, and strikethrough.
- Utility methods for coloring text, applying random styles, and centering text based on terminal size.

### Conversation Management

The **`conversations.py`** module defines the `Conversation` class that:

- Creates and manages conversation history stored as JSON files.
- Generates unique conversation file names based on timestamps and user-provided titles.
- Provides functions to append new messages to the conversation, list conversation histories, and switch between conversations.

### LLM & Tools Integration

The **`llm_processing.py`** module includes:

- A set of utility functions that execute AI-powered tasks such as:
  - Evaluating mathematical expressions.
  - Opening command prompts and websites.
  - Telling the current time and date.
  - Playing videos and analyzing images and audio.
- Integration with a Groq API client to handle chat completions and tool calls.
- Global functions for speech recognition (`get_speech`) and text-to-speech output (`say`).
- Definition of `all_tools` and `all_functions` for dynamically handling available AI functions.

### Main CLI Interface

The **`CLI.py`** file is the entry point for the command-line interface. It:

- Inherits from Python’s built-in `argparse.ArgumentParser` to define various command-line arguments.
- Uses **questionary** for interactive prompts when managing conversations and selecting voices.
- Provides functions to:
  - Start or continue a conversation.
  - Process user input (text and, optionally, speech).
  - Manage conversation history (open, clear, edit, delete, search).
  - Paginate through long lists (e.g., available voices).
- Integrates all other modules to offer a seamless CLI experience.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone -b cli --single-branch https://github.com/Programming-Sai/Conviva-v-2.0.git
   cd Conviva-v-2.0
   ```

2. **Set Up a Virtual Environment (Recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the project root and add your Groq API key:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

---

## Usage

Run the CLI tool using:

```bash
python CLI.py [OPTIONS]
```

### Command-Line Arguments

The following arguments are available for managing conversations and interacting with Conviva:

- **Conversation Management:**

  - `-n, --new-conversation`  
    _Start a new conversation session, separate from previous ones._

  - `-l, --list-conversation`  
    _List all stored conversations with their names and timestamps._

  - `-o, --open-conversation`  
    _Open and view a saved conversation by providing its name (via an interactive prompt)._

  - `-c, --clear-conversation`  
    _Delete all stored conversations and reset conversation history._

  - `-e, --edit-conversation`  
    _Rename a saved conversation by providing its current name._

  - `-d, --delete-conversation`  
    _Delete a specific conversation by providing its name._

  - `-F, --search-conversation`  
    _Enter an interactive mode to search for specific conversations._  
    Use with `-k, --search-key` to provide a keyword.

- **GUI Option:**
  - `--gui`  
    _Launch the graphical user interface (GUI) for the application (if implemented)._

When no arguments are provided, Conviva starts a default text-based conversation.

---

## Future Improvements

- **Standalone Packaging:**  
  Create standalone executables using PyInstaller for easier distribution.
- **Enhanced AI Features:**  
  Expand tool integrations and improve natural language understanding.
- **Refined Speech Integration:**  
  Enhance speech recognition and text-to-speech features across platforms.

---
