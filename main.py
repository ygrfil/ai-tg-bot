import os
from telebot import TeleBot
from telebot.types import Message
from dotenv import load_dotenv
from datetime import datetime, timedelta
from perplexity import generate_perplexity_response
from claude import generate_anthropic_response
from openaicode import generate_openai_response
import time
from telebot.apihelper import ApiTelegramException
# Load environment variables from .env file
load_dotenv()

# Retrieve the Telegram bot token, Anthropic API key, Perplexity API key, allowed user IDs, and system message from environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ALLOWED_USER_IDS = os.getenv("ALLOWED_USER_IDS").split(",")
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the TeleBot instance
bot = TeleBot(TELEGRAM_BOT_TOKEN)

# Initialize the conversation history, last interaction time, and selected model
conversation_history = []
last_interaction_time = datetime.now()
selected_model = "openai"

@bot.message_handler(commands=['start'])
def start_command(message: Message) -> None:
    if str(message.from_user.id) not in ALLOWED_USER_IDS:
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return
    bot.reply_to(message, "Hello! I'm your AI coding assistant. How can I help you today?")

@bot.message_handler(commands=['reset'])
def reset_command(message: Message) -> None:
    if str(message.from_user.id) not in ALLOWED_USER_IDS:
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return
    global conversation_history
    conversation_history = []
    bot.reply_to(message, "Conversation has been reset.")

@bot.message_handler(commands=['model'])
def model_command(message: Message) -> None:
    if str(message.from_user.id) not in ALLOWED_USER_IDS:
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return
    global selected_model
    if len(message.text.split()) == 1:
        bot.reply_to(message, "Please provide a model name: 'openai' 'claude' or 'perplexity'.")
        return
    model_name = message.text.split()[1].lower()
    if model_name == "claude":
        selected_model = "claude"
        bot.reply_to(message, "Switched to claude model.")
    elif model_name == "perplexity":
        selected_model = "perplexity"
        bot.reply_to(message, "Switched to Perplexity model.")
    elif model_name == "openai":
        selected_model = "openai"
        bot.reply_to(message, "Switched to OpenAI model.")
    else:
        bot.reply_to(message, "Invalid model name. Please choose 'openai', 'claude' or 'perplexity'.")

@bot.message_handler(func=lambda message: True)
def handle_message(message: Message) -> None:
    if str(message.from_user.id) not in ALLOWED_USER_IDS:
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return
    global conversation_history, last_interaction_time, selected_model
    # Check if 2 hours have passed since the last interaction
    current_time = datetime.now()
    if current_time - last_interaction_time > timedelta(hours=2):
        conversation_history = []
    # Update the last interaction time
    last_interaction_time = current_time
    # Add user's message to the conversation history
    conversation_history.append({"role": "user", "content": message.text})
    # Limit the conversation history to the last 10 messages
    conversation_history = conversation_history[-10:]
    # Send a placeholder message to indicate that the bot is typing
    placeholder_message = bot.send_message(message.chat.id, "Generating...")
    try:
        if selected_model == "claude":
            response_content = generate_anthropic_response(
                ANTHROPIC_API_KEY, SYSTEM_MESSAGE, conversation_history, placeholder_message, bot
            )
            conversation_history.append({"role": "assistant", "content": response_content})
        elif selected_model == "perplexity":
            response_content = generate_perplexity_response(
                PERPLEXITY_API_KEY, conversation_history, placeholder_message, bot
            )
            conversation_history.append({"role": "assistant", "content": response_content})
        elif selected_model == "openai":
            response_content = generate_openai_response(
                OPENAI_API_KEY, SYSTEM_MESSAGE, conversation_history, placeholder_message, bot
            )
            conversation_history.append({"role": "assistant", "content": response_content})

        # Add a small delay between requests to avoid hitting rate limits
        time.sleep(1)
    except ApiTelegramException as e:
        if e.error_code == 429:
            # Handle "Too Many Requests" error
            retry_after = int(e.result_json['parameters']['retry_after'])
            time.sleep(retry_after)
            # Retry the request
            handle_message(message)
        else:
            # Handle other types of errors
            print(f"Error: {e}")
def main() -> None:
    # Start the bot
    bot.polling()

if __name__ == "__main__":
    main()