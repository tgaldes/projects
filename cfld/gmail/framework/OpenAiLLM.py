from openai import OpenAI
import os

class OpenAiLLM:
    # TODO: both of these
    def __init__(self, api_key_path="/home/tgaldes/Dropbox/Fraternity PM/dev_private/cfldv1_open_api_key.txt", system_background="You work at a property management company that leases out rooms to college students. Answer prospective tenant inquiries about vacancies and other questions they may have. Any new paragraphs in the response you give should be separated by '<br><br>'. Add one at the end of your response as well."):
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

        # TODO
        assistant_emails = ['tyler@cleanfloorslockingdoors.com', 'apply@cleanfloorslockingdoors.com', 'apply@cf-ld.com', 'tyler@cf-ld.com', 'lee@cf-ld.com', 'lee@cleanfloorslockingdoors.com']

        roles = []
        for email, message in zip(emails, messages):
            if email in assistant_emails:
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


