from datetime import datetime

def log_message(role: str, text: str):
    print(f"[{datetime.utcnow().isoformat()}] {role.upper()}: {text}")

def log_feedback(message_id: int | None, rating: int, comment: str | None):
    print(f"[FEEDBACK] id={message_id} rating={rating} comment={comment}")
