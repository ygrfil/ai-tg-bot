from openai import OpenAI

def generate_perplexity_response(PERPLEXITY_API_KEY, conversation_history, placeholder_message, bot):
    messages = [
        {"role": "system", "content": "You are an AI assistant."},
        *conversation_history,
    ]
    client = OpenAI(api_key=PERPLEXITY_API_KEY, base_url="https://api.perplexity.ai")
    response_stream = client.chat.completions.create(
        model="sonar-medium-online",
        messages=messages,
        stream=True,
    )
    buffer = ""
    response_content = ""
    chunk_size = 50  # Adjust the chunk size as needed
    for chunk in response_stream:
        chunk_text = chunk.choices[0].delta.content or ""
        buffer += chunk_text
        if len(buffer) >= chunk_size:
            response_content += buffer
            bot.edit_message_text(
                response_content,
                chat_id=placeholder_message.chat.id,
                message_id=placeholder_message.message_id,
            )
            buffer = ""
    if buffer:
        response_content += buffer
        bot.edit_message_text(
            response_content,
            chat_id=placeholder_message.chat.id,
            message_id=placeholder_message.message_id,
        )
    return response_content