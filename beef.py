import requests
from typing import List, Dict
from dataclasses import dataclass

@dataclass
class Message:
    speaker: str
    content: str
    turn: int

class Beefer():
    """
    stores a generic beefer 
    """
    def  __init__(self, base_url, system_prompt=None, name=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        if name is None:
            self.name = "Generic Beefer (Bro have 0 name)"
        else:
            self.name = name
            
        if system_prompt is None:
            self.system_prompt = ""
        else:
            self.system_prompt = system_prompt

    def generate_beef(self, current_beef, prompt):
        messages = []
        
        if self.system_prompt:
            messages.append({
                "role": "system",
                "content": self.system_prompt
            })
        
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
            return f"unable to generate response, error: {e}"

class LLMBeef():
    def __init__(self, moderator):
        self.moderator = moderator
        self.debaters: List[Beefer] = []
        self.messages: List[Message] = []
        self.turn_count: int = 0
        self.scores: Dict[str, int] = {}

    def add_beefer(self, debater: Beefer):
        self.debaters.append(debater)
        self.scores[debater.name] = 0
    
    def rating_prompt(self, beefer: Beefer):
        return f"""Rate the argument just made by {beefer.name} on a scale of 1-10.
Consider: logic, persuasiveness, clarity, and engagement with the topic.
Respond with ONLY a number from 1-10, nothing else."""

    async def announce_winner(self, topic: str):
        print("\n" + "="*50)
        print("FINAL SCORES:")
        print("="*50)
        for debater_name, score in self.scores.items():
            print(f"{debater_name}: {score} points")
        winner_name = max(self.scores, key=self.scores.get)
        winner_score = self.scores[winner_name]
        print("\n" + "="*50)
        judgment_prompt = f"""The beef on '{topic}' has concluded.
Final scores: {', '.join([f'{name}: {score}' for name, score in self.scores.items()])}
{winner_name} has the highest score with {winner_score} points.
As moderator, give a brief closing statement declaring the winner and why they won."""
        judgement = self.moderator.generate_beef(self.messages, judgment_prompt)
        print(f"{self.moderator.name}: {judgement}")
        print("="*50 + "\n")

    async def start_beef(self, topic: str, mod_prompt=None, rating_prompt=None, turns: int = 6):
        if mod_prompt is None:
            mod_prompt = f"Moderate a debate about '{topic}'. Introduce the topic."
        
        mod_response = self.moderator.generate_beef(self.messages, mod_prompt)
        self.messages.append(Message(self.moderator.name, mod_response, self.turn_count))
        print(f"{self.moderator.name}: {mod_response}\n")
        self.turn_count += 1
        
        for i in range(turns):
            debater = self.debaters[i % len(self.debaters)]
            deb_prompt = f"""Topic: {topic}
You are {debater.name}.
Complain/argue about this topic, you are allowed to use explicit language (max 100 words)."""
            deb_response = debater.generate_beef(self.messages, deb_prompt)
            self.messages.append(Message(debater.name, deb_response, self.turn_count))
            print(f"{debater.name}: {deb_response}\n")
            self.turn_count += 1
            
            if rating_prompt is None:
                rating_prompt = self.rating_prompt(debater)
            
            rating_response = self.moderator.generate_beef(self.messages, rating_prompt)
            
            try:
                rating = int(''.join(filter(str.isdigit, rating_response)))
                rating = max(1, min(10, rating))
                self.scores[debater.name] += rating
                print(f"[{self.moderator.name} rates {debater.name}: {rating}/10]\n")
            except:
                print(f"[{self.moderator.name} couldn't rate that response]\n")
            
            if i % 2 == 1:
                mod_summary_prompt = f"Topic: {topic}\nModerator: Summarize the recent arguments and redirect the discussion."
                mod_response = self.moderator.generate_beef(self.messages, mod_summary_prompt)
                self.messages.append(Message(self.moderator.name, mod_response, self.turn_count))
                print(f"{self.moderator.name}: {mod_response}\n")
                self.turn_count += 1
        
        await self.announce_winner(topic)
