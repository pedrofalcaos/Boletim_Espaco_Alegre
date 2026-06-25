"""
Autenticação por sessão assinada (cookie).
Suporta múltiplos usuários com roles: 'admin' | 'professora'.
"""
import os, hashlib, secrets, time, threading
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from fastapi import Request

# Caracteres sem ambiguidade visual (sem 0/O, 1/l/I) para senhas temporárias
_TEMP_PWD_ALPHABET = "ABCDEFGHJKMNPQRSTUVWXYZabcdefghjkmnpqrstuvwxyz23456789"

# Produção é identificada pela presença do banco gerenciado (Railway/Postgres).
IS_PROD = bool(os.environ.get("DATABASE_URL"))


def _resolve_secret_key() -> str:
    """Chave para assinar os cookies de sessão.

    Preferimos SECRET_KEY do ambiente. Se não houver, derivamos uma chave
    estável a partir do DATABASE_URL (que é secreto) — assim nunca usamos um
    valor público fixo em produção. Em desenvolvimento local (sem banco),
    cai numa chave fixa apenas de dev."""
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    db = os.environ.get("DATABASE_URL")
    if db:
        return hashlib.sha256(("ea-session::" + db).encode("utf-8")).hexdigest()
    return "dev-only-espaco-alegre-key-NAO-USAR-EM-PRODUCAO"


SECRET_KEY  = _resolve_secret_key()
COOKIE_NAME = "ea_session"
COOKIE_MAX  = 60 * 60 * 8  # 8 horas
COOKIE_SECURE = IS_PROD    # cookies de sessão só trafegam por HTTPS em produção

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


def generate_temp_password(length: int = 8) -> str:
    """Gera uma senha temporária aleatória, sem caracteres ambíguos."""
    return "".join(secrets.choice(_TEMP_PWD_ALPHABET) for _ in range(length))


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


def check_admin(request: Request) -> bool:
    """True somente para sessão com role 'admin' (gestão completa)."""
    user = get_session_user(request)
    return bool(user) and user.get("role") == "admin"


def check_staff(request: Request) -> bool:
    """True para sessão com role 'admin' ou 'coordenacao' (acesso a relatórios)."""
    user = get_session_user(request)
    return bool(user) and user.get("role") in ("admin", "coordenacao")


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


# ── Proteção simples contra força bruta no login (em memória) ──────────────────
# Suficiente para o contexto (instância única). Em múltiplas instâncias, migrar
# o contador para o banco/Redis.
_LOGIN_LOCK = threading.Lock()
_login_falhas: dict = {}            # ip -> [timestamps de falhas recentes]
_LOGIN_MAX_FALHAS = 8              # tentativas antes do bloqueio
_LOGIN_JANELA_SEG = 15 * 60       # janela de contagem / duração do bloqueio


def login_bloqueado(ip: str) -> bool:
    """True se o IP excedeu o limite de tentativas na janela atual."""
    agora = time.time()
    with _LOGIN_LOCK:
        recentes = [t for t in _login_falhas.get(ip, []) if agora - t < _LOGIN_JANELA_SEG]
        _login_falhas[ip] = recentes
        return len(recentes) >= _LOGIN_MAX_FALHAS


def registrar_falha_login(ip: str) -> None:
    with _LOGIN_LOCK:
        _login_falhas.setdefault(ip, []).append(time.time())


def limpar_falhas_login(ip: str) -> None:
    with _LOGIN_LOCK:
        _login_falhas.pop(ip, None)
