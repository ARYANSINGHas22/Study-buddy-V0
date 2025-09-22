from flask import Flask, request, jsonify, render_template
import os
import json
import requests
from datetime import datetime
import sqlite3
 

app = Flask(__name__)

# Configuration - hardcoded for simplicity
HARDCODED_GROQ_API_KEY = ""  # Paste your key here
GROQ_API_KEY = HARDCODED_GROQ_API_KEY
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL_NAME = "llama-3.1-8b-instant"

# Ensure Flask instance folder exists and use it for DB (writable location)
try:
    os.makedirs(app.instance_path, exist_ok=True)
except Exception:
    pass
DB_PATH = os.path.join(app.instance_path, 'chatbot.db')

# Initialize SQLite database
def init_db():
    """Initialize the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create conversations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create knowledge base table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Insert some sample knowledge only if table is empty
    cursor.execute('SELECT COUNT(*) FROM knowledge_base')
    row_count = cursor.fetchone()[0]
    if row_count == 0:
        sample_data = [
            ("What is Python?", "Python is a high-level, interpreted programming language known for its simplicity and readability. It's widely used in web development, data science, AI, and automation."),
            ("How do I install Python?", "You can download Python from python.org or use package managers like pip, conda, or brew. For Windows, download from python.org. For Mac, use 'brew install python'. For Linux, use your package manager."),
            ("What is Flask?", "Flask is a lightweight web framework for Python that makes it easy to build web applications. It's known for its simplicity and flexibility."),
            ("What is machine learning?", "Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed for every task."),
            ("How do I get started with programming?", "Start with a beginner-friendly language like Python, practice regularly, build small projects, join coding communities, and don't be afraid to make mistakes - they're part of learning!")
        ]
        cursor.executemany('''
            INSERT INTO knowledge_base (question, answer) VALUES (?, ?)
        ''', sample_data)
    
    conn.commit()
    conn.close()

def get_answer_from_knowledge_base(user_input):
    """Search for answers in the knowledge base"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Search for similar questions
    cursor.execute('''
        SELECT answer FROM knowledge_base 
        WHERE question LIKE ? OR answer LIKE ?
        ORDER BY 
            CASE 
                WHEN question LIKE ? THEN 1
                WHEN answer LIKE ? THEN 2
                ELSE 3
            END
        LIMIT 1
    ''', (f'%{user_input}%', f'%{user_input}%', f'%{user_input}%', f'%{user_input}%'))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def ask_groq_api(user_input):
    """Ask Groq API for a response"""
    if not GROQ_API_KEY:
        return "AI fallback is disabled. To enable it, paste your key into app.py (HARDCODED_GROQ_API_KEY)."
    
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a helpful, friendly AI assistant.\n"
                    "Format your response based on the query:\n"
                    "- If the user asks for steps, return short bullet points (use dashes).\n"
                    "- If the user asks for an explanation, return a compact paragraph.\n"
                    "- Keep it concise, clear, and directly answer the question.\n"
                    "- Use line breaks between bullets; avoid markdown numbering.\n"
                    "- If uncertain, say you are unsure briefly."
                )
            },
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 500,
        "temperature": 0.6
    }
    
    try:
        response = requests.post(GROQ_API_URL, headers=headers, json=data, timeout=10)
        response.raise_for_status()
        response_json = response.json()
        
        if "error" in response_json:
            return f"AI service error: {response_json['error']['message']}"
        
        return response_json["choices"][0]["message"]["content"]
    
    except requests.exceptions.RequestException as e:
        return f"Sorry, I'm having trouble connecting to the AI service. Error: {str(e)}"
    except KeyError as e:
        return "Sorry, I received an unexpected response from the AI service."
    except Exception as e:
        return f"An unexpected error occurred: {str(e)}"

def save_conversation(user_message, bot_response):
    """Save conversation to database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO conversations (user_message, bot_response, timestamp)
            VALUES (?, ?, ?)
        ''', (user_message, bot_response, datetime.now()))
        conn.commit()
    except Exception:
        # Fail silently for storage issues; do not break the chat flow
        pass
    finally:
        try:
            conn.close()
        except Exception:
            pass

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        user_message = data['message'].strip()
        
        if not user_message:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        # First, check knowledge base
        knowledge_answer = get_answer_from_knowledge_base(user_message)
        
        if knowledge_answer:
            bot_response = knowledge_answer
        else:
            # Fallback to Groq API
            bot_response = ask_groq_api(user_message)
        
        # Save conversation
        save_conversation(user_message, bot_response)
        
        return jsonify({
            'response': bot_response,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({'error': f'Internal server error: {str(e)}'}), 500

@app.route('/api/health')
def health():
    """Health check endpoint"""
    try:
        # Check database
        conn = sqlite3.connect(DB_PATH)
        conn.close()
        
        # Check Groq API key
        groq_status = "configured" if GROQ_API_KEY else "missing"
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'groq_api': groq_status,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/api/history')
def get_history():
    """Get conversation history"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT user_message, bot_response, timestamp
            FROM conversations
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        conversations = []
        for row in cursor.fetchall():
            conversations.append({
                'user_message': row[0],
                'bot_response': row[1],
                'timestamp': row[2]
            })
        
        conn.close()
        
        return jsonify({'conversations': conversations})
    
    except Exception as e:
        return jsonify({'error': f'Failed to get history: {str(e)}'}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)

