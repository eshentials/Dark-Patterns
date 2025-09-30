# main.py

from crawler import crawl_site
from api_gemini import analyze_text_with_gemini
import os
import re
import glob
from datetime import datetime
def sanitize_filename(title):
    return re.sub(r'[^a-zA-Z0-9_-]', '_', title)[:50]  # limit length

def extract_title_from_content(content):
    # Extract title from the first line starting with 'Title:'
    for line in content.split('\n'):
        if line.startswith('Title:'):
            return line.replace('Title:', '').strip()
    return "untitled"

if __name__ == "__main__":
    url = input("Enter the website URL to crawl: ").strip()
    
    # Get current timestamp for unique filenames
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Crawl the site and get text data
    data = crawl_site(url, max_pages=1)
    
    # Save the complete crawl data to a text file
    filename = f"crawl_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.writelines(data)
    
    print(f"\nDone! Results saved to {filename}")
    
    # --- Gemini Comparison and Reporting ---
    # Find all previous crawl files (excluding the current one)
    crawl_files = sorted(glob.glob("crawl_*.txt"))
    crawl_files = [f for f in crawl_files if f != filename]  # Exclude current file
    
    if crawl_files:
        # Use the most recent crawl file for comparison
        baseline_file = crawl_files[-1]
        print(f"Comparing with previous crawl: {baseline_file}")
        
        # Read the baseline data
        with open(baseline_file, "r", encoding="utf-8") as f:
            baseline_content = f.read()
        
        # Read the current data
        with open(filename, "r", encoding="utf-8") as f:
            current_content = f.read()
        
        # Generate comparison report
        report = analyze_text_with_gemini(current_content, baseline_content)
        
        # Save the report
        report_filename = f"comparison_report_{timestamp}.txt"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"Comparison report saved to {report_filename}")
    else:
        print("No previous crawl found for comparison.")