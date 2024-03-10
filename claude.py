import anthropic

def generate_anthropic_response(api_key, system_message, conversation_history, placeholder_message, bot):
    response_content = ""
    chunk_size = 50  # Adjust the chunk size as needed

    with anthropic.Client(api_key=api_key).messages.stream(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        system=system_message,
        messages=conversation_history,
    ) as stream:
        buffer = ""
        for text in stream.text_stream:
            buffer += text
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