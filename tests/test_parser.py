import pytest
import os
from tempfile import NamedTemporaryFile
from src.transcript_parser.parser import (
    read_transcript_file,
    clean_transcript_text,
    segment_text_by_word_count,
)

# Tests for read_transcript_file


def test_read_transcript_file_success():
    """Test reading a file successfully."""
    content = "This is a test transcript.\nSecond line."
    with NamedTemporaryFile(mode="w+", delete=False, encoding="utf-8") as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    assert read_transcript_file(tmp_file_path) == content
    os.remove(tmp_file_path)


def test_read_transcript_file_not_found():
    """Test reading a non-existent file."""
    with pytest.raises(FileNotFoundError):
        read_transcript_file("non_existent_file.txt")


# Potentially add a test for IOError, though it's harder to reliably trigger.

# Tests for clean_transcript_text


@pytest.mark.parametrize(
    "input_text, expected_output",
    [
        (
            "Uh, this is, um, like, a test, you know, so... with extra  spaces.",
            "this is a test with extra spaces.",
        ),
        ("no filler words here", "no filler words here"),
        ("  leading and trailing spaces  ", "leading and trailing spaces"),
        ("UM, So, LIKE... very loud fillers!", "very loud fillers!"),
        ("word um word", "word word"),  # Filler in middle
        ("", ""),  # Empty string
        ("multiple   spaces   between   words", "multiple spaces between words"),
        ("newlines\nand\ttabs", "newlines and tabs"),
    ],
)
def test_clean_transcript_text(input_text, expected_output):
    assert clean_transcript_text(input_text) == expected_output


# Tests for segment_text_by_word_count


@pytest.mark.parametrize(
    "input_text, words_per_segment, expected_segments_count, expected_first_segment_approx_words",
    [
        ("one two three four five six seven eight nine ten", 3, 4, 3),  # 3,3,3,1
        (" ".join(["word"] * 10), 3, 4, 3),  # 10 words, 3 per segment
        ("one two three four five", 5, 1, 5),
        ("one two three four five six", 5, 2, 5),  # 5, 1
        ("", 100, 0, 0),  # Empty string
        ("one two", 5, 1, 2),  # Less than words_per_segment
    ],
)
def test_segment_text_by_word_count(
    input_text,
    words_per_segment,
    expected_segments_count,
    expected_first_segment_approx_words,
):
    segments = segment_text_by_word_count(input_text, words_per_segment)
    assert len(segments) == expected_segments_count
    if expected_segments_count > 0 and segments:
        # Check if the first segment has roughly the expected number of words
        # This is an approximation because split() behavior can vary with multiple spaces
        assert len(segments[0].split()) <= words_per_segment
        # A more precise check might be needed if exact word count is critical,
        # but the function joins with single spaces, so this should be fairly close.
        if input_text:  # only check word count if input text is not empty
            assert len(segments[0].split()) == expected_first_segment_approx_words


def test_segment_text_exact_multiple():
    text = " ".join(["word"] * 10)
    segments = segment_text_by_word_count(text, 5)
    assert len(segments) == 2
    assert segments[0] == "word word word word word"
    assert segments[1] == "word word word word word"


def test_segment_text_non_exact_multiple():
    text = " ".join(["word"] * 7)
    segments = segment_text_by_word_count(text, 3)
    assert len(segments) == 3
    assert segments[0] == "word word word"
    assert segments[1] == "word word word"
    assert segments[2] == "word"
