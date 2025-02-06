from openai import OpenAI
import time
import re
import json
import os

def send_answer(text):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(
        api_key=openai_api_key
    )

    with open('assistant_key.json', 'r') as file:
        data = json.load(file)

    assistant = client.beta.assistants.retrieve(data['assistant_key'])

    thread = client.beta.threads.create()

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=text
    )

    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
        instructions="Please search in the file present in the vector and give me only my answer without any other word, and give back an appropriate reply if you cant find an accurate information"
    )

    while True:
        run_status = client.beta.threads.runs.retrieve(thread_id=thread.id,
                                                       run_id=run.id)
        if run_status.status == "completed":
            break
        elif run_status.status == "failed":
            print("Run failed:", run_status.last_error)
            break
        time.sleep(1)

    messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )

    number_of_messages = len(messages.data)

    for message in reversed(messages.data):
        role = message.role
        for content in message.content:
            if content.type == 'text':
                if role == 'assistant': 
                    response = content.text.value
                    pattern = r'【\d:\d†.*?】'
                    cleaned_text = re.sub(pattern, '', response)
                    print(f'\n{role}: {cleaned_text}')
                    return cleaned_text
