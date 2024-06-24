import anthropic
import base64
import requests

def encode_image_to_base64(image_url):
    response = requests.get(image_url)
    return base64.b64encode(response.content).decode('utf-8')

def generate_anthropic_response(api_key, system_message, conversation_history, placeholder_message, bot, image_url=None):
    response_content = ""
    chunk_size = 50  # Adjust the chunk size as needed

    # Convert the conversation history to the format expected by Anthropic
    messages = []
    for i, msg in enumerate(conversation_history):
        if i > 0 and msg['role'] == messages[-1]['role']:
            # If the roles are the same, combine the messages
            if isinstance(messages[-1]['content'], list):
                messages[-1]['content'].extend(msg['content'])
            else:
                messages[-1]['content'] += "\n" + msg['content']
        else:
            if isinstance(msg['content'], list):  # Image message
                image_parts = []
                for part in msg['content']:
                    if part['type'] == 'text':
                        image_parts.append({"type": "text", "text": part['text']})
                    elif part['type'] == 'image_url':
                        base64_image = encode_image_to_base64(part['image_url']['url'])
                        image_parts.append({"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}})
                messages.append({"role": msg["role"], "content": image_parts})
            else:  # Text message
                messages.append({"role": msg["role"], "content": msg["content"]})

    # Add the new image if provided
    if image_url:
        base64_image = encode_image_to_base64(image_url)
        if messages and messages[-1]['role'] == 'user':
            messages[-1]['content'].extend([
                {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                {"type": "text", "text": "What's in this image?"}
            ])
        else:
            messages.append({
                "role": "user",
                "content": [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}},
                    {"type": "text", "text": "What's in this image?"}
                ]
            })

    # Ensure the conversation starts with a user message
    if not messages or messages[0]['role'] != 'user':
        messages.insert(0, {"role": "user", "content": "Hello"})

    with anthropic.Client(api_key=api_key).messages.stream(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1024,
        system=system_message,
        messages=messages,
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