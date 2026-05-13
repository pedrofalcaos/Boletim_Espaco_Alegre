"""
Persistência: PostgreSQL (Railway) quando DATABASE_URL está definida,
JSON local caso contrário (desenvolvimento sem banco).
"""
import json, os, threading

DATABASE_URL = os.environ.get("DATABASE_URL")
SEED_FILE    = "dados.json"
_lock        = threading.Lock()

DISCIPLINAS = [
    'Língua Portuguesa', 'Matemática', 'História', 'Geografia',
    'Ciências', 'Arte', 'Educação Física',
    'Língua Estrangeira – Inglês', 'Produção Textual',
]


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _pg_ready      = False
    _pg_init_lock  = threading.Lock()

    _CREATE_TABLE = """
        CREATE TABLE IF NOT EXISTS alunos (
            matricula         VARCHAR(20)  PRIMARY KEY,
            nome              VARCHAR(255) NOT NULL DEFAULT '',
            turma             VARCHAR(100) NOT NULL DEFAULT '',
            periodo           VARCHAR(50)  NOT NULL DEFAULT '',
            professora        VARCHAR(255) NOT NULL DEFAULT '',
            ano_letivo        VARCHAR(10)  NOT NULL DEFAULT '2026',
            notas             JSONB        NOT NULL DEFAULT '{}',
            freq_total_aulas  VARCHAR(20)  NOT NULL DEFAULT '',
            freq_total_faltas VARCHAR(20)  NOT NULL DEFAULT '',
            observacoes       TEXT         NOT NULL DEFAULT ''
        )
    """

    def _connect():
        return psycopg2.connect(DATABASE_URL)

    def _seed(conn):
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        with conn.cursor() as cur:
            for mat, a in data["alunos"].items():
                notas = a.get("notas", {})
                for disc in DISCIPLINAS:
                    notas.setdefault(disc, {})
                freq = a.get("frequencia", {})
                cur.execute("""
                    INSERT INTO alunos
                        (matricula, nome, turma, periodo, professora, ano_letivo,
                         notas, freq_total_aulas, freq_total_faltas, observacoes)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (matricula) DO NOTHING
                """, (
                    mat,
                    a.get("nome", ""), a.get("turma", ""), a.get("periodo", ""),
                    a.get("professora", ""), a.get("ano_letivo", "2026"),
                    json.dumps(notas, ensure_ascii=False),
                    freq.get("total_aulas", ""), freq.get("total_faltas", ""),
                    a.get("observacoes", ""),
                ))
        conn.commit()

    def _init():
        global _pg_ready
        if _pg_ready:
            return
        with _pg_init_lock:
            if _pg_ready:
                return
            conn = _connect()
            try:
                with conn.cursor() as cur:
                    cur.execute(_CREATE_TABLE)
                    conn.commit()
                    cur.execute("SELECT COUNT(*) FROM alunos")
                    if cur.fetchone()[0] == 0:
                        _seed(conn)
            finally:
                conn.close()
            _pg_ready = True

    def _row(row) -> dict:
        notas = row["notas"] if isinstance(row["notas"], dict) else json.loads(row["notas"])
        return {
            "nome":       row["nome"],
            "turma":      row["turma"],
            "periodo":    row["periodo"],
            "professora": row["professora"],
            "ano_letivo": row["ano_letivo"],
            "notas":      notas,
            "frequencia": {
                "total_aulas":  row["freq_total_aulas"],
                "total_faltas": row["freq_total_faltas"],
            },
            "observacoes": row["observacoes"],
        }

    def get_all_alunos() -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM alunos ORDER BY turma, nome")
                return {r["matricula"]: _row(r) for r in cur.fetchall()}
        finally:
            conn.close()

    def get_aluno(matricula: str) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM alunos WHERE matricula = %s", (matricula,))
                r = cur.fetchone()
            return _row(r) if r else None
        finally:
            conn.close()

    def upsert_aluno(matricula: str, dados: dict):
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM alunos WHERE matricula = %s FOR UPDATE",
                    (matricula,)
                )
                existing = cur.fetchone()

                if existing is None:
                    init_notas = {d: {} for d in DISCIPLINAS}
                    cur.execute("""
                        INSERT INTO alunos
                            (matricula, nome, turma, periodo, professora, ano_letivo,
                             notas, freq_total_aulas, freq_total_faltas, observacoes)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """, (matricula, "", "", "", "", "2026",
                          json.dumps(init_notas, ensure_ascii=False), "", "", ""))
                    cur.execute("SELECT * FROM alunos WHERE matricula = %s", (matricula,))
                    existing = cur.fetchone()

                notas      = existing["notas"] if isinstance(existing["notas"], dict) else json.loads(existing["notas"])
                freq_aulas  = existing["freq_total_aulas"]
                freq_faltas = existing["freq_total_faltas"]
                fields      = {}

                for k, v in dados.items():
                    if k == "notas":
                        for disc, vals in v.items():
                            if disc in DISCIPLINAS:
                                notas[disc] = vals
                    elif k == "frequencia":
                        freq_aulas  = v.get("total_aulas",  freq_aulas)
                        freq_faltas = v.get("total_faltas", freq_faltas)
                    else:
                        fields[k] = v

                cur.execute("""
                    UPDATE alunos SET
                        nome=%s, turma=%s, periodo=%s, professora=%s, ano_letivo=%s,
                        notas=%s, freq_total_aulas=%s, freq_total_faltas=%s, observacoes=%s
                    WHERE matricula=%s
                """, (
                    fields.get("nome",       existing["nome"]),
                    fields.get("turma",      existing["turma"]),
                    fields.get("periodo",    existing["periodo"]),
                    fields.get("professora", existing["professora"]),
                    fields.get("ano_letivo", existing["ano_letivo"]),
                    json.dumps(notas, ensure_ascii=False),
                    freq_aulas, freq_faltas,
                    fields.get("observacoes", existing["observacoes"]),
                    matricula,
                ))
            conn.commit()
        finally:
            conn.close()

    def delete_aluno(matricula: str) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alunos WHERE matricula = %s", (matricula,))
                deleted = cur.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    def reset_db():
        global _pg_ready
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("DELETE FROM alunos")
                conn.commit()
            _seed(conn)
        finally:
            conn.close()
        _pg_ready = True


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    DB_FILE = "banco.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        with open(SEED_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data["alunos"].values():
            notas = entry.get("notas", {})
            for disc in DISCIPLINAS:
                notas.setdefault(disc, {})
            entry["notas"]      = notas
            entry["frequencia"] = entry.get("frequencia", {"total_aulas": "", "total_faltas": ""})
            entry["observacoes"] = entry.get("observacoes", "")
        _save(data)
        return data

    def _save(data: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_all_alunos() -> dict:
        with _lock:
            return _load()["alunos"]

    def get_aluno(matricula: str) -> dict | None:
        with _lock:
            return _load()["alunos"].get(matricula)

    def upsert_aluno(matricula: str, dados: dict):
        with _lock:
            db = _load()
            if matricula not in db["alunos"]:
                db["alunos"][matricula] = {
                    "nome": "", "turma": "", "periodo": "",
                    "professora": "", "ano_letivo": "2026",
                    "notas": {d: {} for d in DISCIPLINAS},
                    "frequencia": {"total_aulas": "", "total_faltas": ""},
                    "observacoes": "",
                }
            for k, v in dados.items():
                if k == "notas":
                    for disc, vals in v.items():
                        if disc in DISCIPLINAS:
                            db["alunos"][matricula]["notas"][disc] = vals
                else:
                    db["alunos"][matricula][k] = v
            _save(db)

    def delete_aluno(matricula: str) -> bool:
        with _lock:
            db = _load()
            if matricula in db["alunos"]:
                del db["alunos"][matricula]
                _save(db)
                return True
            return False

    def reset_db():
        with _lock:
            if os.path.exists(DB_FILE):
                os.remove(DB_FILE)
            _load()
