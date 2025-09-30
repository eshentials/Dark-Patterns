# app.py
from flask import Flask, request, jsonify, send_from_directory
import subprocess
import json
import os
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='static')

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_url():
    try:
        logger.info("Received analyze request")
        data = request.get_json()
        if not data:
            logger.error("No JSON data received")
            return jsonify({'error': 'No data provided'}), 400
            
        url = data.get('url', '').strip()
        logger.info(f"Processing URL: {url}")
        
        if not url:
            logger.error("No URL provided")
            return jsonify({'error': 'URL is required'}), 400
        
        # Create reports directory if it doesn't exist
        reports_dir = 'reports'
        os.makedirs(reports_dir, exist_ok=True)
        logger.info(f"Reports directory: {os.path.abspath(reports_dir)}")
        
        # Call main.py with the URL as an argument
        logger.info("Starting subprocess...")
        try:
            result = subprocess.run(
                ['python3', 'main.py', '--url', url],
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            logger.info(f"Subprocess completed with return code: {result.returncode}")
            
            if result.returncode != 0:
                error_msg = f"Subprocess failed with error: {result.stderr}"
                logger.error(error_msg)
                return jsonify({
                    'error': 'Failed to analyze URL',
                    'details': result.stderr,
                    'stdout': result.stdout
                }), 500
                
        except subprocess.TimeoutExpired:
            error_msg = "Analysis timed out after 5 minutes"
            logger.error(error_msg)
            return jsonify({
                'error': 'Analysis timed out',
                'details': 'The analysis took too long to complete'
            }), 504
                
        # Find the latest comparison report
        logger.info("Looking for report files...")
        try:
            report_files = [
                f for f in os.listdir(reports_dir) 
                if f.endswith('.json')
            ]
            report_files.sort(key=lambda x: os.path.getmtime(os.path.join(reports_dir, x)), reverse=True)
            
            logger.info(f"Found {len(report_files)} report files")
            
            if not report_files:
                error_msg = "No report files found in reports directory"
                logger.error(error_msg)
                return jsonify({
                    'error': 'No reports generated',
                    'details': error_msg,
                    'directory': os.path.abspath(reports_dir),
                    'files': os.listdir(reports_dir)
                }), 500
                
            # Read the latest report
            latest_report = os.path.join(reports_dir, report_files[0])
            logger.info(f"Latest report: {latest_report}")
            
            with open(latest_report, 'r') as f:
                report_data = json.load(f)
                
            logger.info("Successfully loaded report data")
            return jsonify(report_data)
            
        except Exception as e:
            error_msg = f"Error processing report: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return jsonify({
                'error': 'Error processing report',
                'details': str(e),
                'report_files': report_files if 'report_files' in locals() else []
            }), 500
            
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e),
            'type': type(e).__name__
        }), 500

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static', exist_ok=True)
    app.run(debug=True, port=5001)