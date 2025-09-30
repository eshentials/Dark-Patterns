import pandas as pd
import re

def is_false_urgency(text):
    """
    Check if the given text contains false urgency patterns.
    Returns True if it's a false urgency, False otherwise.
    """
    if not isinstance(text, str):
        return False
    
    text = text.lower()
    
    # Common false urgency patterns
    patterns = [
        # Quantity-based urgency
        r'\b(only|just)\s+\d+\s+(left|remaining|in stock|available|copy|copies)\b',
        r'\b(only|just)\s+(a few|a couple of|a handful of)\s+(left|remaining|in stock|available)\b',
        r'\b(only|just)\s+\d+\s+(left|remaining)\s+at\s+this\s+price\b',
        
        # Time-based urgency
        r'\b(ends?|expires?)\s+(in|at|today|tonight|soon|in \d+ (hours?|minutes?|days?))\b',
        r'\b(limited\s+time|time\s+limited|flash\s+sale|flash\s+deal)\b',
        r'\b(one\s+day\s+only|today\s+only|tonight\s+only|this\s+weekend\s+only)\b',
        
        # Scarcity indicators
        r'\b(almost\s+gone|almost\s+sold\s+out|going\s+fast|selling\s+fast|flying\s+off\s+the\s+shelves)\b',
        r'\b(running\s+out|running\s+low|low\s+in\s+stock|low\s+stock|stock\s+is\s+low)\b',
        r'\b(supplies\s+are\s+limited|quantities\s+are\s+limited|while\s+supplies\s+last|while\s+stock\s+lasts)\b',
        
        # Social proof urgency
        r'\b(\d+\s+people\s+(are\s+)?(viewing|watching|purchasing|buying|in\s+line))\b',
        r'\b(\d+\s+(sold|bought|purchased)\s+(in|during)\s+the\s+last\s+\d+\s+(hours?|minutes?|days?))\b',
        
        # Action-oriented urgency
        r'\b(hurry|act\s+now|don\'?t\s+miss|last\s+chance|order\s+now|buy\s+now|shop\s+now)\b',
        r'\b(while\s+supplies\s+last|while\s+stock\s+lasts|while\s+quantities\s+last)\b',
        
        # Price-based urgency
        r'\b(price\s+increase\s+in\s+\d+\s+(hours?|days?)|price\s+goes\s+up\s+soon)\b',
        r'\b(limited\s+time\s+offer|special\s+offer\s+expires\s+soon|today\s+only\s+deal)\b'
    ]
    
    # Check if any pattern matches
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    return False

def clean_dataset(input_file, output_file):
    """
    Clean the dataset by filtering only false urgency patterns.
    """
    try:
        # Read the CSV file
        df = pd.read_csv(input_file)
        
        # Filter rows containing false urgency patterns
        df_filtered = df[df['text'].apply(is_false_urgency)]
        
        # Save the filtered data to a new CSV file
        df_filtered.to_csv(output_file, index=False)
        
        print(f"Original dataset size: {len(df)} rows")
        print(f"Filtered dataset size: {len(df_filtered)} rows")
        print(f"Filtered data saved to: {output_file}")
        
        return df_filtered
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

if __name__ == "__main__":
    input_file = "dark_dataset.csv"
    output_file = "cleaned_dataset.csv"
    
    print("Starting data cleaning process...")
    cleaned_data = clean_dataset(input_file, output_file)
    
    if cleaned_data is not None:
        print("\nSample of filtered data:")
        print(cleaned_data.head())
    else:
        print("Failed to clean the dataset.")