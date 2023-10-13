import os
import requests
import openai
from page import get_page_content
import tiktoken


# Add your Bing Search V7 and OpenAI GPT-3 subscription keys to your environment variables.
bing_subscription_key = os.environ.get("BING_SEARCH_V7_SUBSCRIPTION_KEY")
openai_api_key = os.environ.get('OPENAI_API_KEY')



if bing_subscription_key is None:
    raise ValueError(
        "Bing API key (BING_SEARCH_V7_SUBSCRIPTION_KEY) is not set in environment variables!"
    )
if openai_api_key is None:
    raise ValueError(
        "OpenAI API key (OPENAI_API_KEY) is not set in environment variables!"
    )


# Ensure API keys are available
if not bing_subscription_key or not openai_api_key:
    raise ValueError("API keys for Bing or OpenAI are missing!")

# Initialize OpenAI API client
openai.api_key = openai_api_key


def get_bing_search_results(query, mkt="fr-FR", count=3):
    params = {"q": query, "mkt": mkt, "count": count}
    headers = {"Ocp-Apim-Subscription-Key": bing_subscription_key}
    try:
        response = requests.get(
            "https://api.bing.microsoft.com/v7.0/search", headers=headers, params=params
        )
        response.raise_for_status()
        results = response.json()

        names, URLs, snippets = [], [], []

        if "webPages" in results and "value" in results["webPages"]:
            for item in results["webPages"]["value"]:
                names.append(item["name"])
                URLs.append(item["url"])
                snippets.append(item["snippet"])

        return names, URLs, snippets

    except Exception as ex:
        # Make sure to handle the exception appropriately
        # For instance, log the error or print it
        print(f"An error occurred: {str(ex)}")
        return None, None, None


def query_gpt_3(prompt, model="gpt-3.5-turbo-0613", max_tokens=1000):
    try:
        response = openai.Completion.create(
            engine=model, prompt=prompt, max_tokens=max_tokens
        )
        message = response.choices[0].text.strip()
        return message
    except Exception as ex:
        return f"An error occurred while querying GPT-3: {str(ex)}"


def num_tokens_from_messages(prompt, model="gpt-3.5-turbo-0613"):
    """Returns the number of tokens used by a list of messages."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    num_tokens = 0
    num_tokens += 4  # every message follows <im_start>{role/name}\n{content}<im_end>\n
    num_tokens += len(encoding.encode(prompt))
    num_tokens += 2  # every reply is primed with <im_start>assistant
    return num_tokens


def main():
    MODEL = "gpt-3.5-turbo-instruct"
    NUMBER_OF_QUERIES = 10
    MAX_SCRAP_CHAR = 100
    ALLOW_SCRAP = False

    query = input("Please enter a search query: ")
    print()

    names, URLs, snippets = get_bing_search_results(query, count=NUMBER_OF_QUERIES)

    if (names, URLs, snippets) == (None, None, None):
        print("Bing request failed")
        exit()

    chat_prompt = f'Voici les {NUMBER_OF_QUERIES} premiers resultats de recherche sur BING correpondant a la question "{query}" :\n'
    for i in range(len(names)):
        if ALLOW_SCRAP:
            chat_prompt += f'{i+1}. {names[i]}\n{snippets[i]}\n\n{get_page_content(URLs[i], MAX_SCRAP_CHAR)}\n{40 * "-"}\n\n'
        else:
            chat_prompt += f'{i+1}. {names[i]}\n{snippets[i]}\n{40 * "-"}\n\n'

    chat_prompt += f"Maintenant, reponds a la question {query}"

    print(chat_prompt)
    print()

    print(f"Prompt len : {len(chat_prompt)}")
    print(f"# Tokens : {num_tokens_from_messages(chat_prompt, MODEL)}")

    ENABLE_GPT = True

    if ENABLE_GPT:
        # Send concatenated string to GPT-3
        gpt_response = query_gpt_3(chat_prompt, MODEL)

        # Display GPT-3 response
        print(f"GPT-3 Response: {gpt_response}")


# main()
