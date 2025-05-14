from src.output_formatter.formatter import (
    format_plain_text_output,
    ProcessedSegmentData,
)
from typing import List

# Sample data for testing
SAMPLE_SEGMENT_1: ProcessedSegmentData = {
    "key_concepts": "Concept: Alpha\nDefinition: First letter.",
    "qa_pairs": "Q: What is Alpha?\nA: The first letter.",
}

SAMPLE_SEGMENT_2_NO_QA: ProcessedSegmentData = {
    "key_concepts": "Concept: Beta\nDefinition: Second letter.",
    "qa_pairs": None,
}

SAMPLE_SEGMENT_3_NO_CONCEPTS: ProcessedSegmentData = {
    "key_concepts": None,
    "qa_pairs": "Q: What is Gamma?\nA: The third letter.",
}

SAMPLE_SEGMENT_4_EMPTY_STRINGS: ProcessedSegmentData = {
    "key_concepts": "",  # Empty string, not None
    "qa_pairs": "Q: What is Delta?\nA: The fourth letter.",
}

SAMPLE_SEGMENT_5_ALL_NONE: ProcessedSegmentData = {
    "key_concepts": None,
    "qa_pairs": None,
}


def test_format_plain_text_empty_input():
    """Test formatting with no segments provided."""
    assert format_plain_text_output([]) == ""


def test_format_plain_text_single_segment_full_data():
    """Test formatting a single segment with all data present."""
    data: List[ProcessedSegmentData] = [SAMPLE_SEGMENT_1]
    output = format_plain_text_output(data)
    assert "STUDY GUIDE" in output
    assert "--- SEGMENT 1 ---" in output
    assert "Key Concepts & Definitions:" in output
    assert "Concept: Alpha" in output
    assert "Definition: First letter." in output
    assert "Practice Questions & Answers:" in output
    assert "Q: What is Alpha?" in output
    assert "A: The first letter." in output


def test_format_plain_text_multiple_segments_mixed_data():
    """Test formatting multiple segments with some missing data."""
    data: List[ProcessedSegmentData] = [
        SAMPLE_SEGMENT_1,
        SAMPLE_SEGMENT_2_NO_QA,
        SAMPLE_SEGMENT_3_NO_CONCEPTS,
        SAMPLE_SEGMENT_5_ALL_NONE,
    ]
    output = format_plain_text_output(data)

    # Check Segment 1 (full data)
    assert "--- SEGMENT 1 ---" in output
    assert "Concept: Alpha" in output
    assert "Q: What is Alpha?" in output

    # Check Segment 2 (no Q&A)
    assert "--- SEGMENT 2 ---" in output
    assert "Concept: Beta" in output
    assert "Practice Questions & Answers: Not generated for this segment." in output

    # Check Segment 3 (no Key Concepts)
    assert "--- SEGMENT 3 ---" in output
    assert "Key Concepts & Definitions: Not generated for this segment." in output
    assert "Q: What is Gamma?" in output

    # Check Segment 4 (all None)
    assert (
        "--- SEGMENT 4 ---" in output
    )  # Segment 5 in sample data list, but 4th in processing order
    assert "Key Concepts & Definitions: Not generated for this segment." in output
    assert "Practice Questions & Answers: Not generated for this segment." in output


def test_format_plain_text_segment_with_empty_string_data():
    """Test formatting a segment where data is an empty string instead of None."""
    data: List[ProcessedSegmentData] = [SAMPLE_SEGMENT_4_EMPTY_STRINGS]
    output = format_plain_text_output(data)
    assert "--- SEGMENT 1 ---" in output
    # The current formatter will print the section title and then an empty line from .strip()
    # This behavior is acceptable for MVP.
    assert (
        "Key Concepts & Definitions:\n------------------------------\n\n" in output
    )  # .strip() on empty string is empty
    assert "Q: What is Delta?" in output


def test_format_plain_text_output_structure():
    """Check overall structure, titles, and separators."""
    data: List[ProcessedSegmentData] = [SAMPLE_SEGMENT_1, SAMPLE_SEGMENT_2_NO_QA]
    output = format_plain_text_output(data)
    lines = output.split("\n")

    assert lines[0] == "STUDY GUIDE"
    assert lines[1] == "=" * 40
    # Expect blank line at lines[2]
    assert lines[3] == "--- SEGMENT 1 ---"
    # ... further structural checks can be added if very specific formatting is critical

    # Verify that content for each segment is grouped correctly
    segment1_text = output.split("--- SEGMENT 2 ---")[0]
    segment2_text = output.split("--- SEGMENT 2 ---")[1]

    assert "Concept: Alpha" in segment1_text
    assert (
        "Concept: Beta" not in segment1_text
    )  # Ensure data doesn't leak between segments

    assert "Concept: Beta" in segment2_text
    assert "Concept: Alpha" not in segment2_text
