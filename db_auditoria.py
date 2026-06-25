"""
Trilha de auditoria das alterações feitas pela equipe (admin/coordenação/
professora). Registra quem fez o quê e quando, para acompanhamento interno.

Backends: PostgreSQL (Railway) quando DATABASE_URL existe; JSON local caso
contrário — mesmo padrão de db.py / db_relatorio.py / db_acesso.py.
"""
import json, os, threading
from datetime import datetime, timedelta, timezone

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()

# Horário de Brasília/Recife (UTC-3, sem horário de verão).
_TZ_BR = timezone(timedelta(hours=-3))

def _agora() -> str:
    return datetime.now(_TZ_BR).replace(tzinfo=None).isoformat(sep=" ")[:19]


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _ready = False
    _init_lock = threading.Lock()

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS auditoria (
            id        SERIAL PRIMARY KEY,
            usuario   VARCHAR(120) NOT NULL DEFAULT '',
            role      VARCHAR(20)  NOT NULL DEFAULT '',
            acao      VARCHAR(120) NOT NULL DEFAULT '',
            alvo      VARCHAR(200) NOT NULL DEFAULT '',
            detalhe   VARCHAR(400) NOT NULL DEFAULT '',
            criado_em VARCHAR(20)  NOT NULL DEFAULT ''
        );
    """

    def _connect():
        return psycopg2.connect(DATABASE_URL)

    def _init():
        global _ready
        if _ready:
            return
        with _init_lock:
            if _ready:
                return
            conn = _connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(_SCHEMA)
                conn.commit()
            finally:
                conn.close()
            _ready = True

    def registrar(usuario: str, role: str, acao: str, alvo: str = "", detalhe: str = "") -> None:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO auditoria (usuario, role, acao, alvo, detalhe, criado_em)
                       VALUES (%s,%s,%s,%s,%s,%s)""",
                    (usuario[:120], role[:20], acao[:120], alvo[:200], detalhe[:400], _agora()),
                )
            conn.commit()
        finally:
            conn.close()

    def listar(limit: int = 500) -> list:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM auditoria ORDER BY id DESC LIMIT %s", (limit,))
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    DB_FILE = "auditoria.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"itens": [], "_seq": 1}

    def _save(db: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def registrar(usuario: str, role: str, acao: str, alvo: str = "", detalhe: str = "") -> None:
        with _lock:
            db = _load()
            db["itens"].append({
                "id": db.get("_seq", 1),
                "usuario": usuario, "role": role, "acao": acao,
                "alvo": alvo, "detalhe": detalhe, "criado_em": _agora(),
            })
            db["_seq"] = db.get("_seq", 1) + 1
            _save(db)

    def listar(limit: int = 500) -> list:
        with _lock:
            db = _load()
            return list(reversed(db["itens"]))[:limit]
