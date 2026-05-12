"""
Camada de persistência simples: JSON em disco.
Em produção pode ser substituído por SQLite ou PostgreSQL.
"""
import json, os, threading
from dados import ALUNOS as ALUNOS_INICIAIS

DB_FILE = "banco.json"
_lock = threading.Lock()

DISCIPLINAS = [
    'Língua Portuguesa','Matemática','História','Geografia',
    'Ciências','Arte','Educação Física',
    'Língua Estrangeira – Inglês','Produção Textual',
]

def _load() -> dict:
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    # Primeira vez: inicializa com os dados já cadastrados
    data = {"alunos": {}}
    for mat, al in ALUNOS_INICIAIS.items():
        entry = dict(al)
        # Garante que todas as disciplinas existem nas notas
        notas = entry.get("notas", {})
        for disc in DISCIPLINAS:
            if disc not in notas:
                notas[disc] = {}
        entry["notas"] = notas
        entry["frequencia"] = entry.get("frequencia", {"total_aulas": "", "total_faltas": ""})
        entry["observacoes"] = entry.get("observacoes", "")
        data["alunos"][mat] = entry
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
    """Cria ou atualiza um aluno."""
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
        # Merge seguro
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
