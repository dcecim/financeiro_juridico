from contextvars import ContextVar
from typing import Optional
import uuid

# ContextVar to store the current user ID
current_user_id_context: ContextVar[Optional[uuid.UUID]] = ContextVar("current_user_id", default=None)
