# Apollo AI (iOS) LM Studio Proxy
A Flask-based proxy for integrating [**Apollo AI: Private & Local AI**](https://apps.apple.com/us/app/apollo-ai-private-local-ai/id6448019325) with [**LM Studio**](https://lmstudio.ai/) via [**ngrok**](https://ngrok.com/). It intercepts and modifies requests, ensuring correct formatting, conversation consistency, and seamless communication between the app and LM Studio.

##

### TL;DR
These scripts allow you to connect to your local network AI **chatbot**, over the internet, with your **iPhone**  😬

## 

### Setup

In the Apollo app, set the prompt to:

	“Here is my iOS metadata dump:”

This ensures that the first message contains reference to your iOS telemetry data if enabled. Otherwise you should leave it blank or use it to fine tune the main prompt.

**Edit** the *promptfile.txt* with your desired prompt information, this will apply to **all** loaded models.
