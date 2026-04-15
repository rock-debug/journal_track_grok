from flask import Flask, jsonify
import sys
import os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        "status": "ok",
        "message": "Vercel Python works!",
        "python_version": sys.version
    })

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/<path:path>')
def catch_all(path):
    return jsonify({"status": "ok", "path": path})
