# Study Context

## Overview

This is a command-line interface (CLI) tool that processes lecture transcripts to automatically create study guides. It segments the transcript, uses OpenAI's powerful language models to extract key concepts and generate question/answer pairs, and then formats this information into a plain text study guide.

## Features

*   Parses plain text transcripts.
*   Cleans transcript data by removing filler words and normalizing whitespace.
*   Segments the transcript into manageable chunks based on word count.
*   Utilizes OpenAI's GPT models (currently defaults to `gpt-4o`) to:
    *   Extract key concepts with comprehensive explanations.
    *   Generate insightful question and answer pairs that promote deeper understanding.
*   Formats the output into a structured plain text study guide.
*   Allows output to a specified file or prints to the console.
*   Includes basic error handling and retry logic for API calls.

## Prerequisites

*   Python 3.10 or higher
*   pip (Python package installer)

## Setup

1.  **Clone the Repository (if applicable)**
    If you've cloned this project from a Git repository, navigate to the project directory:
    ```bash
    git clone <repository_url>
    cd studycontext
    ```
    If you have the files locally, ensure you are in the root directory of the project (`studycontext`).

2.  **Create and Activate a Virtual Environment**
    It's highly recommended to use a virtual environment to manage project dependencies.

    *   Create a virtual environment (e.g., named `.venv`):
        ```bash
        python3 -m venv .venv
        ```
    *   Activate the virtual environment:
        *   On macOS and Linux:
            ```bash
            source .venv/bin/activate
            ```
        *   On Windows:
            ```bash
            .\.venv\Scripts\activate
            ```

3.  **Install Dependencies**
    With the virtual environment activated, install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set Up OpenAI API Key**
    The tool requires an OpenAI API key to function. You need to set this key as an environment variable named `OPENAI_API_KEY`.

    *   **Option 1: Export for the current session (macOS/Linux)**
        ```bash
        export OPENAI_API_KEY="YOUR_API_KEY_HERE"
        ```
        Replace `"YOUR_API_KEY_HERE"` with your actual OpenAI API key.
        To make this persistent across sessions, you can add this line to your shell's configuration file (e.g., `~/.bashrc`, `~/.zshrc`).

    *   **Option 2: Using a file (example for macOS/Linux)**
        If you have your API key in a file (e.g., `~/.openaikey`), you can set it like this:
        ```bash
        export OPENAI_API_KEY=$(cat ~/.openaikey)
        ```
    *   **Option 3: Windows (Command Prompt)**
        ```bash
        set OPENAI_API_KEY=YOUR_API_KEY_HERE
        ```
    *   **Option 4: Windows (PowerShell)**
        ```bash
        $env:OPENAI_API_KEY="YOUR_API_KEY_HERE"
        ```
        For persistence on Windows, you can set it through the System Properties > Environment Variables.

    **Important:** Keep your API key secure and do not commit it to version control.

## Running the Tool

Once the setup is complete, you can run the Study Guide Generator from the root directory of the project (`studycontext`) using the following command structure:

```bash
python src/main.py <transcript_file_path> [options]
```

**Arguments:**

*   `transcript_file_path`: (Required) The path to the plain text transcript file you want to process.

**Options:**

*   `-o OUTPUT_FILE`, `--output_file OUTPUT_FILE`: (Optional) The path to the file where the study guide will be saved. If not provided, the study guide will be printed to the console.
*   `-w WORDS_PER_SEGMENT`, `--words_per_segment WORDS_PER_SEGMENT`: (Optional) The approximate number of words each text segment should contain before being sent to the LLM. Defaults to 750. Adjust this based on the nature of your transcript and desired granularity.

**Examples:**

1.  Process `week1_transcript.txt` and print the study guide to the console:
    ```bash
    python src/main.py week1_transcript.txt
    ```

2.  Process `my_lecture.txt`, save the output to `my_study_guide.txt`, and use 1000 words per segment:
    ```bash
    python src/main.py my_lecture.txt --output_file my_study_guide.txt --words_per_segment 1000
    ```

## Output

The tool will generate a plain text (`.txt`) study guide. The guide is structured with:
*   A main title.
*   Separators for each processed segment.
*   For each segment:
    *   "Key Concepts & Definitions" section with comprehensive explanations.
    *   "Practice Questions & Answers" section with insightful Q&A pairs.

If an output file is specified, the guide will be saved there. Otherwise, it will be printed to your terminal.

## OpenAI Model Choice

*   This tool utilizes an OpenAI language model to generate the content for the study guide.
*   Currently, it defaults to using the `gpt-4o` model, which is known for its strong comprehension and generation capabilities, making it well-suited for creating detailed and nuanced study materials.
*   The model is defined as a default parameter in the `call_llm` function within the `src/llm_chain/chain.py` file. Advanced users can modify this if they wish to experiment with other models (e.g., `gpt-3.5-turbo` for faster, more cost-effective processing, though potentially with less depth).

## Troubleshooting

*   **`ModuleNotFoundError: No module named 'openai'` (or other packages):**
    *   Ensure your virtual environment is activated.
    *   Make sure you have installed the dependencies: `pip install -r requirements.txt`

*   **`ValueError: Missing API Key: Please set the OPENAI_API_KEY environment variable.`:**
    *   Double-check that you have correctly set the `OPENAI_API_KEY` environment variable and that it's available in your current terminal session.
    *   Verify that the API key itself is correct and active.

*   **API Errors (e.g., `RateLimitError`, `APIError`):**
    *   The tool has a basic retry mechanism. However, if errors persist, you might be exceeding your OpenAI API rate limits or encountering temporary service issues. Check your OpenAI account status and usage limits.
    *   Ensure your OpenAI account has sufficient credits or a valid payment method.

## Contributing

We welcome contributions to the Study Guide Generator! If you'd like to contribute, please consider the following:

*   **Reporting Bugs:** If you find a bug, please open an issue in the project's issue tracker (if available). Include steps to reproduce the bug, expected behavior, and actual behavior.
*   **Suggesting Enhancements:** If you have ideas for new features or improvements, feel free to open an issue to discuss them.
*   **Pull Requests:**
    1.  Fork the repository (if applicable).
    2.  Create a new branch for your feature or bug fix (`git checkout -b feature/your-feature-name` or `bugfix/your-bug-fix`).
    3.  Make your changes and commit them with clear, descriptive messages.
    4.  Ensure your code adheres to the project's coding standards (e.g., run linters like `flake8` and formatters like `black`).
    5.  Write or update tests for your changes.
    6.  Push your branch and open a pull request.

Please note that this project is currently maintained by a small team, so response times may vary.

## License

MIT License (see `LICENSE.md`)