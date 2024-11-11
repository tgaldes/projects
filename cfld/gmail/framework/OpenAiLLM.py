from openai import OpenAI
import os
import pdb

class OpenAiLLM:
    def __init__(self, system_background, api_key_path="/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_open_api_key.txt"):
        with open(api_key_path) as f:
            api_key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()

        self.system_background = system_background
        # add system background to the messages
        self.system_message = {"role": "system", "content": system_background}

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

    def generate_response(self, thread):
        roles = self.convert_thread_to_user_and_assitant_roles(thread)
        messages = [self.system_message] + roles
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content


