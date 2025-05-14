import os
import logging
from openai import OpenAI, APIError, RateLimitError
import time
import random
from typing import TypeAlias

logger = logging.getLogger(__name__)

API_KEY_ENV_VAR = "OPENAI_API_KEY"
PROMPT_DIR = os.path.join(os.path.dirname(__file__), "prompts")

def get_openai_api_key() -> str:
    """
    Retrieves the OpenAI API key from environment variables.

    Returns:
        The OpenAI API key.

    Raises:
        ValueError: If the OPENAI_API_KEY environment variable is not set.
    """
    api_key = os.environ.get(API_KEY_ENV_VAR)
    if not api_key:
        logger.error(f"The environment variable {API_KEY_ENV_VAR} is not set.")
        raise ValueError(f"Missing API Key: Please set the {API_KEY_ENV_VAR} environment variable.")
    logger.info(f"Successfully retrieved {API_KEY_ENV_VAR}.")
    return api_key

# Global OpenAI client instance, initialized when first needed or explicitly.
# This helps avoid re-initializing the client for every call.
_openai_client = None

def _initialize_openai_client() -> OpenAI:
    """Initializes and returns the OpenAI client, creating it if it doesn't exist."""
    global _openai_client
    if _openai_client is None:
        api_key = get_openai_api_key()
        _openai_client = OpenAI(api_key=api_key)
        logger.info("OpenAI client initialized.")
    return _openai_client

def _load_prompt_template(template_name: str) -> str:
    """Loads a prompt template from the prompts directory."""
    file_path = os.path.join(PROMPT_DIR, template_name)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            template = f.read()
        logger.info(f"Successfully loaded prompt template: {template_name}")
        return template
    except FileNotFoundError:
        logger.error(f"Prompt template file not found: {file_path}")
        # Depending on how critical, could raise or return a default/error string
        raise
    except IOError as e:
        logger.error(f"Error reading prompt template file {file_path}: {e}")
        raise

# Changed LlmResponse from a function to a TypeAlias
LlmResponse: TypeAlias = str

def call_llm(
    prompt: str,
    model: str = "gpt-4o", # Default to a cost-effective model for now
    max_tokens: int = 1500,      # Sensible default for study guide content
    temperature: float = 0.7,    # Balance creativity and determinism
    max_retries: int = 3,
    base_delay_seconds: float = 1.0 
) -> LlmResponse | None:
    """
    Calls the OpenAI API (ChatCompletion) with a given prompt and handles basic retry logic.

    Args:
        prompt: The prompt to send to the LLM.
        model: The OpenAI model to use (e.g., "gpt-3.5-turbo", "gpt-4o").
        max_tokens: The maximum number of tokens to generate in the completion.
        temperature: Sampling temperature to use.
        max_retries: Maximum number of retry attempts for API errors.
        base_delay_seconds: Initial delay for exponential backoff.

    Returns:
        The LLM's response content as a string, or None if the call fails after retries.
    """
    client = _initialize_openai_client()
    attempt = 0

    while attempt <= max_retries:
        try:
            logger.info(f"Attempt {attempt + 1}/{max_retries + 1} to call LLM (model: {model}). Prompt length: {len(prompt)} chars.")
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                # top_p=1, # Default
                # frequency_penalty=0, # Default
                # presence_penalty=0 # Default
            )
            
            content = response.choices[0].message.content
            
            # Basic token usage logging (as per plan step 4d - console for now)
            # More detailed logging (to DB or structured logs) would be for a later phase.
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            logger.info(
                f"LLM call successful. Model: {model}, Prompt Tokens: {prompt_tokens}, "
                f"Completion Tokens: {completion_tokens}, Total Tokens: {total_tokens}"
            )

            if content is None:
                logger.warning("LLM response content is None.")
                # This case might indicate an issue with the response structure or an empty completion.
                # Depending on strictness, could retry or return None immediately.
                # For now, we let it return None if that's what the API gives after a successful call.

            return content

        except (APIError, RateLimitError) as e:
            logger.warning(f"LLM API error on attempt {attempt + 1}: {e}")
            if attempt < max_retries:
                delay = (base_delay_seconds ** attempt) + random.uniform(0, 0.1 * (base_delay_seconds ** attempt))
                logger.info(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
                attempt += 1
            else:
                logger.error(f"LLM call failed after {max_retries + 1} attempts due to API/RateLimit error: {e}")
                return None
        except Exception as e:
            # Catch any other unexpected errors during the API call
            logger.error(f"An unexpected error occurred during LLM call: {e}", exc_info=True)
            return None # Do not retry on unexpected errors by default
    
    return None # Should be unreachable if loop logic is correct, but as a safeguard


# --- Placeholder for specific extraction/generation functions using call_llm ---
# These will be developed in sub-step 4b and will use call_llm with specific prompts.

def extract_key_concepts(text_segment: str) -> LlmResponse | None:
    # 1. Load/format a specific prompt template for key concept extraction from prompts/
    # 2. Call call_llm with this prompt and the text_segment
    # 3. Potentially do some basic parsing/validation of the response if needed
    try:
        prompt_template = _load_prompt_template("extract_concepts_prompt.txt")
        prompt = prompt_template.format(text_segment=text_segment)
        logger.info("Calling LLM to extract key concepts.")
        return call_llm(prompt)
    except Exception as e:
        logger.error(f"Error in extract_key_concepts: {e}", exc_info=True)
        return None

def generate_qa_pairs(text_segment: str) -> LlmResponse | None:
    # Similar to extract_key_concepts, but with a Q&A generation prompt
    try:
        prompt_template = _load_prompt_template("generate_qa_prompt.txt")
        prompt = prompt_template.format(text_segment=text_segment)
        logger.info("Calling LLM to generate Q&A pairs.")
        return call_llm(prompt)
    except Exception as e:
        logger.error(f"Error in generate_qa_pairs: {e}", exc_info=True)
        return None

# (Other functions for definitions, examples, insights will follow a similar pattern)


# Example of how it might be used (will be part of a class or other functions later)
# class LLMChain:
#     def __init__(self):
#         self.api_key = get_openai_api_key()
        # Initialize OpenAI client here with self.api_key 