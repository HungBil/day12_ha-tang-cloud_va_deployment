"""
LLM Router — tự động chọn OpenAI thật hoặc Mock LLM.

Nếu OPENAI_API_KEY được set → gọi GPT-4o-mini thật.
Nếu không → fallback về mock_llm (không cần API key).
"""
import logging

logger = logging.getLogger(__name__)

# Try to detect which LLM to use at import time
_use_real_llm = False
_openai_client = None

try:
    from app.config import settings
    if settings.openai_api_key:
        from openai import OpenAI
        _openai_client = OpenAI(api_key=settings.openai_api_key)
        _use_real_llm = True
        logger.info("LLM Router: Using REAL OpenAI GPT-4o-mini")
    else:
        logger.info("LLM Router: No OPENAI_API_KEY → using Mock LLM")
except Exception as e:
    logger.warning(f"LLM Router: Failed to init OpenAI client: {e} → using Mock LLM")


def ask(question: str) -> str:
    """
    Route question to real OpenAI or mock LLM.
    Returns the answer string.
    """
    if _use_real_llm and _openai_client:
        return _ask_openai(question)
    else:
        from utils.mock_llm import ask as mock_ask
        return mock_ask(question)


def _ask_openai(question: str) -> str:
    """Call OpenAI GPT-4o-mini API."""
    try:
        response = _openai_client.chat.completions.create(
            model=settings.llm_model,  # "gpt-4o-mini"
            messages=[
                {
                    "role": "system",
                    "content": "Bạn là một AI agent thông minh được deploy trên cloud. "
                               "Trả lời ngắn gọn, chính xác, bằng tiếng Việt nếu câu hỏi bằng tiếng Việt."
                },
                {"role": "user", "content": question},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        # Fallback to mock on error
        from utils.mock_llm import ask as mock_ask
        return f"[OpenAI Error → fallback] {mock_ask(question)}"


def get_backend_name() -> str:
    """Return which backend is active."""
    return "openai" if _use_real_llm else "mock"
