import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message
from claude import generate_anthropic_response
from openaicode import generate_openai_response, generate_openai_vision_response
from perplexity import generate_perplexity_response

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ALLOWED_USER_IDS = set(os.getenv("ALLOWED_USER_IDS").split(","))
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE")
SYSTEM_MESSAGE_DATE = os.getenv("SYSTEM_MESSAGE_DATE")
SYSTEM_MESSAGE_DATE1 = os.getenv("SYSTEM_MESSAGE_DATE1")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

user_settings = {}
bot = TeleBot(TELEGRAM_BOT_TOKEN)
conversation_history = []
last_interaction_time = datetime.now()
selected_model = "openai"
vision_prompt = "describe, use eloquent and precise language"

def is_authorized(message: Message) -> bool:
    return str(message.from_user.id) in ALLOWED_USER_IDS

def reset_conversation_if_needed() -> None:
    global conversation_history, last_interaction_time
    if datetime.now() - last_interaction_time > timedelta(hours=2):
        conversation_history = []
        last_interaction_time = datetime.now()

def limit_conversation_history() -> None:
    global conversation_history
    max_history = 1 if SYSTEM_MESSAGE in [SYSTEM_MESSAGE_DATE, SYSTEM_MESSAGE_DATE1] else 10
    conversation_history = conversation_history[-max_history:]

def handle_api_error(e: ApiTelegramException, message: Message) -> None:
    if e.error_code == 429:
        retry_after = int(e.result_json['parameters']['retry_after'])
        time.sleep(retry_after)
        handle_message(message)
    else:
        print(f"Error: {e}")

@bot.message_handler(commands=['sm'])
def system_message_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    user_id = message.from_user.id
    options = message.text.split()[1:]

    if not options:
        bot.reply_to(message, "Please provide a system message option: 'standard' or 'play'.")
        return

    option = options[0].lower()

    if option == "standard":
        user_settings[user_id] = user_settings.get(user_id, {})
        user_settings[user_id]['system_message'] = os.getenv("SYSTEM_MESSAGE")
        bot.reply_to(message, "Switched to standard system message.")
    elif option in ["play", "play1"]:
        user_settings[user_id] = user_settings.get(user_id, {})
        user_settings[user_id]['system_message'] = os.getenv(f"SYSTEM_MESSAGE_DATE{'' if option == 'play' else '1'}")
        bot.reply_to(message, "Switched to play system message.")
    else:
        bot.reply_to(message, "Invalid option. Please choose 'standard' or 'play'.")

@bot.message_handler(commands=['start'])
def start_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    bot.reply_to(message, "Hello! I'm your AI coding assistant. How can I help you today?")

@bot.message_handler(commands=['reset'])
def reset_command(message: Message) -> None:
    global conversation_history
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    conversation_history = []
    bot.reply_to(message, "Conversation has been reset.")

@bot.message_handler(commands=['model'])
def model_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    user_id = message.from_user.id
    models = message.text.split()[1:]

    if not models:
        bot.reply_to(message, "Please provide a model name: 'openai', 'claude', or 'perplexity'.")
        return

    model_name = models[0].lower()

    if model_name in ["claude", "perplexity", "openai"]:
        user_settings[user_id] = user_settings.get(user_id, {})
        user_settings[user_id]['selected_model'] = model_name
        bot.reply_to(message, f"Switched to {model_name} model.")
    else:
        bot.reply_to(message, "Invalid model name. Please choose 'openai', 'claude', or 'perplexity'.")

@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    user_id = message.from_user.id
    user_settings[user_id] = user_settings.get(user_id, {})
    selected_model = user_settings[user_id].get('selected_model', "openai")
    system_message = user_settings[user_id].get('system_message', SYSTEM_MESSAGE)

    reset_conversation_if_needed()

    if message.content_type == 'photo':
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        conversation_history.append({"role": "user", "content": image_url})
        if message.caption:
            vision_prompt = message.caption
        else:
            vision_prompt = "describe, use eloquent and precise language"
    else:
        conversation_history.append({"role": "user", "content": message.text})

    limit_conversation_history()
    placeholder_message = bot.send_message(message.chat.id, "Generating...")

    try:
        if selected_model == "claude":
            response_content = generate_anthropic_response(
                ANTHROPIC_API_KEY, system_message, conversation_history, placeholder_message, bot
            )
        elif selected_model == "perplexity":
            response_content = generate_perplexity_response(
                PERPLEXITY_API_KEY, message.text, placeholder_message, bot
            )
        elif selected_model == "openai":
            if message.content_type == 'photo':
                response_content = generate_openai_vision_response(
                    image_url, OPENAI_API_KEY, vision_prompt, placeholder_message, bot
                )
            else:
                response_content = generate_openai_response(
                    OPENAI_API_KEY, system_message, conversation_history, placeholder_message, bot
                )

        conversation_history.append({"role": "assistant", "content": response_content})
        time.sleep(1)
    except ApiTelegramException as e:
        handle_api_error(e, message)

def main() -> None:
    bot.polling()

if __name__ == "__main__":
    main()