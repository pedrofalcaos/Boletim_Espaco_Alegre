# 🏫 Boletim Online — Escola Espaço Alegre

## Como funciona

### Para os pais
Acessa a URL do site → digita a matrícula → vê **só** o boletim do próprio filho.
Nenhum pai consegue ver dados de outro aluno.

### Para a professora / coordenação
Acessa `/admin` → faz login → pode **adicionar, editar e excluir** alunos e notas.

---

## 🔐 Credenciais padrão (MUDE antes de publicar!)

| Campo    | Valor padrão |
|----------|-------------|
| Usuário  | `admin`     |
| Senha    | `escola2026` |

Para mudar, defina variáveis de ambiente antes de iniciar:
```bash
export ADMIN_USER=professora
export ADMIN_PASSWORD=suasenhaforte
export SECRET_KEY=qualquer-texto-secreto-longo
uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 🚀 Subir no Railway (gratuito)

1. Acesse https://railway.app e crie conta
2. **New Project → Deploy from GitHub** (suba os arquivos num repositório)
3. Em **Variables**, adicione:
   - `ADMIN_PASSWORD` = sua senha
   - `SECRET_KEY` = texto aleatório longo
4. Em **Settings → Start Command**:
   ```
   uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
5. Pronto! Você recebe uma URL pública para compartilhar com os pais.

---

## 📁 Arquivos

| Arquivo          | Função |
|------------------|--------|
| `main.py`        | Rotas do servidor (FastAPI) |
| `db.py`          | Leitura e escrita do banco (JSON) |
| `dados.py`       | Dados iniciais dos alunos |
| `boletim_html.py`| Gera o HTML do boletim |
| `templates.py`   | HTML do painel administrativo |
| `auth.py`        | Login e sessão segura |
| `banco.json`     | Criado automaticamente na 1ª execução |

---

## ➕ Adicionar alunos

**Via painel:** acesse `/admin`, clique em **＋ Novo Aluno** e preencha o formulário.

**Via código:** edite `dados.py` e reinicie o servidor.
