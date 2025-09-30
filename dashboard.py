from flask import Flask, render_template, jsonify, send_from_directory
import os
import glob
import json
from datetime import datetime

app = Flask(__name__)

# Serve static files
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/crawls')
def get_crawls():
    # Get all crawl files
    crawl_files = sorted(glob.glob("crawl_*.txt"), reverse=True)
    crawls = []
    
    for file in crawl_files:
        timestamp = file.replace("crawl_", "").replace(".txt", "")
        try:
            dt = datetime.strptime(timestamp, "%Y%m%d_%H%M%S")
            crawls.append({
                'filename': file,
                'timestamp': dt.strftime("%Y-%m-%d %H:%M:%S"),
                'date': dt.strftime("%Y-%m-%d"),
                'time': dt.strftime("%H:%M:%S")
            })
        except:
            continue
    
    return jsonify(crawls)

@app.route('/api/crawl/<filename>')
def get_crawl(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'filename': filename,
            'content': content,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 404

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Start the Flask app
    app.run(debug=True, port=5000)
