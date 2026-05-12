"""
Autenticação simples por sessão assinada (cookie).
Senha configurável via variável de ambiente ADMIN_PASSWORD.
"""
import os, hashlib
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request
from fastapi.responses import RedirectResponse

SECRET_KEY    = os.environ.get("SECRET_KEY", "espaco-alegre-2026-chave-secreta")
ADMIN_USER    = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS    = os.environ.get("ADMIN_PASSWORD", "escola2026")
COOKIE_NAME   = "ea_session"
COOKIE_MAX    = 60 * 60 * 8  # 8 horas

_s = URLSafeTimedSerializer(SECRET_KEY)

def make_session_token() -> str:
    return _s.dumps({"user": ADMIN_USER})

def check_session(request: Request) -> bool:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        return False
    try:
        _s.loads(token, max_age=COOKIE_MAX)
        return True
    except (BadSignature, SignatureExpired):
        return False

def require_admin(request: Request):
    if not check_session(request):
        raise _Redirect("/admin/login")

class _Redirect(Exception):
    def __init__(self, url): self.url = url
