# Apollo AI (iOS) LM Studio Proxy
Apollo AI LM Studio Proxy: A Flask-based proxy for integrating [**Apollo AI: Private & Local AI**](https://apps.apple.com/us/app/apollo-ai-private-local-ai/id6448019325) with [**LM Studio**](https://lmstudio.ai/) via [**ngrok**](https://ngrok.com/). It intercepts and modifies requests, ensuring correct formatting, conversation consistency, and seamless communication between the app and LM Studio.


## Setup

In the Apollo app, set the prompt to:

	“Here is my iOS metadata dump:”

This ensures that the first message contains reference to your iOS telemetry data if enabled. Otherwise you should leave it blank.
