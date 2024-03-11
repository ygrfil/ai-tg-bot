AI Assisintant

Features
Supports multiple AI models: OpenAI, Claude, and Perplexity
Maintains conversation history for context-aware responses
Resets conversation history after 2 hours of inactivity
Limits conversation history to the last 10 messages
Handles rate limiting and retries requests when necessary
Prerequisites
Before running the bot, make sure you have the following:

Python 3.x installed
Required Python packages: telebot, python-dotenv
Telegram bot token obtained from BotFather
API keys for the desired AI models (OpenAI, Anthropic, Perplexity)
Setup
Clone the repository:


Copy code
git clone https://github.com/your-username/ai-coding-assistant-bot.git
Install the required Python packages:


Copy code
pip install -r requirements.txt
Create a .env file in the project directory and provide the necessary environment variables:


Copy code
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PERPLEXITY_API_KEY=your_perplexity_api_key
ALLOWED_USER_IDS=user_id1,user_id2
SYSTEM_MESSAGE=your_system_message
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
Replace the placeholders with your actual values.

Usage
Run the bot:


Copy code
python main.py
Start a conversation with the bot on Telegram.

Use the following commands to interact with the bot:

/start: Start the conversation and receive a welcome message.
/reset: Reset the conversation history.
/model <model_name>: Switch between different AI models (openai, claude, perplexity).
Send your coding-related questions or prompts to the bot, and it will generate responses using the selected AI model.

Customization
Modify the SYSTEM_MESSAGE environment variable to customize the initial message sent by the bot.
Adjust the conversation history limit by modifying the conversation_history[-10:] line in the code.
Customize the response generation logic in the generate_*_response functions according to your specific requirements.