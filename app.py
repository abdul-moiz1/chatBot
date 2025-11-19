import os
from flask import Flask, request, render_template_string, jsonify
from openai import OpenAI

app = Flask(__name__)

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ask a Question</title>
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
            max-width: 500px;
            width: 100%;
        }
        h1 {
            color: #333;
            margin-bottom: 30px;
            text-align: center;
            font-size: 28px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 500;
        }
        input[type="text"],
        input[type="email"],
        textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e1e1;
            border-radius: 6px;
            font-size: 16px;
            transition: border-color 0.3s;
        }
        input[type="text"]:focus,
        input[type="email"]:focus,
        textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        textarea {
            resize: vertical;
            min-height: 120px;
            font-family: inherit;
        }
        button {
            width: 100%;
            padding: 14px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
        }
        button:active {
            transform: translateY(0);
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
        <h1>Ask a Question</h1>
        <form method="POST" action="/chat">
            <div class="form-group">
                <label for="name">Name</label>
                <input type="text" id="name" name="name" required>
            </div>
            <div class="form-group">
                <label for="email">Email</label>
                <input type="email" id="email" name="email" required>
            </div>
            <div class="form-group">
                <label for="question">Question</label>
                <textarea id="question" name="question" required></textarea>
            </div>
            <button type="submit">Submit Question</button>
        </form>
    </div>
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
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    return response.choices[0].message.content


@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE)


@app.route('/chat', methods=['POST'])
def chat():
    name = request.form.get('name', '')
    email = request.form.get('email', '')
    question = request.form.get('question', '')
    
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
        return f"Error: {str(e)}", 500


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
    app.run(host='0.0.0.0', port=8000, debug=True)
