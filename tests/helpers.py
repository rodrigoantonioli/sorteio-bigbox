import secrets
import string

def generate_random_password(length=12):
    """Gera uma senha aleatória segura."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def generate_random_email(domain="test.com"):
    """Gera um email aleatório."""
    local_part = secrets.token_hex(8)
    return f"{local_part}@{domain}" 