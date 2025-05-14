import argparse
import logging
import sys # For sys.exit

# Project-specific imports
from transcript_parser.parser import (
    read_transcript_file,
    clean_transcript_text,
    segment_text_by_word_count
)
from llm_chain.chain import (
    extract_key_concepts, 
    generate_qa_pairs,
    # Potentially get_openai_api_key here if we want to pre-check or initialize client early
)
from output_formatter.formatter import format_plain_text_output, ProcessedSegmentData

# Configure basic logging for the application
# This will catch logs from all modules if they use logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__) # Logger for main.py

def main():
    """
    Main function to parse arguments and orchestrate the study guide generation.
    """
    parser = argparse.ArgumentParser(description="Study-Guide Generator CLI")
    parser.add_argument(
        "transcript_file",
        type=str,
        help="Path to the plain text lecture transcript file."
    )
    parser.add_argument(
        "-o",
        "--output_file",
        type=str,
        help="Optional path to save the generated study guide. If not provided, prints to console.",
        default=None
    )
    parser.add_argument(
        "--words_per_segment",
        type=int,
        default=500, # Default from parser.py
        help="Approximate number of words for each text segment sent to the LLM."
    )
    # Placeholder for future arguments like --obsidian, --model, etc.

    args = parser.parse_args()

    logger.info(f"Starting study guide generation for: {args.transcript_file}")

    all_processed_segments: list[ProcessedSegmentData] = []

    try:
        # 1. Read and Parse Transcript
        logger.info("Step 1: Reading and parsing transcript...")
        raw_content = read_transcript_file(args.transcript_file)
        cleaned_content = clean_transcript_text(raw_content)
        text_segments = segment_text_by_word_count(cleaned_content, args.words_per_segment)
        logger.info(f"Transcript processed into {len(text_segments)} segments.")

        if not text_segments:
            logger.warning("No text segments found after parsing. Exiting.")
            print("No content to process after parsing the transcript.")
            return # Or sys.exit(1)

        # 2. Process each segment with LLM
        logger.info("Step 2: Processing segments with LLM...")
        for i, segment in enumerate(text_segments):
            logger.info(f"Processing segment {i + 1}/{len(text_segments)}...")
            segment_data: ProcessedSegmentData = {}
            
            # Extract Key Concepts
            # In a more robust version, we might want to handle LLM call failures per-item
            # For MVP, if one call fails, we log it and continue, segment_data will have None for that key
            key_concepts_output = extract_key_concepts(segment)
            if key_concepts_output:
                segment_data["key_concepts"] = key_concepts_output
            else:
                logger.warning(f"Failed to extract key concepts for segment {i + 1}.")
                segment_data["key_concepts"] = None # Explicitly None

            # Generate Q&A Pairs
            qa_pairs_output = generate_qa_pairs(segment)
            if qa_pairs_output:
                segment_data["qa_pairs"] = qa_pairs_output
            else:
                logger.warning(f"Failed to generate Q&A pairs for segment {i + 1}.")
                segment_data["qa_pairs"] = None # Explicitly None
            
            # Add other LLM calls here (definitions, examples, insights) as they are implemented
            all_processed_segments.append(segment_data)
        
        logger.info("LLM processing complete for all segments.")

        # 3. Format Output
        logger.info("Step 3: Formatting output...")
        formatted_study_guide = format_plain_text_output(all_processed_segments)

        # 4. Write to output_file or print to console
        logger.info("Step 4: Outputting study guide...")
        if args.output_file:
            try:
                with open(args.output_file, 'w', encoding='utf-8') as f:
                    f.write(formatted_study_guide)
                logger.info(f"Study guide successfully written to: {args.output_file}")
                print(f"Study guide saved to {args.output_file}")
            except IOError as e:
                logger.error(f"Error writing study guide to file {args.output_file}: {e}")
                print(f"Error: Could not write to output file {args.output_file}. Printing to console instead.")
                print("\n-- STUDY GUIDE CONTENT --\n")
                print(formatted_study_guide)
        else:
            logger.info("Printing study guide to console.")
            print("\n-- STUDY GUIDE CONTENT --\n")
            print(formatted_study_guide)
        
        logger.info("Study guide generation finished successfully.")

    except FileNotFoundError:
        logger.error(f"Input transcript file not found: {args.transcript_file}")
        print(f"Error: Transcript file not found at '{args.transcript_file}'. Please check the path.")
        sys.exit(1)
    except ValueError as ve:
        # This can be raised by get_openai_api_key if env var is missing
        logger.error(f"Configuration error: {ve}")
        print(f"Error: A configuration error occurred: {ve}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred during study guide generation: {e}", exc_info=True)
        print(f"An unexpected error occurred: {e}. Check logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 