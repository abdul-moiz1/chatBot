import os
from flask import Flask, request, render_template_string, jsonify
from openai import OpenAI

app = Flask(__name__)

api_key = os.environ.get("OPENAI_API_KEY", "").strip()
client = OpenAI(api_key=api_key)

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Chat Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 20px 24px;
            border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            color: #1a1a2e;
            text-align: center;
            font-weight: 700;
            font-size: 20px;
            box-shadow: 0 2px 20px rgba(0, 0, 0, 0.08);
            letter-spacing: -0.5px;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 32px 20px;
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .chat-container::-webkit-scrollbar {
            width: 8px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: rgba(255, 255, 255, 0.3);
            border-radius: 10px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: rgba(255, 255, 255, 0.4);
        }
        .message {
            display: flex;
            gap: 14px;
            max-width: 900px;
            margin: 0 auto;
            width: 100%;
            animation: fadeIn 0.4s ease-out;
        }
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        .message.user {
            flex-direction: row-reverse;
        }
        .avatar {
            width: 42px;
            height: 42px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-weight: 700;
            font-size: 13px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }
        .message.user .avatar {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .message.ai .avatar {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
        }
        .message-content {
            background: rgba(255, 255, 255, 0.98);
            padding: 16px 20px;
            border-radius: 16px;
            color: #2d3748;
            line-height: 1.7;
            max-width: 70%;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
            font-size: 15px;
        }
        .message.user .message-content {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        .input-container {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-top: 1px solid rgba(0, 0, 0, 0.05);
            box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.08);
        }
        .input-wrapper {
            max-width: 900px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        #messageInput {
            flex: 1;
            background: white;
            border: 2px solid #e2e8f0;
            border-radius: 14px;
            padding: 14px 18px;
            color: #2d3748;
            font-size: 15px;
            font-family: inherit;
            resize: none;
            max-height: 200px;
            min-height: 24px;
            transition: all 0.2s ease;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        }
        #messageInput:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.15);
        }
        #messageInput::placeholder {
            color: #a0aec0;
        }
        #sendButton {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 14px;
            cursor: pointer;
            font-weight: 700;
            font-size: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 16px rgba(102, 126, 234, 0.3);
        }
        #sendButton:hover:not(:disabled) {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }
        #sendButton:active:not(:disabled) {
            transform: translateY(0);
        }
        #sendButton:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            box-shadow: none;
        }
        .typing-indicator {
            display: none;
            gap: 6px;
            padding: 16px 20px;
        }
        .typing-indicator.active {
            display: flex;
        }
        .typing-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            animation: typing 1.4s infinite ease-in-out;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { 
                transform: translateY(0);
                opacity: 0.5;
            }
            30% { 
                transform: translateY(-12px);
                opacity: 1;
            }
        }
        .welcome-message {
            text-align: center;
            color: rgba(255, 255, 255, 0.95);
            padding: 60px 20px;
            max-width: 600px;
            margin: auto;
            animation: fadeIn 0.6s ease-out;
        }
        .welcome-message h2 {
            color: white;
            margin-bottom: 20px;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
        }
        .welcome-message p {
            font-size: 17px;
            line-height: 1.6;
            opacity: 0.9;
        }
        @media (max-width: 768px) {
            .header {
                font-size: 18px;
                padding: 18px 20px;
            }
            .message-content {
                max-width: 85%;
                font-size: 14px;
                padding: 14px 16px;
            }
            .input-wrapper {
                gap: 10px;
            }
            #sendButton {
                padding: 14px 20px;
                font-size: 14px;
            }
            .welcome-message h2 {
                font-size: 28px;
            }
            .welcome-message p {
                font-size: 16px;
            }
        }
    </style>
</head>
<body>
    <div class="header">
        AI Chat Assistant
    </div>
    
    <div class="chat-container" id="chatContainer">
        <div class="welcome-message">
            <h2>👋 Welcome!</h2>
            <p>I'm your AI assistant. Ask me anything and I'll help you out!</p>
        </div>
    </div>
    
    <div class="input-container">
        <div class="input-wrapper">
            <textarea id="messageInput" placeholder="Type your message here..." rows="1"></textarea>
            <button id="sendButton">Send</button>
        </div>
    </div>

    <script>
        const chatContainer = document.getElementById('chatContainer');
        const messageInput = document.getElementById('messageInput');
        const sendButton = document.getElementById('sendButton');
        
        messageInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 200) + 'px';
        });
        
        messageInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
        
        sendButton.addEventListener('click', sendMessage);
        
        function addMessage(content, isUser) {
            const welcome = document.querySelector('.welcome-message');
            if (welcome) welcome.remove();
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${isUser ? 'user' : 'ai'}`;
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = isUser ? 'You' : 'AI';
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            messageContent.textContent = content;
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(messageContent);
            chatContainer.appendChild(messageDiv);
            
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function showTypingIndicator() {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message ai';
            messageDiv.id = 'typingIndicator';
            
            const avatar = document.createElement('div');
            avatar.className = 'avatar';
            avatar.textContent = 'AI';
            
            const typingDiv = document.createElement('div');
            typingDiv.className = 'typing-indicator active';
            typingDiv.innerHTML = '<div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div>';
            
            messageDiv.appendChild(avatar);
            messageDiv.appendChild(typingDiv);
            chatContainer.appendChild(messageDiv);
            chatContainer.scrollTop = chatContainer.scrollHeight;
        }
        
        function hideTypingIndicator() {
            const indicator = document.getElementById('typingIndicator');
            if (indicator) indicator.remove();
        }
        
        async function sendMessage() {
            const message = messageInput.value.trim();
            if (!message) return;
            
            addMessage(message, true);
            messageInput.value = '';
            messageInput.style.height = 'auto';
            sendButton.disabled = true;
            
            showTypingIndicator();
            
            try {
                const response = await fetch('/api/chat', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        name: 'User',
                        email: 'user@example.com',
                        question: message
                    })
                });
                
                const data = await response.json();
                hideTypingIndicator();
                
                if (data.answer) {
                    addMessage(data.answer, false);
                } else if (data.error) {
                    addMessage('Sorry, I encountered an error: ' + data.error, false);
                }
            } catch (error) {
                hideTypingIndicator();
                addMessage('Sorry, something went wrong. Please try again.', false);
            }
            
            sendButton.disabled = false;
            messageInput.focus();
        }
    </script>
</body>
</html>
"""

RESPONSE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Response</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
            max-width: 600px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
        }
        .info-section {
            margin-bottom: 25px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 6px;
        }
        .info-label {
            font-weight: 600;
            color: #667eea;
            margin-bottom: 5px;
        }
        .info-content {
            color: #333;
            line-height: 1.6;
        }
        .ai-response {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 25px;
            line-height: 1.8;
        }
        .back-link {
            display: inline-block;
            padding: 12px 30px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: 600;
            transition: transform 0.2s;
        }
        .back-link:hover {
            transform: translateY(-2px);
        }
        @media (max-width: 600px) {
            .container {
                padding: 30px 20px;
            }
            h1 {
                font-size: 24px;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>AI Response</h1>
        
        <div class="info-section">
            <div class="info-label">Name:</div>
            <div class="info-content">{{ name }}</div>
        </div>
        
        <div class="info-section">
            <div class="info-label">Email:</div>
            <div class="info-content">{{ email }}</div>
        </div>
        
        <div class="info-section">
            <div class="info-label">Your Question:</div>
            <div class="info-content">{{ question }}</div>
        </div>
        
        <div class="ai-response">
            <strong>AI Answer:</strong><br><br>
            {{ answer }}
        </div>
        
        <a href="/" class="back-link">Ask Another Question</a>
    </div>
</body>
</html>
"""


def get_ai_response(name, question):
    prompt = f"Answer the user politely and clearly in 3 to 5 short lines. User name: {name}. Question: {question}."
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "user", "content": prompt}
            ],
            timeout=30.0
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"OpenAI API Error: {type(e).__name__}: {str(e)}")
        raise Exception("Unable to get AI response. Please try again later.")


WEBHOOK_TEST_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Webhook Tester</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #1a1a2e;
            margin-bottom: 10px;
            font-size: 28px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
        }
        input, textarea {
            width: 100%;
            padding: 12px 16px;
            border: 2px solid #e2e8f0;
            border-radius: 8px;
            font-size: 15px;
            font-family: inherit;
        }
        input:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 100px;
        }
        button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 14px 32px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 700;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:disabled {
            background: #cbd5e0;
            cursor: not-allowed;
            transform: none;
        }
        .response {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
            display: none;
        }
        .response.show {
            display: block;
        }
        .response.success {
            background: #d4edda;
            border: 2px solid #28a745;
        }
        .response.error {
            background: #f8d7da;
            border: 2px solid #dc3545;
        }
        .response-title {
            font-weight: 700;
            margin-bottom: 10px;
            font-size: 18px;
        }
        .response-content {
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 14px;
        }
        .back-link {
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 600;
        }
        .back-link:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Webhook Tester</h1>
        <p class="subtitle">Test your /webhook/make endpoint</p>
        
        <div class="form-group">
            <label for="apiKey">API Key (WEBHOOK_API_KEY)</label>
            <input type="text" id="apiKey" placeholder="Enter your webhook API key" value="my-secret-webhook-key-2025">
        </div>
        
        <div class="form-group">
            <label for="question">Question</label>
            <textarea id="question" placeholder="Enter a question for the AI">Give me a motivational quote</textarea>
        </div>
        
        <div class="form-group">
            <label for="name">Name (optional)</label>
            <input type="text" id="name" placeholder="Your name" value="Test User">
        </div>
        
        <button id="testBtn" onclick="testWebhook()">Test Webhook</button>
        
        <div id="response" class="response"></div>
        
        <a href="/" class="back-link">← Back to Chat</a>
    </div>
    
    <script>
        async function testWebhook() {
            const btn = document.getElementById('testBtn');
            const responseDiv = document.getElementById('response');
            const apiKey = document.getElementById('apiKey').value.trim();
            const question = document.getElementById('question').value.trim();
            const name = document.getElementById('name').value.trim() || 'User';
            
            if (!apiKey) {
                alert('Please enter an API key');
                return;
            }
            
            if (!question) {
                alert('Please enter a question');
                return;
            }
            
            btn.disabled = true;
            btn.textContent = 'Testing...';
            responseDiv.className = 'response';
            responseDiv.style.display = 'none';
            
            try {
                const response = await fetch('/webhook/make', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer ' + apiKey
                    },
                    body: JSON.stringify({
                        question: question,
                        name: name
                    })
                });
                
                const data = await response.json();
                
                if (response.ok) {
                    responseDiv.className = 'response success show';
                    responseDiv.innerHTML = `
                        <div class="response-title">✅ Success!</div>
                        <div class="response-content">${JSON.stringify(data, null, 2)}</div>
                    `;
                } else {
                    responseDiv.className = 'response error show';
                    responseDiv.innerHTML = `
                        <div class="response-title">❌ Error ${response.status}</div>
                        <div class="response-content">${JSON.stringify(data, null, 2)}</div>
                    `;
                }
            } catch (error) {
                responseDiv.className = 'response error show';
                responseDiv.innerHTML = `
                    <div class="response-title">❌ Network Error</div>
                    <div class="response-content">${error.message}</div>
                `;
            }
            
            btn.disabled = false;
            btn.textContent = 'Test Webhook';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)


@app.route('/test-webhook')
def test_webhook():
    return render_template_string(WEBHOOK_TEST_TEMPLATE)


@app.route('/chat', methods=['POST'])
def chat():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    question = request.form.get('question', '')
    
    if not name or not question:
        return "Error: Name and question are required", 400
    
    try:
        answer = get_ai_response(name, question)
        
        return render_template_string(
            RESPONSE_TEMPLATE,
            name=name,
            email=email,
            question=question,
            answer=answer
        )
    except Exception as e:
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Error</title>
            <style>
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    padding: 20px;
                }}
                .container {{
                    background: white;
                    border-radius: 12px;
                    padding: 40px;
                    max-width: 500px;
                    width: 100%;
                    text-align: center;
                }}
                h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                .error {{ color: #555; margin-bottom: 30px; line-height: 1.6; }}
                a {{ 
                    display: inline-block;
                    padding: 12px 30px;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    text-decoration: none;
                    border-radius: 6px;
                    font-weight: 600;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>⚠️ Error</h1>
                <div class="error">{str(e)}</div>
                <a href="/">Try Again</a>
            </div>
        </body>
        </html>
        """
        return error_html, 500


@app.route('/api/chat', methods=['POST'])
def api_chat():
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    name = data.get('name', '')
    email = data.get('email', '')
    question = data.get('question', '')
    
    if not name or not question:
        return jsonify({"error": "Name and question are required"}), 400
    
    try:
        answer = get_ai_response(name, question)
        return jsonify({"answer": answer})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/webhook/make', methods=['POST'])
def webhook_make():
    webhook_key = os.environ.get("WEBHOOK_API_KEY", "").strip()
    
    auth_header = request.headers.get('Authorization', '')
    provided_key = auth_header.replace('Bearer ', '').strip()
    
    if not webhook_key or provided_key != webhook_key:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "No JSON data provided"}), 400
    
    question = data.get('question', '')
    name = data.get('name', 'User')
    
    if not question:
        return jsonify({"error": "Question is required"}), 400
    
    try:
        answer = get_ai_response(name, question)
        return jsonify({
            "success": True,
            "question": question,
            "answer": answer,
            "name": name
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
