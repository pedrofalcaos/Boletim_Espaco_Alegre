"""
Autenticação por sessão assinada (cookie).
Suporta múltiplos usuários com roles: 'admin' | 'professora'.
"""
import os, hashlib, secrets
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request

SECRET_KEY  = os.environ.get("SECRET_KEY", "espaco-alegre-2026-chave-secreta")
COOKIE_NAME = "ea_session"
COOKIE_MAX  = 60 * 60 * 8  # 8 horas

# Mantidos para seed do usuário admin padrão em db_relatorio.py
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASSWORD", "escola2026")

_s = URLSafeTimedSerializer(SECRET_KEY)


# ── Senha ─────────────────────────────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Retorna 'salt$hash' usando PBKDF2-HMAC-SHA256."""
    salt = secrets.token_hex(16)
    h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode(), 260_000)
    return f"{salt}${h.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, h = stored.split("$", 1)
        new_h = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode(), 260_000)
        return secrets.compare_digest(new_h.hex(), h)
    except Exception:
        return False


# ── Token de sessão ───────────────────────────────────────────────────────────

def make_session_token(user: dict) -> str:
    """Cria token assinado com dados do usuário logado."""
    return _s.dumps({
        "user_id":  user["id"],
        "username": user["username"],
        "role":     user["role"],
        "nome":     user["nome"],
    })


def get_session_user(request: Request) -> dict | None:
    """Retorna dict do usuário logado ou None se sessão inválida/expirada."""
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return None
    try:
        return _s.loads(token, max_age=COOKIE_MAX)
    except (BadSignature, SignatureExpired):
        return None


def check_session(request: Request) -> bool:
    """Compatibilidade com código existente — retorna True se há sessão válida."""
    return get_session_user(request) is not None


# ── Guards de rota ────────────────────────────────────────────────────────────

def require_admin(request: Request):
    """Levanta _Redirect se o usuário não for admin."""
    user = get_session_user(request)
    if not user or user.get("role") != "admin":
        raise _Redirect("/admin/login")


def require_professora(request: Request):
    """Levanta _Redirect se não houver sessão válida (admin também passa)."""
    user = get_session_user(request)
    if not user:
        raise _Redirect("/professora/login")
    if user.get("role") not in ("admin", "professora"):
        raise _Redirect("/professora/login")


class _Redirect(Exception):
    def __init__(self, url):
        self.url = url
