import os
import sys

from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

# TODO: eventually I'll need to install the actual package
sys.path.append('/home/tgaldes/git/3rdparty/browser-use')

import asyncio

from browser_use import Agent
from browser_use.controller.service import Controller
from browser_use.agent.views import ActionModel, ActionResult
from time import sleep

async def run_browser_use(query: str, max_steps: int):

    # wait action
    class WaitAction(BaseModel):
        seconds: int

    controller = Controller()
    @controller.action('Wait for a given number of seconds.', param_model=WaitAction)
    def wait(params: WaitAction):
        sleep(params.seconds)

    model = ChatOpenAI(model='gpt-4o', temperature=0.3)
    agent = Agent(
        task=query,
        llm=model,
        controller=controller,
    )

    history = await agent.run(max_steps=max_steps)
    actions = [h.model_output.action for h in history if h.model_output and h.model_output.action]
    final_action_model = actions[-1].model_dump(exclude_unset=True)

    if 'done' in final_action_model and 'success' in final_action_model['done']['text'].lower():
        return 0
    return 1

def main():
    rc = asyncio.run(run_browser_use('Navigate to https://www.google.com, then finish unsuccessfully', 4))
    exit(rc)

if __name__ == '__main__':
    main()
