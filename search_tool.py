import os
from typing import List
import requests
from dotenv import load_dotenv

#* load environment variables from .env file
load_dotenv()
SERP_API_KEY = os.getenv('SERP_API_KEY')

#* function to perform web search using SerpAPI
def web_search(query: str) -> dict:
    """
    Perform a web search using SerpAPI and return the results.
    Args:
        query (str): The search query.
    Returns:
        dict: A dictionary containing the search results.
    """
    #* SerpAPI endpoint and parameters
    url = 'https://serpapi.com/search'
    params = {
        "engine": "google",
        "num": 5,
        'q': query,
        'api_key': SERP_API_KEY
    }

    #* make the API request and handle potential errors
    try:
        response = requests.get(url, params= params)

        #* check response for errors
        if response.status_code == 401:
            raise ValueError('Invalid API Key')
        if response.status_code == 429:
            raise ValueError('Too many requests')
        if response.status_code == 500:
            raise ValueError('Internal Server Error')

        #* return the search results
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        error_msg = f"Error fetching search results: {e}"
        #* check if the error response contains additional details
        if hasattr(e, 'response') and e.response:
            try:
                error_details = e.response.json()
                error_msg = f"{error_msg} - {error_details.get('message', '')}"
            except:
                pass
        return {"error": error_msg}
    
#* function to extract relevant content from search results
def extract_content(search_results) -> str:
    """Extract relevant content from the search results.

    Args:
        search_results (dict): A dictionary containing the search results.
    Returns:        
        str: A string containing the extracted content.
    """
    content = []

    #* 
    if 'organic_results' in search_results and search_results['organic_results']:
        for result in search_results['organic_results']:
            if 'snippet' in result:
                content.append(result['snippet'])
    if 'answer_box' in search_results and search_results['answer_box']:
        content.insert(0,search_results['answer_box']['answer'])
    return "\n\n".join(content)

def main():
    #* Define the search tool
    query = "Tell me about the latest advancements in AI research."
    search_results = web_search(query, SERP_API_KEY)
    content = extract_content(search_results)
    print(content)

if __name__ == "__main__":
    main()