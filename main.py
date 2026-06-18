import os, re
from urllib.parse import quote
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from db import get_aluno, get_all_alunos, upsert_aluno, delete_aluno, reset_db, DISCIPLINAS
from boletim_html import gerar_boletim_html, gerar_boletins_multiplos_html
from auth import (check_session, get_session_user, make_session_token,
                  COOKIE_NAME, COOKIE_MAX)
from db_relatorio import (
    authenticate_user,
    get_all_usuarios, create_usuario, delete_usuario,
    update_usuario_turmas, update_usuario_senha, reset_usuario_senha, get_usuario_by_id,
    get_all_temas, create_tema, update_tema, delete_tema,
    create_subtema, update_subtema, delete_subtema,
    get_relatorio, get_relatorio_by_id, upsert_relatorio, update_relatorio,
    set_relatorio_trancado,
    get_respostas, save_respostas,
    update_subtema_turmas, get_temas_para_turma,
    get_status_relatorios,
    get_all_topicos, create_topico, update_topico, delete_topico,
    update_topico_turmas, update_tema_turmas,
)
from templates import login_page, admin_dashboard, aluno_form
from templates_admin_extras import (
    admin_professoras_page, admin_temas_page, admin_relatorios_page,
    admin_aluno_relatorios_page, aluno_infantil_form,
)
from templates_professora import (
    professora_login_page, professora_dashboard, professora_turma_page,
    professora_trocar_senha_page, is_infantil
)
from templates_relatorio import relatorio_form_page
from relatorio_print import gerar_relatorio_print_html

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
<title>Escola Espaço Alegre – Portal do Responsável</title>
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
.body{padding:28px 32px 24px;}
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
.divider{border-top:1px solid #f0f0ee;margin:20px 0 0;}
.prof-link{display:flex;align-items:center;justify-content:center;gap:8px;
  padding:16px 32px;text-decoration:none;color:#2b3990;font-size:13px;font-weight:800;
  transition:background .15s;}
.prof-link:hover{background:#f7f8ff;}
.prof-link span{background:#e8eaf8;border-radius:8px;padding:4px 10px;font-size:11px;font-weight:900;}
.footer{border-top:1px solid #f0f0ee;padding:11px 32px;text-align:center;font-size:11px;color:#ccc;}
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
    <h1>Área do Responsável</h1>
    <p>Informe a matrícula para acompanhar o desempenho do seu filho</p>
  </div>
  <div class="body">
    <form id="frm" onsubmit="buscar(event)">
      <label for="mat">Número de Matrícula</label>
      <div class="inp-wrap">
        <input type="text" id="mat" placeholder="Digite o número da matrícula"
               maxlength="12" autocomplete="off" inputmode="numeric"
               oninput="limpaErro()">
        <button type="button" class="clr" onclick="limpar()">✕</button>
      </div>
      <button type="submit" class="btn">🔍 &nbsp;Consultar</button>
    </form>
    <div class="loading" id="loading"><div class="spinner"></div><p style="font-size:12px;color:#aaa;">Buscando...</p></div>
    <div class="erro" id="erro">❌ Matrícula não encontrada. Verifique o número e tente novamente.</div>
  </div>
  <div class="divider"></div>
  <a href="/professora/login" class="prof-link">
    👩‍🏫 &nbsp;Sou Professor(a) &nbsp;<span>Acessar →</span>
  </a>
  <div class="footer">Escola Espaço Alegre &nbsp;|&nbsp; Ed. Infantil e Fundamental Anos Iniciais &nbsp;|&nbsp; Bilíngue &nbsp;|&nbsp; 2026</div>
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
async def ver_boletim(matricula: str, ref: str = ""):
    mat_clean = re.sub(r'\D', '', matricula)
    if not mat_clean:
        return RedirectResponse("/?erro=1")

    aluno = get_aluno(mat_clean)
    if not aluno:
        return RedirectResponse("/?erro=1")

    aluno_completo = dict(aluno)
    aluno_completo['matricula'] = mat_clean
    back_url = "/admin" if ref == "admin" else "/"
    return HTMLResponse(gerar_boletim_html(aluno_completo, back_url=back_url))

@app.get("/admin/imprimir", response_class=HTMLResponse)
async def imprimir_boletins(request: Request, turma: str = "todos"):
    if not check_session(request):
        return _redir_login()
    alunos = get_all_alunos()
    if turma == "todos":
        lista = sorted(
            [dict(a, matricula=m) for m, a in alunos.items()],
            key=lambda x: (x['turma'], x['nome'])
        )
        titulo = "Todos os Alunos"
    else:
        lista = sorted(
            [dict(a, matricula=m) for m, a in alunos.items() if a['turma'] == turma],
            key=lambda x: x['nome']
        )
        titulo = turma
    return HTMLResponse(gerar_boletins_multiplos_html(lista, titulo))

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
    user = authenticate_user(usuario, senha)
    if user and user.get("role") == "admin":
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie(COOKIE_NAME, make_session_token(user),
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
    # Busca status dos relatórios dos alunos do Infantil em uma única query
    matriculas_inf = [m for m, a in alunos.items() if is_infantil(a.get("turma", ""))]
    rel_status = get_status_relatorios(matriculas_inf) if matriculas_inf else {}
    return admin_dashboard(alunos, resetado=bool(resetado), rel_status=rel_status)

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

@app.get("/admin/aluno/{matricula}/editar-infantil", response_class=HTMLResponse)
async def editar_aluno_infantil(request: Request, matricula: str, ok: str = ""):
    if not check_session(request):
        return _redir_login()
    al = get_aluno(matricula)
    if not al:
        return RedirectResponse("/admin", status_code=302)
    turma = al.get("turma", "")
    temas = get_temas_para_turma(turma)
    msg = "Observações salvas com sucesso!" if ok else ""
    return aluno_infantil_form(matricula, al, temas, msg=msg)

@app.post("/admin/aluno/{matricula}/editar-infantil/salvar")
async def salvar_aluno_infantil(request: Request, matricula: str):
    if not check_session(request):
        return _redir_login()
    al = get_aluno(matricula)
    if not al:
        return RedirectResponse("/admin", status_code=302)
    form = dict(await request.form())
    al["observacoes"] = form.get("observacoes", "").strip()
    upsert_aluno(matricula, al)
    return RedirectResponse(f"/admin/aluno/{matricula}/editar-infantil?ok=1", status_code=302)

@app.post("/admin/resetar")
async def resetar_banco(request: Request):
    if not check_session(request):
        return _redir_login()
    reset_db()
    return RedirectResponse("/admin?resetado=1", status_code=302)


@app.post("/admin/seed-infantil")
async def seed_infantil_route(request: Request):
    """Importa alunos e professoras da Ed. Infantil — idempotente, seguro para rodar várias vezes."""
    if not check_session(request):
        return _redir_login()
    from seed_infantil import run_seed
    r = run_seed()
    msg = f"{r['alunos']}+alunos+e+{r['professoras']}+professoras+importados"
    return RedirectResponse(f"/admin?resetado=1&seed_msg={msg}", status_code=302)


@app.post("/admin/seed-estrutura-avaliativa")
async def seed_estrutura_avaliativa_route(request: Request):
    """Importa a estrutura avaliativa (Tópico→Tema→Subtema) da Ed. Infantil — idempotente."""
    if not check_session(request):
        return _redir_login()
    from seed_estrutura_avaliativa import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil3")
async def seed_estrutura_infantil3_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 3 (A e B) — idempotente."""
    if not check_session(request):
        return _redir_login()
    from seed_estrutura_infantil3 import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil4")
async def seed_estrutura_infantil4_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 4 (A e B) — idempotente."""
    if not check_session(request):
        return _redir_login()
    from seed_estrutura_infantil4 import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil5")
async def seed_estrutura_infantil5_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 5 (A) — idempotente."""
    if not check_session(request):
        return _redir_login()
    from seed_estrutura_infantil5 import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


# ════════════════════════════════════════════════════════════════════════════
#  FASE 2 — Professoras
# ════════════════════════════════════════════════════════════════════════════

def _alunos_por_professora() -> dict:
    """Retorna {nome_prof: [turmas_distintas]} a partir dos alunos cadastrados."""
    alunos = get_all_alunos()
    mapa: dict = {}
    for al in alunos.values():
        prof = al.get("professora", "").strip()
        turma = al.get("turma", "").strip()
        if prof:
            if prof not in mapa:
                mapa[prof] = set()
            if turma:
                mapa[prof].add(turma)
    return {k: sorted(v) for k, v in mapa.items()}


@app.get("/admin/professoras", response_class=HTMLResponse)
async def listar_professoras(request: Request, ok: str = "", erro: str = "", senha_gerada: str = ""):
    if not check_session(request):
        return _redir_login()
    professoras = [u for u in get_all_usuarios() if u["role"] == "professora"]
    alunos_map = _alunos_por_professora()
    return admin_professoras_page(professoras, alunos_map, msg=ok, erro=erro, senha_gerada=senha_gerada)


@app.post("/admin/professoras/nova")
async def criar_professora(request: Request):
    if not check_session(request):
        return _redir_login()
    form  = await request.form()
    nome  = form.get("nome", "").strip()
    username = form.get("username", "").strip()
    senha = form.get("senha", "").strip()
    turmas = list(form.getlist("turma"))

    if len(senha) < 6:
        return RedirectResponse("/admin/professoras?erro=Senha+deve+ter+ao+menos+6+caracteres", status_code=302)
    try:
        create_usuario(username, senha, nome, role="professora", turmas=turmas)
        return RedirectResponse(f"/admin/professoras?ok=Professora+{nome}+cadastrada", status_code=302)
    except ValueError:
        return RedirectResponse("/admin/professoras?erro=Usu%C3%A1rio+j%C3%A1+existe", status_code=302)


@app.post("/admin/professoras/{user_id}/turmas")
async def salvar_turmas_professora(request: Request, user_id: int):
    if not check_session(request):
        return _redir_login()
    form   = await request.form()
    turmas = list(form.getlist("turma"))
    update_usuario_turmas(user_id, turmas)
    return RedirectResponse("/admin/professoras?ok=Turmas+atualizadas", status_code=302)


@app.post("/admin/professoras/{user_id}/excluir")
async def excluir_professora(request: Request, user_id: int):
    if not check_session(request):
        return _redir_login()
    delete_usuario(user_id)
    return RedirectResponse("/admin/professoras?ok=Professora+removida", status_code=302)


@app.post("/admin/professoras/{user_id}/resetar-senha")
async def resetar_senha_professora(request: Request, user_id: int):
    if not check_session(request):
        return _redir_login()
    nova_senha = reset_usuario_senha(user_id)
    if nova_senha:
        return RedirectResponse(
            f"/admin/professoras?ok=Senha+resetada+com+sucesso&senha_gerada={quote(nova_senha)}",
            status_code=302,
        )
    return RedirectResponse("/admin/professoras?erro=N%C3%A3o+foi+poss%C3%ADvel+resetar+a+senha", status_code=302)


@app.get("/admin/aluno/{matricula}/relatorios", response_class=HTMLResponse)
async def admin_ver_relatorios_aluno(request: Request, matricula: str):
    """Página que mostra os relatórios semestrais de um aluno Infantil."""
    if not check_session(request):
        return _redir_login()
    aluno = get_aluno(matricula)
    if not aluno or not is_infantil(aluno.get("turma", "")):
        return RedirectResponse("/admin", status_code=302)
    ano  = aluno.get("ano_letivo", "2026")
    rel1 = get_relatorio(matricula, 1, ano)
    rel2 = get_relatorio(matricula, 2, ano)
    return admin_aluno_relatorios_page(aluno, matricula, rel1, rel2)


# ════════════════════════════════════════════════════════════════════════════
#  FASE 2 — Temas e Subtemas Avaliativos
# ════════════════════════════════════════════════════════════════════════════

@app.get("/admin/temas", response_class=HTMLResponse)
async def listar_temas(request: Request, ok: str = "", erro: str = ""):
    if not check_session(request):
        return _redir_login()
    topicos = get_all_topicos()
    return admin_temas_page(topicos, msg=ok, erro=erro)


# ── Tópicos ──────────────────────────────────────────────────────────────────

@app.post("/admin/topicos/novo")
async def criar_topico(request: Request, nome: str = Form(...)):
    if not check_session(request):
        return _redir_login()
    nome = nome.strip()
    if not nome:
        return RedirectResponse("/admin/temas?erro=Nome+do+t%C3%B3pico+n%C3%A3o+pode+ser+vazio", status_code=302)
    create_topico(nome)
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+criado+com+sucesso", status_code=302)


@app.post("/admin/topicos/{topico_id}/editar")
async def editar_topico(request: Request, topico_id: int, nome: str = Form(...)):
    if not check_session(request):
        return _redir_login()
    update_topico(topico_id, nome.strip())
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+atualizado", status_code=302)


@app.post("/admin/topicos/{topico_id}/excluir")
async def excluir_topico(request: Request, topico_id: int):
    if not check_session(request):
        return _redir_login()
    delete_topico(topico_id)
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+removido", status_code=302)


# ── Temas ─────────────────────────────────────────────────────────────────────

@app.post("/admin/temas/novo")
async def criar_tema(request: Request):
    if not check_session(request):
        return _redir_login()
    form = dict(await request.form())
    nome = form.get("nome", "").strip()
    topico_id_raw = form.get("topico_id", "").strip()
    if not nome:
        return RedirectResponse("/admin/temas?erro=Nome+do+tema+n%C3%A3o+pode+ser+vazio", status_code=302)
    topico_id = int(topico_id_raw) if topico_id_raw.isdigit() else None
    create_tema(nome, topico_id=topico_id)
    return RedirectResponse("/admin/temas?ok=Tema+criado+com+sucesso", status_code=302)


@app.post("/admin/temas/{tema_id}/editar")
async def editar_tema(request: Request, tema_id: int, nome: str = Form(...)):
    if not check_session(request):
        return _redir_login()
    update_tema(tema_id, nome.strip())
    return RedirectResponse("/admin/temas?ok=Tema+atualizado", status_code=302)


@app.post("/admin/temas/{tema_id}/excluir")
async def excluir_tema(request: Request, tema_id: int):
    if not check_session(request):
        return _redir_login()
    delete_tema(tema_id)
    return RedirectResponse("/admin/temas?ok=Tema+removido", status_code=302)


@app.post("/admin/temas/{tema_id}/subtema")
async def criar_subtema(request: Request, tema_id: int, descricao: str = Form(...)):
    if not check_session(request):
        return _redir_login()
    descricao = descricao.strip()
    if not descricao:
        return RedirectResponse("/admin/temas?erro=Descri%C3%A7%C3%A3o+do+subtema+n%C3%A3o+pode+ser+vazia", status_code=302)
    create_subtema(tema_id, descricao)
    return RedirectResponse("/admin/temas?ok=Subtema+adicionado", status_code=302)


@app.post("/admin/subtemas/{subtema_id}/editar")
async def editar_subtema(request: Request, subtema_id: int, descricao: str = Form(...)):
    if not check_session(request):
        return _redir_login()
    descricao = descricao.strip()
    if not descricao:
        return RedirectResponse("/admin/temas?erro=Descri%C3%A7%C3%A3o+do+subtema+n%C3%A3o+pode+ser+vazia", status_code=302)
    update_subtema(subtema_id, descricao)
    return RedirectResponse("/admin/temas?ok=Subtema+atualizado", status_code=302)


@app.post("/admin/subtemas/{subtema_id}/excluir")
async def excluir_subtema(request: Request, subtema_id: int):
    if not check_session(request):
        return _redir_login()
    delete_subtema(subtema_id)
    return RedirectResponse("/admin/temas?ok=Subtema+removido", status_code=302)


@app.post("/admin/topicos/{topico_id}/turmas")
async def salvar_turmas_topico(request: Request, topico_id: int):
    if not check_session(request):
        return _redir_login()
    form = await request.form()
    turmas = list(form.getlist("turma"))
    update_topico_turmas(topico_id, turmas)
    return RedirectResponse("/admin/temas?ok=Turmas+do+t%C3%B3pico+salvas", status_code=302)


@app.post("/admin/temas/{tema_id}/turmas")
async def salvar_turmas_tema(request: Request, tema_id: int):
    if not check_session(request):
        return _redir_login()
    form = await request.form()
    turmas = list(form.getlist("turma"))
    update_tema_turmas(tema_id, turmas)
    return RedirectResponse("/admin/temas?ok=Turmas+do+tema+salvas", status_code=302)


# ════════════════════════════════════════════════════════════════════════════
#  FASE 3 — Área da Professora
# ════════════════════════════════════════════════════════════════════════════

def _redir_prof_login():
    return RedirectResponse("/professora/login", status_code=302)


def _check_prof(request: Request) -> dict | None:
    """Retorna o usuário da sessão se for professora ou admin, senão None."""
    user = get_session_user(request)
    if not user or user.get("role") not in ("admin", "professora"):
        return None
    return user


def _precisa_trocar_senha(user: dict) -> bool:
    """True se a professora estiver com uma senha temporária pendente de troca."""
    if user.get("role") != "professora":
        return False
    atual = get_usuario_by_id(user["user_id"])
    return bool(atual and atual.get("senha_temporaria"))


def _dados_turmas(nome_prof: str, ano_letivo: str = "2026") -> list:
    """
    Retorna lista de dicts por turma com status dos relatórios.
    Filtra alunos cujo campo `professora` bate exatamente com nome_prof.
    """
    from urllib.parse import quote as _q
    all_alunos = get_all_alunos()
    meus = {mat: al for mat, al in all_alunos.items()
            if al.get("professora", "").strip() == nome_prof}

    # Agrupa por turma
    por_turma: dict = {}
    for mat, al in meus.items():
        t = al.get("turma", "Sem turma")
        por_turma.setdefault(t, {"periodo": al.get("periodo", ""), "alunos": []})
        por_turma[t]["alunos"].append(mat)

    resultado = []
    for turma, info in sorted(por_turma.items()):
        infantil = is_infantil(turma)
        pendentes = andamento = concluidos = 0

        if infantil:
            for mat in info["alunos"]:
                for sem in (1, 2):
                    rel = get_relatorio(mat, sem, ano_letivo)
                    status = rel["status"] if rel else "pendente"
                    if status == "concluido":
                        concluidos += 1
                    elif status == "em_andamento":
                        andamento += 1
                    else:
                        pendentes += 1

        resultado.append({
            "turma":        turma,
            "periodo":      info["periodo"],
            "total_alunos": len(info["alunos"]),
            "is_infantil":  infantil,
            "pendentes":    pendentes,
            "andamento":    andamento,
            "concluidos":   concluidos,
        })
    return resultado


def _dados_alunos_turma(nome_prof: str, turma: str, ano_letivo: str = "2026") -> list:
    """Retorna lista de alunos da turma com status dos seus relatórios."""
    all_alunos = get_all_alunos()
    infantil = is_infantil(turma)
    resultado = []
    for mat, al in all_alunos.items():
        if al.get("professora", "").strip() != nome_prof:
            continue
        if al.get("turma", "") != turma:
            continue
        aluno_dict = {"matricula": mat, "nome": al["nome"], "is_infantil": infantil}
        if infantil:
            for sem in (1, 2):
                rel = get_relatorio(mat, sem, ano_letivo)
                aluno_dict[f"status_s{sem}"] = rel["status"] if rel else "pendente"
        resultado.append(aluno_dict)
    return resultado


# ── Rotas ────────────────────────────────────────────────────────────────────

@app.get("/professora/login", response_class=HTMLResponse)
async def prof_get_login(request: Request, erro: str = ""):
    user = get_session_user(request)
    # Apenas professoras já autenticadas pulam o login; admin sempre vê o formulário
    if user and user.get("role") == "professora":
        return RedirectResponse("/professora", status_code=302)
    return professora_login_page(erro="1" in erro)


@app.post("/professora/login")
async def prof_post_login(
    request: Request,
    usuario: str = Form(...),
    senha:   str = Form(...),
):
    user = authenticate_user(usuario, senha)
    if user and user.get("role") in ("admin", "professora"):
        resp = RedirectResponse("/professora?bemvindo=1", status_code=302)
        resp.set_cookie(COOKIE_NAME, make_session_token(user),
                        max_age=COOKIE_MAX, httponly=True, samesite="lax")
        return resp
    return RedirectResponse("/professora/login?erro=1", status_code=302)


@app.get("/professora/logout")
async def prof_logout():
    resp = RedirectResponse("/professora/login", status_code=302)
    resp.delete_cookie(COOKIE_NAME)
    return resp


@app.get("/professora", response_class=HTMLResponse)
async def prof_dashboard(request: Request, ok: str = "", bemvindo: str = ""):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()
    if _precisa_trocar_senha(user):
        return RedirectResponse("/professora/trocar-senha", status_code=302)
    turmas = _dados_turmas(user["nome"])
    return professora_dashboard(user, turmas, msg=ok, bemvindo=(bemvindo == "1"))


@app.get("/professora/turma/{turma}", response_class=HTMLResponse)
async def prof_turma(request: Request, turma: str, ok: str = ""):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()
    if _precisa_trocar_senha(user):
        return RedirectResponse("/professora/trocar-senha", status_code=302)
    alunos = _dados_alunos_turma(user["nome"], turma)
    return professora_turma_page(user, turma, alunos, msg=ok)


@app.get("/professora/trocar-senha", response_class=HTMLResponse)
async def prof_trocar_senha_form(request: Request, erro: str = ""):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()
    obrigatorio = _precisa_trocar_senha(user)
    return professora_trocar_senha_page(user, obrigatorio=obrigatorio, erro=erro)


@app.post("/professora/trocar-senha")
async def prof_trocar_senha_salvar(
    request: Request,
    nova_senha: str = Form(...),
    confirmar_senha: str = Form(...),
):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()
    if len(nova_senha) < 6:
        return RedirectResponse("/professora/trocar-senha?erro=A+senha+deve+ter+ao+menos+6+caracteres", status_code=302)
    if nova_senha != confirmar_senha:
        return RedirectResponse("/professora/trocar-senha?erro=As+senhas+n%C3%A3o+coincidem", status_code=302)
    update_usuario_senha(user["user_id"], nova_senha)
    return RedirectResponse("/professora?ok=Senha+atualizada+com+sucesso", status_code=302)


# ════════════════════════════════════════════════════════════════════════════
#  FASE 4 — Formulário do Relatório Semestral
# ════════════════════════════════════════════════════════════════════════════

def _parse_respostas(form: dict) -> dict:
    """Extrai {subtema_id: resposta} do form POST."""
    result = {}
    for key, val in form.items():
        if key.startswith("resposta_"):
            try:
                sid = int(key[9:])
                if val.strip():
                    result[sid] = val.strip()
            except ValueError:
                pass
    return result


def _check_acesso_aluno(user: dict, matricula: str) -> dict | None:
    """
    Retorna o aluno se o usuário tiver acesso (admin: qualquer aluno;
    professora: só seus alunos). Retorna None se não tiver acesso.
    """
    aluno = get_aluno(matricula)
    if not aluno:
        return None
    if user.get("role") == "admin":
        return aluno
    # Professora só acessa seus próprios alunos
    if aluno.get("professora", "").strip() == user.get("nome", "").strip():
        return aluno
    return None


@app.get("/professora/relatorio/{matricula}/{semestre}", response_class=HTMLResponse)
async def prof_relatorio_get(request: Request, matricula: str, semestre: int, msg: str = "", erro: str = ""):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()
    if _precisa_trocar_senha(user):
        return RedirectResponse("/professora/trocar-senha", status_code=302)

    if semestre not in (1, 2):
        return RedirectResponse("/professora", status_code=302)

    aluno = _check_acesso_aluno(user, matricula)
    if not aluno:
        return RedirectResponse("/professora", status_code=302)

    if not is_infantil(aluno.get("turma", "")):
        return RedirectResponse("/professora", status_code=302)

    ano = aluno.get("ano_letivo", "2026")
    turma = aluno.get("turma", "")
    temas = get_temas_para_turma(turma)  # só subtemas configurados para esta turma

    # Cria o relatório se não existir ainda
    relatorio = upsert_relatorio(matricula, semestre, user["user_id"], ano)

    respostas = get_respostas(relatorio["id"])
    return relatorio_form_page(user, aluno, matricula, semestre, relatorio, temas, respostas, msg=msg, erro=erro)


@app.post("/professora/relatorio/{matricula}/{semestre}/salvar")
async def prof_relatorio_salvar(request: Request, matricula: str, semestre: int):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()

    aluno = _check_acesso_aluno(user, matricula)
    if not aluno:
        return RedirectResponse("/professora", status_code=302)

    ano = aluno.get("ano_letivo", "2026")
    relatorio = upsert_relatorio(matricula, semestre, user["user_id"], ano)

    # Impede edição por professora após confirmar ou se o admin trancou
    if relatorio.get("trancado") and user.get("role") == "professora":
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Relat%C3%B3rio+trancado+pelo+administrador",
            status_code=302,
        )
    if relatorio["status"] == "concluido" and user.get("role") == "professora":
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Relat%C3%B3rio+j%C3%A1+confirmado",
            status_code=302,
        )

    form = dict(await request.form())
    respostas  = _parse_respostas(form)
    descricao  = form.get("descricao_final", "").strip()

    save_respostas(relatorio["id"], respostas)
    update_relatorio(relatorio["id"], "em_andamento", descricao)

    return RedirectResponse(
        f"/professora/relatorio/{matricula}/{semestre}?msg=Rascunho+salvo+com+sucesso",
        status_code=302,
    )


@app.post("/professora/relatorio/{matricula}/{semestre}/confirmar")
async def prof_relatorio_confirmar(request: Request, matricula: str, semestre: int):
    user = _check_prof(request)
    if not user:
        return _redir_prof_login()

    aluno = _check_acesso_aluno(user, matricula)
    if not aluno:
        return RedirectResponse("/professora", status_code=302)

    ano = aluno.get("ano_letivo", "2026")
    relatorio = upsert_relatorio(matricula, semestre, user["user_id"], ano)

    # Professora não pode confirmar relatório trancado pelo admin ou já concluído
    if relatorio.get("trancado") and user.get("role") == "professora":
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Relat%C3%B3rio+trancado+pelo+administrador",
            status_code=302,
        )
    if relatorio["status"] == "concluido" and user.get("role") == "professora":
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Relat%C3%B3rio+j%C3%A1+confirmado",
            status_code=302,
        )

    form = dict(await request.form())
    respostas = _parse_respostas(form)
    descricao = form.get("descricao_final", "").strip()

    # Validação server-side: todos os subtemas da turma respondidos
    turma = aluno.get("turma", "")
    temas = get_temas_para_turma(turma)
    todos_ids = [st["id"] for t in temas for st in t.get("subtemas", [])]
    faltando  = [sid for sid in todos_ids if sid not in respostas or not respostas[sid]]
    if faltando:
        save_respostas(relatorio["id"], respostas)
        update_relatorio(relatorio["id"], "em_andamento", descricao)
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Preencha+todos+os+{len(todos_ids)}+subtemas+antes+de+confirmar",
            status_code=302,
        )

    if len(descricao) < 10:
        save_respostas(relatorio["id"], respostas)
        update_relatorio(relatorio["id"], "em_andamento", descricao)
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=A+descri%C3%A7%C3%A3o+final+%C3%A9+obrigat%C3%B3ria",
            status_code=302,
        )

    save_respostas(relatorio["id"], respostas)
    update_relatorio(relatorio["id"], "concluido", descricao)

    turma_enc = aluno.get("turma", "").replace(" ", "%20")
    return RedirectResponse(
        f"/professora/turma/{turma_enc}?ok=Relat%C3%B3rio+de+{matricula}+confirmado+com+sucesso",
        status_code=302,
    )


# ════════════════════════════════════════════════════════════════════════════
#  FASE 5 — Painel de relatórios do admin + edição + impressão
# ════════════════════════════════════════════════════════════════════════════

def _painel_relatorios_data(turma_f: str = "", semestre_f: str = "", status_f: str = "", ano: str = "2026"):
    """Agrega alunos de Ed. Infantil com status dos seus relatórios."""
    all_alunos = get_all_alunos()

    # Coleta turmas Infantil disponíveis (para o filtro)
    turmas_inf = sorted({
        al.get("turma", "") for al in all_alunos.values()
        if is_infantil(al.get("turma", ""))
    })

    rows = []
    pend_total = and_total = conc_total = 0

    for mat, al in sorted(all_alunos.items(), key=lambda x: (x[1].get("turma",""), x[1].get("nome",""))):
        turma = al.get("turma", "")
        if not is_infantil(turma):
            continue
        if turma_f and turma != turma_f:
            continue

        rel1 = get_relatorio(mat, 1, ano)
        rel2 = get_relatorio(mat, 2, ano)
        s1   = rel1["status"] if rel1 else "pendente"
        s2   = rel2["status"] if rel2 else "pendente"

        # Filtro por semestre + status
        if semestre_f == "1" and status_f and s1 != status_f:
            continue
        if semestre_f == "2" and status_f and s2 != status_f:
            continue
        if not semestre_f and status_f:
            if s1 != status_f and s2 != status_f:
                continue

        # Contadores globais (sem filtro de status)
        for s in (s1, s2):
            if s == "concluido":
                conc_total += 1
            elif s == "em_andamento":
                and_total += 1
            else:
                pend_total += 1

        rows.append({
            "matricula": mat,
            "nome":      al.get("nome", ""),
            "turma":     turma,
            "professora":al.get("professora", ""),
            "s1_status": s1,
            "s1_id":     rel1["id"] if rel1 else None,
            "s1_trancado": bool(rel1.get("trancado")) if rel1 else False,
            "s2_status": s2,
            "s2_id":     rel2["id"] if rel2 else None,
            "s2_trancado": bool(rel2.get("trancado")) if rel2 else False,
        })

    contadores = {
        "total":     len(rows),
        "pendentes": pend_total,
        "andamento": and_total,
        "concluidos":conc_total,
    }
    return rows, turmas_inf, contadores


@app.get("/admin/relatorios", response_class=HTMLResponse)
async def admin_relatorios(
    request: Request,
    turma: str = "", semestre: str = "", status: str = "",
    ok: str = "", erro: str = "",
):
    if not check_session(request):
        return _redir_login()
    rows, turmas_inf, cont = _painel_relatorios_data(turma, semestre, status)
    filtros = {"turma": turma, "semestre": semestre, "status": status}
    return admin_relatorios_page(rows, turmas_inf, filtros, cont, msg=ok, erro=erro)


@app.get("/admin/relatorio/{rel_id}", response_class=HTMLResponse)
async def admin_ver_relatorio(request: Request, rel_id: int, msg: str = "", erro: str = ""):
    if not check_session(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    aluno = get_aluno(relatorio["matricula"])
    if not aluno:
        return RedirectResponse("/admin/relatorios", status_code=302)

    temas    = get_all_temas()
    respostas = get_respostas(rel_id)
    user_admin = get_session_user(request)
    prefix   = f"/admin/relatorio/{rel_id}"

    return relatorio_form_page(
        user_admin, aluno, relatorio["matricula"], relatorio["semestre"],
        relatorio, temas, respostas, msg=msg, erro=erro, form_prefix=prefix,
    )


@app.post("/admin/relatorio/{rel_id}/salvar")
async def admin_salvar_relatorio(request: Request, rel_id: int):
    if not check_session(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    form      = dict(await request.form())
    respostas = _parse_respostas(form)
    descricao = form.get("descricao_final", "").strip()
    novo_status = "em_andamento" if relatorio["status"] == "pendente" else relatorio["status"]

    save_respostas(rel_id, respostas)
    update_relatorio(rel_id, novo_status, descricao)

    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Alterações+salvas+com+sucesso", status_code=302)


@app.post("/admin/relatorio/{rel_id}/confirmar")
async def admin_confirmar_relatorio(request: Request, rel_id: int):
    if not check_session(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    form      = dict(await request.form())
    respostas = _parse_respostas(form)
    descricao = form.get("descricao_final", "").strip()

    aluno_rel = get_aluno(relatorio["matricula"])
    turma_rel = aluno_rel.get("turma", "") if aluno_rel else ""
    temas    = get_temas_para_turma(turma_rel)
    todos_ids = [st["id"] for t in temas for st in t.get("subtemas", [])]
    faltando  = [sid for sid in todos_ids if sid not in respostas]

    if faltando:
        save_respostas(rel_id, respostas)
        update_relatorio(rel_id, "em_andamento", descricao)
        return RedirectResponse(
            f"/admin/relatorio/{rel_id}?erro=Preencha+todos+os+subtemas+antes+de+confirmar",
            status_code=302,
        )

    save_respostas(rel_id, respostas)
    update_relatorio(rel_id, "concluido", descricao)
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+confirmado+com+sucesso", status_code=302)


@app.post("/admin/relatorio/{rel_id}/trancar")
async def admin_trancar_relatorio(request: Request, rel_id: int):
    if not check_session(request):
        return _redir_login()
    set_relatorio_trancado(rel_id, True)
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+trancado", status_code=302)


@app.post("/admin/relatorio/{rel_id}/destrancar")
async def admin_destrancar_relatorio(request: Request, rel_id: int):
    if not check_session(request):
        return _redir_login()
    set_relatorio_trancado(rel_id, False)
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+destrancado", status_code=302)


@app.get("/admin/relatorio/{rel_id}/imprimir", response_class=HTMLResponse)
async def admin_imprimir_relatorio(request: Request, rel_id: int):
    if not check_session(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    aluno    = get_aluno(relatorio["matricula"])
    temas    = get_all_temas()
    respostas = get_respostas(rel_id)

    return HTMLResponse(gerar_relatorio_print_html(
        aluno, relatorio["matricula"], relatorio["semestre"],
        relatorio, temas, respostas,
    ))

