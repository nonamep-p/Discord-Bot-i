from flask import Flask, jsonify
import threading
import time
import psutil
import os
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def home():
    """Home route for keep-alive."""
    return jsonify({
        "status": "online",
        "message": "Epic RPG Helper Bot is running!",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/health')
def health():
    """Health check endpoint."""
    try:
        # Get system information
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        return jsonify({
            "status": "healthy",
            "uptime": time.time(),
            "cpu_usage": f"{cpu_percent}%",
            "memory_usage": f"{memory.percent}%",
            "memory_available": f"{memory.available // 1024 // 1024}MB",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/status')
def status():
    """Detailed status information."""
    try:
        return jsonify({
            "bot_name": "Epic RPG Helper",
            "version": "2.0.0",
            "python_version": f"{psutil.sys.version_info.major}.{psutil.sys.version_info.minor}.{psutil.sys.version_info.micro}",
            "system": {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent
            },
            "features": [
                "RPG System",
                "Economy System", 
                "Moderation Tools",
                "AI Chatbot",
                "Interactive UI"
            ],
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

def run():
    """Run the Flask app."""
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    """Start the keep-alive server in a separate thread."""
    server_thread = threading.Thread(target=run)
    server_thread.daemon = True
    server_thread.start()
    print(f"Keep-alive server started on port {os.getenv('PORT', 5000)}")
