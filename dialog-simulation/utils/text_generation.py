import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

LM_MAX_TOKENS_DICT = {
    "gpt-3.5-turbo-16k": 16384,
    "gpt-4": 8192
}

# Get OpenAI API key from environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = os.getenv("OPENAI_ORGANIZATION")

def generate(LM, system_prompt, context, max_tokens=512, temperature=0.5, use_openai=True):
    """
    Generates a text completion for a given prompt using either the OpenAI GPT-3 API or the Hugging Face GPT-3 model.
    
    Args:
    - LM (str): The language model to use for text generation.
    - system_prompt (str): The system prompt to establish the identity of the agent, e.g., "You are a helpful assistant."
    - context (list): A list of dicts representing the conversation history, e.g. [{"role": "user", "content": "Hello!"}, {"role": "assistant", "content": "Hi!"}]. Each dict has two keys: "role" (should be either "user" or "assistant") and "content".
    - max_tokens (int): The maximum number of tokens to generate.
    - temperature (float): The temperature to use for text generation. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
    - use_openai (bool): A boolean flag indicating whether to use the OpenAI API (True) or the Hugging Face GPT-3 model (False).

    Returns:
    - str: The generated text completion.
    """
    if use_openai:
        response = openai.ChatCompletion.create(
            model=LM,
            messages=[{"role": "system", "content": system_prompt}] + context,
            max_tokens=max_tokens,
            n=1,
            stop=None,
            temperature=temperature,
        )
        message = response["choices"][0]["message"]
        role = message["role"]
        assert role == "assistant"
        content = message["content"].strip()
        total_tokens_used = response["usage"]["total_tokens"]
        return content, total_tokens_used
    else:
        return NotImplementedError

def get_rating(x):
    """
    Extracts a rating from a string.
    
    Args:
    - x (str): The string to extract the rating from.
    
    Returns:
    - int: The rating extracted from the string, or None if no rating is found.
    """
    nums = [int(i) for i in re.findall(r'\d+', x)]
    if len(nums)>0:
        return min(nums)
    else:
        return None

# Summarize simulation loop with OpenAI GPT-4
def summarize_simulation(LM, log_output):
    prompt = f"Summarize the simulation loop:\n\n{log_output}"
    context = [{"role": "user", "content": prompt}]
    response = generate(LM, system_prompt="", context=context, max_tokens=1024, temperature=0.0)
    return response


if __name__ == "__main__":
    # test generation
    LM = "gpt-3.5-turbo-16k"
    system_prompt = "You are Carson Crimson (he/him), a talented glassblower who owns a small studio in Seattle's Fremont neighborhood. You specialize in creating intricate glass sculptures and jewelry. You are passionate and intense, much like the deep crimson of his favorite color. You're known for his fiery determination and unwavering commitment to his craft. Your mbti is ENTJ and Your star sign is Aries. Your hobbies are competitive rowing, attending glass art workshops."
    context = [{"role": "user", "content": ''' You are participating in a group speed dating event, with 4 men and 4 women in total. In each round, you have 5 minutes to talk to another woman, including a 2-min introduction and a 3-min free chat. Try to decide how much you like each woman in this process and also make an impression of yourself.
    
Now, you are going to meet the first woman, Azealia Azure, a marine biologist who works at a research institute in Port Townsend. She's dedicated to studying the rich marine life of the Puget Sound. She's calm, analytical, and introspective, and embody the tranquility of the azure waters she study. She's a deep thinker and a gentle soul who prefers spending time by the water's edge. Her mbti is INFP and her star sign is Pisces. Her hobbies are playing acoustic guitar, stargazing, writing poetry. 

What do you want to say to Azealia?
(Say your part in the format of Carson: "{your response}". Don't try to play Azealia.)'''}
               ]
    msg, tokens_used = generate(LM, system_prompt, context)
    print(msg, tokens_used)

