"""
Utility functions for OpenAI API interactions with improved error handling and retry logic.
"""
import os
import time
import json
from typing import Dict, Any, Optional, List
from openai import OpenAI
import openai

# Initialize the OpenAI client with timeout configuration
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
    timeout=60.0,  # 60 second timeout for each request (increased from 30)
    max_retries=0  # We'll implement our own retry logic
)

def make_openai_request(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    response_format: Optional[Dict[str, str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 1500,
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Optional[Dict[str, Any]]:
    """
    Make an OpenAI API request with exponential backoff retry logic.
    
    Args:
        messages: List of message dictionaries for the chat completion
        model: The model to use (default: gpt-4o)
        response_format: Response format specification (e.g., {"type": "json_object"})
        temperature: Temperature for response generation
        max_tokens: Maximum tokens in the response
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries (doubles each time)
    
    Returns:
        Dict containing the parsed response or None if all retries failed
    """
    last_error = None
    
    # Calculate dynamic timeout based on max_tokens
    # Base timeout of 30 seconds + 15 seconds per 1000 tokens
    dynamic_timeout = 30 + (max_tokens / 1000) * 15
    
    print(f"Using dynamic timeout of {dynamic_timeout:.1f} seconds for {max_tokens} max tokens")
    
    # Create a new client with the dynamic timeout for this request
    request_client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY"),
        timeout=dynamic_timeout,
        max_retries=0
    )
    
    for attempt in range(max_retries):
        try:
            # Build the request parameters
            request_params = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Add response format if specified
            if response_format:
                request_params["response_format"] = response_format
            
            # Make the API call with the request-specific client
            response = request_client.chat.completions.create(**request_params)
            
            # Parse the response based on format
            if response_format and response_format.get("type") == "json_object":
                try:
                    return json.loads(response.choices[0].message.content)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response: {e}")
                    # Return the raw content if JSON parsing fails
                    return {"raw_content": response.choices[0].message.content}
            else:
                return {"content": response.choices[0].message.content}
                
        except openai.RateLimitError as e:
            last_error = e
            wait_time = initial_delay * (2 ** attempt)  # Exponential backoff
            print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
            time.sleep(wait_time)
            
        except openai.APITimeoutError as e:
            last_error = e
            print(f"Request timeout on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(initial_delay)
                
        except openai.APIConnectionError as e:
            last_error = e
            print(f"Connection error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(initial_delay * (2 ** attempt))
                
        except openai.APIError as e:
            last_error = e
            print(f"OpenAI API error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            # Don't retry on certain API errors
            if "invalid_api_key" in str(e).lower():
                break
            if attempt < max_retries - 1:
                time.sleep(initial_delay)
                
        except Exception as e:
            last_error = e
            print(f"Unexpected error on attempt {attempt + 1}/{max_retries}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(initial_delay)
    
    print(f"All retry attempts failed. Last error: {str(last_error)}")
    return None


def batch_openai_requests(
    requests: List[Dict[str, Any]],
    delay_between_requests: float = 0.5
) -> List[Optional[Dict[str, Any]]]:
    """
    Make multiple OpenAI requests with delays between them to avoid rate limits.
    
    Args:
        requests: List of request configurations (each should contain args for make_openai_request)
        delay_between_requests: Delay in seconds between requests
    
    Returns:
        List of responses (None for failed requests)
    """
    results = []
    
    for i, request_config in enumerate(requests):
        if i > 0:
            time.sleep(delay_between_requests)
        
        result = make_openai_request(**request_config)
        results.append(result)
    
    return results