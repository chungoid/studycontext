import pytest
from unittest.mock import MagicMock, patch
import os
from src.llm_chain import chain  # Use this to allow monkeypatching chain._openai_client
from openai import APIError, RateLimitError
import time  # Import the time module
import httpx


# Fixture to set and unset the API key for tests
@pytest.fixture(autouse=True)
def manage_api_key_env(monkeypatch):
    """Set a dummy API key for testing and ensure _openai_client is reset."""
    monkeypatch.setenv("OPENAI_API_KEY", "test_api_key_value")
    # Reset the global client in the chain module before each test
    # to ensure it re-initializes with monkeypatched env/mocks
    chain._openai_client = None
    yield
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    chain._openai_client = None  # Clean up after test


@pytest.fixture
def mock_openai_client(monkeypatch):
    """Fixture to mock the OpenAI client and its chat completions create method."""
    mock_client = MagicMock()
    # The path to patch is where chain._initialize_openai_client looks for OpenAI class
    # This can be tricky. If _initialize_openai_client is `from openai import OpenAI`,
    # then you patch 'src.llm_chain.chain.OpenAI'
    monkeypatch.setattr("src.llm_chain.chain.OpenAI", lambda api_key: mock_client)
    # If _openai_client was already initialized by a previous test without this specific mock,
    # we need to ensure our mock_client is used. Resetting it in manage_api_key_env helps.
    # Forcing re-initialization to use the patched OpenAI class:
    chain._openai_client = None  # Ensure re-initialization with the MagicMock
    # We will call _initialize_openai_client directly or indirectly in tests to set chain._openai_client
    return mock_client


# Mock response structures
def create_mock_chat_completion_response(
    content: str, prompt_tokens=10, completion_tokens=20
):
    mock_choice = MagicMock()
    mock_choice.message.content = content

    mock_usage = MagicMock()
    mock_usage.prompt_tokens = prompt_tokens
    mock_usage.completion_tokens = completion_tokens
    mock_usage.total_tokens = prompt_tokens + completion_tokens

    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage = mock_usage
    return mock_response


# --- Tests for get_openai_api_key --- (This is implicitly tested by client init)


def test_get_openai_api_key_success(
    manage_api_key_env,
):  # manage_api_key_env ensures key is set
    assert chain.get_openai_api_key() == "test_api_key_value"


def test_get_openai_api_key_not_set(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    with pytest.raises(ValueError, match="Missing API Key"):  # Make match more specific
        chain.get_openai_api_key()


# --- Tests for _load_prompt_template ---
PROMPT_TEST_DIR = os.path.join(
    os.path.dirname(__file__), "test_prompts_for_chain_tests"
)


@pytest.fixture(scope="module", autouse=True)
def create_test_prompt_files():
    """Create dummy prompt files for testing _load_prompt_template."""
    if not os.path.exists(PROMPT_TEST_DIR):
        os.makedirs(PROMPT_TEST_DIR)

    with open(os.path.join(PROMPT_TEST_DIR, "test_prompt.txt"), "w") as f:
        f.write("This is a {{ variable }} prompt.")

    yield  # Teardown (optional, could remove files but usually not necessary for simple tests)
    # import shutil
    # shutil.rmtree(PROMPT_TEST_DIR) # If cleanup is desired


def test_load_prompt_template_success(monkeypatch, create_test_prompt_files):
    # Patch chain.PROMPT_DIR to point to our test prompts directory
    monkeypatch.setattr(chain, "PROMPT_DIR", PROMPT_TEST_DIR)
    template_content = chain._load_prompt_template("test_prompt.txt")
    assert template_content == "This is a {{ variable }} prompt."


def test_load_prompt_template_not_found(monkeypatch):
    monkeypatch.setattr(chain, "PROMPT_DIR", PROMPT_TEST_DIR)  # Point to a known dir
    with pytest.raises(FileNotFoundError):
        chain._load_prompt_template("non_existent_prompt.txt")


# --- Tests for call_llm ---


def test_call_llm_success(mock_openai_client):
    """Test call_llm successful response on first try."""
    mock_response_content = "LLM says hello!"
    mock_openai_client.chat.completions.create.return_value = (
        create_mock_chat_completion_response(mock_response_content)
    )

    result = chain.call_llm("A simple prompt")

    assert result == mock_response_content
    mock_openai_client.chat.completions.create.assert_called_once()
    # Further assertions can be made on the call arguments to create
    call_args = mock_openai_client.chat.completions.create.call_args
    assert call_args[1]["model"] == "gpt-4o"  # Updated to gpt-4o
    assert call_args[1]["messages"][0]["content"] == "A simple prompt"


def test_call_llm_retry_on_ratelimiterror_then_success(mock_openai_client, monkeypatch):
    """Test retry logic on RateLimitError, then success."""
    mock_response_content = "Success after retry!"
    # Simulate failure then success
    mock_openai_client.chat.completions.create.side_effect = [
        RateLimitError(
            "Simulated Rate Limit",
            response=MagicMock(
                spec=httpx.Response,
                status_code=429,
                headers=MagicMock(spec=httpx.Headers)
            ),
            body=None
        ),
        create_mock_chat_completion_response(mock_response_content),
    ]

    # Patch time.sleep to avoid actual waiting during test
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    result = chain.call_llm("Prompt needing retry", max_retries=1)

    assert result == mock_response_content
    assert mock_openai_client.chat.completions.create.call_count == 2


def test_call_llm_failure_after_max_retries(mock_openai_client, monkeypatch):
    """Test call_llm returns None after exhausting retries."""
    # Simulate persistent failure
    mock_openai_client.chat.completions.create.side_effect = APIError(
        "Persistent API Error", request=MagicMock(spec=httpx.Request), body=None
    )
    monkeypatch.setattr(time, "sleep", lambda seconds: None)

    result = chain.call_llm("Another prompt", max_retries=2)

    assert result is None
    assert (
        mock_openai_client.chat.completions.create.call_count == 3
    )  # 1 initial + 2 retries


def test_call_llm_unexpected_error(mock_openai_client):
    """Test call_llm handles non-APIError exceptions gracefully."""
    mock_openai_client.chat.completions.create.side_effect = Exception(
        "Totally unexpected!"
    )

    result = chain.call_llm("Prompt leading to chaos")

    assert result is None
    mock_openai_client.chat.completions.create.assert_called_once()


# --- Tests for extract_key_concepts and generate_qa_pairs (mocking call_llm indirectly) ---
# These tests will verify that the correct prompt templates are loaded and call_llm is invoked.


@patch("src.llm_chain.chain.call_llm")  # Patch call_llm where it's defined
def test_extract_key_concepts_uses_correct_prompt(
    mock_call_llm, monkeypatch, create_test_prompt_files
):
    monkeypatch.setattr(chain, "PROMPT_DIR", PROMPT_TEST_DIR)
    # Keep the original _load_prompt_template to ensure the formatting logic in extract_key_concepts is tested
    original_load_prompt_template = chain._load_prompt_template

    def mock_load_template(template_name):
        if template_name == "extract_concepts_prompt.txt":
            # Return a simple template string for testing formatting
            return "Key concept prompt: {text_segment}"
        return original_load_prompt_template(
            template_name
        )  # Fallback for other prompts if any

    monkeypatch.setattr(chain, "_load_prompt_template", mock_load_template)

    expected_response = "Mocked key concepts"
    mock_call_llm.return_value = expected_response

    segment = "This is a test segment for concepts."
    result = chain.extract_key_concepts(segment)

    assert result == expected_response
    mock_call_llm.assert_called_once()
    called_prompt = mock_call_llm.call_args[0][0]
    # Now assert that the prompt passed to call_llm is the formatted one
    assert called_prompt == "Key concept prompt: This is a test segment for concepts."


@patch("src.llm_chain.chain.call_llm")
def test_generate_qa_pairs_uses_correct_prompt(
    mock_call_llm, monkeypatch, create_test_prompt_files
):
    monkeypatch.setattr(chain, "PROMPT_DIR", PROMPT_TEST_DIR)
    original_load_prompt_template = chain._load_prompt_template

    def mock_load_template(template_name):
        if template_name == "generate_qa_prompt.txt":
            return "Q&A prompt: {text_segment}"
        return original_load_prompt_template(template_name)

    monkeypatch.setattr(chain, "_load_prompt_template", mock_load_template)

    expected_response = "Mocked Q&A pairs"
    mock_call_llm.return_value = expected_response

    segment = "This is a test segment for Q&A."
    result = chain.generate_qa_pairs(segment)

    assert result == expected_response
    mock_call_llm.assert_called_once()
    called_prompt = mock_call_llm.call_args[0][0]
    assert called_prompt == "Q&A prompt: This is a test segment for Q&A."


def test_extract_key_concepts_handles_call_llm_failure(
    monkeypatch, create_test_prompt_files
):
    monkeypatch.setattr(chain, "PROMPT_DIR", PROMPT_TEST_DIR)
    monkeypatch.setattr(
        chain, "_load_prompt_template", lambda name: "Prompt: {{text_segment}}"
    )
    # Mock call_llm to return None, simulating a failure
    monkeypatch.setattr(chain, "call_llm", lambda prompt, **kwargs: None)

    result = chain.extract_key_concepts("some segment")
    assert result is None


# It's good practice to also test that _initialize_openai_client is called only once
# for multiple call_llm invocations within a test if not reset, but our autouse fixture
# resets _openai_client for each test, so direct testing of that aspect here is tricky
# without more complex fixture scoping or modifying the autouse behavior.
# The current setup ensures a fresh client state per test.
