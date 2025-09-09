"""
Simple OpenAI API warmup and connection pooling for Replit.
Sends a lightweight warmup request to establish TLS/DNS connections.
"""
import os
import time
import json
import requests
from typing import Dict, Any, Optional, List
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter

# Global session for connection pooling
_session = None

def get_session():
    """Get or create a requests session with connection pooling."""
    global _session
    
    if _session is None:
        _session = requests.Session()
        
        # Configure retry strategy
        retry = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        
        # Add adapter with connection pooling
        adapter = HTTPAdapter(
            max_retries=retry,
            pool_connections=10,
            pool_maxsize=10
        )
        
        _session.mount("https://", adapter)
        _session.mount("http://", adapter)
        
        # Set default headers
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key:
            _session.headers.update({
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            })
    
    return _session


def warmup_openai_connection():
    """
    Send a minimal warmup request to OpenAI to establish connection.
    This helps avoid cold start timeouts on the first real request.
    """
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OpenAI API key not found, skipping warmup")
        return False
    
    try:
        print("Warming up OpenAI connection...")
        start_time = time.time()
        
        session = get_session()
        
        # Minimal request to establish connection
        response = session.post(
            "https://api.openai.com/v1/chat/completions",
            json={
                "model": "gpt-3.5-turbo",  # Cheaper model
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1,
                "temperature": 0
            },
            timeout=(10, 30)  # 10s connect, 30s read
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            print(f"✓ OpenAI connection warmed up in {elapsed:.2f}s")
            return True
        else:
            print(f"Warmup request returned status {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("Warmup timed out (connection partially established)")
        return False
    except Exception as e:
        print(f"Warmup failed: {e}")
        return False


def make_openai_request_with_session(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o",
    response_format: Optional[Dict[str, str]] = None,
    temperature: float = 0.7,
    max_tokens: int = 1500,
    max_retries: int = 3
) -> Optional[Dict[str, Any]]:
    """
    Make OpenAI request using persistent session with connection pooling.
    
    Args:
        messages: Chat messages
        model: Model to use
        response_format: Optional response format
        temperature: Generation temperature
        max_tokens: Max tokens in response
        max_retries: Number of retries
        
    Returns:
        Response dict or None if failed
    """
    session = get_session()
    
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    if response_format:
        payload["response_format"] = response_format
    
    # Dynamic timeout based on max_tokens
    timeout = (10, 30 + (max_tokens / 1000) * 20)
    
    for attempt in range(max_retries):
        try:
            response = session.post(
                "https://api.openai.com/v1/chat/completions",
                json=payload,
                timeout=timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Parse JSON if needed
                if response_format and response_format.get("type") == "json_object":
                    try:
                        return json.loads(data["choices"][0]["message"]["content"])
                    except json.JSONDecodeError:
                        return {"raw_content": data["choices"][0]["message"]["content"]}
                
                return data
            
            elif response.status_code == 429:
                # Rate limited
                retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                print(f"Rate limited, waiting {retry_after}s...")
                time.sleep(retry_after)
            
            else:
                print(f"Request failed with status {response.status_code}")
                
        except requests.exceptions.Timeout:
            print(f"Request timeout on attempt {attempt + 1}/{max_retries}")
            
            # On first timeout, might be cold connection
            if attempt == 0:
                print("First timeout - connection might be cold, retrying...")
                time.sleep(1)
                
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error on attempt {attempt + 1}: {e}")
            time.sleep(2 ** attempt)
            
        except Exception as e:
            print(f"Unexpected error: {e}")
            
        if attempt < max_retries - 1:
            time.sleep(1)
    
    return None