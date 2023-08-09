import openai
import re
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

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
        return message
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
    LM = "gpt-4"
    system_prompt = "You are Violet, an comic book writer."
    context = [{"role": "user", "content": "Hello! What's your name?"},
               {"role": "assistant", "content": "Hi! I'm Violet."},
               {"role": "user", "content": "Nice to meet you, Violet. I'm John. What do you do for a living?"},
               ]
    response = generate(LM, system_prompt, context)
    print(response)

