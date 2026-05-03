from diskcache import Cache

cache = Cache("./cache/processed_emails")

def is_processed(email_id):
    return True if email_id in cache else False

def mark_processed(email_id):
        cache[email_id] = True