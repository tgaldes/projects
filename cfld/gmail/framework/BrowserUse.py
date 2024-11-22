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
    controller = Controller()

    # wait action
    class WaitAction(BaseModel):
        seconds: int

    @controller.action('Wait for a given number of seconds.', param_model=WaitAction)
    def wait(params: WaitAction):
        sleep(params.seconds)

    # finished unsuccessfully action
    class DoneUnsuccessfullyAction(BaseModel):
        text: str

    @controller.action('Were not able to complete the task, so finish at the current step unsuccessfully.', param_model=DoneUnsuccessfullyAction)
    def done_unsuccessfully(params: DoneUnsuccessfullyAction) -> ActionResult:
        print(params.text)
        return ActionResult(is_done=True)

    model = ChatOpenAI(model='gpt-4o', temperature=0.3)
    agent = Agent(
        task=query,
        llm=model,
        controller=controller,
    )

    history = await agent.run(max_steps=max_steps)
    actions = [h.model_output.action for h in history if h.model_output and h.model_output.action]
    action_names = [list(action.model_dump(exclude_unset=True).keys())[0] for action in actions]

    if 'done_unsuccessfully' in action_names:
        return 1
    return 0
def main():
    rc = asyncio.run(run_browser_use('Navigate to https://www.google.com, then finish unsuccessfully', 4))
    exit(rc)

if __name__ == '__main__':
    main()
