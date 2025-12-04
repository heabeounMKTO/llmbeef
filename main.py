from beef import LLMBeef, Beefer
import asyncio

if __name__ == "__main__":
    moderator = Beefer(base_url="http://192.168.231.52:9997", name="The judge",
                       system_prompt="You are a debate moderator. Keep things civil but let the debaters get spicy. You roast the debaters every chance you get",
                       api_key=None)
    beef = LLMBeef(moderator=moderator)
    qwen3_4b = Beefer(base_url="http://0.0.0.0:7000", 
                      name="bigger qwen", 
                      system_prompt="You're a creative professional worried about AI replacing human creativity.") 
    qwen2_1_5b = Beefer(base_url="http://0.0.0.0:7001", 
                        name="smol qwen", 
                        system_prompt="You're an annoying retard tech enthusiast who will take the opposite stance of whatever your opponent is taking") 
    beef.add_beefer(qwen3_4b)
    beef.add_beefer(qwen2_1_5b)
    asyncio.run(beef.start_beef("Ai is not all that important lmao"))
