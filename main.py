from beef import LLMBeef, Beefer

if __name__ == "__main__":
    moderator = Beefer(base_url="http://192.168.231.52:9997", name="the judge", system_prompt=None, api_key=None)
    beef = LLMBeef(moderator=moderator)
    
