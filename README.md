# AI Coding Assistant Bot

The AI Coding Assistant Bot leverages the power of cutting-edge AI models to provide context-aware responses to coding-related queries directly within Telegram. Built for developers, enthusiasts, and students alike, this bot introduces a convenient and interactive way to solve programming challenges.

## Features

- **Multiple AI Models Support**: Choose from OpenAI, Claude, and Perplexity for varied responses.
- **Context-Aware Conversations**: Maintains a history of the last 10 messages for personalized and relevant replies.
- **Auto-Reset**: Automatically resets conversation history after 2 hours of inactivity for privacy.
- **Rate Limit Handling**: Smartly manages API requests, with retries implemented for occasional rate limits.

## Prerequisites

To get started with the AI Coding Assistant Bot, ensure you have the following:

- Python 3.x
- Required Python Packages: `telebot`, `python-dotenv`
- A Telegram bot token (obtainable from BotFather)
- API keys for the desired AI models (OpenAI, Anthropic, Perplexity)

## Setup

### Clone the Repository

```bash
git clone https://github.com/your-username/ai-coding-assistant-bot.git
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project directory with the following:

```plaintext
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
PERPLEXITY_API_KEY=your_perplexity_api_key
ALLOWED_USER_IDS=user_id1,user_id2
SYSTEM_MESSAGE=your_system_message
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

Replace placeholder values with your actual API keys and bot token.

## Usage

1. **Start the Bot**

   ```bash
   python main.py
   ```

2. **Interact on Telegram**

   - `/start`: Initialize the chat and receive a welcome message.
   - `/reset`: Clear your conversation history.
   - `/model <model_name>`: Switch AI models (`openai`, `claude`, `perplexity`).

Send your coding queries or prompts, and the bot will generate insightful responses using the chosen AI model.

## Customization

- **Initial Message**: Modify the `SYSTEM_MESSAGE` environment variable in your `.env` file to change the bot's initial greeting.
- **History Limit**: Adjust the conversation history limit by editing `conversation_history[-10:]` in the code.
- **Response Logic**: Tailor the `generate_*_response` functions to fine-tune response generation as per your requirements.
