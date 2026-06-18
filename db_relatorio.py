"""
Banco de dados para o módulo de Relatório Semestral da Educação Infantil.
Mesma estratégia de db.py: PostgreSQL (Railway) ou JSON local.
"""
import json, os, threading
from auth import hash_password, verify_password, generate_temp_password, ADMIN_USER, ADMIN_PASS

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()

# Turmas de Ed. Infantil — usadas no filtro de subtemas e na UI admin
TURMAS_INFANTIL = [
    "Infantil 1 – A", "Infantil 1 – B",
    "Infantil 2 – A", "Infantil 2 – B",
    "Infantil 3 – A", "Infantil 3 – B",
    "Infantil 4 – A", "Infantil 4 – B",
    "Infantil 5 – A",
]


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
            id               SERIAL PRIMARY KEY,
            username         VARCHAR(100) UNIQUE NOT NULL,
            password         VARCHAR(400) NOT NULL,
            nome             VARCHAR(255) NOT NULL DEFAULT '',
            role             VARCHAR(20)  NOT NULL DEFAULT 'professora',
            turmas           JSONB        NOT NULL DEFAULT '[]',
            ativo            BOOLEAN DEFAULT TRUE,
            senha_temporaria BOOLEAN DEFAULT FALSE,
            criado_em        TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS topicos (
            id        SERIAL PRIMARY KEY,
            nome      VARCHAR(255) NOT NULL,
            ordem     INTEGER DEFAULT 0,
            ativo     BOOLEAN DEFAULT TRUE,
            turmas    JSONB DEFAULT '[]',
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS temas (
            id        SERIAL PRIMARY KEY,
            topico_id INTEGER REFERENCES topicos(id) ON DELETE SET NULL,
            nome      VARCHAR(255) NOT NULL,
            ordem     INTEGER DEFAULT 0,
            ativo     BOOLEAN DEFAULT TRUE,
            turmas    JSONB DEFAULT '[]',
            criado_em TIMESTAMP DEFAULT NOW()
        );

        CREATE TABLE IF NOT EXISTS subtemas (
            id        SERIAL PRIMARY KEY,
            tema_id   INTEGER REFERENCES temas(id) ON DELETE CASCADE,
            descricao TEXT NOT NULL,
            ordem     INTEGER DEFAULT 0,
            ativo     BOOLEAN DEFAULT TRUE,
            turmas    JSONB DEFAULT '[]'
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

    _SEED_USUARIOS = [
        # (username, senha, nome, role)
        (ADMIN_USER, ADMIN_PASS, "Administrador", "admin"),
        ("vanessa@espacoalegre.com",  "EA@2026", "Vanessa",  "professora"),
        ("erika@espacoalegre.com",    "EA@2026", "Erika",    "professora"),
        ("cilene@espacoalegre.com",   "EA@2026", "Cilene",   "professora"),
        ("patricia@espacoalegre.com", "EA@2026", "Patrícia", "professora"),
        ("fabiana@espacoalegre.com",  "EA@2026", "Fabiana",  "professora"),
        ("andrea@espacoalegre.com",   "EA@2026", "Andrea",   "professora"),
    ]

    def _seed_admin(conn):
        with conn.cursor() as cur:
            for username, senha, nome, role in _SEED_USUARIOS:
                cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
                if not cur.fetchone():
                    cur.execute(
                        "INSERT INTO usuarios (username, password, nome, role) VALUES (%s,%s,%s,%s)",
                        (username, hash_password(senha), nome, role),
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
                    # Migrações para instalações existentes
                    cur.execute("ALTER TABLE subtemas ADD COLUMN IF NOT EXISTS turmas JSONB DEFAULT '[]'")
                    cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS turmas JSONB DEFAULT '[]'")
                    cur.execute("ALTER TABLE temas ADD COLUMN IF NOT EXISTS topico_id INTEGER REFERENCES topicos(id) ON DELETE SET NULL")
                    cur.execute("ALTER TABLE topicos ADD COLUMN IF NOT EXISTS turmas JSONB DEFAULT '[]'")
                    cur.execute("ALTER TABLE temas ADD COLUMN IF NOT EXISTS turmas JSONB DEFAULT '[]'")
                    cur.execute("ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS senha_temporaria BOOLEAN DEFAULT FALSE")
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
                    "SELECT id, username, nome, role, turmas, ativo, senha_temporaria, criado_em "
                    "FROM usuarios ORDER BY nome"
                )
                return [dict(r) for r in cur.fetchall()]
        finally:
            conn.close()

    def get_usuario_by_id(user_id: int) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT id, username, nome, role, turmas, ativo, senha_temporaria "
                    "FROM usuarios WHERE id = %s",
                    (user_id,),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        finally:
            conn.close()

    def create_usuario(username: str, password: str, nome: str, role: str = "professora", turmas: list = None) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO usuarios (username, password, nome, role, turmas) VALUES (%s,%s,%s,%s,%s) RETURNING id, username, nome, role, turmas, ativo",
                    (username, hash_password(password), nome, role, json.dumps(turmas or [], ensure_ascii=False)),
                )
                user = cur.fetchone()
            conn.commit()
            return dict(user)
        finally:
            conn.close()

    def update_usuario_turmas(user_id: int, turmas: list) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET turmas = %s WHERE id = %s",
                    (json.dumps(turmas, ensure_ascii=False), user_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def update_usuario_senha(user_id: int, nova_senha: str) -> bool:
        """Define nova senha definida pelo próprio usuário e encerra o estado de senha temporária."""
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET password = %s, senha_temporaria = FALSE WHERE id = %s",
                    (hash_password(nova_senha), user_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def reset_usuario_senha(user_id: int) -> str | None:
        """Gera uma senha aleatória, marca como temporária e retorna a senha em texto puro."""
        _init()
        nova_senha = generate_temp_password()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE usuarios SET password = %s, senha_temporaria = TRUE "
                    "WHERE id = %s AND role != 'admin'",
                    (hash_password(nova_senha), user_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return nova_senha if ok else None
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

    # ── Tópicos ───────────────────────────────────────────────────────────────

    def get_all_topicos() -> list:
        """Retorna hierarquia completa: Tópico → Tema → Subtema."""
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM topicos WHERE ativo = TRUE ORDER BY ordem, id")
                topicos = [dict(r) for r in cur.fetchall()]
                cur.execute("SELECT * FROM temas WHERE ativo = TRUE ORDER BY ordem, id")
                temas = [dict(r) for r in cur.fetchall()]
                for tema in temas:
                    cur.execute(
                        "SELECT * FROM subtemas WHERE tema_id = %s AND ativo = TRUE ORDER BY ordem, id",
                        (tema["id"],),
                    )
                    tema["subtemas"] = [dict(r) for r in cur.fetchall()]
            topico_map = {tp["id"]: tp for tp in topicos}
            for tp in topicos:
                tp["temas"] = []
            sem_topico = {"id": None, "nome": "Sem tópico", "temas": []}
            for tema in temas:
                tid = tema.get("topico_id")
                if tid and tid in topico_map:
                    topico_map[tid]["temas"].append(tema)
                else:
                    sem_topico["temas"].append(tema)
            result = list(topicos)  # todos os tópicos, incluindo os sem temas
            if sem_topico["temas"]:
                result.append(sem_topico)
            return result
        finally:
            conn.close()

    def create_topico(nome: str, ordem: int = 0) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO topicos (nome, ordem) VALUES (%s,%s) RETURNING *",
                    (nome, ordem),
                )
                tp = cur.fetchone()
            conn.commit()
            return dict(tp)
        finally:
            conn.close()

    def update_topico(topico_id: int, nome: str) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute("UPDATE topicos SET nome = %s WHERE id = %s", (nome, topico_id))
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def delete_topico(topico_id: int) -> bool:
        """Remove tópico e, em cascata, todos os seus temas e subtemas."""
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                # Busca temas do tópico
                cur.execute("SELECT id FROM temas WHERE topico_id = %s AND ativo = TRUE", (topico_id,))
                tema_ids = [r[0] for r in cur.fetchall()]
                # Desativa subtemas de cada tema
                if tema_ids:
                    cur.execute(
                        "UPDATE subtemas SET ativo = FALSE WHERE tema_id = ANY(%s)",
                        (tema_ids,),
                    )
                # Desativa temas
                cur.execute("UPDATE temas SET ativo = FALSE WHERE topico_id = %s", (topico_id,))
                # Desativa tópico
                cur.execute("UPDATE topicos SET ativo = FALSE WHERE id = %s", (topico_id,))
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def update_topico_turmas(topico_id: int, turmas: list) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE topicos SET turmas = %s WHERE id = %s",
                    (json.dumps(turmas, ensure_ascii=False), topico_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def update_tema_turmas(tema_id: int, turmas: list) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE temas SET turmas = %s WHERE id = %s",
                    (json.dumps(turmas, ensure_ascii=False), tema_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
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

    def create_tema(nome: str, ordem: int = 0, topico_id: int = None) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "INSERT INTO temas (nome, ordem, topico_id) VALUES (%s,%s,%s) RETURNING *",
                    (nome, ordem, topico_id),
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

    def update_subtema(subtema_id: int, descricao: str) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE subtemas SET descricao = %s WHERE id = %s", (descricao, subtema_id)
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
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

    def update_subtema_turmas(subtema_id: int, turmas: list) -> bool:
        """Define quais turmas este subtema avalia. Lista vazia = todas as turmas."""
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "UPDATE subtemas SET turmas = %s WHERE id = %s",
                    (json.dumps(turmas, ensure_ascii=False), subtema_id),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()

    def get_temas_para_turma(turma: str) -> list:
        """Cascata: tópico.turmas → tema.turmas → todos os subtemas do tema."""
        topicos = get_all_topicos()
        result = []
        for topico in topicos:
            tp_turmas = topico.get("turmas") or []
            if tp_turmas and turma not in tp_turmas:
                continue
            temas_filtrados = []
            for tema in topico.get("temas", []):
                t_turmas = tema.get("turmas") or []
                if t_turmas and turma not in t_turmas:
                    continue
                subtemas = tema.get("subtemas", [])
                if subtemas:
                    t = dict(tema)
                    t["subtemas"] = subtemas
                    temas_filtrados.append(t)
            if temas_filtrados:
                tp = dict(topico)
                tp["temas"] = temas_filtrados
                result.append(tp)
        return result

    def get_status_relatorios(matriculas: list, ano_letivo: str = "2026") -> dict:
        """Retorna {matricula: {semestre: status}} em uma única query — eficiente para o painel admin."""
        if not matriculas:
            return {}
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT matricula, semestre, status FROM relatorios_semestrais WHERE matricula = ANY(%s) AND ano_letivo = %s",
                    (list(matriculas), ano_letivo),
                )
                result: dict = {}
                for r in cur.fetchall():
                    result.setdefault(r["matricula"], {})[r["semestre"]] = r["status"]
            return result
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
                db = json.load(f)
            changed = False
            if "topicos" not in db:
                db["topicos"] = []
                changed = True
            if "topicos" not in db.get("_seq", {}):
                db.setdefault("_seq", {})["topicos"] = 1
                changed = True
            for tp in db.get("topicos", []):
                if "turmas" not in tp:
                    tp["turmas"] = []
                    changed = True
            for t in db.get("temas", []):
                if "turmas" not in t:
                    t["turmas"] = []
                    changed = True
            for u in db.get("usuarios", []):
                if "senha_temporaria" not in u:
                    u["senha_temporaria"] = False
                    changed = True
            if changed:
                _save(db)
            return db
        return _new_db()

    _SEED_USUARIOS_JSON = [
        # (username, senha, nome, role)
        (ADMIN_USER, ADMIN_PASS, "Administrador", "admin"),
        ("vanessa@espacoalegre.com",  "EA@2026", "Vanessa",  "professora"),
        ("erika@espacoalegre.com",    "EA@2026", "Erika",    "professora"),
        ("cilene@espacoalegre.com",   "EA@2026", "Cilene",   "professora"),
        ("patricia@espacoalegre.com", "EA@2026", "Patrícia", "professora"),
        ("fabiana@espacoalegre.com",  "EA@2026", "Fabiana",  "professora"),
        ("andrea@espacoalegre.com",   "EA@2026", "Andrea",   "professora"),
    ]

    def _new_db() -> dict:
        db = {
            "usuarios": [],
            "topicos": [],
            "temas": [],
            "subtemas": [],
            "relatorios_semestrais": [],
            "respostas_subtemas": [],
            "_seq": {
                "usuarios": len(_SEED_USUARIOS_JSON) + 1,
                "topicos": 1,
                "temas": 1,
                "subtemas": 1,
                "relatorios_semestrais": 1,
                "respostas_subtemas": 1,
            },
        }
        for i, (username, senha, nome, role) in enumerate(_SEED_USUARIOS_JSON, 1):
            db["usuarios"].append({
                "id": i,
                "username": username,
                "password": hash_password(senha),
                "nome": nome,
                "role": role,
                "turmas": [],
                "ativo": True,
                "senha_temporaria": False,
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

    def get_usuario_by_id(user_id: int) -> dict | None:
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id:
                    return {k: v for k, v in u.items() if k != "password"}
            return None

    def create_usuario(username: str, password: str, nome: str, role: str = "professora", turmas: list = None) -> dict:
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
                "turmas": turmas or [],
                "ativo": True,
            }
            db["usuarios"].append(user)
            _save(db)
            return {k: v for k, v in user.items() if k != "password"}

    def update_usuario_turmas(user_id: int, turmas: list) -> bool:
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id:
                    u["turmas"] = turmas
                    _save(db)
                    return True
            return False

    def update_usuario_senha(user_id: int, nova_senha: str) -> bool:
        """Define nova senha definida pelo próprio usuário e encerra o estado de senha temporária."""
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id:
                    u["password"] = hash_password(nova_senha)
                    u["senha_temporaria"] = False
                    _save(db)
                    return True
            return False

    def reset_usuario_senha(user_id: int) -> str | None:
        """Gera uma senha aleatória, marca como temporária e retorna a senha em texto puro."""
        with _lock:
            db = _load()
            for u in db["usuarios"]:
                if u["id"] == user_id and u["role"] != "admin":
                    nova_senha = generate_temp_password()
                    u["password"] = hash_password(nova_senha)
                    u["senha_temporaria"] = True
                    _save(db)
                    return nova_senha
            return None

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

    # ── Tópicos ───────────────────────────────────────────────────────────────

    def get_all_topicos() -> list:
        """Retorna hierarquia completa: Tópico → Tema → Subtema."""
        with _lock:
            db = _load()
            topicos = sorted(
                [dict(tp) for tp in db.get("topicos", []) if tp.get("ativo", True)],
                key=lambda tp: (tp.get("ordem", 0), tp["id"]),
            )
            temas = sorted(
                [dict(t) for t in db["temas"] if t.get("ativo", True)],
                key=lambda t: (t.get("ordem", 0), t["id"]),
            )
            for tema in temas:
                subs = []
                for s in db["subtemas"]:
                    if s["tema_id"] == tema["id"] and s.get("ativo", True):
                        sd = dict(s)
                        sd.setdefault("turmas", [])
                        subs.append(sd)
                tema["subtemas"] = sorted(subs, key=lambda s: (s.get("ordem", 0), s["id"]))
            topico_map = {tp["id"]: tp for tp in topicos}
            for tp in topicos:
                tp["temas"] = []
            sem_topico = {"id": None, "nome": "Sem tópico", "temas": []}
            for tema in temas:
                tid = tema.get("topico_id")
                if tid and tid in topico_map:
                    topico_map[tid]["temas"].append(tema)
                else:
                    sem_topico["temas"].append(tema)
            result = list(topicos)  # todos os tópicos, incluindo os sem temas
            if sem_topico["temas"]:
                result.append(sem_topico)
            return result

    def create_topico(nome: str, ordem: int = 0) -> dict:
        with _lock:
            db = _load()
            new_id = _next_id(db, "topicos")
            tp = {"id": new_id, "nome": nome, "ordem": ordem, "ativo": True}
            db["topicos"].append(tp)
            _save(db)
            return tp

    def update_topico(topico_id: int, nome: str) -> bool:
        with _lock:
            db = _load()
            for tp in db.get("topicos", []):
                if tp["id"] == topico_id:
                    tp["nome"] = nome
                    _save(db)
                    return True
            return False

    def delete_topico(topico_id: int) -> bool:
        """Remove tópico e, em cascata, todos os seus temas e subtemas."""
        with _lock:
            db = _load()
            found = False
            for tp in db.get("topicos", []):
                if tp["id"] == topico_id:
                    tp["ativo"] = False
                    found = True
                    break
            if not found:
                return False
            # Coleta ids dos temas deste tópico
            tema_ids = {
                t["id"] for t in db.get("temas", [])
                if t.get("topico_id") == topico_id and t.get("ativo", True)
            }
            # Desativa temas
            for t in db.get("temas", []):
                if t.get("topico_id") == topico_id:
                    t["ativo"] = False
            # Desativa subtemas dos temas removidos
            for s in db.get("subtemas", []):
                if s.get("tema_id") in tema_ids:
                    s["ativo"] = False
            _save(db)
            return True

    def update_topico_turmas(topico_id: int, turmas: list) -> bool:
        with _lock:
            db = _load()
            for tp in db.get("topicos", []):
                if tp["id"] == topico_id:
                    tp["turmas"] = turmas
                    _save(db)
                    return True
            return False

    def update_tema_turmas(tema_id: int, turmas: list) -> bool:
        with _lock:
            db = _load()
            for t in db["temas"]:
                if t["id"] == tema_id:
                    t["turmas"] = turmas
                    _save(db)
                    return True
            return False

    # ── Temas e Subtemas ──────────────────────────────────────────────────────

    def get_all_temas() -> list:
        with _lock:
            db = _load()
            temas = sorted(
                [dict(t) for t in db["temas"] if t.get("ativo", True)],
                key=lambda t: (t.get("ordem", 0), t["id"]),
            )
            for tema in temas:
                subs = []
                for s in db["subtemas"]:
                    if s["tema_id"] == tema["id"] and s.get("ativo", True):
                        sd = dict(s)
                        sd.setdefault("turmas", [])
                        subs.append(sd)
                tema["subtemas"] = sorted(subs, key=lambda s: (s.get("ordem", 0), s["id"]))
            return temas

    def create_tema(nome: str, ordem: int = 0, topico_id: int = None) -> dict:
        with _lock:
            db = _load()
            new_id = _next_id(db, "temas")
            tema = {"id": new_id, "topico_id": topico_id, "nome": nome, "ordem": ordem, "ativo": True}
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
            st = {"id": new_id, "tema_id": tema_id, "descricao": descricao,
                  "ordem": ordem, "ativo": True, "turmas": []}
            db["subtemas"].append(st)
            _save(db)
            return st

    def update_subtema(subtema_id: int, descricao: str) -> bool:
        with _lock:
            db = _load()
            for s in db["subtemas"]:
                if s["id"] == subtema_id:
                    s["descricao"] = descricao
                    _save(db)
                    return True
            return False

    def delete_subtema(subtema_id: int) -> bool:
        with _lock:
            db = _load()
            for s in db["subtemas"]:
                if s["id"] == subtema_id:
                    s["ativo"] = False
                    _save(db)
                    return True
            return False

    def update_subtema_turmas(subtema_id: int, turmas: list) -> bool:
        with _lock:
            db = _load()
            for s in db["subtemas"]:
                if s["id"] == subtema_id:
                    s["turmas"] = turmas
                    _save(db)
                    return True
            return False

    def get_temas_para_turma(turma: str) -> list:
        """Cascata: tópico.turmas → tema.turmas → todos os subtemas do tema."""
        topicos = get_all_topicos()
        result = []
        for topico in topicos:
            tp_turmas = topico.get("turmas") or []
            if tp_turmas and turma not in tp_turmas:
                continue
            temas_filtrados = []
            for tema in topico.get("temas", []):
                t_turmas = tema.get("turmas") or []
                if t_turmas and turma not in t_turmas:
                    continue
                subtemas = tema.get("subtemas", [])
                if subtemas:
                    t = dict(tema)
                    t["subtemas"] = subtemas
                    temas_filtrados.append(t)
            if temas_filtrados:
                tp = dict(topico)
                tp["temas"] = temas_filtrados
                result.append(tp)
        return result

    def get_status_relatorios(matriculas: list, ano_letivo: str = "2026") -> dict:
        if not matriculas:
            return {}
        with _lock:
            db = _load()
            result: dict = {}
            for r in db["relatorios_semestrais"]:
                if r["matricula"] in matriculas and r["ano_letivo"] == ano_letivo:
                    result.setdefault(r["matricula"], {})[r["semestre"]] = r["status"]
            return result

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
