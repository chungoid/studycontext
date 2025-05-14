import logging
import re

logger = logging.getLogger(__name__)


def read_transcript_file(file_path: str) -> str:
    """
    Reads the content of the transcript file.

    Args:
        file_path: The path to the transcript file.

    Returns:
        The content of the file as a string.

    Raises:
        FileNotFoundError: If the file does not exist.
        IOError: If there is an error reading the file.
    """
    logger.info(f"Attempting to read transcript file: {file_path}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        logger.info(
            f"Successfully read file: {file_path}. Length: {len(content)} characters."
        )
        return content
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading file {file_path}: {e}")
        raise


def clean_transcript_text(text: str) -> str:
    """
    Cleans the transcript text by removing common filler words and normalizing whitespace.

    Args:
        text: The raw transcript text.

    Returns:
        The cleaned transcript text.
    """
    logger.info(f"Starting transcript cleaning. Original length: {len(text)}")

    filler_words = ["uh", "um", "like", "you know", "so"]
    cleaned_text = text

    # Initial normalization of all whitespace to single spaces
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    # Remove filler words
    for word_to_remove in filler_words:
        pattern = r"\b" + re.escape(word_to_remove) + r"\b"
        cleaned_text = re.sub(pattern, "", cleaned_text, flags=re.IGNORECASE)

    # Collapse multiple spaces that may have resulted from removal, and strip
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    # Handle ellipses: replace " . . . " or similar forms with a single "..."
    # This is to counteract the effect of previous rules that might space out dots.
    # And ensure "..." is treated as a single token for spacing later.
    cleaned_text = re.sub(r"\s*\.\s*\.\s*\.\s*", " ... ", cleaned_text)

    # Add a single space after major punctuation (. , ! ?) if not already there and not EOL
    # And ensure no space before them.
    # Step 1: Remove spaces before these punctuation marks.
    cleaned_text = re.sub(r"\s+([,.!?])", r"\1", cleaned_text)
    # Step 2: Ensure one space after, unless it's end of string or followed by another space.
    cleaned_text = re.sub(r"([,.!?])(?!$| \s|[,.!?])", r"\1 ", cleaned_text)

    # Collapse multiple commas (e.g., ", , ," or ", ,") into a single comma followed by a space
    cleaned_text = re.sub(r"(,\s*)+", ", ", cleaned_text)

    # Collapse multiple periods if they are not part of an ellipsis
    # e.g. "word. . another" -> "word. another"
    # This is a bit more complex; for now, we assume ellipsis handling is primary.

    # Normalize spaces again after punctuation adjustments
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    # Remove leading punctuation (comma) if followed by a space, or just the comma if no space
    if cleaned_text.startswith(", "):
        cleaned_text = cleaned_text[2:]
    elif cleaned_text.startswith(","):
        cleaned_text = cleaned_text[1:].strip()

    # If, after filler removal, string starts with "...", remove it.
    # This is based on "UM, So, LIKE... very loud fillers!" -> "very loud fillers!" test
    if cleaned_text.startswith("... "):
        cleaned_text = cleaned_text[4:]
    elif cleaned_text.startswith("..."):  # If no space after leading "..."
        cleaned_text = cleaned_text[3:].strip()

    # Remove trailing comma
    if cleaned_text.endswith(","):
        cleaned_text = cleaned_text[:-1].strip()

    # Remove trailing ellipsis if it is left hanging (e.g. "text ...")
    if cleaned_text.endswith(" ..."):
        cleaned_text = cleaned_text[:-4].strip()  # Remove " ..."
    elif cleaned_text.endswith("..."):
        cleaned_text = cleaned_text[:-3].strip()

    # Final whitespace cleanup
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()

    logger.info(f"Cleaning complete. Cleaned length: {len(cleaned_text)}")
    return cleaned_text


def segment_text_by_word_count(text: str, words_per_segment: int = 500) -> list[str]:
    """
    Segments the text into chunks, each containing approximately words_per_segment words.

    Args:
        text: The text to segment.
        words_per_segment: The approximate number of words for each segment.

    Returns:
        A list of text segments.
    """
    logger.info(
        f"Starting text segmentation. Total words: {len(text.split())}, Words per segment: {words_per_segment}"
    )
    if not text:
        logger.warning("Input text for segmentation is empty. Returning empty list.")
        return []

    words = text.split()
    segments = []
    current_segment_words = []

    for word in words:
        current_segment_words.append(word)
        if len(current_segment_words) >= words_per_segment:
            segments.append(" ".join(current_segment_words))
            current_segment_words = []

    # Add any remaining words as the last segment
    if current_segment_words:
        segments.append(" ".join(current_segment_words))

    logger.info(f"Segmentation complete. Number of segments: {len(segments)}")
    return segments
