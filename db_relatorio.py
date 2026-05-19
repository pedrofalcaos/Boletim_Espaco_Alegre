"""
Banco de dados para o módulo de Relatório Semestral da Educação Infantil.
Mesma estratégia de db.py: PostgreSQL (Railway) ou JSON local.
"""
import json, os, threading
from auth import hash_password, verify_password, ADMIN_USER, ADMIN_PASS

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _ready = False
    _init_lock = threading.Lock()

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS usuarios (
            id        SERIAL PRIMARY KEY,
            username  VARCHAR(100) UNIQUE NOT NULL,
            password  VARCHAR(400) NOT NULL,
            nome      VARCHAR(255) NOT NULL DEFAULT '',
            role      VARCHAR(20)  NOT NULL DEFAULT 'professora',
            ativo     BOOLEAN DEFAULT TRUE,
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS temas (
            id        SERIAL PRIMARY KEY,
            nome      VARCHAR(255) NOT NULL,
            ordem     INTEGER DEFAULT 0,
            ativo     BOOLEAN DEFAULT TRUE,
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS subtemas (
            id        SERIAL PRIMARY KEY,
            tema_id   INTEGER REFERENCES temas(id) ON DELETE CASCADE,
            descricao TEXT NOT NULL,
            ordem     INTEGER DEFAULT 0,
            ativo     BOOLEAN DEFAULT TRUE
        );

        CREATE TABLE IF NOT EXISTS relatorios_semestrais (
            id              SERIAL PRIMARY KEY,
            matricula       VARCHAR(20) NOT NULL,
            semestre        INTEGER NOT NULL,
            ano_letivo      VARCHAR(10) NOT NULL DEFAULT '2026',
            professora_id   INTEGER REFERENCES usuarios(id),
            status          VARCHAR(20) DEFAULT 'pendente',
            descricao_final TEXT DEFAULT '',
            confirmado_em   TIMESTAMP,
            criado_em       TIMESTAMP DEFAULT NOW(),
            atualizado_em   TIMESTAMP DEFAULT NOW(),
            UNIQUE (matricula, semestre, ano_letivo)
        );

        CREATE TABLE IF NOT EXISTS respostas_subtemas (
            id           SERIAL PRIMARY KEY,
            relatorio_id INTEGER REFERENCES relatorios_semestrais(id) ON DELETE CASCADE,
            subtema_id   INTEGER REFERENCES subtemas(id),
            resposta     VARCHAR(30),
            UNIQUE (relatorio_id, subtema_id)
        );
    """

    def _connect():
        return psycopg2.connect(DATABASE_URL)

    def _seed_admin(conn):
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM usuarios WHERE username = %s", (ADMIN_USER,))
            if not cur.fetchone():
                cur.execute(
                    "INSERT INTO usuarios (username, password, nome, role) VALUES (%s,%s,%s,%s)",
                    (ADMIN_USER, hash_password(ADMIN_PASS), "Administrador", "admin"),
                )
        conn.commit()

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
                _seed_admin(conn)
            finally:
                conn.close()
            _ready = True

    # ── Usuários ──────────────────────────────────────────────────────────────

    def authenticate_user(username: str, password: str) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM usuarios WHERE username = %s AND ativo = TRUE",
                    (username,),
                )
                user = cur.fetchone()
            if user and verify_password(password, user["password"]):
                return dict(user)
            return None
        finally:
            conn.close()

    def get_all_usuarios() -> list:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, username, nome, role, ativo, criado_em FROM usuarios ORDER BY nome"
                )
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def create_usuario(username: str, password: str, nome: str, role: str = "professora") -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO usuarios (username, password, nome, role) VALUES (%s,%s,%s,%s) RETURNING id, username, nome, role, ativo",
                    (username, hash_password(password), nome, role),
                )
                user = cur.fetchone()
            conn.commit()
            return dict(user)
        finally:
            conn.close()

    def update_usuario_senha(user_id: int, nova_senha: str) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET password = %s WHERE id = %s",
                    (hash_password(nova_senha), user_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def delete_usuario(user_id: int) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM usuarios WHERE id = %s AND role != 'admin'", (user_id,)
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def get_usuario_by_id(user_id: int) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, username, nome, role, ativo FROM usuarios WHERE id = %s",
                    (user_id,),
                )
                r = cur.fetchone()
            return dict(r) if r else None
        finally:
            conn.close()

    # ── Temas e Subtemas ──────────────────────────────────────────────────────

    def get_all_temas() -> list:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM temas WHERE ativo = TRUE ORDER BY ordem, id"
                )
                temas = [dict(r) for r in cur.fetchall()]
                for tema in temas:
                    cur.execute(
                        "SELECT * FROM subtemas WHERE tema_id = %s AND ativo = TRUE ORDER BY ordem, id",
                        (tema["id"],),
                    )
                    tema["subtemas"] = [dict(r) for r in cur.fetchall()]
            return temas
        finally:
            conn.close()

    def create_tema(nome: str, ordem: int = 0) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO temas (nome, ordem) VALUES (%s,%s) RETURNING *",
                    (nome, ordem),
                )
                tema = cur.fetchone()
            conn.commit()
            return dict(tema)
        finally:
            conn.close()

    def update_tema(tema_id: int, nome: str) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE temas SET nome = %s WHERE id = %s", (nome, tema_id))
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def delete_tema(tema_id: int) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE temas SET ativo = FALSE WHERE id = %s", (tema_id,))
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def create_subtema(tema_id: int, descricao: str, ordem: int = 0) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO subtemas (tema_id, descricao, ordem) VALUES (%s,%s,%s) RETURNING *",
                    (tema_id, descricao, ordem),
                )
                st = cur.fetchone()
            conn.commit()
            return dict(st)
        finally:
            conn.close()

    def delete_subtema(subtema_id: int) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE subtemas SET ativo = FALSE WHERE id = %s", (subtema_id,)
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    # ── Relatórios Semestrais ─────────────────────────────────────────────────

    def get_relatorio(matricula: str, semestre: int, ano_letivo: str = "2026") -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM relatorios_semestrais WHERE matricula=%s AND semestre=%s AND ano_letivo=%s",
                    (matricula, semestre, ano_letivo),
                )
                r = cur.fetchone()
            return dict(r) if r else None
        finally:
            conn.close()

    def get_relatorio_by_id(relatorio_id: int) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM relatorios_semestrais WHERE id = %s", (relatorio_id,)
                )
                r = cur.fetchone()
            return dict(r) if r else None
        finally:
            conn.close()

    def get_all_relatorios(turma: str = None, semestre: int = None, status: str = None) -> list:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT r.*, a.nome AS aluno_nome, a.turma, a.periodo,
                           u.nome AS professora_nome
                    FROM relatorios_semestrais r
                    LEFT JOIN alunos a ON r.matricula = a.matricula
                    LEFT JOIN usuarios u ON r.professora_id = u.id
                    WHERE 1=1
                """
                params = []
                if turma:
                    query += " AND a.turma = %s"
                    params.append(turma)
                if semestre:
                    query += " AND r.semestre = %s"
                    params.append(semestre)
                if status:
                    query += " AND r.status = %s"
                    params.append(status)
                query += " ORDER BY a.turma, a.nome, r.semestre"
                cur.execute(query, params)
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def upsert_relatorio(matricula: str, semestre: int, professora_id: int, ano_letivo: str = "2026") -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    INSERT INTO relatorios_semestrais (matricula, semestre, ano_letivo, professora_id)
                    VALUES (%s,%s,%s,%s)
                    ON CONFLICT (matricula, semestre, ano_letivo) DO UPDATE SET atualizado_em = NOW()
                    RETURNING *
                """, (matricula, semestre, ano_letivo, professora_id))
                r = cur.fetchone()
            conn.commit()
            return dict(r)
        finally:
            conn.close()

    def update_relatorio(relatorio_id: int, status: str, descricao_final: str = "") -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                if status == "concluido":
                    cur.execute("""
                        UPDATE relatorios_semestrais
                        SET status=%s, descricao_final=%s, confirmado_em=NOW(), atualizado_em=NOW()
                        WHERE id=%s
                    """, (status, descricao_final, relatorio_id))
                else:
                    cur.execute("""
                        UPDATE relatorios_semestrais
                        SET status=%s, descricao_final=%s, atualizado_em=NOW()
                        WHERE id=%s
                    """, (status, descricao_final, relatorio_id))
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def get_relatorios_por_professora(professora_id: int) -> list:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT r.*, a.nome AS aluno_nome, a.turma, a.periodo
                    FROM relatorios_semestrais r
                    JOIN alunos a ON r.matricula = a.matricula
                    WHERE r.professora_id = %s
                    ORDER BY a.turma, a.nome, r.semestre
                """, (professora_id,))
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    # ── Respostas por Subtema ─────────────────────────────────────────────────

    def get_respostas(relatorio_id: int) -> dict:
        """Retorna {subtema_id: resposta} para um relatório."""
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT subtema_id, resposta FROM respostas_subtemas WHERE relatorio_id = %s",
                    (relatorio_id,),
                )
                return {r["subtema_id"]: r["resposta"] for r in cur.fetchall()}
        finally:
            conn.close()

    def save_respostas(relatorio_id: int, respostas: dict) -> None:
        """Salva ou atualiza respostas. respostas = {subtema_id: resposta}."""
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                for subtema_id, resposta in respostas.items():
                    cur.execute("""
                        INSERT INTO respostas_subtemas (relatorio_id, subtema_id, resposta)
                        VALUES (%s,%s,%s)
                        ON CONFLICT (relatorio_id, subtema_id) DO UPDATE SET resposta = EXCLUDED.resposta
                    """, (relatorio_id, int(subtema_id), resposta))
            conn.commit()
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    from datetime import datetime

    DB_FILE = "banco_relatorio.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return _new_db()

    def _new_db() -> dict:
        db = {
            "usuarios": [],
            "temas": [],
            "subtemas": [],
            "relatorios_semestrais": [],
            "respostas_subtemas": [],
            "_seq": {
                "usuarios": 2,
                "temas": 1,
                "subtemas": 1,
                "relatorios_semestrais": 1,
                "respostas_subtemas": 1,
            },
        }
        db["usuarios"].append({
            "id": 1,
            "username": ADMIN_USER,
            "password": hash_password(ADMIN_PASS),
            "nome": "Administrador",
            "role": "admin",
            "ativo": True,
        })
        _save(db)
        return db

    def _save(db: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def _next_id(db: dict, table: str) -> int:
        seq = db["_seq"].get(table, 1)
        db["_seq"][table] = seq + 1
        return seq

    # ── Usuários ──────────────────────────────────────────────────────────────

    def authenticate_user(username: str, password: str) -> dict | None:
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["username"] == username and u.get("ativo", True):
                    if verify_password(password, u["password"]):
                        return {k: v for k, v in u.items() if k != "password"}
            return None

    def get_all_usuarios() -> list:
        with _lock:
            db = _load()
            return [{k: v for k, v in u.items() if k != "password"} for u in db["usuarios"]]

    def create_usuario(username: str, password: str, nome: str, role: str = "professora") -> dict:
        with _lock:
            db = _load()
            if any(u["username"] == username for u in db["usuarios"]):
                raise ValueError("Usuário já existe")
            new_id = _next_id(db, "usuarios")
            user = {
                "id": new_id,
                "username": username,
                "password": hash_password(password),
                "nome": nome,
                "role": role,
                "ativo": True,
            }
            db["usuarios"].append(user)
            _save(db)
            return {k: v for k, v in user.items() if k != "password"}

    def update_usuario_senha(user_id: int, nova_senha: str) -> bool:
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id:
                    u["password"] = hash_password(nova_senha)
                    _save(db)
                    return True
            return False

    def delete_usuario(user_id: int) -> bool:
        with _lock:
            db = _load()
            for i, u in enumerate(db["usuarios"]):
                if u["id"] == user_id and u["role"] != "admin":
                    db["usuarios"].pop(i)
                    _save(db)
                    return True
            return False

    def get_usuario_by_id(user_id: int) -> dict | None:
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id:
                    return {k: v for k, v in u.items() if k != "password"}
            return None

    # ── Temas e Subtemas ──────────────────────────────────────────────────────

    def get_all_temas() -> list:
        with _lock:
            db = _load()
            temas = sorted(
                [dict(t) for t in db["temas"] if t.get("ativo", True)],
                key=lambda t: (t.get("ordem", 0), t["id"]),
            )
            for tema in temas:
                tema["subtemas"] = sorted(
                    [dict(s) for s in db["subtemas"] if s["tema_id"] == tema["id"] and s.get("ativo", True)],
                    key=lambda s: (s.get("ordem", 0), s["id"]),
                )
            return temas

    def create_tema(nome: str, ordem: int = 0) -> dict:
        with _lock:
            db = _load()
            new_id = _next_id(db, "temas")
            tema = {"id": new_id, "nome": nome, "ordem": ordem, "ativo": True}
            db["temas"].append(tema)
            _save(db)
            return tema

    def update_tema(tema_id: int, nome: str) -> bool:
        with _lock:
            db = _load()
            for t in db["temas"]:
                if t["id"] == tema_id:
                    t["nome"] = nome
                    _save(db)
                    return True
            return False

    def delete_tema(tema_id: int) -> bool:
        with _lock:
            db = _load()
            for t in db["temas"]:
                if t["id"] == tema_id:
                    t["ativo"] = False
                    _save(db)
                    return True
            return False

    def create_subtema(tema_id: int, descricao: str, ordem: int = 0) -> dict:
        with _lock:
            db = _load()
            new_id = _next_id(db, "subtemas")
            st = {"id": new_id, "tema_id": tema_id, "descricao": descricao, "ordem": ordem, "ativo": True}
            db["subtemas"].append(st)
            _save(db)
            return st

    def delete_subtema(subtema_id: int) -> bool:
        with _lock:
            db = _load()
            for s in db["subtemas"]:
                if s["id"] == subtema_id:
                    s["ativo"] = False
                    _save(db)
                    return True
            return False

    # ── Relatórios Semestrais ─────────────────────────────────────────────────

    def get_relatorio(matricula: str, semestre: int, ano_letivo: str = "2026") -> dict | None:
        with _lock:
            db = _load()
            for r in db["relatorios_semestrais"]:
                if r["matricula"] == matricula and r["semestre"] == semestre and r["ano_letivo"] == ano_letivo:
                    return dict(r)
            return None

    def get_relatorio_by_id(relatorio_id: int) -> dict | None:
        with _lock:
            db = _load()
            for r in db["relatorios_semestrais"]:
                if r["id"] == relatorio_id:
                    return dict(r)
            return None

    def get_all_relatorios(turma: str = None, semestre: int = None, status: str = None) -> list:
        from db import get_all_alunos
        with _lock:
            db = _load()
        alunos = get_all_alunos()
        usuarios = {u["id"]: u for u in db["usuarios"]}
        result = []
        for r in db["relatorios_semestrais"]:
            if semestre and r["semestre"] != semestre:
                continue
            if status and r["status"] != status:
                continue
            aluno = alunos.get(r["matricula"], {})
            if turma and aluno.get("turma") != turma:
                continue
            prof = usuarios.get(r.get("professora_id"))
            row = dict(r)
            row["aluno_nome"] = aluno.get("nome", "")
            row["turma"] = aluno.get("turma", "")
            row["periodo"] = aluno.get("periodo", "")
            row["professora_nome"] = prof["nome"] if prof else ""
            result.append(row)
        return sorted(result, key=lambda x: (x.get("turma", ""), x.get("aluno_nome", ""), x.get("semestre", 0)))

    def upsert_relatorio(matricula: str, semestre: int, professora_id: int, ano_letivo: str = "2026") -> dict:
        with _lock:
            db = _load()
            for r in db["relatorios_semestrais"]:
                if r["matricula"] == matricula and r["semestre"] == semestre and r["ano_letivo"] == ano_letivo:
                    return dict(r)
            new_id = _next_id(db, "relatorios_semestrais")
            r = {
                "id": new_id,
                "matricula": matricula,
                "semestre": semestre,
                "ano_letivo": ano_letivo,
                "professora_id": professora_id,
                "status": "pendente",
                "descricao_final": "",
                "confirmado_em": None,
            }
            db["relatorios_semestrais"].append(r)
            _save(db)
            return dict(r)

    def update_relatorio(relatorio_id: int, status: str, descricao_final: str = "") -> bool:
        with _lock:
            db = _load()
            for r in db["relatorios_semestrais"]:
                if r["id"] == relatorio_id:
                    r["status"] = status
                    r["descricao_final"] = descricao_final
                    if status == "concluido":
                        r["confirmado_em"] = datetime.now().isoformat()
                    _save(db)
                    return True
            return False

    def get_relatorios_por_professora(professora_id: int) -> list:
        from db import get_all_alunos
        with _lock:
            db = _load()
        alunos = get_all_alunos()
        result = []
        for r in db["relatorios_semestrais"]:
            if r.get("professora_id") != professora_id:
                continue
            aluno = alunos.get(r["matricula"], {})
            row = dict(r)
            row["aluno_nome"] = aluno.get("nome", "")
            row["turma"] = aluno.get("turma", "")
            row["periodo"] = aluno.get("periodo", "")
            result.append(row)
        return sorted(result, key=lambda x: (x.get("turma", ""), x.get("aluno_nome", ""), x.get("semestre", 0)))

    # ── Respostas por Subtema ─────────────────────────────────────────────────

    def get_respostas(relatorio_id: int) -> dict:
        with _lock:
            db = _load()
            return {
                r["subtema_id"]: r["resposta"]
                for r in db["respostas_subtemas"]
                if r["relatorio_id"] == relatorio_id
            }

    def save_respostas(relatorio_id: int, respostas: dict) -> None:
        with _lock:
            db = _load()
            existing = {
                r["subtema_id"]: r
                for r in db["respostas_subtemas"]
                if r["relatorio_id"] == relatorio_id
            }
            for subtema_id, resposta in respostas.items():
                sid = int(subtema_id)
                if sid in existing:
                    existing[sid]["resposta"] = resposta
                else:
                    new_id = _next_id(db, "respostas_subtemas")
                    db["respostas_subtemas"].append({
                        "id": new_id,
                        "relatorio_id": relatorio_id,
                        "subtema_id": sid,
                        "resposta": resposta,
                    })
            _save(db)
