# 🤖 AI Chatbot Application

A modern, beautiful chatbot application built with Flask and featuring a responsive web interface. The bot uses a local knowledge base and can fall back to Groq's AI API for responses.

## ✨ Features

- 🎨 **Beautiful Modern UI** - Responsive design with gradient backgrounds and smooth animations
- 🧠 **Smart Responses** - Local knowledge base with AI fallback
- 💾 **Conversation History** - SQLite database stores all conversations
- 🔄 **Real-time Chat** - Instant messaging with typing indicators
- 📱 **Mobile Friendly** - Works perfectly on all devices
- 🚀 **Easy Setup** - Simple installation and configuration

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Your API Key (Optional)
Open `app.py` and paste your key into:
```python
HARDCODED_GROQ_API_KEY = "your_groq_api_key_here"
```
You can leave it empty to disable AI fallback and use only the local knowledge base.

### 3. Run the Application
```bash
python app.py
```

### 4. Open Your Browser
Visit: `http://localhost:5000`

## 🎯 How It Works

1. **Knowledge Base First**: The bot checks its local SQLite database for answers
2. **AI Fallback**: If no local answer is found, it uses Groq's AI API
3. **Conversation Storage**: All chats are saved for history and learning
4. **Beautiful Interface**: Modern, responsive design with real-time updates

## 📁 Project Structure

```
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── templates/         # HTML templates
│   └── index.html     # Main chat interface
├── README.md          # This file
└── chatbot.db         # SQLite database (created automatically)
```

## 🔧 Configuration

### Environment Variables
- `GROQ_API_KEY`: Your Groq API key (optional, for AI fallback)

### Database
The application uses SQLite, so no external database setup is required. The database file (`chatbot.db`) is created automatically.

## 🌐 API Endpoints

- `GET /` - Main chat interface
- `POST /api/chat` - Send a message to the bot
- `GET /api/health` - Check application health
- `GET /api/history` - Get conversation history

## 💡 Usage Examples

### Chat API
```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is Python?"}'
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

## 🎨 Customization

### Adding Knowledge
Edit the `init_db()` function in `app.py` to add more knowledge to the database:

```python
sample_data = [
    ("Your question?", "Your answer here"),
    # Add more Q&A pairs
]
```

### Styling
Modify the CSS in `templates/index.html` to customize the appearance.

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use**: Change the port in `app.py`:
   ```python
   app.run(debug=True, host='0.0.0.0', port=5001)
   ```

2. **Groq API errors**: Make sure your API key is correct and you have credits

3. **Database errors**: Delete `chatbot.db` to reset the database

## 📦 Dependencies

- **Flask**: Web framework
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management
- **sqlite3**: Built-in database (no installation needed)

## 🚀 Deployment

### Local Development
```bash
python app.py
```

### Production
For production deployment, consider using:
- **Gunicorn**: WSGI server
- **Nginx**: Reverse proxy
- **Docker**: Containerization

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Feel free to submit issues, feature requests, or pull requests!

---

**Enjoy chatting with your AI assistant!** 🎉
