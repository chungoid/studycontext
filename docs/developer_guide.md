# Study-Guide Generator - Developer Guide

**Version:** 0.1.0

## 1. Introduction

This guide provides instructions for developers working on the Study-Guide Generator project. It covers setup, dependencies, running the tool, and executing tests.

## 2. Project Structure

```
studycontext/
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   └── developer_guide.md
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── llm_chain/
│   │   ├── __init__.py
│   │   ├── chain.py
│   │   └── prompts/
│   │       ├── __init__.py
│   │       ├── extract_concepts_prompt.txt
│   │       └── generate_qa_prompt.txt
│   ├── output_formatter/
│   │   ├── __init__.py
│   │   └── formatter.py
│   └── transcript_parser/
│       ├── __init__.py
│       └── parser.py
├── tests/
│   ├── __init__.py
│   ├── test_chain.py
│   ├── test_formatter.py
│   ├── test_parser.py
│   └── test_prompts_for_chain_tests/ # Created by test_chain.py module fixture
│       └── test_prompt.txt
├── .gitignore
├── README.md
├── requirements.txt
└── status.md
```

-   `.github/workflows/`: Contains GitHub Actions CI configuration.
-   `docs/`: Project documentation.
-   `src/`: Source code for the application.
    -   `main.py`: CLI entry point and orchestration logic.
    -   `transcript_parser/`: Module for reading, cleaning, and segmenting transcripts.
    -   `llm_chain/`: Module for interacting with the LLM (OpenAI API).
        -   `prompts/`: Directory for storing LLM prompt templates.
    -   `output_formatter/`: Module for formatting the generated study guide.
-   `tests/`: Unit tests for the project. Contains a sub-directory `test_prompts_for_chain_tests` created by a `pytest` fixture in `test_chain.py` for its own prompt loading tests.
-   `requirements.txt`: Lists project dependencies.
-   `status.md`: Tracks project progress.

## 3. Setup and Dependencies

### 3.1. Prerequisites

-   Python 3.10 or higher.
-   `pip` (Python package installer).
-   Git (for version control).

### 3.2. Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone <repository_url>
    cd studycontext
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv # Or `python -m venv .venv` depending on your python alias
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `openai`, `pytest`, `black`, `flake8`, and `mypy`.

### 3.3. Environment Variables

To interact with the OpenAI API, you need to set the `OPENAI_API_KEY` environment variable.

```bash
export OPENAI_API_KEY="your_actual_openai_api_key"
```

**Note:** For running tests, a dummy API key is used by the CI script (`ci.yml`). For local testing where the client might be initialized (even if API calls are mocked), ensure this variable is set. The unit tests in `tests/test_chain.py` are designed to mock out actual API calls but still require the key to be set for the client initialization logic within the module to pass or be correctly patched by `monkeypatch`.

## 4. Running the Tool (CLI)

The main entry point for the CLI tool is `src/main.py`.

**Synopsis:**

```bash
python src/main.py <transcript_file_path> [options]
```

**Arguments:**

-   `transcript_file_path`: (Required) Path to the plain text lecture transcript file.
-   `-o <output_file_path>`, `--output_file <output_file_path>`: (Optional) Path to save the generated study guide. If not provided, the output will be printed to the console.
-   `-w <words_per_segment>`, `--words_per_segment <words_per_segment>`: (Optional) Approximate number of words for each text segment sent to the LLM. Defaults to 750.

**Example:**

```bash
# To process a transcript and print to console
python src/main.py path/to/your/transcript.txt

# To process a transcript and save to a file
python src/main.py path/to/your/transcript.txt -o path/to/your/study_guide.txt

# To specify segment length
python src/main.py path/to/your/transcript.txt --words_per_segment 300
```

## 5. Running Linters and Formatters

### 5.1. Black (Formatter)

To check formatting (without making changes):
```bash
black --check --diff .
```

To apply formatting:
```bash
black .
```

### 5.2. Flake8 (Linter)

```bash
flake8 .
```

### 5.3. MyPy (Type Checker)

```bash
mypy src/
```
(The CI pipeline uses `mypy src/ --ignore-missing-imports` for broader compatibility initially)

## 6. Running Tests

Tests are written using `pytest`.

1.  **Ensure `OPENAI_API_KEY` is set in your environment**, even if it's a dummy value like "test_key". The test suite for `llm_chain` expects this for client initialization code paths, although actual API calls are mocked.

2.  **Navigate to the project root directory.**

3.  **Run all tests:**
    ```bash
    pytest
    ```

4.  **Run tests with coverage:**
    ```bash
    pytest --cov=src
    ```
    This will output a coverage report to the console. HTML and XML reports are also generated by the CI pipeline (in `htmlcov/` and `coverage.xml` respectively if you run with the same flags: `pytest tests/ --cov=src --cov-report=xml --cov-report=html`).

## 7. CI Pipeline

The project uses GitHub Actions for Continuous Integration. The workflow is defined in `.github/workflows/ci.yml`. It automatically runs linters, formatters, type checks, and tests on pushes and pull requests to the `main` branch.

 