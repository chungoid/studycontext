import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

# For the MVP, we assume llm_processed_data for each segment is a dictionary
# containing raw string outputs from the LLM for different categories.
# e.g., {"key_concepts": "Concept1...", "qa_pairs": "Q: What is...?\nA: ..."}
# Later, this structure might become more refined (e.g., lists of objects).

ProcessedSegmentData = Dict[str, Optional[str]]


def format_plain_text_output(all_segments_data: List[ProcessedSegmentData]) -> str:
    """
    Formats the processed data from all segments into a single plain text string.

    Args:
        all_segments_data: A list where each item is a dictionary containing
                           the LLM-generated content for a segment (e.g.,
                           key concepts string, Q&A string).

    Returns:
        A single string representing the formatted plain text study guide.
    """
    logger.info(
        f"Starting plain text formatting for {len(all_segments_data)} segments."
    )
    output_lines = []

    if not all_segments_data:
        logger.warning(
            "No processed data provided for formatting. Returning empty string."
        )
        return ""

    output_lines.append("STUDY GUIDE")
    output_lines.append("=" * 40)
    output_lines.append("")

    for i, segment_data in enumerate(all_segments_data):
        output_lines.append(f"--- SEGMENT {i + 1} ---")
        output_lines.append("")

        key_concepts = segment_data.get("key_concepts")
        if key_concepts is not None:
            output_lines.append("Key Concepts & Definitions:")
            output_lines.append("-" * 30)
            output_lines.append(key_concepts.strip())
            output_lines.append("")
        else:
            output_lines.append(
                "Key Concepts & Definitions: Not generated for this segment."
            )
            output_lines.append("")

        qa_pairs = segment_data.get("qa_pairs")
        if qa_pairs is not None:
            output_lines.append("Practice Questions & Answers:")
            output_lines.append("-" * 30)
            output_lines.append(qa_pairs.strip())
            output_lines.append("")
        else:
            output_lines.append(
                "Practice Questions & Answers: Not generated for this segment."
            )
            output_lines.append("")

        # Placeholder for other content types (Examples, Insights) as they are added
        # instructor_insights = segment_data.get("instructor_insights")
        # if instructor_insights is not None:
        #     output_lines.append("Instructor Insights:")
        #     output_lines.append("-" * 30)
        #     output_lines.append(instructor_insights.strip())
        #     output_lines.append("")

        output_lines.append("=" * 40)
        output_lines.append("")

    formatted_text = "\n".join(output_lines)
    logger.info(
        f"Plain text formatting complete. Total length: {len(formatted_text)} characters."
    )
    return formatted_text


# Example Usage (for testing this module independently):
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     sample_data_segment_1 = {
#         "key_concepts": "Concept: Big O Notation\nDefinition: Describes algorithm efficiency.",
#         "qa_pairs": "Q: What is Big O?\nA: A way to measure an algorithm\'s complexity."
#     }
#     sample_data_segment_2 = {
#         "key_concepts": "Concept: Recursion\nDefinition: A function calling itself.",
#         "qa_pairs": None # Simulate missing Q&A for a segment
#     }
#     sample_data_segment_3 = {
#         "key_concepts": None,
#         "qa_pairs": "Q: What is python?\nA: A snake."
#     }

#     all_data = [sample_data_segment_1, sample_data_segment_2, sample_data_segment_3]
#     formatted_guide = format_plain_text_output(all_data)
#     print(formatted_guide)
