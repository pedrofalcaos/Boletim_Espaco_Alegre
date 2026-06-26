"""
Armazena a URL da foto (Cloudinary) de cada aluno e de cada membro da equipe.

Apenas a URL é guardada aqui — a imagem em si fica no Cloudinary. Chave no
formato 'aluno:<matricula>' ou 'usuario:<id>'.

Backends: PostgreSQL (Railway) quando DATABASE_URL existe; JSON local caso
contrário — mesmo padrão dos demais módulos db_*.
"""
import json, os, threading

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()


def chave_aluno(matricula: str) -> str:
    return f"aluno:{matricula}"

def chave_usuario(user_id) -> str:
    return f"usuario:{user_id}"


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _ready = False
    _init_lock = threading.Lock()

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS fotos (
            chave VARCHAR(80) PRIMARY KEY,
            url   TEXT NOT NULL DEFAULT ''
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

    def get_foto(chave: str) -> str | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT url FROM fotos WHERE chave=%s", (chave,))
                row = cur.fetchone()
            return row[0] if row and row[0] else None
        finally:
            conn.close()

    def get_fotos_map(prefix: str = "") -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                if prefix:
                    cur.execute("SELECT chave, url FROM fotos WHERE chave LIKE %s", (prefix + "%",))
                else:
                    cur.execute("SELECT chave, url FROM fotos")
                return {r["chave"]: r["url"] for r in cur.fetchall() if r["url"]}
        finally:
            conn.close()

    def set_foto(chave: str, url: str) -> None:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO fotos (chave, url) VALUES (%s,%s) "
                    "ON CONFLICT (chave) DO UPDATE SET url=EXCLUDED.url",
                    (chave, url),
                )
            conn.commit()
        finally:
            conn.close()

    def remover_foto(chave: str) -> None:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM fotos WHERE chave=%s", (chave,))
            conn.commit()
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    DB_FILE = "fotos.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _save(db: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def get_foto(chave: str) -> str | None:
        with _lock:
            return _load().get(chave) or None

    def get_fotos_map(prefix: str = "") -> dict:
        with _lock:
            db = _load()
            return {k: v for k, v in db.items() if v and (not prefix or k.startswith(prefix))}

    def set_foto(chave: str, url: str) -> None:
        with _lock:
            db = _load()
            db[chave] = url
            _save(db)

    def remover_foto(chave: str) -> None:
        with _lock:
            db = _load()
            if chave in db:
                del db[chave]
                _save(db)
