from datetime import datetime
from fastapi import APIRouter
import logging

class TokenCounter:
    def __init__(self):
        self.total_tokens = 0
        self.warning_threshold = 10000
        self.final_warning_threshold = 100000
        self.last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    def add_tokens(self, tokens: int):
        self.total_tokens += tokens
        self.last_updated = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return self._check_thresholds()

    def _check_thresholds(self) -> str:
        if self.total_tokens >= self.final_warning_threshold:
            return "FINAL WARNING: Token usage has exceeded 100,000 tokens!"
        elif self.total_tokens >= self.warning_threshold:
            return "WARNING: Token usage has exceeded 10,000 tokens!"
        return ""

    def get_status(self) -> dict:
        return {
            "total_tokens": self.total_tokens,
            "last_updated": self.last_updated,
            "warning_status": self._check_thresholds()
        }

# Create a global instance
token_counter = TokenCounter()

# Create router for token endpoints
token_router = APIRouter()

@token_router.get("/token-count")
async def get_token_count():
    status = token_counter.get_status()
    return {
        "token_count": status["total_tokens"],
        "last_updated": status["last_updated"],
        "warning_message": status["warning_status"]
    }