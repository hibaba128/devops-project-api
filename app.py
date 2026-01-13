from flask import Flask, request, jsonify
from flask_cors import CORS
from prometheus_flask_exporter import PrometheusMetrics
import logging
import uuid
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Prometheus metrics
metrics = PrometheusMetrics(app)

# In-memory database
todos = {}

@app.before_request
def before_request():
    request.start_time = time.time()
    logger.info(f"Request: {request.method} {request.path}")

@app.after_request
def after_request(response):
    duration = time.time() - request.start_time
    logger.info(f"Response: {response.status_code} - Duration: {duration:.3f}s")
    return response

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.utcnow().isoformat()}), 200

@app.route('/todos', methods=['GET'])
def get_todos():
    logger.info(f"Fetching all todos. Count: {len(todos)}")
    return jsonify(list(todos.values())), 200

@app.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        logger.warning("Invalid request: missing title")
        return jsonify({"error": "Title is required"}), 400
    
    todo_id = str(uuid.uuid4())
    todo = {
        "id": todo_id,
        "title": data['title'],
        "description": data.get('description', ''),
        "completed": False,
        "created_at": datetime.utcnow().isoformat()
    }
    todos[todo_id] = todo
    logger.info(f"Created todo: {todo_id}")
    return jsonify(todo), 201

@app.route('/todos/<todo_id>', methods=['GET'])
def get_todo(todo_id):
    todo = todos.get(todo_id)
    if not todo:
        logger.warning(f"Todo not found: {todo_id}")
        return jsonify({"error": "Todo not found"}), 404
    return jsonify(todo), 200

@app.route('/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    if todo_id not in todos:
        return jsonify({"error": "Todo not found"}), 404
    
    data = request.get_json()
    todo = todos[todo_id]
    todo['title'] = data.get('title', todo['title'])
    todo['description'] = data.get('description', todo['description'])
    todo['completed'] = data.get('completed', todo['completed'])
    
    logger.info(f"Updated todo: {todo_id}")
    return jsonify(todo), 200

@app.route('/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    if todo_id not in todos:
        return jsonify({"error": "Todo not found"}), 404
    
    del todos[todo_id]
    logger.info(f"Deleted todo: {todo_id}")
    return jsonify({"message": "Todo deleted"}), 200

@app.errorhandler(Exception)
def handle_error(error):
    logger.error(f"Error occurred: {str(error)}")
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    logger.info("Starting Todo API server...")
    app.run(host='0.0.0.0', port=5001, debug=False)