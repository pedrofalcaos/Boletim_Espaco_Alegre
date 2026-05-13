import os, re
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from db import get_aluno, get_all_alunos, upsert_aluno, delete_aluno, reset_db, DISCIPLINAS
from boletim_html import gerar_boletim_html
from auth import (check_session, make_session_token,
                  ADMIN_USER, ADMIN_PASS, COOKIE_NAME, COOKIE_MAX)
from templates import login_page, admin_dashboard, aluno_form

app = FastAPI(docs_url=None, redoc_url=None)

# ── Estáticos ────────────────────────────────────────────────────────────────
@app.get("/static/logo.jpg")
async def logo():
    path = "/mnt/user-data/uploads/logo_espaço_alegre_com_qualidade_page-0001.jpg"
    if not os.path.exists(path):
        path = "static/logo.jpg"
    return FileResponse(path)

# ════════════════════════════════════════════════════════════════════════════
#  ÁREA PÚBLICA — consulta de boletim por matrícula
# ════════════════════════════════════════════════════════════════════════════

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Escola Espaço Alegre – Consulta de Boletim</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Nunito',sans-serif;
  background:linear-gradient(160deg,#1a2570 0%,#2b3990 40%,#1a5fa8 100%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px 16px;}
.card{background:#fff;border-radius:20px;box-shadow:0 8px 48px rgba(0,0,0,.28);width:100%;max-width:440px;overflow:hidden;}
.top{background:#2b3990;padding:28px 32px 22px;text-align:center;border-bottom:4px solid #f7d800;}
.top img{height:64px;object-fit:contain;margin-bottom:10px;display:block;margin-left:auto;margin-right:auto;}
.top h1{font-family:'Fredoka One',cursive;font-size:21px;color:#fff;}
.top p{font-size:11.5px;color:#b0b8e8;margin-top:4px;}
.body{padding:28px 32px 32px;}
label{display:block;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#aaa;margin-bottom:6px;}
.inp-wrap{position:relative;margin-bottom:18px;}
input[type=text]{width:100%;font-family:'Nunito',sans-serif;font-size:20px;font-weight:800;
  color:#2b3990;letter-spacing:3px;text-align:center;padding:14px 44px 14px 16px;
  border:2px solid #ddd;border-radius:12px;outline:none;background:#f7f7f5;transition:border-color .2s;}
input[type=text]:focus{border-color:#2b3990;box-shadow:0 0 0 3px rgba(43,57,144,.1);}
input::placeholder{font-size:13px;color:#ccc;letter-spacing:1px;font-weight:600;}
.clr{position:absolute;right:14px;top:50%;transform:translateY(-50%);
  background:none;border:none;font-size:18px;color:#ccc;cursor:pointer;display:none;}
input:not(:placeholder-shown)~.clr{display:block;}
.btn{width:100%;font-family:'Nunito',sans-serif;font-size:15px;font-weight:900;
  background:#2b3990;color:#fff;border:none;border-radius:12px;padding:14px;cursor:pointer;transition:background .15s;}
.btn:hover{background:#1a2570;}
.erro{display:none;background:#fef2f2;border:1px solid #fecaca;border-radius:10px;
  padding:12px 16px;margin-top:14px;font-size:13px;color:#991b1b;font-weight:600;text-align:center;}
.erro.show{display:block;}
.footer{border-top:1px solid #f0f0ee;padding:13px 32px;text-align:center;font-size:11px;color:#ccc;}
.loading{display:none;text-align:center;padding:16px 0 2px;}
.loading.show{display:block;}
.spinner{width:26px;height:26px;border:3px solid #e8eaf8;border-top-color:#2b3990;
  border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 7px;}
@keyframes spin{to{transform:rotate(360deg)}}
</style>
</head>
<body>
<div class="card">
  <div class="top">
    <img src="/static/logo.jpg" alt="Escola Espaço Alegre">
    <h1>Consulta de Boletim</h1>
    <p>Digite a matrícula do aluno para visualizar o boletim</p>
  </div>
  <div class="body">
    <form id="frm" onsubmit="buscar(event)">
      <label for="mat">Número de Matrícula</label>
      <div class="inp-wrap">
        <input type="text" id="mat" placeholder="Ex.: 20261047"
               maxlength="12" autocomplete="off" inputmode="numeric"
               oninput="limpaErro()">
        <button type="button" class="clr" onclick="limpar()">✕</button>
      </div>
      <button type="submit" class="btn">🔍 &nbsp;Ver Boletim</button>
    </form>
    <div class="loading" id="loading"><div class="spinner"></div><p style="font-size:12px;color:#aaa;">Buscando...</p></div>
    <div class="erro" id="erro">❌ Matrícula não encontrada. Verifique o número e tente novamente.</div>
  </div>
  <div class="footer">Escola Espaço Alegre &nbsp;|&nbsp; Ensino Fundamental I &nbsp;|&nbsp; 2026</div>
</div>
<script>
function buscar(e){
  e.preventDefault();
  const m=document.getElementById('mat').value.trim();
  if(!m)return;
  document.getElementById('loading').classList.add('show');
  document.getElementById('erro').classList.remove('show');
  setTimeout(()=>{ window.location.href='/boletim/'+encodeURIComponent(m); },350);
}
function limpaErro(){
  document.getElementById('erro').classList.remove('show');
  document.getElementById('loading').classList.remove('show');
}
function limpar(){
  document.getElementById('mat').value='';
  document.getElementById('mat').focus();
  limpaErro();
}
if(new URLSearchParams(location.search).get('erro')==='1')
  document.getElementById('erro').classList.add('show');
</script>
</body>
</html>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return INDEX_HTML

@app.get("/boletim/{matricula}", response_class=HTMLResponse)
async def ver_boletim(matricula: str):
    # Segurança: sanitiza a matrícula (só dígitos)
    mat_clean = re.sub(r'\D', '', matricula)
    if not mat_clean:
        return RedirectResponse("/?erro=1")

    aluno = get_aluno(mat_clean)
    if not aluno:
        return RedirectResponse("/?erro=1")

    aluno_completo = dict(aluno)
    aluno_completo['matricula'] = mat_clean
    return HTMLResponse(gerar_boletim_html(aluno_completo))

# ════════════════════════════════════════════════════════════════════════════
#  ÁREA ADMINISTRATIVA — acesso restrito por login
# ════════════════════════════════════════════════════════════════════════════

def _redir_login():
    return RedirectResponse("/admin/login", status_code=302)

@app.get("/admin/login", response_class=HTMLResponse)
async def get_login(request: Request, erro: str = ""):
    if check_session(request):
        return RedirectResponse("/admin", status_code=302)
    return login_page(erro="1" in erro)

@app.post("/admin/login")
async def post_login(
    request: Request,
    usuario: str = Form(...),
    senha:   str = Form(...),
):
    if usuario == ADMIN_USER and senha == ADMIN_PASS:
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie(COOKIE_NAME, make_session_token(),
                        max_age=COOKIE_MAX, httponly=True, samesite="lax")
        return resp
    return RedirectResponse("/admin/login?erro=1", status_code=302)

@app.get("/admin/logout")
async def logout():
    resp = RedirectResponse("/admin/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp

@app.get("/admin", response_class=HTMLResponse)
async def painel(request: Request, resetado: str = ""):
    if not check_session(request):
        return _redir_login()
    alunos = get_all_alunos()
    return admin_dashboard(alunos, resetado=bool(resetado))

@app.get("/admin/aluno/novo", response_class=HTMLResponse)
async def novo_aluno_form(request: Request):
    if not check_session(request):
        return _redir_login()
    vazio = {
        "nome":"","turma":"1º Ano – A","periodo":"Manhã",
        "professora":"","ano_letivo":"2026",
        "notas":{d:{} for d in DISCIPLINAS},
        "frequencia":{"total_aulas":"","total_faltas":""},
        "observacoes":"",
    }
    return aluno_form("", vazio, novo=True)

@app.get("/admin/aluno/{matricula}", response_class=HTMLResponse)
async def editar_aluno_form(request: Request, matricula: str, ok: str = ""):
    if not check_session(request):
        return _redir_login()
    al = get_aluno(matricula)
    if not al:
        return RedirectResponse("/admin", status_code=302)
    msg = "Dados salvos com sucesso!" if ok else ""
    return aluno_form(matricula, al, novo=False, msg=msg)

def _disc_sid(d: str) -> str:
    """Gera o identificador de campo para uma disciplina (mesmo padrão do templates.py)."""
    return d.replace(' ', '_').replace('–', '_').replace('/', '_')

def _parse_form(form: dict) -> dict:
    """Extrai dados do formulário em estrutura de aluno."""
    DISC_LIST = DISCIPLINAS
    notas = {d: {} for d in DISC_LIST}

    for key, val in form.items():
        val = val.strip()
        if key.startswith("nota_"):
            # nota_Língua_Portuguesa_p1  →  disc=Língua Portuguesa, campo=p1
            parts = key[5:].rsplit("_", 1)
            if len(parts) == 2:
                disc_sid, campo = parts
                for d in DISC_LIST:
                    if _disc_sid(d) == disc_sid:
                        if val:
                            notas[d][campo] = val
                        break

    freq = {
        "total_aulas":  form.get("total_aulas","").strip(),
        "total_faltas": form.get("total_faltas","").strip(),
    }
    return {
        "nome":        form.get("nome","").strip(),
        "turma":       form.get("turma","").strip(),
        "periodo":     form.get("periodo","").strip(),
        "professora":  form.get("professora","").strip(),
        "ano_letivo":  form.get("ano_letivo","2026").strip(),
        "notas":       notas,
        "frequencia":  freq,
        "observacoes": form.get("observacoes","").strip(),
    }

@app.post("/admin/aluno/{matricula}/salvar")
async def salvar_aluno(request: Request, matricula: str):
    if not check_session(request):
        return _redir_login()
    form = dict(await request.form())
    dados = _parse_form(form)

    # Para aluno novo, matrícula vem do form
    if matricula == "novo":
        mat = re.sub(r'\D','', form.get("matricula",""))
        if not mat:
            return RedirectResponse("/admin/aluno/novo?erro=mat", status_code=302)
    else:
        mat = matricula

    upsert_aluno(mat, dados)
    return RedirectResponse(f"/admin/aluno/{mat}?ok=1", status_code=302)

@app.get("/admin/aluno/{matricula}/excluir")
async def excluir_aluno(request: Request, matricula: str):
    if not check_session(request):
        return _redir_login()
    delete_aluno(matricula)
    return RedirectResponse("/admin", status_code=302)

@app.post("/admin/resetar")
async def resetar_banco(request: Request):
    if not check_session(request):
        return _redir_login()
    reset_db()
    return RedirectResponse("/admin?resetado=1", status_code=302)

