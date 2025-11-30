def normalizar_email(email: str):
    if not email:
        return None
    return email.strip().lower()
