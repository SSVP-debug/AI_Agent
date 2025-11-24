from openai import OpenAI, APIError, BadRequestError, RateLimitError, APIConnectionError
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

def llm_chat(system_prompt, user_prompt, temperature=0.2, max_tokens=1500):
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp.choices[0].message.content

    except BadRequestError as e:
        raise RuntimeError(f"BadRequestError: {e}") from e

    except RateLimitError as e:
        raise RuntimeError("Rate limit hit. Try again later.") from e

    except APIConnectionError as e:
        raise RuntimeError("Network connection error while calling OpenAI API.") from e

    except APIError as e:
        raise RuntimeError(f"OpenAI API error: {e}") from e

    except Exception as e:
        raise RuntimeError(f"Unknown error: {e}") from e
