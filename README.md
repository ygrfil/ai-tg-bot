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

# Quick Start Guide to Deploy AI Coding Assistant Bot with Docker Compose

Quickly deploy your AI Coding Assistant Bot using Docker Compose, utilizing the latest features for an efficient and straightforward setup process.

## Prerequisites

- Ensure you have the latest versions of **Docker** and **Docker Compose** installed on your system. You can download and install these from the [official Docker website](https://docs.docker.com/get-docker/).

## Steps

### 1. Prepare Your Docker Compose File

use `docker-compose.yml` . This file defines your bot service and sets it up to run in a Docker container:



### 2. Deploy with Docker Compose

With the `docker-compose.yml` ready, open a terminal/command prompt, and navigate to your project directory. Deploy your bot by executing:

```bash
docker compose up -d
```

Notice the use of `docker compose` (without the hyphen) reflecting recent syntax updates in newer Docker versions.

### 3. Verify the Deployment

To check the status of your bot and ensure it's running as expected, view the logs by running:

```bash
docker compose logs
```

This command shows the output from your bot, including any startup messages or errors.

## Stopping the Bot

When you need to stop the bot, use the following command in the same directory as your `docker-compose.yml`:

```bash
docker compose down
```

This will stop and remove the containers created for your bot.

---

