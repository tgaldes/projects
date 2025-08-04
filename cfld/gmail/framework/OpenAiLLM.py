from openai import OpenAI
import pdb
import os
from framework.Config import Config

from bs4 import BeautifulSoup
import re


def extract_meaningful_text_from_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")

    # Remove non-content tags
    for tag in soup(["script", "style", "img", "meta", "link", "title", "head", "footer"]):
        tag.decompose()

    body = soup.body or soup
    text = body.get_text(separator="\n", strip=True)

    lines = text.splitlines()
    cleaned_lines = []

    boilerplate_patterns = [
        r"^Send application$",
        r"^You can reply directly.*$",
        r"^Or see .*$",
        r"^Use our online application.*$",
        r"^About .*?$",
        r"^Reminder:$",
        r".*Fair Housing Act.*",
        r".*voucher assistance programs.*",
        r".*Respectful Renting Pledge.*",
        r"^Other helpful links$",
        r"^Found a tenant.*$",
        r"^Report spam$",
        r"^Privacy policy$",
        r"^Update your preferences$",
        r"^Download the free Zillow Rental Manager app$",
        r"^Manage this listing.*$",
        r"^Additional laws in your area.*$",
        r"Section 8",
        r"^Add photos and get notifications.*$",
        r"^\d{4}.*Avenue.*$",  # address lines
        r"^© \d{4}-\d{4}$",
        r"^FAQ page$",
        r"^Customer Support.*$",
        r".*phone contact info.*",
        r".*\bFREE\b.*for landlords.*",
        r".*prohibits housing discrimination.*",
        r".*the basics of fair housing laws.*",
        r"^Is this inquiry spam\?$",
        r".*Have questions or need help.*",
        r".*contact Customer Support.*",
        r"^Seattle, WA \d{5}$",
        r"^Rental application$",
        r"^The federal$",
        r"^Learn more about$",
        r"^and$",
        r"^Credit report$",
        r"^Background check$",
        r".*Learn more about our online applications.*",
        r"^Questions\?$",
        r"^.*Zillow.*$",  # any general Zillow-related text
    ]

    for line in lines:
        line = line.strip()
        if not line:
            continue
        if any(re.search(p, line, re.IGNORECASE) for p in boilerplate_patterns):
            continue
        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()

class OpenAiLLM:
    def __init__(self, system_background, example_threads=None):
        api_key_path = Config()['open_ai_api_key_path']
        with open(api_key_path) as f:
            api_key = f.read().strip()
        os.environ["OPENAI_API_KEY"] = api_key
        self.client = OpenAI()

        # add system background to the messages
        self.system_message = self.build_system_message(system_background, example_threads)
        print("System message built:", self.system_message)
        self.system_message_json = {"role": "system", "content": ''}

    def build_system_message(self, base_prompt, example_threads):
        if not example_threads:
            return base_prompt

        example_texts = []
        for i, thread in enumerate(example_threads):
            roles = self.convert_thread_to_user_and_assitant_roles(thread)
            conversation_lines = []
            for role in roles:
                prefix = "User:" if role["role"] == "user" else "Assistant:"
                conversation_lines.append(f"{prefix} {role['content']}")
            example_texts.append(f"Example Conversation {i + 1}:\n" + "\n".join(conversation_lines))

        examples_combined = "\n\n".join(example_texts)
        extended_prompt =  ["Here are some example conversations:"] + example_texts + base_prompt
        return extended_prompt


    def convert_thread_to_user_and_assitant_roles(self, thread):
        emails = thread.get_thread_emails()
        messages = thread.get_thread_messages()

        assistant_domains = ['cleanfloorslockingdoors.com', 'cf-ld.com']
        user_auto_email = 'wordpress@cleanfloorslockingdoors.com'

        roles = []
        for email, message in zip(emails, messages):
            # replace all newline newlines with '<br><br>'
            message = message.replace('\r\n', '<br>')
            # These were inserted when we moved to a newline with text wrapping, so we don't want them in the training data
            message = message.replace('\n', '')
            if email == user_auto_email:
                roles.append({"role": "user", "content": message}) # don't need to filter these messages
            elif email.split('@')[1] in assistant_domains:
                roles.append({"role": "assistant", "content": message})
            else:
                roles.append({"role": "user", "content": extract_meaningful_text_from_html(message)})
        return roles

    def add_subject_to_system_background(self, thread):
        subject = thread.subject()
        self.system_message_json['content'] = ' '.join(self.system_message) + '\n The subject of the current email thread is: ' + subject

    def generate_response(self, thread):
        roles = self.convert_thread_to_user_and_assitant_roles(thread)
        self.add_subject_to_system_background(thread)
        messages = [self.system_message_json] + roles
        completion = self.client.chat.completions.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message.content.replace('\n', '<br>')


