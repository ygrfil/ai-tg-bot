```markdown
# AI-Powered Telegram Bot

This Telegram bot leverages multiple AI models to provide various functionalities, including text generation, image description, and image creation. It supports OpenAI, Perplexity, Groq, Claude, and TensorArt models.

## Features

- Multi-model support: OpenAI, Perplexity, Groq, Claude, and TensorArt
- Conversation memory with automatic reset after 2 hours of inactivity
- Image processing capabilities
- Customizable system messages to set AI behavior and context
- User authorization system
- Conversation summarization
- SQLite database for storing user preferences

## Commands

- `/start`: Introduces the bot and explains available commands
- `/model`: Select the AI model to use
- `/tensorart`: Generate images using TensorArt (provide a prompt)
- `/sm`: Select a system message to set AI behavior and context
- `/reset`: Reset the conversation history
- `/summarize`: Summarize the current conversation

## Setup

1. Clone the repository
2. Install required packages: `pip install -r requirements.txt`
3. Create a `.env` file with the following variables:
   ```
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   PERPLEXITY_API_KEY=your_perplexity_api_key
   ALLOWED_USER_IDS=comma_separated_user_ids
   SYSTEM_MESSAGE=your_default_system_message
   SYSTEM_MESSAGE_DATE=your_date_system_message
   SYSTEM_MESSAGE_SDXL=your_sdxl_system_message
   SYSTEM_MESSAGE_SDXL1=your_sdxl1_system_message
   SYSTEM_MESSAGE_GERMAN=your_german_system_message
   ANTHROPIC_API_KEY=your_anthropic_api_key
   OPENAI_API_KEY=your_openai_api_key
   GROQ_API_KEY=your_groq_api_key
   ```
4. Run the bot: `python main.py`

## Dependencies

- python-telegram-bot
- python-dotenv
- requests
- anthropic
- openai
- groq

```
