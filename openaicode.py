from openai import OpenAI

def generate_openai_response(api_key, system_message, conversation_history, placeholder_message, bot, image_url=None):
    client = OpenAI(api_key=api_key)

    messages = [{"role": "system", "content": system_message}]
    
    for msg in conversation_history:
        if isinstance(msg['content'], list):  # Image message
            messages.append(msg)
        else:  # Text message
            messages.append({"role": msg["role"], "content": msg["content"]})

    if image_url:
        messages.append({
            "role": "user",
            "content": [
   #             {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        })

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=1024,
        n=1,
        temperature=1,
        stream=True,
    )

    buffer = ""
    response_content = ""
    chunk_size = 50

    for chunk in response:
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