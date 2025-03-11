"""proxy.py"""
from flask import Flask, request, Response, jsonify
import requests
import json
import os
from llama_cpp import Llama  # Import llama-cpp-python

# Flask setup
app = Flask(__name__)

# LM Studio API URL for chat completions (Update this to match your setup)
LM_STUDIO_URL = "http://<CHANGE-IP>:1234/v1/chat/completions"

# Path to your GGUF model (Update this to match your setup)
MODEL_PATH = "/Users/<CHANGE-USERNAME>/.lmstudio/models/Orenguteng/Llama-3.1-8B-Lexi-Uncensored-V2-GGUF/Llama-3.1-8B-Lexi-Uncensored_V2_Q8.gguf"

# Define maximum allowed tokens before trimming
TOKEN_MAX = 82944  # Adjust based on model's context size

# Load the model once (Avoid reloading on every request)
llm = Llama(model_path=MODEL_PATH)

def get_token_count(text):
    """Tokenize the text using llama.cpp locally and return token count."""
    try:
        tokens = llm.tokenize(text.encode("utf-8"), add_bos=False)
        return len(tokens)  # Return number of tokens
    except Exception as e:
        print(f"[Error] Failed to tokenize text: {str(e)}")
        return 0  # Return 0 instead of None to avoid errors

def load_prompt():
    """Load the system prompt from a text file."""
    prompt_file = "promptfile.txt"

    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    return "You are a helpful assistant. Please provide concise and accurate responses."

# Default system prompt injection
DEFAULT_SYSTEM_PROMPT = load_prompt()

def trim_messages(messages, max_tokens):
    """Trims messages while keeping the first user message and ensuring conversation coherence."""
    total_tokens = sum(msg["token_count"] for msg in messages)

    if total_tokens <= max_tokens:
        return messages  # No trimming needed

    print(f"\n[Trimming Messages] Total tokens: {total_tokens}, Max: {max_tokens}")

    # Preserve the first two messages (location/time + system prompt)
    preserved_messages = messages[:2]
    conversation_messages = messages[2:]  # The rest are eligible for trimming

    # Trim in pairs (user → assistant) while staying under TOKEN_MAX
    while len(conversation_messages) > 1 and total_tokens > max_tokens:
        removed_user = conversation_messages.pop(0)  # Remove oldest user message
        removed_assistant = conversation_messages.pop(0) if conversation_messages else None  # Remove its assistant reply
        total_tokens -= removed_user["token_count"]
        total_tokens -= removed_assistant["token_count"] if removed_assistant else 0

        print(f"[Removed] {removed_user['role']}: {removed_user['content'][:50]}...")
        if removed_assistant:
            print(f"[Removed] {removed_assistant['role']}: {removed_assistant['content'][:50]}...")

    return preserved_messages + conversation_messages

def stream_response(response):
    """Streams the response from LM Studio to the chat app in real-time."""
    for line in response.iter_lines():
        if line and line.startswith(b"data: "):  # Ignore empty lines, process JSON chunks
            json_chunk = line[6:].decode("utf-8")  # Strip "data: " prefix
            try:
                parsed_chunk = json.loads(json_chunk)
                yield f"data: {json.dumps(parsed_chunk)}\n\n"  # Maintain event-stream format
            except json.JSONDecodeError:
                print("\n[Error Parsing Chunk]:", json_chunk)  # Debugging

@app.route("/v1/chat/completions", methods=["POST"])
def proxy_request():
    try:
        # Get incoming JSON request
        data = request.get_json()

        # Log original request
        print("\n[Received Request]:", json.dumps(data, indent=2))

        if "messages" in data:
            messages = data["messages"]

            # Ensure the first message is preserved (location/time data)
            if not messages or messages[0]["role"] != "user":
                print("[Warning] First message is not from user, unexpected format.")

            first_message_content = messages[0]["content"].strip().lower()

            # **Detect chat title request**
            is_chat_title_request = (
                "write a very short title for the chat" in first_message_content
                and "return only the title" in first_message_content
            )

            # **Insert a blank `user` message after phone metadata if needed**
            if messages[0]["role"] == "system" and len(messages) > 1 and messages[1]["role"] != "user":
                print("[Info] Inserting a blank user message for conversation flow.")
                messages.insert(1, {"role": "user", "content": ""})  # Add blank user message

            # **Append system prompt if it's NOT a chat title request**
            if not is_chat_title_request:
                system_prompt = {"role": "user", "content": DEFAULT_SYSTEM_PROMPT}  # Ensure `user` role
                messages.insert(0, system_prompt)

            # **Fix role → content order before any processing**
            fixed_messages = []
            for msg in messages:
                fixed_msg = {
                    "role": msg.get("role", "user"),  # Default to "user" if missing
                    "content": msg.get("content", "")  # Ensure content is always present
                }
                fixed_messages.append(fixed_msg)

            # Now calculate token counts **after fixing the message format**
            total_tokens = 0
            for msg in fixed_messages:
                msg["token_count"] = get_token_count(msg["content"])  # Store temporarily
                total_tokens += msg["token_count"]

            # Trim messages if needed (skipping first two messages)
            trimmed_messages = trim_messages(fixed_messages, TOKEN_MAX)

            # **Remove token count before sending to LM Studio**
            for msg in trimmed_messages:
                msg.pop("token_count", None)

            data["messages"] = trimmed_messages

        # Log modified request
        print("\n[Modified Request]:", json.dumps(data, indent=2))

        # Forward request to LM Studio
        headers = {"Content-Type": "application/json"}
        response = requests.post(LM_STUDIO_URL, data=json.dumps(data), headers=headers, stream=not is_chat_title_request)

        # Log the raw response
        print("\n[Streaming Response from LM Studio]" if not is_chat_title_request else "\n[Non-Streaming Response from LM Studio]")

        # **Return response based on streaming mode**
        if is_chat_title_request:
            return jsonify(response.json()), response.status_code  # Return JSON response (non-streaming)
        else:
            return Response(stream_response(response), content_type="text/event-stream")  # Regular streaming

    except Exception as e:
        print("\n[Error]:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=True)
