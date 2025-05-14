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

    # Define common filler words (case-insensitive removal)
    # As per PRD (Feature 4.1, AC3): "uh", "um", "like", "you know", "so"
    filler_words = ["uh", "um", "like", "you know", "so"]

    cleaned_text = text
    for word_to_remove in filler_words:
        # Build a regex pattern that matches the word, case-insensitively,
        # and handles various spacing/punctuation scenarios around it.
        # This is complex. A simpler start is to ensure spaces are handled.
        
        # Pattern 1: Space + Word + Space -> replace with single space
        pattern1 = r"\s+" + re.escape(word_to_remove) + r"\s+"
        cleaned_text = re.sub(pattern1, " ", cleaned_text, flags=re.IGNORECASE)
        
        # Pattern 2: Start of string + Word + Space -> replace with empty string (handled by strip later or more specific regex)
        pattern2_start = r"^" + re.escape(word_to_remove) + r"\s+"
        cleaned_text = re.sub(pattern2_start, "", cleaned_text, flags=re.IGNORECASE)

        # Pattern 3: Space + Word + End of string -> replace with empty string (handled by strip later or more specific regex)
        pattern3_end = r"\s+" + re.escape(word_to_remove) + r"$"
        cleaned_text = re.sub(pattern3_end, "", cleaned_text, flags=re.IGNORECASE)
        
        # Pattern 4: Start of string + Word + End of string (word is the whole text)
        pattern4_whole = r"^" + re.escape(word_to_remove) + r"$"
        cleaned_text = re.sub(pattern4_whole, "", cleaned_text, flags=re.IGNORECASE)

    # Normalize multiple whitespaces (including newlines, tabs) to a single space
    cleaned_text = re.sub(r"\s+", " ", cleaned_text).strip()
    
    # Attempt to clean up orphaned commas or commas with spaces before them due to filler word removal.
    # This is a heuristic and might need refinement.
    # Example: "word , other" -> "word, other"
    cleaned_text = re.sub(r"\s+,\s*", ", ", cleaned_text) 
    # Example: "word,  other" -> "word, other" (already handled by \s+ normalize but good to be sure)
    # Example: if a sentence starts with ", " after cleaning, strip it.
    if cleaned_text.startswith(", "):
        cleaned_text = cleaned_text[2:]
    # Remove trailing commas if they are left hanging
    cleaned_text = cleaned_text.strip().removesuffix(",")
    cleaned_text = cleaned_text.strip() # Final strip

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
