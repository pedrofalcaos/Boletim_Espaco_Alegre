"""
Registro de acessos dos responsáveis aos documentos dos alunos
(boletim, relatório semestral e avaliação de inglês).

Como o sistema não possui login individual de responsável — os pais acessam
apenas informando a matrícula — o "responsável" é anônimo. Registramos o que é
possível observar: aluno, documento, data/hora, IP, navegador e dispositivo.
Serve como histórico interno de engajamento para a coordenação.

Backends: PostgreSQL (Railway) quando DATABASE_URL existe; JSON local caso
contrário — mesmo padrão de db.py / db_relatorio.py / db_avaliacao.py.
"""
import json, os, threading
from datetime import datetime, timedelta

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()

# Tipos de documento e rótulos amigáveis
DOCUMENTOS = {
    "boletim":          "Boletim",
    "relatorio":        "Relatório Semestral",
    "avaliacao_ingles": "Avaliação de Inglês",
}

# Janela (minutos) para considerar recarregamentos como o mesmo acesso e não
# duplicar o registro.
DEDUP_MINUTOS = 30


def detectar_dispositivo(user_agent: str) -> str:
    """Classifica o dispositivo a partir do user-agent: 'tablet', 'mobile' ou 'web'."""
    ua = (user_agent or "").lower()
    if "ipad" in ua or "tablet" in ua or ("android" in ua and "mobile" not in ua):
        return "tablet"
    if "mobi" in ua or "iphone" in ua or "ipod" in ua or "windows phone" in ua:
        return "mobile"
    return "web"


def _agora() -> str:
    return datetime.now().isoformat(sep=" ")[:19]


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _ready = False
    _init_lock = threading.Lock()

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS acessos_documentos (
            id          SERIAL PRIMARY KEY,
            matricula   VARCHAR(20)  NOT NULL,
            nome_aluno  VARCHAR(255) NOT NULL DEFAULT '',
            turma       VARCHAR(100) NOT NULL DEFAULT '',
            documento   VARCHAR(40)  NOT NULL,
            ip          VARCHAR(60)  NOT NULL DEFAULT '',
            user_agent  VARCHAR(400) NOT NULL DEFAULT '',
            dispositivo VARCHAR(20)  NOT NULL DEFAULT 'web',
            acessado_em TIMESTAMP DEFAULT NOW()
        );
        CREATE INDEX IF NOT EXISTS idx_acessos_matricula ON acessos_documentos (matricula);
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

    def registrar_acesso(matricula: str, nome_aluno: str, turma: str, documento: str,
                         ip: str = "", user_agent: str = "") -> bool:
        """Registra um acesso. Retorna False (sem inserir) se um acesso idêntico
        (mesma matrícula+documento+IP) ocorreu dentro da janela de dedup."""
        if documento not in DOCUMENTOS:
            return False
        _init()
        disp = detectar_dispositivo(user_agent)
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """SELECT 1 FROM acessos_documentos
                       WHERE matricula=%s AND documento=%s AND ip=%s
                         AND acessado_em > NOW() - (%s * INTERVAL '1 minute')
                       LIMIT 1""",
                    (matricula, documento, ip, DEDUP_MINUTOS),
                )
                if cur.fetchone():
                    return False
                cur.execute(
                    """INSERT INTO acessos_documentos
                           (matricula, nome_aluno, turma, documento, ip, user_agent, dispositivo)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)""",
                    (matricula, nome_aluno, turma, documento, ip, (user_agent or "")[:400], disp),
                )
            conn.commit()
            return True
        finally:
            conn.close()

    def listar_acessos() -> list:
        """Todos os registros, mais recentes primeiro."""
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM acessos_documentos ORDER BY acessado_em DESC")
                rows = []
                for r in cur.fetchall():
                    d = dict(r)
                    if d.get("acessado_em") is not None:
                        d["acessado_em"] = str(d["acessado_em"])[:19]
                    rows.append(d)
                return rows
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    DB_FILE = "acessos_log.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"itens": [], "_seq": 1}

    def _save(db: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def registrar_acesso(matricula: str, nome_aluno: str, turma: str, documento: str,
                         ip: str = "", user_agent: str = "") -> bool:
        if documento not in DOCUMENTOS:
            return False
        with _lock:
            db = _load()
            limite = (datetime.now() - timedelta(minutes=DEDUP_MINUTOS)).isoformat(sep=" ")[:19]
            for it in db["itens"]:
                if (it["matricula"] == matricula and it["documento"] == documento
                        and it.get("ip", "") == ip and it.get("acessado_em", "") > limite):
                    return False
            db["itens"].append({
                "id": db.get("_seq", 1),
                "matricula": matricula,
                "nome_aluno": nome_aluno,
                "turma": turma,
                "documento": documento,
                "ip": ip,
                "user_agent": (user_agent or "")[:400],
                "dispositivo": detectar_dispositivo(user_agent),
                "acessado_em": _agora(),
            })
            db["_seq"] = db.get("_seq", 1) + 1
            _save(db)
            return True

    def listar_acessos() -> list:
        with _lock:
            db = _load()
            return sorted(db["itens"], key=lambda r: r.get("acessado_em", ""), reverse=True)


# ── Agregação (independente do backend) ──────────────────────────────────────
def agregar_por_aluno_documento(rows: list) -> dict:
    """Agrupa os acessos por (matricula, documento), retornando contagem,
    último acesso e dispositivo/IP do último acesso.

    Retorna: {(matricula, documento): {qtd, ultimo, dispositivo, ip, nome_aluno, turma}}"""
    agg: dict = {}
    for r in rows:
        chave = (r["matricula"], r["documento"])
        a = agg.get(chave)
        if a is None:
            agg[chave] = {
                "matricula": r["matricula"],
                "nome_aluno": r.get("nome_aluno", ""),
                "turma": r.get("turma", ""),
                "documento": r["documento"],
                "qtd": 1,
                "ultimo": r.get("acessado_em", ""),
                "dispositivo": r.get("dispositivo", "web"),
                "ip": r.get("ip", ""),
            }
        else:
            a["qtd"] += 1
            if r.get("acessado_em", "") > a["ultimo"]:
                a["ultimo"] = r.get("acessado_em", "")
                a["dispositivo"] = r.get("dispositivo", "web")
                a["ip"] = r.get("ip", "")
    return agg
