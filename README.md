# Apollo AI to LM Studio Proxy Bridge

Lightweight Flask middleware that routes iOS chat requests through a local LLM inference server via ngrok tunneling. Handles API translation, prompt injection, and conversation state consistency.

## Problem
Mobile AI clients often lack native support for local inference backends. This proxy bridges the gap by translating standard OpenAI-compatible payloads to match LM Studio endpoints.

## Architecture
iOS Client -> ngrok Tunnel -> Flask Proxy (request interception/payload reformatting) -> Localhost:1234 (LM Studio)

The proxy intercepts incoming requests, modifies headers and payload structure for endpoint compatibility, injects custom system prompts from a local file, and maintains conversation history across sessions.

## Setup
1. Install dependencies: `pip install flask requests`
2. Start ngrok tunnel to your LM Studio port: `ngrok http 1234`
3. Update the proxy base URL in Apollo AI settings with your ngrok endpoint
4. Run the server: `python app.py`

## Configuration
- Edit `promptfile.txt` for system prompt injection
- Adjust timeout values and retry logic in `config.py` as needed
- Authentication tokens can be passed via request headers or environment variables

## External Tools
- [Apollo AI](https://apps.apple.com/app/apollo-ai-chat/id1574928630) (iOS client)
- [LM Studio](https://lmstudio.ai/) (Local inference server)
- [ngrok](https://ngrok.com/) (Tunneling service)

## Tech Stack
Python, Flask, OpenAI API format, ngrok tunneling, JSON payload manipulation

## Usage Notes
The proxy runs statelessly. Conversation history is managed by the client application and forwarded with each request. Prompt injection applies to every session unless overridden in the payload.