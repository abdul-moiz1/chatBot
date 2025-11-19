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
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #343541;
            height: 100vh;
            display: flex;
            flex-direction: column;
            overflow: hidden;
        }
        .header {
            background: #202123;
            padding: 16px 20px;
            border-bottom: 1px solid #444654;
            color: white;
            text-align: center;
            font-weight: 600;
            font-size: 18px;
        }
        .chat-container {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }
        .message {
            display: flex;
            gap: 12px;
            max-width: 800px;
            margin: 0 auto;
            width: 100%;
        }
        .message.user {
            flex-direction: row-reverse;
        }
        .avatar {
            width: 36px;
            height: 36px;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
            font-weight: 600;
            font-size: 14px;
        }
        .message.user .avatar {
            background: #5436da;
            color: white;
        }
        .message.ai .avatar {
            background: #19c37d;
            color: white;
        }
        .message-content {
            background: #444654;
            padding: 12px 16px;
            border-radius: 8px;
            color: #ececf1;
            line-height: 1.6;
            max-width: 70%;
        }
        .message.user .message-content {
            background: #5436da;
        }
        .input-container {
            background: #40414f;
            padding: 20px;
            border-top: 1px solid #444654;
        }
        .input-wrapper {
            max-width: 800px;
            margin: 0 auto;
            display: flex;
            gap: 12px;
            align-items: flex-end;
        }
        #messageInput {
            flex: 1;
            background: #40414f;
            border: 1px solid #565869;
            border-radius: 8px;
            padding: 12px 16px;
            color: white;
            font-size: 16px;
            font-family: inherit;
            resize: none;
            max-height: 200px;
            min-height: 24px;
        }
        #messageInput:focus {
            outline: none;
            border-color: #19c37d;
        }
        #sendButton {
            background: #19c37d;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 600;
            font-size: 16px;
            transition: background 0.2s;
        }
        #sendButton:hover:not(:disabled) {
            background: #1a8b5e;
        }
        #sendButton:disabled {
            background: #565869;
            cursor: not-allowed;
        }
        .typing-indicator {
            display: none;
            gap: 4px;
            padding: 12px 16px;
        }
        .typing-indicator.active {
            display: flex;
        }
        .typing-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #888;
            animation: typing 1.4s infinite;
        }
        .typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .typing-dot:nth-child(3) { animation-delay: 0.4s; }
        @keyframes typing {
            0%, 60%, 100% { transform: translateY(0); }
            30% { transform: translateY(-10px); }
        }
        .welcome-message {
            text-align: center;
            color: #8e8ea0;
            padding: 40px 20px;
            max-width: 600px;
            margin: auto;
        }
        .welcome-message h2 {
            color: #ececf1;
            margin-bottom: 16px;
            font-size: 24px;
        }
        @media (max-width: 768px) {
            .message-content {
                max-width: 85%;
            }
            .input-wrapper {
                gap: 8px;
            }
            #sendButton {
                padding: 12px 16px;
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


@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)


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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
