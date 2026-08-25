"""
actions/llm.py
==============
Local LLM integration using Ollama's REST API (100% offline).
Routes general questions to local AI models like llama3.2 or mistral.
"""
from __future__ import annotations
import requests
from config.settings import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


def ask_llm(prompt: str) -> str:
    """
    Send *prompt* to local Ollama LLM and return concise spoken answer.
    """
    if not prompt:
        return "What question would you like to ask?"

    if not Settings.OLLAMA_ENABLED:
        return "Local AI assistant feature is currently disabled in settings."

    url = f"{Settings.OLLAMA_URL.rstrip('/')}/api/generate"
    payload = {
        "model": Settings.OLLAMA_MODEL,
        "prompt": f"Respond concisely in 2-3 spoken sentences. Question: {prompt}",
        "stream": False,
        "options": {
            "num_predict": Settings.LLM_MAX_TOKENS,
        },
    }

    try:
        logger.info(f"Querying local Ollama model ({Settings.OLLAMA_MODEL}) for: '{prompt}'")
        res = requests.post(url, json=payload, timeout=12)
        if res.status_code == 200:
            data = res.json()
            response_text = data.get("response", "").strip()
            if response_text:
                logger.info(f"Ollama response: '{response_text}'")
                return response_text
        elif res.status_code == 404:
            logger.warning(f"Ollama model '{Settings.OLLAMA_MODEL}' not found.")
            return f"The model '{Settings.OLLAMA_MODEL}' is not pulled in Ollama yet."

        logger.warning(f"Ollama returned HTTP status {res.status_code}")
        return "Sorry, I could not get an answer from the local AI model."

    except requests.exceptions.ConnectionError:
        logger.warning("Ollama ConnectionError — Ollama service is not running locally.")
        return "Local AI model is currently offline. Please ensure Ollama is running."
    except requests.exceptions.Timeout:
        logger.warning("Ollama query timed out after 12 seconds.")
        return "Thinking took too long. Please try a simpler question."
    except Exception as e:
        logger.error(f"Error calling Ollama API: {e}")
        return "Sorry, an error occurred while processing your request with the AI model."
