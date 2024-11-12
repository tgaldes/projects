from openai import OpenAI
import os
from framework.Config import Config

class OpenAiLLM:
    def __init__(self, system_background):
        api_key_path = Config()['open_ai_api_key_path']
        with open(api_key_path) as f:
            api_key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()

        self.system_background = system_background
        # add system background to the messages
        self.system_message = system_background
        self.system_message_json = {"role": "system", "content": system_background}

    def convert_thread_to_user_and_assitant_roles(self, thread):
        emails = thread.get_thread_emails()
        messages = thread.get_thread_messages()

        assistant_domains = ['@cleanfloorslockingdoors.com', '@cf-ld.com']

        roles = []
        for email, message in zip(emails, messages):
            if email.split('@')[1] in assistant_domains:
                roles.append({"role": "assistant", "content": message})
            else:
                roles.append({"role": "user", "content": message})
        return roles

    def add_subject_to_system_background(self, thread):
        subject = thread.subject()
        self.system_message_json['content'] = self.system_message + '\n The subject of the current email thread is: ' + subject

    def generate_response(self, thread):
        roles = self.convert_thread_to_user_and_assitant_roles(thread)
        self.add_subject_to_system_background(thread)
        messages = [self.system_message_json] + roles
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content


