# api_gemini.py

import json
import logging
import os
import csv
from openai import OpenAI

# Setup basic logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure the OpenAI API client using OPENAI_API_KEY
try:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Environment variable OPENAI_API_KEY is not set")
    logging.debug("Initializing OpenAI client with provided API key.")
    client = OpenAI(api_key=api_key)
except Exception as e:
    logging.error(f"Failed to initialize OpenAI client: {e}")
    client = None

def load_dark_pattern_examples():
    """
    Load examples of dark patterns from the cleaned dataset.
    
    Returns:
    - list: List of dark pattern examples
    """
    examples = []
    dataset_candidates = [
        os.path.join(os.path.dirname(__file__), 'cleaned_dataset.csv'),
        os.path.join(os.path.dirname(__file__), 'dark_dataset.csv'),
    ]

    for dataset_path in dataset_candidates:
        try:
            if not os.path.exists(dataset_path):
                continue
            with open(dataset_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    label_value = row.get('label') or row.get('is_dark_pattern') or row.get('is_dark')
                    text_value = row.get('text') or row.get('content') or row.get('example')
                    if label_value in ('1', 'true', 'True', 'yes', 'Yes') and text_value:
                        examples.append(text_value)
            if examples:
                return examples
        except Exception as e:
            logging.error(f"Error loading dark pattern examples from {dataset_path}: {e}")

    # Fallback examples
    return [
        "Hurry! Only 2 left in stock",
        "15 people are looking at this right now",
        "Limited time offer!",
        "Selling fast!",
        "Only 3 items left at this price"
    ]

def analyze_text_with_gemini(current_content, reference_content):
    """
    Analyzes text content for dark patterns using the Gemini model.
    
    Parameters:
    - current_content (str): The current crawl content to analyze.
    - reference_content (str): Previous crawl content for comparison.
    
    Returns:
    - str: Analysis result from the Gemini model.
    """
    logging.debug("Preparing prompt for OpenAI model.")
    
    # Load dark pattern examples from cleaned dataset
    dark_pattern_examples = load_dark_pattern_examples()
    
    # Select a subset of examples (to avoid making the prompt too long)
    example_subset = dark_pattern_examples[:20]  # Use first 20 examples
    examples_text = '\n- '.join([''] + example_subset)  # Format as bullet points

    # Build messages for Chat Completions
    system_message = (
        "You are an expert in detecting dark patterns in ecommerce websites."
    )
    user_message = f"""
Detect words/phrases that indicate False Urgency.
False Urgency means falsely stating or implying urgency or scarcity to mislead a user into immediate action.

Examples include:
{examples_text}

Compare the two versions of website content.

--- PREVIOUS CRAWL ---
{reference_content}

--- CURRENT CRAWL ---
{current_content}

Provide a concise report focusing on false urgency or scarcity tactics. For each finding include:
- Was there indicative dark pattern: <Yes/No + brief reason>
- Rationale: <brief justification>

If none are found, reply exactly with: No dark patterns detected.
"""

    # Call the OpenAI model and return the response
    try:
        logging.debug("Sending messages to OpenAI model.")
        if not client:
            raise Exception("OpenAI client not initialized.")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            temperature=0.2,
        )
        logging.debug("Received response from OpenAI model.")
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        logging.error(f"Error during OpenAI API call: {e}")
        return f"Error during analysis: {str(e)}"
