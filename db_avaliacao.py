"""
Avaliações em PDF vinculadas a cada aluno (ex.: Avaliação de Inglês).

Estrutura genérica e escalável: a mesma tabela atende a qualquer disciplina
(Inglês, Espanhol, Artes, Música…) através do campo `disciplina`. Para cada
disciplina há uma pasta no projeto onde os PDFs ficam guardados.

Backends: PostgreSQL (Railway) quando DATABASE_URL existe; JSON local caso
contrário — mesmo padrão de db.py / db_relatorio.py.
"""
import json, os, re, threading, unicodedata
from datetime import datetime

DATABASE_URL = os.environ.get("DATABASE_URL")
_lock = threading.Lock()

# ── Disciplinas suportadas ──────────────────────────────────────────────────
# Para adicionar uma nova disciplina no futuro, basta acrescentar uma entrada
# aqui e criar a pasta correspondente — nenhuma outra mudança é necessária.
DISCIPLINAS_PDF = {
    "ingles": {"label": "Avaliação de Inglês", "pasta": "avaliacao_ingles", "icone": "🇬🇧"},
}
DISCIPLINA_PADRAO = "ingles"

# Limite de tamanho de upload (bytes)
MAX_UPLOAD_BYTES = 15 * 1024 * 1024  # 15 MB


# ── Utilitários de arquivo (independentes do backend) ────────────────────────
def disciplina_valida(disciplina: str) -> bool:
    return disciplina in DISCIPLINAS_PDF

def info_disciplina(disciplina: str) -> dict:
    return DISCIPLINAS_PDF.get(disciplina, DISCIPLINAS_PDF[DISCIPLINA_PADRAO])

def _pasta(disciplina: str) -> str:
    pasta = info_disciplina(disciplina)["pasta"]
    os.makedirs(pasta, exist_ok=True)
    return pasta

def listar_arquivos(disciplina: str = DISCIPLINA_PADRAO) -> list[str]:
    """Nomes dos PDFs disponíveis na pasta da disciplina (ordenados)."""
    pasta = _pasta(disciplina)
    try:
        nomes = [n for n in os.listdir(pasta) if n.lower().endswith(".pdf")]
    except FileNotFoundError:
        nomes = []
    return sorted(nomes, key=lambda s: s.lower())

def resolver_caminho(disciplina: str, arquivo: str) -> str | None:
    """Caminho absoluto seguro do PDF, ou None se inválido/inexistente.

    Protege contra path traversal: só aceita um nome de arquivo simples dentro
    da pasta da disciplina (sem subpastas, sem '..')."""
    if not arquivo:
        return None
    base = os.path.basename(arquivo)            # descarta qualquer diretório
    if base != arquivo or not base.lower().endswith(".pdf"):
        return None
    pasta = os.path.abspath(_pasta(disciplina))
    caminho = os.path.abspath(os.path.join(pasta, base))
    if os.path.commonpath([pasta, caminho]) != pasta:
        return None
    return caminho if os.path.isfile(caminho) else None


def _sanitizar_nome(nome: str) -> str:
    """Gera um nome de arquivo seguro preservando acentos/espaços legíveis."""
    nome = os.path.basename(nome).strip()
    nome = nome.replace("/", "-").replace("\\", "-")
    nome = re.sub(r'[\x00-\x1f<>:"|?*]', "", nome)
    if not nome.lower().endswith(".pdf"):
        nome += ".pdf"
    return nome or "avaliacao.pdf"

def salvar_upload(disciplina: str, conteudo: bytes, nome_original: str) -> str:
    """Salva o PDF na pasta da disciplina, sem sobrescrever outro arquivo.
    Retorna o nome final usado em disco."""
    pasta = _pasta(disciplina)
    base = _sanitizar_nome(nome_original)
    destino = os.path.join(pasta, base)
    if os.path.exists(destino):
        raiz, ext = os.path.splitext(base)
        i = 2
        while os.path.exists(os.path.join(pasta, f"{raiz} ({i}){ext}")):
            i += 1
        base = f"{raiz} ({i}){ext}"
        destino = os.path.join(pasta, base)
    with open(destino, "wb") as f:
        f.write(conteudo)
    return base


# ── Sugestão automática de vínculo por nome do arquivo ───────────────────────
def _norm(s: str) -> str:
    """Normaliza para comparação: sem acento, minúsculo, espaços colapsados."""
    s = unicodedata.normalize("NFKD", s or "")
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s

def _nome_do_arquivo(arquivo: str) -> str:
    """Extrai o nome do aluno embutido no arquivo: 'Nome - TURMA.pdf' -> 'Nome'."""
    base = os.path.splitext(os.path.basename(arquivo))[0]
    return base.split(" - ")[0].strip()

def sugerir_vinculos(alunos: dict, disciplina: str = DISCIPLINA_PADRAO) -> dict:
    """Mapeia matricula -> arquivo sugerido, casando o nome do aluno com o nome
    embutido no arquivo (ex.: 'João Pedro - INFANTIL 4A.pdf' -> aluno João Pedro).

    alunos: {matricula: {nome, turma, ...}}"""
    arquivos = listar_arquivos(disciplina)
    por_nome = {_norm(_nome_do_arquivo(a)): a for a in arquivos}
    sugestoes = {}
    for mat, al in alunos.items():
        chave = _norm(al.get("nome", ""))
        if chave and chave in por_nome:
            sugestoes[mat] = por_nome[chave]
    return sugestoes


# ══════════════════════════════════════════════════════════════════
#  BACKEND  PostgreSQL
# ══════════════════════════════════════════════════════════════════
if DATABASE_URL:
    import psycopg2
    from psycopg2.extras import RealDictCursor

    _ready = False
    _init_lock = threading.Lock()

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS avaliacoes_pdf (
            id            SERIAL PRIMARY KEY,
            matricula     VARCHAR(20)  NOT NULL,
            disciplina    VARCHAR(40)  NOT NULL DEFAULT 'ingles',
            arquivo       VARCHAR(300) NOT NULL,
            nome_original VARCHAR(300) NOT NULL DEFAULT '',
            enviado_por   VARCHAR(120) NOT NULL DEFAULT '',
            criado_em     TIMESTAMP DEFAULT NOW(),
            atualizado_em TIMESTAMP DEFAULT NOW(),
            UNIQUE (matricula, disciplina)
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

    def _row(r) -> dict:
        d = dict(r)
        for k in ("criado_em", "atualizado_em"):
            if d.get(k) is not None:
                d[k] = str(d[k])[:19]
        return d

    def get_avaliacao(matricula: str, disciplina: str = DISCIPLINA_PADRAO) -> dict | None:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM avaliacoes_pdf WHERE matricula=%s AND disciplina=%s",
                    (matricula, disciplina),
                )
                r = cur.fetchone()
            return _row(r) if r else None
        finally:
            conn.close()

    def get_avaliacoes_map(disciplina: str = DISCIPLINA_PADRAO) -> dict:
        _init()
        conn = _connect()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT * FROM avaliacoes_pdf WHERE disciplina=%s", (disciplina,)
                )
                return {r["matricula"]: _row(r) for r in cur.fetchall()}
        finally:
            conn.close()

    def set_avaliacao(matricula: str, arquivo: str, nome_original: str,
                      enviado_por: str, disciplina: str = DISCIPLINA_PADRAO) -> None:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO avaliacoes_pdf
                           (matricula, disciplina, arquivo, nome_original, enviado_por)
                       VALUES (%s,%s,%s,%s,%s)
                       ON CONFLICT (matricula, disciplina) DO UPDATE SET
                           arquivo=EXCLUDED.arquivo,
                           nome_original=EXCLUDED.nome_original,
                           enviado_por=EXCLUDED.enviado_por,
                           atualizado_em=NOW()""",
                    (matricula, disciplina, arquivo, nome_original, enviado_por),
                )
            conn.commit()
        finally:
            conn.close()

    def remover_avaliacao(matricula: str, disciplina: str = DISCIPLINA_PADRAO) -> bool:
        _init()
        conn = _connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "DELETE FROM avaliacoes_pdf WHERE matricula=%s AND disciplina=%s",
                    (matricula, disciplina),
                )
                ok = cur.rowcount > 0
            conn.commit()
            return ok
        finally:
            conn.close()


# ══════════════════════════════════════════════════════════════════
#  BACKEND  JSON local (sem DATABASE_URL)
# ══════════════════════════════════════════════════════════════════
else:
    DB_FILE = "avaliacoes_pdf.json"

    def _load() -> dict:
        if os.path.exists(DB_FILE):
            with open(DB_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"itens": [], "_seq": 1}

    def _save(db: dict):
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

    def get_avaliacao(matricula: str, disciplina: str = DISCIPLINA_PADRAO) -> dict | None:
        with _lock:
            db = _load()
            for it in db["itens"]:
                if it["matricula"] == matricula and it["disciplina"] == disciplina:
                    return dict(it)
            return None

    def get_avaliacoes_map(disciplina: str = DISCIPLINA_PADRAO) -> dict:
        with _lock:
            db = _load()
            return {it["matricula"]: dict(it)
                    for it in db["itens"] if it["disciplina"] == disciplina}

    def set_avaliacao(matricula: str, arquivo: str, nome_original: str,
                      enviado_por: str, disciplina: str = DISCIPLINA_PADRAO) -> None:
        with _lock:
            db = _load()
            agora = datetime.now().isoformat()[:19]
            for it in db["itens"]:
                if it["matricula"] == matricula and it["disciplina"] == disciplina:
                    it.update(arquivo=arquivo, nome_original=nome_original,
                              enviado_por=enviado_por, atualizado_em=agora)
                    _save(db)
                    return
            db["itens"].append({
                "id": db.get("_seq", 1),
                "matricula": matricula,
                "disciplina": disciplina,
                "arquivo": arquivo,
                "nome_original": nome_original,
                "enviado_por": enviado_por,
                "criado_em": agora,
                "atualizado_em": agora,
            })
            db["_seq"] = db.get("_seq", 1) + 1
            _save(db)

    def remover_avaliacao(matricula: str, disciplina: str = DISCIPLINA_PADRAO) -> bool:
        with _lock:
            db = _load()
            antes = len(db["itens"])
            db["itens"] = [it for it in db["itens"]
                           if not (it["matricula"] == matricula and it["disciplina"] == disciplina)]
            if len(db["itens"]) != antes:
                _save(db)
                return True
            return False
