# Project Status: Study-Guide Generator

**Version:** 0.1.0 (MVP - In Development)
**Date:** $(date +%Y-%m-%d)

## Overall Progress

- [ ] Phase 1: Core MVP (CLI, Plain Text Output)
  - [X] Step 1: Basic project structure setup
  - [X] Step 2: CLI argument parsing (`src/main.py`)
  - [X] Step 3: `transcript_parser` module (read, clean, segment)
  - [X] Step 4: `llm_chain` module (API key, basic LLM calls, retry, token logging, prompt templates)
  - [X] Step 5: `output_formatter` module (plain text formatting)
  - [X] Step 6: Integration of modules in `src/main.py`
  - [X] Step 7: Initial unit tests (parser, formatter, mocked LLM chain)
  - [X] Step 8: Basic CI pipeline setup (lint, format, type check, test)
  - [ ] Step 9: Placeholder `status.md` and basic `README.md` (README was pre-existing)
  - [ ] Step 10: Draft `docs/developer_guide.md`
- [ ] Phase 2: Enhancements & Obsidian Output (Future)
- [ ] Phase 3: Future Considerations (Future)

## Current Focus

- Completing initial documentation for MVP (status.md, developer_guide.md).

## Key Milestones & Dates

*   **MVP (Phase 1) Target:** TBD

## Completed Tasks (Details)

*   **Project Setup:** Initial directories and files created.
*   **CLI:** `argparse` implemented in `src/main.py` for input/output files.
*   **Transcript Parser:** Functions for reading, cleaning (filler words, whitespace), and segmenting (by word count) transcripts are in `src/transcript_parser/parser.py`.
*   **LLM Chain:** 
    *   Secure loading of `OPENAI_API_KEY` from environment.
    *   `call_llm` function with retry logic and basic token console logging.
    *   Prompt template loading mechanism and initial templates for concept extraction and Q&A.
    *   Placeholder functions `extract_key_concepts` and `generate_qa_pairs`.
*   **Output Formatter:** `format_plain_text_output` implemented in `src/output_formatter/formatter.py`.
*   **Integration:** Modules are integrated in `src/main.py` to perform the end-to-end flow.
*   **Unit Tests:** Initial tests for parser, formatter, and mocked LLM chain logic are in place.
*   **CI Pipeline:** GitHub Actions workflow configured for linting, formatting checks, type checking, and running tests with coverage.

## Next Steps (Immediate)

1.  Finalize placeholder content for `status.md`.
2.  Draft initial `docs/developer_guide.md`.
3.  Perform a manual end-to-end test run of the CLI tool.

## Blockers / Risks

-   `OPENAI_API_KEY` must be configured in the environment for the tool to run (though tests are mocked).
-   Quality of LLM output is dependent on prompt engineering (initial prompts are basic).

## Notes

*   This document should be updated regularly as tasks are completed. 