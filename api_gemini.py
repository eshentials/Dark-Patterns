# api_gemini.py

import google.generativeai as genai
import json
import logging
import os
import csv

# Setup basic logging configuration
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Configure the Gemini API key (Note: Hardcoding keys is not recommended for production use)
try:
    logging.debug("Configuring Gemini API with provided API key.")
    genai.configure(api_key="AIzaSyC2N3MtEuXakJj6hp7eutYFmgu5opFuGRY")
except Exception as e:
    logging.error(f"Failed to configure API key: {e}")

# Initialize the Gemini model
try:
    logging.debug("Initializing Gemini model: models/gemini-2.5-flash-preview-04-17")
    model = genai.GenerativeModel("models/gemini-2.5-flash-preview-04-17")
except Exception as e:
    logging.error(f"Error initializing Gemini model: {e}")
    model = None  # fallback to prevent usage of an uninitialized model

def load_dark_pattern_examples():
    """
    Load examples of dark patterns from the cleaned dataset.
    
    Returns:
    - list: List of dark pattern examples
    """
    examples = []
    dataset_path = os.path.join(os.path.dirname(__file__), 'cleaned_dataset.csv')
    
    try:
        with open(dataset_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['label'] == '1':  # Only include confirmed dark patterns
                    examples.append(row['text'])
        return examples
    except Exception as e:
        logging.error(f"Error loading dark pattern examples: {e}")
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
    logging.debug("Preparing prompt for Gemini model.")
    
    # Load dark pattern examples from cleaned dataset
    dark_pattern_examples = load_dark_pattern_examples()
    
    # Select a subset of examples (to avoid making the prompt too long)
    example_subset = dark_pattern_examples[:20]  # Use first 20 examples
    examples_text = '\n- '.join([''] + example_subset)  # Format as bullet points

    # Construct the prompt
    prompt = f"""
You are an expert in detecting dark patterns in ecommerce websites. You have to find words which indicate false urgency
"False Urgency” means falsely stating or implying the sense of urgency or scarcity so as to mislead a user into making an immediate purchase or take an immediate action, which may lead to a purchase; including:
i. Showing false popularity of a product or service to manipulate user decision;
ii. Stating that quantities of a particular product or service are more limited than they actually are.
Examples: i. Limited time deal, Limited availbility 
ii. Only a few left in stocks

Examples of False Urgency:{examples_text}

These examples demonstrate common dark patterns that create false urgency or scarcity. Look for similar patterns in the following website content.

Compare the following two versions of website content. The first is from a previous crawl, and the second is from the current crawl.

--- PREVIOUS CRAWL ---
{reference_content}

--- CURRENT CRAWL ---
{current_content}

Analyze both versions and provide a detailed report on any dark patterns found, focusing on false urgency or scarcity tactics. For each finding, include:
Was there indicative dark pattern: Your response 
Rationale: Your justification

If no dark patterns are found, simply state "No dark patterns detected."
"""

    # Call the model and return the response
    try:
        logging.debug("Sending prompt to Gemini model.")
        if not model:
            raise Exception("Model not initialized.")
        response = model.generate_content(prompt)
        logging.debug("Received response from Gemini model.")
        return response.text.strip()
    except Exception as e:
        logging.error(f"Error during Gemini API call: {e}")
        return f"Error during analysis: {str(e)}"
