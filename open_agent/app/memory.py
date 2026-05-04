from diskcache import Cache

cache = Cache("./cache/processed_emails")

def is_processed(email_id):
    return email_id in cache

def mark_processed(email_id, details=None):
    cache[email_id] = details or True

def get_history():
    return [cache[k] for k in cache if isinstance(cache[k], dict)]