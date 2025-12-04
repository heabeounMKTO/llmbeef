from pydantic import BaseModel
import requests
from typing import List
from dataclasses import dataclass

@dataclass
class Message:
    speaker: str
    content: str
    turn: int

class Beefer(BaseModel):
    """
    stores a generic beefer 
    """
    name: str = None
    base_url: str
    api_key: str = None
    system_prompt: str = None
    def  __init__(self, base_url, system_prompt, name = None, api_key = None, **data):
        super().__init__(base_url=base_url, name=name, api_key=api_key, **data)
        if name is None:
            self.name = "Generic Beefer (Bro have 0 name)"
        else:
            self.name = name
    def generate_beef(self, current_beef, prompt):
        messages = []
        for msg in current_beef:
            messages.append({
                "role": "assistant",
                "content": f"{msg.speaker}: {msg.content}"
            })
        messages.append({"role": "user", "content": prompt})
        try:
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": messages,
                    "max_tokens": 150,
                    "temperature": 0.9
                },
                timeout=3600
            )
            response.raise_for_status()
            data = response.json()
            return data['choices'][0]['message']['content'].strip()
        except Exception as e:
            return f"unable to generate response , error : {e}"
    class Config:
        arbitrary_types_allowed = True

class LLMBeef(BaseModel):
    moderator: Beefer
    debaters: List[Beefer] = []
    messages: List[Message] = []
    turn_count: int = 0

    def __init__(self, moderator):
        self.moderator=moderator

    def add_beefer(self, debater: Beefer):
        self.debaters.append(debater)
    
    async def start_beef(self, topic: str, turns: int = 6):
        mod_prompt = f"Moderate a debate about '{topic}'. Introduce the topic."
