#!/bin/bash

# Define the local port
LMSTUDIO_PORT=1234  # LM Studio Default
PROXY_PORT=5050 # Change if needed

# Start ngrok using --url (since hostname breaks it)
ngrok http --url=<CHANGE-TO-YOUR-FREE-STATIC-URL>.ngrok-free.app $PROXY_PORT
