import os
import time
import sqlite3
from contextlib import closing
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telebot import TeleBot
from telebot.apihelper import ApiTelegramException
from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from claude import generate_anthropic_response
from openaicode import generate_openai_response
from perplexity import generate_perplexity_response
from groqcode import generate_groq_response
from tensorart import generate_tensorart_image

load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
ALLOWED_USER_IDS = set(os.getenv("ALLOWED_USER_IDS").split(","))
SYSTEM_MESSAGE = os.getenv("SYSTEM_MESSAGE")
SYSTEM_MESSAGE_DATE = os.getenv("SYSTEM_MESSAGE_DATE")
SYSTEM_MESSAGE_SDXL = os.getenv("SYSTEM_MESSAGE_SDXL")
SYSTEM_MESSAGE_SDXL1 = os.getenv("SYSTEM_MESSAGE_SDXL1")
SYSTEM_MESSAGE_GERMAN = os.getenv("SYSTEM_MESSAGE_GERMAN")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

bot = TeleBot(TELEGRAM_BOT_TOKEN)
user_conversation_history = {}
last_interaction_time = {}
vision_prompt = "describe, use eloquent and precise language"

def init_db():
    with closing(sqlite3.connect('user_preferences.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    user_id INTEGER PRIMARY KEY,
                    selected_model TEXT,
                    system_message TEXT
                )
            ''')
        conn.commit()

def get_user_preferences(user_id):
    with closing(sqlite3.connect('user_preferences.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('SELECT selected_model, system_message FROM user_preferences WHERE user_id = ?', (user_id,))
            result = cursor.fetchone()
            if result:
                return {'selected_model': result[0], 'system_message': result[1]}
            return None

def save_user_preferences(user_id, selected_model, system_message):
    with closing(sqlite3.connect('user_preferences.db')) as conn:
        with closing(conn.cursor()) as cursor:
            cursor.execute('''
                INSERT OR REPLACE INTO user_preferences (user_id, selected_model, system_message)
                VALUES (?, ?, ?)
            ''', (user_id, selected_model, system_message))
        conn.commit()

def ensure_user_preferences(user_id):
    user_prefs = get_user_preferences(user_id)
    if user_prefs is None:
        save_user_preferences(user_id, 'claude', SYSTEM_MESSAGE)

def is_authorized(message: Message) -> bool:
    return str(message.from_user.id) in ALLOWED_USER_IDS

def reset_conversation_if_needed(user_id: int) -> None:
    if datetime.now() - last_interaction_time.get(user_id, datetime.min) > timedelta(hours=2):
        user_conversation_history[user_id] = []
    last_interaction_time[user_id] = datetime.now()

def limit_conversation_history(user_id: int, system_message: str) -> None:
    max_history = 1 if system_message in [SYSTEM_MESSAGE_DATE, SYSTEM_MESSAGE_SDXL, SYSTEM_MESSAGE_SDXL1] else 10
    user_conversation_history[user_id] = user_conversation_history[user_id][-max_history:]

def handle_api_error(e: ApiTelegramException, message: Message) -> None:
    if e.error_code == 429:
        retry_after = int(e.result_json['parameters']['retry_after'])
        time.sleep(retry_after)
        handle_message(message)
    else:
        print(f"Error: {e}")

def create_model_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("OpenAI", callback_data="model_openai"),
                 InlineKeyboardButton("Perplexity", callback_data="model_perplexity"),
                 InlineKeyboardButton("Groq", callback_data="model_groq"),
                 InlineKeyboardButton("Claude", callback_data="model_claude"),
                 InlineKeyboardButton("TensorArt", callback_data="model_tensorart"))
    return keyboard

def create_system_message_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Standard", callback_data="sm_standard"),
                 InlineKeyboardButton("Play", callback_data="sm_play"),
                 InlineKeyboardButton("Image", callback_data="sm_image"),
                 InlineKeyboardButton("Image1", callback_data="sm_image1"),
                 InlineKeyboardButton("DE", callback_data="sm_de"))
    return keyboard

@bot.message_handler(commands=['model'])
def model_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    bot.send_message(message.chat.id, "Select a model:", reply_markup=create_model_keyboard())

@bot.message_handler(commands=['tensorart'])
def tensorart_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    bot.reply_to(message, "Please provide a prompt for generating an image.")

@bot.message_handler(func=lambda message: get_user_preferences(message.from_user.id) is not None and get_user_preferences(message.from_user.id).get('selected_model') == 'tensorart')
def handle_tensorart_message(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    placeholder_message = bot.send_message(message.chat.id, "Generating image...")

    try:
        image_url = generate_tensorart_image(message.text)
        bot.send_photo(message.chat.id, photo=image_url)
    except ApiTelegramException as e:
        handle_api_error(e, message)
    finally:
        bot.delete_message(message.chat.id, placeholder_message.message_id)

@bot.message_handler(commands=['sm'])
def system_message_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    bot.send_message(message.chat.id, "Select a system message:", reply_markup=create_system_message_keyboard())

@bot.callback_query_handler(func=lambda call: call.data.startswith('model_'))
def model_callback(call) -> None:
    user_id = call.from_user.id
    model_name = call.data.split('_')[1]

    ensure_user_preferences(user_id)
    user_prefs = get_user_preferences(user_id) or {}
    user_prefs['selected_model'] = model_name
    save_user_preferences(user_id, model_name, user_prefs.get('system_message', SYSTEM_MESSAGE))

    bot.answer_callback_query(call.id, f"Switched to {model_name} model.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.callback_query_handler(func=lambda call: call.data.startswith('sm_'))
def system_message_callback(call) -> None:
    user_id = call.from_user.id
    option = call.data.split('_')[1]

    ensure_user_preferences(user_id)
    user_prefs = get_user_preferences(user_id) or {}

    if option == "standard":
        system_message = SYSTEM_MESSAGE
    elif option == "play":
        system_message = SYSTEM_MESSAGE_DATE
    elif option == "image":
        system_message = SYSTEM_MESSAGE_SDXL
    elif option == "image1":
        system_message = SYSTEM_MESSAGE_SDXL1
    elif option == "de":
        system_message = SYSTEM_MESSAGE_GERMAN

    user_prefs['system_message'] = system_message
    save_user_preferences(user_id, user_prefs.get('selected_model', 'openai'), system_message)

    bot.answer_callback_query(call.id, f"Switched to {option} system message.")
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)

@bot.message_handler(commands=['start'])
def start_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    bot.reply_to(message, "Welcome! Here are the available commands:\n"
                          "/start: Introduces the bot and explains the available AI models.\n"
                          "/model: Select the AI model (OpenAI, Perplexity, Groq, Claude, or TensorArt).\n"
                          "/tensorart: Generate images using TensorArt (provide a prompt).\n"
                          "/sm: Select a system message to set the AI behavior and context.\n"
                          "/reset: Reset the conversation history.\n"
                          "/summarize: Summarize the current conversation.\n"
                          "Created by Yegor")

@bot.message_handler(commands=['reset'])
def reset_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    user_id = message.from_user.id
    user_conversation_history[user_id] = []
    bot.reply_to(message, "Conversation has been reset.")

def summarize_conversation(conversation_history, api_key):
    summary_prompt = "Summarize the following conversation concisely:"
    for message in conversation_history:
        summary_prompt += f"\n{message['role'].capitalize()}: {message['content']}"
    
    summary = generate_openai_response(
        api_key,
        "You are a helpful assistant that summarizes conversations.",
        [{"role": "user", "content": summary_prompt}],
        None,
        None
    )
    return summary

@bot.message_handler(commands=['summarize'])
def summarize_command(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)
    user_id = message.from_user.id
    if user_id not in user_conversation_history or not user_conversation_history[user_id]:
        bot.reply_to(message, "There's no conversation to summarize.")
        return

    placeholder_message = bot.send_message(message.chat.id, "Generating summary...")
    summary = summarize_conversation(user_conversation_history[user_id], OPENAI_API_KEY)
    bot.edit_message_text(summary, chat_id=message.chat.id, message_id=placeholder_message.message_id)

@bot.message_handler(content_types=['text', 'photo'])
def handle_message(message: Message) -> None:
    if not is_authorized(message):
        bot.reply_to(message, "Sorry, you are not authorized to use this bot.")
        return

    ensure_user_preferences(message.from_user.id)

    user_id = message.from_user.id
    user_prefs = get_user_preferences(user_id) or {}
    selected_model = user_prefs.get('selected_model', "openai")
    system_message = user_prefs.get('system_message', SYSTEM_MESSAGE)

    reset_conversation_if_needed(user_id)

    image_url = None
    if message.content_type == 'photo':
        photo = message.photo[-1]
        file_info = bot.get_file(photo.file_id)
        image_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
        user_conversation_history.setdefault(user_id, []).append({
            "role": "user",
            "content": [
                {"type": "text", "text": message.caption},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        })
    else:
        user_conversation_history.setdefault(user_id, []).append({"role": "user", "content": message.text})

    limit_conversation_history(user_id, system_message)
    placeholder_message = bot.send_message(message.chat.id, "Generating...")

    try:
        if selected_model == "perplexity":
            response_content = generate_perplexity_response(
                PERPLEXITY_API_KEY, message.text, placeholder_message, bot
            )
        elif selected_model == "openai":
            response_content = generate_openai_response(
                OPENAI_API_KEY, system_message, user_conversation_history[user_id], placeholder_message, bot, image_url
            )
        elif selected_model == "groq":
            response_content = generate_groq_response(
                GROQ_API_KEY, system_message, user_conversation_history[user_id], placeholder_message, bot
            )
        elif selected_model == "claude":
            response_content = generate_anthropic_response(
        ANTHROPIC_API_KEY, system_message, user_conversation_history[user_id], placeholder_message, bot, image_url
            )

        user_conversation_history[user_id].append({"role": "assistant", "content": response_content})
        time.sleep(1)
    except ApiTelegramException as e:
        handle_api_error(e, message)

def main() -> None:
    init_db()
    bot.polling()

if __name__ == "__main__":
    main()