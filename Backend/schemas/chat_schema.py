from pydantic import BaseModel, Field
from typing import List, Optional

class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    top_k: int = 4
    intent: Optional[str] = None

    def get_last_user_message(self) -> Optional[str]:
        for m in reversed(self.messages):
            if m.role == "user":
                return m.content
        return None

    def query_text(self) -> str:
        return self.get_last_user_message() or ""

class ChatResponse(BaseModel):
    answer: str
    citations: List[str] = Field(default_factory=list)

class FeedbackPayload(BaseModel):
    message_id: Optional[int] = None
    rating: int  # -1, 0, 1
    comment: Optional[str] = None
