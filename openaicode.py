from openai import OpenAI

def generate_openai_response(api_key, system_message, conversation_history, placeholder_message, bot):
    # Instantiate the OpenAI client with your API key
    client = OpenAI(api_key=api_key)

    # Prepare the messages for the API call
    messages = [{"role": "system", "content": system_message}]
    messages.extend(conversation_history)

    # Create the chat completion
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=messages,
        max_tokens=1024,
        n=1,
        temperature=1,
        stream=True,
    )

    buffer = ""
    response_content = ""
    chunk_size = 50  # Adjust the chunk size as needed
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
### vision

def generate_openai_vision_response(image_url, api_key, vision_prompt, placeholder_message, bot):
    # Instantiate the OpenAI client with your API key
    client = OpenAI(api_key=api_key)

    # Prepare the messages for the API call
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": vision_prompt},
                {"type": "image_url", "image_url": {"url": image_url}},
            ],
        }
    ]

    # Create the chat completion
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=messages,
        max_tokens=1024,
        n=1,
        temperature=1,
        stream=True,
    )

    buffer = ""
    response_content = ""
    chunk_size = 50  # Adjust the chunk size as needed

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