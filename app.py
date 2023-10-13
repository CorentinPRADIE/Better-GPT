import streamlit as st
import os
import requests
import openai

st.set_page_config(layout="wide")

# Assuming the functions are defined in test.py
from test import get_bing_search_results, num_tokens_from_messages, query_gpt_3, get_page_content

# API keys retrieval and verification
bing_subscription_key = os.environ.get('BING_SEARCH_V7_SUBSCRIPTION_KEY')
openai_api_key = os.environ.get('OPENAI_API_KEY')

if bing_subscription_key is None:
    raise ValueError("Bing API key (BING_SEARCH_V7_SUBSCRIPTION_KEY) is not set in environment variables!")
if openai_api_key is None:
    raise ValueError("OpenAI API key (OPENAI_API_KEY) is not set in environment variables!")

openai.api_key = openai_api_key

# Streamlit interface
st.title("Better GPT ✨")

# Adding button before text input as per the request


number_of_queries = st.slider("Number of Bing Search Results", min_value=1, max_value=10, value=3)
allow_scrap = st.checkbox("Allow Scrap", value=True)
show_prompt = st.checkbox("Show GPT-3 Prompt", value=False)

query = st.text_input("Please enter a search query:")

if st.button("Search and Generate Response"):
    names, URLs, snippets = get_bing_search_results(query, count=number_of_queries)

    if (names, URLs, snippets) == (None, None, None):
        st.error('Bing request failed')
    else:
        chat_prompt = f'Voici les {number_of_queries} premiers resultats de recherche sur BING correpondant a la question "{query}" :\n'
        for i in range(len(names)):
            if allow_scrap:
                chat_prompt += f'{i+1}. {names[i]}\n{snippets[i]}\n\n{get_page_content(URLs[i], 100)}\n\n'
            else:
                chat_prompt += f'{i+1}. {names[i]}\n{snippets[i]}\n{40 * "-"}\n\n'

        chat_prompt += f"Maintenant, reponds a la question {query}"

        if show_prompt:
            st.caption(chat_prompt)

        st.write(f'Nombre de Tokens : {num_tokens_from_messages(chat_prompt, "gpt-3.5-turbo-instruct")}')

    
        gpt_response = query_gpt_3(chat_prompt, "gpt-3.5-turbo-instruct")
        st.write("GPT-3 Response:")
        st.subheader(gpt_response)
