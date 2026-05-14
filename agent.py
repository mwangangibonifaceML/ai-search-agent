from __future__ import annotations

import os
import json
import random
import asyncio
from dotenv import load_dotenv
from huggingface_hub import InferenceClient
from search_tool import web_search, extract_content

load_dotenv()
hf_api_key = os.getenv('HF_API_KEY')

def process_query(query: str, hf_api_key: str = hf_api_key) -> str:
    """Process the user query by performing a web search and extracting relevant content.

    Args:
        query (str): The user's query.

    Returns:
        str: The extracted content from the web search.
    """
    #* instantiate a client for SerpAPI and perform the web search
    client = InferenceClient(
        model= "openai/gpt-oss-20b:groq",
        api_key=hf_api_key
    )
    
    #* define the search tool with the web_search function
    search_tools = {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Perform a web search using SerpAPI and return the results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query."
                    }
                },
                "required": ["query"]
            }
        }
    }
    
    #* first LLM call to get the assistant's response and determine if a tool call is needed
    response = client.chat_completion(
        messages=[
            {"role": "system", "content": "You are a helpful assistant that provides concise answers based on web search results."},
            {"role": "user", "content": f"Please perform a web search for the following query and extract relevant content: {query}"}
        ],
        tools = [search_tools]
    )
    
    #* function registry to map tool names to actual functions
    tool_registry = {
        "web_search": web_search
    }
    
    #* handle tool calls in the response
    if response.choices[0].message.tool_calls:
        print("Searching the web...")
        
        for tool_call in response.choices[0].message.tool_calls:
            tool_name = tool_registry.get(tool_call.function.name, None)
            tool_args = json.loads(tool_call.function.arguments)
            print(f"Tool called: {tool_name.__name__} with arguments: {tool_args}\n\n")
            
            #* check if the tool is in the registry and call it with the provided arguments
            if tool_name is not None:
                search_results = tool_name(tool_args['query'])
                
                if 'error' in search_results:
                    if search_results['error'] == 'Invalid API Key':
                        return "Authentication error: Invalid API Key. Please check your SerpAPI key and try again."
                    elif search_results['error'] == 'Too many requests':
                        return "Too many requests. Please try again later."
                    elif search_results['error'] == 'Internal Server Error':
                        return "SerpAPI is currently experiencing issues. Please try again later."
                    else:
                        return search_results['error']
                
                #* extract relevant content from the search results
                content = extract_content(search_results)
                if not content:
                    return "No relevant content found in the search results."
            else:
                print(f"Tool {tool_name.name} not found in registry.")
                return "Sorry, I couldn't perform the web search."
            
        #* second call to complete the response after tool execution
        final_response = client.chat_completion(
            messages=[
                {"role": "user", "content": query},
                {"role": "assistant", "content": response.choices[0].message.content},
                {"role": "tool",
                "name": tool_name.__name__,
                "content": str(content[:4000]),  #* limit content to avoid token overflow
                "tool_call_id": tool_call.id
                }
            ],
            tools = [search_tools],
            tool_choice= "none"
        )
        return final_response.choices[0].message.content
    else:
        print("No tools were called in the response.")
        return response.choices[0].message.content
    
if __name__ == "__main__":
    question = input("What do you want to search today: ")
    content = process_query(question, hf_api_key)
    print(f"Extracted content: {content}")