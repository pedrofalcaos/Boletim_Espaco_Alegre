import os, re, unicodedata
from urllib.parse import quote
from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from db import (get_aluno, get_all_alunos, upsert_aluno, delete_aluno, reset_db, DISCIPLINAS,
                renomear_professora)
from boletim_html import gerar_boletim_html, gerar_boletins_multiplos_html
from auth import (check_session, check_admin, check_staff, get_session_user, make_session_token,
                  COOKIE_NAME, COOKIE_MAX, COOKIE_SECURE, IS_PROD,
                  login_bloqueado, registrar_falha_login, limpar_falhas_login,
                  consulta_bloqueada)
from db_relatorio import (
    authenticate_user,
    get_all_usuarios, create_usuario, delete_usuario,
    update_usuario_turmas, update_usuario_senha, reset_usuario_senha, get_usuario_by_id,
    update_usuario_nome,
    create_tema, update_tema, delete_tema,
    create_subtema, update_subtema, delete_subtema,
    get_relatorio, get_relatorio_by_id, upsert_relatorio, update_relatorio,
    set_relatorio_trancado, reabrir_relatorio,
    get_respostas, save_respostas,
    update_subtema_turmas, get_temas_para_turma,
    get_status_relatorios,
    get_all_topicos, create_topico, update_topico, delete_topico,
    update_topico_turmas, update_tema_turmas,
    get_pais_liberado, set_pais_liberado,
)
import db_avaliacao as dav
import db_acesso as dac
import db_auditoria as daud
from sanitize import sanitizar_html
from templates import login_page, admin_dashboard, aluno_form
from templates_admin_extras import (
    admin_professoras_page, admin_temas_page, admin_relatorios_page,
    admin_aluno_relatorios_page, aluno_infantil_form, admin_avaliacoes_page,
    card_avaliacao_pais, admin_acessos_page, banner_festas_pais, admin_auditoria_page,
)
from templates_professora import (
    professora_login_page, professora_dashboard, professora_turma_page,
    professora_trocar_senha_page, is_infantil
)
from templates_relatorio import relatorio_form_page
from relatorio_print import (
    gerar_relatorio_print_html, gerar_relatorios_print_html_multiplos,
    gerar_relatorios_aluno_print_html,
    gerar_escolha_semestre_html, gerar_relatorio_indisponivel_html,
)
from music_player import inject_player

app = FastAPI(docs_url=None, redoc_url=None)

# ── Cabeçalhos de segurança + cache em conteúdo sensível ─────────────────────
_CSP = (
    "default-src 'self'; "
    "img-src 'self' data:; "
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; "
    "script-src 'self' 'unsafe-inline'; "
    "media-src 'self'; object-src 'self'; "
    "base-uri 'self'; form-action 'self'; frame-ancestors 'self'"
)
# Prefixos cujo conteúdo não deve ser cacheado (dados pessoais / painel).
_SEM_CACHE = ("/boletim", "/relatorio", "/avaliacao-ingles", "/admin", "/professora")


@app.middleware("http")
async def _security_headers(request: Request, call_next):
    resp = await call_next(request)
    resp.headers.setdefault("X-Content-Type-Options", "nosniff")
    resp.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
    resp.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    resp.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
    resp.headers.setdefault("Content-Security-Policy", _CSP)
    if IS_PROD:
        resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    path = request.url.path
    if any(path.startswith(p) for p in _SEM_CACHE):
        resp.headers["Cache-Control"] = "private, no-store"
    return resp

# ── Estáticos ────────────────────────────────────────────────────────────────
@app.get("/static/logo.png")
async def logo():
    # Logo com fundo transparente (PNG). Mantém compat. com /static/logo.jpg.
    path = "static/logo.png"
    if not os.path.exists(path):
        path = "static/logo.jpg"
    return FileResponse(path)

@app.get("/static/logo.jpg")
async def logo_jpg():
    # Compatibilidade: PDFs e páginas antigas que ainda referenciam o .jpg.
    return FileResponse("static/logo.jpg")

@app.get("/static/favicon.png")
async def favicon_png():
    return FileResponse("static/favicon.png", media_type="image/png")

@app.get("/favicon.ico")
async def favicon_ico():
    # Navegadores pedem /favicon.ico por padrão — servimos o PNG personalizado.
    path = "static/favicon.png"
    if os.path.exists(path):
        return FileResponse(path, media_type="image/png")
    return FileResponse("static/logo.png", media_type="image/png")

@app.get("/static/musica_escola.mp3")
async def musica_escola():
    path = "/mnt/user-data/uploads/musica_escola.mp3"
    if not os.path.exists(path):
        path = "static/musica_escola.mp3"
    return FileResponse(path, media_type="audio/mpeg")

# ════════════════════════════════════════════════════════════════════════════
#  ÁREA PÚBLICA — consulta de boletim por matrícula
# ════════════════════════════════════════════════════════════════════════════

INDEX_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Escola Espaço Alegre – Portal do Responsável</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Plus Jakarta Sans','Nunito',sans-serif;-webkit-font-smoothing:antialiased;
  background:linear-gradient(160deg,#1a2570 0%,#2b3990 40%,#1a5fa8 100%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px 16px;
  position:relative;overflow-x:hidden;}
.lg-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;}
.lg-blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.45;animation:lg-float 18s ease-in-out infinite;}
.lg-blob-1{width:460px;height:460px;top:-140px;left:-120px;background:#7d8bff;}
.lg-blob-2{width:400px;height:400px;bottom:-160px;right:-100px;background:#f7d800;opacity:.3;animation-delay:-6s;}
.lg-blob-3{width:340px;height:340px;top:45%;left:65%;background:#19c7b4;opacity:.26;animation-delay:-11s;}
@keyframes lg-float{0%,100%{transform:translate(0,0) scale(1);}50%{transform:translate(26px,-32px) scale(1.07);}}
@media(prefers-reduced-motion:reduce){.lg-blob{animation:none;}}
.card{position:relative;z-index:1;background:rgba(255,255,255,.62);backdrop-filter:blur(26px) saturate(180%);
  -webkit-backdrop-filter:blur(26px) saturate(180%);border:1px solid rgba(255,255,255,.55);
  border-radius:26px;box-shadow:0 20px 60px rgba(10,15,50,.35),inset 0 1px 0 rgba(255,255,255,.6);
  width:100%;max-width:440px;overflow:hidden;
  opacity:0;transform:translateY(18px);animation:lg-enter .6s cubic-bezier(.2,.7,.2,1) .05s forwards;}
@keyframes lg-enter{to{opacity:1;transform:translateY(0);}}
@media(prefers-reduced-motion:reduce){.card{animation:none;opacity:1;transform:none;}}
.top{background:linear-gradient(135deg,#3b49b8,#1a2570);padding:34px 32px 26px;text-align:center;
  border-bottom:4px solid #f7d800;position:relative;overflow:hidden;}
.top::after{content:'';position:absolute;top:-60%;left:-20%;width:140%;height:160%;
  background:radial-gradient(circle at 30% 20%,rgba(255,255,255,.16),transparent 60%);pointer-events:none;}
.top img{height:54px;object-fit:contain;margin-bottom:14px;display:block;margin-left:auto;margin-right:auto;
  background:#fff;padding:10px 18px;border-radius:18px;position:relative;z-index:1;
  box-shadow:0 6px 18px rgba(0,0,0,.22);}
.top h1{font-family:'Fredoka One',cursive;font-size:22px;color:#fff;letter-spacing:.2px;
  position:relative;z-index:1;line-height:1.25;}
.top p{font-size:12.5px;color:#c7cdf5;margin-top:6px;font-weight:600;position:relative;z-index:1;}
.body{padding:30px 32px 26px;}
label{display:block;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.8px;color:#6b7094;margin-bottom:7px;}
.inp-wrap{position:relative;margin-bottom:16px;}
.inp-wrap svg{position:absolute;left:16px;top:50%;transform:translateY(-50%);
  width:18px;height:18px;stroke:#8b90b3;pointer-events:none;}
input[type=text]{width:100%;font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:19px;font-weight:800;
  color:#2b3990;letter-spacing:2.5px;text-align:left;padding:15px 44px 15px 44px;
  border:1.5px solid rgba(43,57,144,.18);border-radius:16px;outline:none;
  background:rgba(255,255,255,.55);backdrop-filter:blur(8px);transition:border-color .2s,box-shadow .2s;}
input[type=text]:focus{border-color:#2b3990;box-shadow:0 0 0 4px rgba(43,57,144,.14);}
input[type=text]:focus-visible{outline:2px solid #2b3990;outline-offset:2px;}
input::placeholder{font-size:13px;color:#a9aec8;letter-spacing:.5px;font-weight:600;}
.clr{position:absolute;right:14px;top:50%;transform:translateY(-50%);
  background:none;border:none;font-size:18px;color:#ccc;cursor:pointer;display:none;padding:6px;}
input:not(:placeholder-shown)~.clr{display:block;}
.btn{width:100%;font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:15px;font-weight:800;
  background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;border:none;border-radius:999px;
  padding:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;gap:8px;
  box-shadow:0 8px 22px rgba(26,37,112,.4),inset 0 1px 0 rgba(255,255,255,.25);
  transition:transform .15s ease,filter .15s ease,box-shadow .2s ease;}
.btn:hover{transform:translateY(-1px);filter:brightness(1.08);box-shadow:0 10px 30px rgba(26,37,112,.5),0 0 0 5px rgba(43,57,144,.12),inset 0 1px 0 rgba(255,255,255,.25);}
.btn:active{transform:translateY(0) scale(.98);}
.btn:focus-visible{outline:2px solid #fff;outline-offset:3px;}
.erro{display:none;background:rgba(254,242,242,.85);border:1px solid #fecaca;border-radius:14px;
  padding:12px 16px;margin-top:14px;font-size:13px;color:#991b1b;font-weight:600;text-align:center;}
.erro.show{display:block;}
.divider{border-top:1px solid rgba(0,0,0,.06);margin:22px 0 0;}
.prof-link{display:flex;align-items:center;justify-content:center;gap:8px;
  padding:17px 32px;text-decoration:none;color:#2b3990;font-size:13px;font-weight:800;
  transition:background .15s;}
.prof-link:hover{background:rgba(247,248,255,.6);}
.prof-link span{background:rgba(232,234,248,.8);border-radius:999px;padding:4px 12px;font-size:11px;font-weight:900;}
.footer{border-top:1px solid rgba(0,0,0,.08);padding:16px 28px 18px;text-align:center;}
.footer-name{font-family:'Fredoka One',cursive;font-size:12.5px;color:#2b3990;letter-spacing:.2px;}
.footer-sub{font-size:10.5px;color:#8b90b3;font-weight:600;margin-top:3px;letter-spacing:.3px;}
.footer-link{display:inline-block;margin-top:11px;font-size:11px;font-weight:800;color:#2b3990;
  text-decoration:none;background:rgba(43,57,144,.09);padding:6px 16px;border-radius:999px;transition:background .15s,transform .15s;}
.footer-link:hover{background:rgba(43,57,144,.17);transform:translateY(-1px);}
.footer-link:focus-visible{outline:2px solid #2b3990;outline-offset:2px;}
.loading{display:none;text-align:center;padding:16px 0 2px;}
.loading.show{display:block;}
.spinner{width:26px;height:26px;border:3px solid #e8eaf8;border-top-color:#2b3990;
  border-radius:50%;animation:spin .7s linear infinite;margin:0 auto 7px;}
@keyframes spin{to{transform:rotate(360deg)}}
@media(max-width:480px){
  .lg-blob{filter:blur(44px);}
  .lg-blob-1,.lg-blob-2,.lg-blob-3{width:220px;height:220px;}
  .top{padding:26px 22px 22px;}
  .top h1{font-size:19px;}
  .body{padding:22px 22px 20px;}
}
</style>
</head>
<body>
<div class="lg-bg" aria-hidden="true">
  <span class="lg-blob lg-blob-1"></span>
  <span class="lg-blob lg-blob-2"></span>
  <span class="lg-blob lg-blob-3"></span>
</div>
<div class="card">
  <div class="top">
    <img src="/static/logo.png" alt="Escola Espaço Alegre">
    <h1>Acompanhe a jornada do seu filho</h1>
    <p>Boletins e relatórios escolares, sempre à mão</p>
  </div>
  <div class="body">
    <form id="frm" onsubmit="buscar(event)">
      <label for="mat">Número de Matrícula</label>
      <div class="inp-wrap">
        <svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
          <circle cx="11" cy="11" r="7"></circle><line x1="21" y1="21" x2="16.6" y2="16.6"></line>
        </svg>
        <input type="text" id="mat" placeholder="Digite o número da matrícula"
               maxlength="12" autocomplete="off" inputmode="numeric"
               aria-label="Número de Matrícula"
               oninput="limpaErro()">
        <button type="button" class="clr" onclick="limpar()" aria-label="Limpar campo">✕</button>
      </div>
      <button type="submit" class="btn">Consultar boletim →</button>
    </form>
    <div class="loading" id="loading"><div class="spinner"></div><p style="font-size:12px;color:#7d83a3;">Buscando...</p></div>
    <div class="erro" id="erro" role="alert">❌ Matrícula não encontrada. Verifique o número e tente novamente.</div>
  </div>
  <div class="divider"></div>
  <a href="/professora/login" class="prof-link">
    👩‍🏫 &nbsp;Sou Professor(a) &nbsp;<span>Acessar →</span>
  </a>
  <div class="footer">
    <div class="footer-name">Escola Espaço Alegre</div>
    <div class="footer-sub">Ed. Infantil e Fundamental Anos Iniciais · Bilíngue · 2026</div>
    <a href="/privacidade" class="footer-link">🔒 Política de Privacidade</a>
  </div>
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

MANUTENCAO_HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Escola Espaço Alegre – Em atualização</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Plus Jakarta Sans','Nunito',sans-serif;-webkit-font-smoothing:antialiased;
  background:linear-gradient(160deg,#1a2570 0%,#2b3990 40%,#1a5fa8 100%);
  min-height:100vh;display:flex;align-items:center;justify-content:center;padding:24px 16px;
  position:relative;overflow-x:hidden;}
.lg-bg{position:fixed;inset:0;z-index:0;overflow:hidden;pointer-events:none;}
.lg-blob{position:absolute;border-radius:50%;filter:blur(70px);opacity:.45;}
.lg-blob-1{width:460px;height:460px;top:-140px;left:-120px;background:#7d8bff;}
.lg-blob-2{width:400px;height:400px;bottom:-160px;right:-100px;background:#f7d800;opacity:.3;}
.card{position:relative;z-index:1;background:rgba(255,255,255,.62);backdrop-filter:blur(26px) saturate(180%);
  -webkit-backdrop-filter:blur(26px) saturate(180%);border:1px solid rgba(255,255,255,.55);
  border-radius:26px;box-shadow:0 20px 60px rgba(10,15,50,.35),inset 0 1px 0 rgba(255,255,255,.6);
  width:100%;max-width:440px;overflow:hidden;text-align:center;}
.top{background:linear-gradient(135deg,#3b49b8,#1a2570);padding:34px 32px 26px;
  border-bottom:4px solid #f7d800;}
.top img{height:54px;object-fit:contain;background:#fff;padding:10px 18px;border-radius:18px;
  box-shadow:0 6px 18px rgba(0,0,0,.22);}
.body{padding:34px 32px 32px;}
.icone{font-size:46px;margin-bottom:14px;line-height:1;}
.body h1{font-family:'Fredoka One',cursive;font-size:21px;color:#1a2570;line-height:1.3;margin-bottom:12px;}
.body p{font-size:14px;color:#41476b;font-weight:600;line-height:1.6;}
.body p.sub{font-size:12.5px;color:#7d83a3;margin-top:14px;}
.btn{display:inline-flex;align-items:center;gap:8px;margin-top:24px;
  font-family:'Plus Jakarta Sans',sans-serif;font-size:14px;font-weight:800;text-decoration:none;
  background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;border-radius:999px;
  padding:13px 26px;box-shadow:0 8px 22px rgba(26,37,112,.4);}
.footer{border-top:1px solid rgba(0,0,0,.06);padding:13px 32px;font-size:11px;color:#7d83a3;}
</style>
</head>
<body>
<div class="lg-bg" aria-hidden="true">
  <span class="lg-blob lg-blob-1"></span>
  <span class="lg-blob lg-blob-2"></span>
</div>
<div class="card">
  <div class="top"><img src="/static/logo.png" alt="Escola Espaço Alegre"></div>
  <div class="body">
    <div class="icone">🛠️</div>
    <h1>Estamos preparando tudo para você</h1>
    <p>A área de boletins e relatórios está <b>temporariamente indisponível</b>
       enquanto a coordenação atualiza as informações na plataforma.</p>
    <p class="sub">Por favor, volte um pouco mais tarde para consultar o material do seu filho. 💛</p>
    <a href="/" class="btn">Voltar ao início</a>
  </div>
  <div class="footer">Escola Espaço Alegre &nbsp;|&nbsp; Ed. Infantil e Fundamental Anos Iniciais</div>
</div>
</body>
</html>"""

def _pais_bloqueado(request: Request, ref: str = "") -> bool:
    """True quando a área dos pais está desativada e o acesso deve ser barrado.

    Liberada -> nunca bloqueia.
    Desativada -> bloqueia todos (inclusive admin/coordenação abrindo o link
    público, para que o efeito do botão seja visível ao testar). A equipe só
    continua acessando quando abre pelo painel ("Ver Boletim", ref=admin)."""
    if get_pais_liberado():
        return False
    if ref == "admin" and check_staff(request):
        return False
    return True


def _client_ip(request: Request) -> str:
    """IP real do visitante, considerando o proxy do Railway (X-Forwarded-For)."""
    xff = request.headers.get("x-forwarded-for", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.client.host if request.client else ""


_CONSULTA_BLOQUEADA_HTML = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<link rel="icon" type="image/png" href="/static/favicon.png">
<title>Muitas consultas</title>
<style>body{font-family:'Nunito',system-ui,sans-serif;background:linear-gradient(160deg,#1a2570,#1a5fa8);
min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;padding:24px;}
.c{background:#fff;border-radius:22px;padding:38px 34px;max-width:420px;text-align:center;
box-shadow:0 20px 60px rgba(10,15,50,.35);}h1{font-size:20px;color:#1a2570;margin:10px 0;}
p{font-size:14px;color:#555;line-height:1.6;}a{display:inline-block;margin-top:22px;text-decoration:none;
background:#2b3990;color:#fff;font-weight:800;padding:12px 26px;border-radius:999px;font-size:14px;}</style>
</head><body><div class="c"><div style="font-size:44px;">🛡️</div>
<h1>Muitas consultas em pouco tempo</h1>
<p>Detectamos um número alto de consultas a partir deste acesso. Por segurança dos dados dos
alunos, aguarde alguns minutos e tente novamente.</p>
<a href="/">Voltar ao início</a></div></body></html>"""


def _auditar(request: Request, acao: str, alvo: str = "", detalhe: str = ""):
    """Registra na trilha de auditoria uma ação feita por um usuário logado."""
    user = get_session_user(request) or {}
    daud.registrar(
        usuario=user.get("nome") or user.get("username", "?"),
        role=user.get("role", ""),
        acao=acao, alvo=alvo, detalhe=detalhe,
    )


def _consulta_bloqueada_resp(request: Request, matricula: str):
    """Retorna uma resposta de bloqueio se o visitante (não-equipe) estiver
    fazendo varredura de matrículas; caso contrário, None."""
    if check_staff(request):
        return None
    if consulta_bloqueada(_client_ip(request), matricula):
        return HTMLResponse(_CONSULTA_BLOQUEADA_HTML, status_code=429)
    return None


def _registrar_acesso_pai(request: Request, aluno: dict, matricula: str, documento: str, ref: str = ""):
    """Registra o acesso de um responsável a um documento.

    Só NÃO conta quando a equipe abre pelo painel ("Ver Boletim", ref=admin) —
    aí é gestão interna. Abrir o link público normal conta como acesso (mesmo
    logado), o que também permite à coordenação testar a funcionalidade."""
    if ref == "admin" and check_staff(request):
        return
    dac.registrar_acesso(
        matricula=matricula,
        nome_aluno=aluno.get("nome", ""),
        turma=aluno.get("turma", ""),
        documento=documento,
        ip=_client_ip(request),
        user_agent=request.headers.get("user-agent", ""),
    )


@app.get("/", response_class=HTMLResponse)
async def index():
    return inject_player(INDEX_HTML)


PRIVACIDADE_HTML = """<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Política de Privacidade — Escola Espaço Alegre</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:linear-gradient(160deg,#e9ecfb,#cfe7f0);
  color:#2b3344;min-height:100vh;padding:28px 16px;}
.wrap{max-width:760px;margin:0 auto;background:#fff;border-radius:22px;padding:34px 32px;
  box-shadow:0 16px 50px rgba(43,57,144,.16);}
h1{font-family:'Fredoka One',cursive;color:#2b3990;font-size:24px;margin-bottom:4px;}
.sub{color:#7d83a3;font-size:13px;margin-bottom:22px;}
h2{color:#2b3990;font-size:16px;margin:22px 0 8px;}
p,li{font-size:14px;line-height:1.7;color:#41476b;}
ul{margin:6px 0 6px 20px;}
.back{display:inline-block;margin-top:26px;text-decoration:none;background:#2b3990;color:#fff;
  font-weight:800;padding:12px 26px;border-radius:999px;font-size:14px;}
.box{background:#f5f7ff;border:1px solid #e0e5ff;border-radius:12px;padding:14px 16px;margin-top:10px;font-size:13px;}
</style></head><body>
<div class="wrap">
  <h1>Política de Privacidade</h1>
  <div class="sub">Escola Espaço Alegre — tratamento de dados conforme a LGPD (Lei nº 13.709/2018)</div>

  <p>Esta plataforma permite que responsáveis consultem boletins, relatórios semestrais e
  avaliações dos alunos, e que a equipe pedagógica gerencie essas informações.</p>

  <h2>1. Quais dados tratamos</h2>
  <ul>
    <li><strong>Dos alunos (crianças):</strong> nome, turma, período, professora, matrícula, notas,
        frequência, observações pedagógicas, relatórios e avaliações em PDF.</li>
    <li><strong>Da equipe (usuários internos):</strong> nome, usuário/e-mail de acesso e senha (armazenada
        de forma criptografada).</li>
    <li><strong>De navegação:</strong> ao abrir um documento, registramos data/hora, tipo de documento,
        dispositivo (web/celular/tablet) e um <strong>IP parcial/anonimizado</strong>, para acompanhamento
        interno de acesso. Não usamos cookies de rastreamento ou publicidade.</li>
  </ul>

  <h2>2. Por que tratamos esses dados</h2>
  <p>Para a finalidade educacional de acompanhamento escolar e comunicação com as famílias
  (execução do contrato educacional e legítimo interesse pedagógico da escola).</p>

  <h2>3. Quem tem acesso</h2>
  <p>Apenas a administração e a coordenação têm acesso pleno. Professoras acessam somente as turmas
  vinculadas a elas. Os responsáveis acessam exclusivamente os documentos do próprio aluno.</p>

  <h2>4. Por quanto tempo guardamos</h2>
  <p>Os dados são mantidos enquanto durar o vínculo escolar e pelo prazo necessário ao cumprimento de
  obrigações legais. Registros de acesso são mantidos apenas pelo tempo útil ao acompanhamento.</p>

  <h2>5. Seus direitos</h2>
  <p>O titular (ou seu responsável legal) pode solicitar confirmação, acesso, correção, anonimização
  ou exclusão de dados, bem como informações sobre o tratamento.</p>
  <div class="box">📧 Para exercer seus direitos ou tirar dúvidas, entre em contato com a secretaria da
  Escola Espaço Alegre.</div>

  <h2>6. Segurança</h2>
  <p>Adotamos medidas técnicas como senhas criptografadas, acesso restrito por perfil, conexão segura
  (HTTPS), cabeçalhos de segurança e registro de acessos. Ainda assim, nenhum sistema é 100% imune;
  trabalhamos continuamente para proteger os dados das crianças e famílias.</p>

  <a href="/" class="back">← Voltar ao início</a>
</div>
</body></html>"""


@app.get("/privacidade", response_class=HTMLResponse)
async def privacidade():
    return HTMLResponse(PRIVACIDADE_HTML)

@app.get("/boletim/{matricula}", response_class=HTMLResponse)
async def ver_boletim(request: Request, matricula: str, ref: str = ""):
    if _pais_bloqueado(request, ref):
        return HTMLResponse(MANUTENCAO_HTML)
    mat_clean = re.sub(r'\D', '', matricula)
    if not mat_clean:
        return RedirectResponse("/?erro=1")
    bloq = _consulta_bloqueada_resp(request, mat_clean)
    if bloq:
        return bloq

    aluno = get_aluno(mat_clean)
    if not aluno:
        return RedirectResponse("/?erro=1")

    # Alunos da Ed. Infantil não têm boletim — têm relatório semestral.
    if is_infantil(aluno.get("turma", "")):
        return RedirectResponse(f"/relatorio/{mat_clean}")

    aluno_completo = dict(aluno)
    aluno_completo['matricula'] = mat_clean
    back_url = "/admin" if ref == "admin" else "/"
    _registrar_acesso_pai(request, aluno, mat_clean, "boletim", ref=ref)
    sems = dav.semestres_disponiveis(mat_clean)
    card = card_avaliacao_pais(mat_clean, sems) if sems else ""
    extra = banner_festas_pais() + card
    return HTMLResponse(inject_player(gerar_boletim_html(aluno_completo, back_url=back_url, extra_html=extra)))


def _aluno_infantil_responsavel(matricula: str):
    """Resolve o aluno infantil para a área do responsável.
    Retorna (aluno, mat_clean) ou (None, RedirectResponse)."""
    mat_clean = re.sub(r'\D', '', matricula)
    if not mat_clean:
        return None, RedirectResponse("/?erro=1")
    aluno = get_aluno(mat_clean)
    if not aluno:
        return None, RedirectResponse("/?erro=1")
    if not is_infantil(aluno.get("turma", "")):
        return None, RedirectResponse(f"/boletim/{mat_clean}")
    return (aluno, mat_clean), None


@app.get("/relatorio/{matricula}", response_class=HTMLResponse)
async def ver_relatorio_responsavel(request: Request, matricula: str):
    """Tela onde o responsável escolhe qual semestre do relatório deseja ver."""
    if _pais_bloqueado(request):
        return HTMLResponse(MANUTENCAO_HTML)
    bloq = _consulta_bloqueada_resp(request, re.sub(r'\D', '', matricula))
    if bloq:
        return bloq
    dados, redir = _aluno_infantil_responsavel(matricula)
    if redir:
        return redir
    aluno, mat_clean = dados

    ano = aluno.get("ano_letivo", "2026")
    disponivel = {}
    for semestre in (1, 2):
        rel = get_relatorio(mat_clean, semestre, ano)
        disponivel[semestre] = bool(rel and rel.get("status") == "concluido")

    _registrar_acesso_pai(request, aluno, mat_clean, "relatorio")
    sems = dav.semestres_disponiveis(mat_clean)
    card = card_avaliacao_pais(mat_clean, sems) if sems else ""
    extra = banner_festas_pais() + card
    return HTMLResponse(inject_player(gerar_escolha_semestre_html(aluno, mat_clean, disponivel, extra_html=extra)))


@app.get("/relatorio/{matricula}/{semestre}", response_class=HTMLResponse)
async def ver_relatorio_semestre(request: Request, matricula: str, semestre: int):
    """Mostra o relatório do semestre escolhido (se concluído e liberado);
    caso contrário, exibe a mensagem amigável de indisponível."""
    if _pais_bloqueado(request):
        return HTMLResponse(MANUTENCAO_HTML)
    bloq = _consulta_bloqueada_resp(request, re.sub(r'\D', '', matricula))
    if bloq:
        return bloq
    dados, redir = _aluno_infantil_responsavel(matricula)
    if redir:
        return redir
    aluno, mat_clean = dados
    if semestre not in (1, 2):
        return RedirectResponse(f"/relatorio/{mat_clean}")

    ano = aluno.get("ano_letivo", "2026")
    relatorio = get_relatorio(mat_clean, semestre, ano)
    if not (relatorio and relatorio.get("status") == "concluido"):
        return HTMLResponse(inject_player(gerar_relatorio_indisponivel_html(aluno, mat_clean, semestre)))

    temas = get_temas_para_turma(aluno.get("turma", ""))
    respostas = get_respostas(relatorio["id"])
    itens = [(semestre, relatorio, temas, respostas)]
    return HTMLResponse(inject_player(gerar_relatorios_aluno_print_html(aluno, mat_clean, itens)))

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
    return login_page(erro="1" in erro, bloqueado="bloqueado" in erro)

@app.post("/admin/login")
async def post_login(
    request: Request,
    usuario: str = Form(...),
    senha:   str = Form(...),
):
    ip = _client_ip(request)
    if login_bloqueado(ip):
        return RedirectResponse("/admin/login?erro=bloqueado", status_code=302)
    user = authenticate_user(usuario, senha)
    if user and user.get("role") in ("admin", "coordenacao"):
        limpar_falhas_login(ip)
        resp = RedirectResponse("/admin", status_code=302)
        resp.set_cookie(COOKIE_NAME, make_session_token(user),
                        max_age=COOKIE_MAX, httponly=True, samesite="lax",
                        secure=COOKIE_SECURE)
        return resp
    registrar_falha_login(ip)
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
    if not check_admin(request):
        return RedirectResponse("/admin/relatorios", status_code=302)
    alunos = get_all_alunos()
    # Busca status dos relatórios dos alunos do Infantil em uma única query
    matriculas_inf = [m for m, a in alunos.items() if is_infantil(a.get("turma", ""))]
    rel_status = get_status_relatorios(matriculas_inf) if matriculas_inf else {}
    return admin_dashboard(alunos, resetado=bool(resetado), rel_status=rel_status)

@app.get("/admin/aluno/novo", response_class=HTMLResponse)
async def novo_aluno_form(request: Request):
    if not check_admin(request):
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
    if not check_admin(request):
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
    if not check_admin(request):
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

    novo = matricula == "novo"
    upsert_aluno(mat, dados)
    _auditar(request, "Cadastrar aluno" if novo else "Editar aluno",
             alvo=mat, detalhe=dados.get("nome", ""))
    return RedirectResponse(f"/admin/aluno/{mat}?ok=1", status_code=302)

@app.get("/admin/aluno/{matricula}/excluir")
async def excluir_aluno(request: Request, matricula: str):
    if not check_admin(request):
        return _redir_login()
    alvo = (get_aluno(matricula) or {}).get("nome", matricula)
    delete_aluno(matricula)
    _auditar(request, "Excluir aluno", alvo=matricula, detalhe=alvo)
    return RedirectResponse("/admin", status_code=302)

@app.get("/admin/aluno/{matricula}/editar-infantil", response_class=HTMLResponse)
async def editar_aluno_infantil(request: Request, matricula: str, ok: str = ""):
    if not check_admin(request):
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
    if not check_admin(request):
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
    if not check_admin(request):
        return _redir_login()
    reset_db()
    return RedirectResponse("/admin?resetado=1", status_code=302)


@app.post("/admin/seed-infantil")
async def seed_infantil_route(request: Request):
    """Importa alunos e professoras da Ed. Infantil — idempotente, seguro para rodar várias vezes."""
    if not check_admin(request):
        return _redir_login()
    from seed_infantil import run_seed
    r = run_seed()
    msg = f"{r['alunos']}+alunos+e+{r['professoras']}+professoras+importados"
    return RedirectResponse(f"/admin?resetado=1&seed_msg={msg}", status_code=302)


@app.post("/admin/seed-estrutura-avaliativa")
async def seed_estrutura_avaliativa_route(request: Request):
    """Importa a estrutura avaliativa (Tópico→Tema→Subtema) da Ed. Infantil — idempotente."""
    if not check_admin(request):
        return _redir_login()
    from seed_estrutura_avaliativa import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil3")
async def seed_estrutura_infantil3_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 3 (A e B) — idempotente."""
    if not check_admin(request):
        return _redir_login()
    from seed_estrutura_infantil3 import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil4")
async def seed_estrutura_infantil4_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 4 (A e B) — idempotente."""
    if not check_admin(request):
        return _redir_login()
    from seed_estrutura_infantil4 import run_seed
    r = run_seed()
    msg = f"{r['topicos']}+t%C3%B3picos%2C+{r['temas']}+temas+e+{r['subtemas']}+subtemas+importados"
    return RedirectResponse(f"/admin/temas?ok={msg}", status_code=302)


@app.post("/admin/seed-estrutura-infantil5")
async def seed_estrutura_infantil5_route(request: Request):
    """Importa a estrutura avaliativa específica do Infantil 5 (A) — idempotente."""
    if not check_admin(request):
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
    if not check_admin(request):
        return _redir_login()
    todos = get_all_usuarios()
    professoras = [u for u in todos if u["role"] == "professora"]
    coordenadoras = [u for u in todos if u["role"] == "coordenacao"]
    alunos_map = _alunos_por_professora()
    return admin_professoras_page(professoras, alunos_map, msg=ok, erro=erro,
                                   senha_gerada=senha_gerada, coordenadoras=coordenadoras)


@app.post("/admin/coordenacao/nova")
async def criar_coordenadora(request: Request):
    if not check_admin(request):
        return _redir_login()
    form = await request.form()
    nome = form.get("nome", "").strip()
    username = form.get("username", "").strip()
    senha = form.get("senha", "").strip()

    if len(senha) < 6:
        return RedirectResponse("/admin/professoras?erro=Senha+deve+ter+ao+menos+6+caracteres", status_code=302)
    try:
        create_usuario(username, senha, nome, role="coordenacao")
        return RedirectResponse(f"/admin/professoras?ok=Coordenadora+{nome}+cadastrada", status_code=302)
    except ValueError:
        return RedirectResponse("/admin/professoras?erro=Usu%C3%A1rio+j%C3%A1+existe", status_code=302)


@app.post("/admin/professoras/nova")
async def criar_professora(request: Request):
    if not check_admin(request):
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
        _auditar(request, "Cadastrar professora", alvo=nome)
        return RedirectResponse(f"/admin/professoras?ok=Professora+{nome}+cadastrada", status_code=302)
    except ValueError:
        return RedirectResponse("/admin/professoras?erro=Usu%C3%A1rio+j%C3%A1+existe", status_code=302)


@app.post("/admin/professoras/renomear")
async def renomear_professora_route(request: Request):
    """Corrige o nome de uma professora: atualiza todos os alunos vinculados
    (boletins e relatórios passam a exibir o nome correto) e, se existir, a
    conta de login correspondente."""
    if not check_admin(request):
        return _redir_login()
    form = await request.form()
    antigo = form.get("antigo", "").strip()
    novo   = form.get("novo", "").strip()
    if not antigo or not novo:
        return RedirectResponse("/admin/professoras?erro=Informe+o+nome+atual+e+o+novo+nome", status_code=302)
    if antigo == novo:
        return RedirectResponse("/admin/professoras?erro=O+novo+nome+%C3%A9+igual+ao+atual", status_code=302)

    n = renomear_professora(antigo, novo)
    # Corrige também a conta de login da professora, se houver uma com esse nome.
    for u in get_all_usuarios():
        if u.get("nome", "").strip() == antigo:
            update_usuario_nome(u["id"], novo)
    _auditar(request, "Renomear professora", alvo=novo, detalhe=f"'{antigo}' → '{novo}' ({n} aluno(s))")
    msg = f"Nome corrigido para '{novo}' em {n} aluno(s). Boletins e relatórios já refletem a mudança."
    return RedirectResponse(f"/admin/professoras?ok={quote(msg)}", status_code=302)


@app.post("/admin/professoras/{user_id}/turmas")
async def salvar_turmas_professora(request: Request, user_id: int):
    if not check_admin(request):
        return _redir_login()
    form   = await request.form()
    turmas = list(form.getlist("turma"))
    update_usuario_turmas(user_id, turmas)
    alvo = (get_usuario_by_id(user_id) or {}).get("nome", str(user_id))
    _auditar(request, "Atualizar turmas da professora", alvo=alvo, detalhe=", ".join(turmas))
    return RedirectResponse("/admin/professoras?ok=Turmas+atualizadas", status_code=302)


@app.post("/admin/professoras/{user_id}/excluir")
async def excluir_professora(request: Request, user_id: int):
    if not check_admin(request):
        return _redir_login()
    alvo = (get_usuario_by_id(user_id) or {}).get("nome", str(user_id))
    delete_usuario(user_id)
    _auditar(request, "Excluir colaboradora", alvo=alvo)
    return RedirectResponse("/admin/professoras?ok=Professora+removida", status_code=302)


@app.post("/admin/professoras/{user_id}/resetar-senha")
async def resetar_senha_professora(request: Request, user_id: int):
    if not check_admin(request):
        return _redir_login()
    nova_senha = reset_usuario_senha(user_id)
    if nova_senha:
        alvo = (get_usuario_by_id(user_id) or {}).get("nome", str(user_id))
        _auditar(request, "Resetar senha", alvo=alvo)
        return RedirectResponse(
            f"/admin/professoras?ok=Senha+resetada+com+sucesso&senha_gerada={quote(nova_senha)}",
            status_code=302,
        )
    return RedirectResponse("/admin/professoras?erro=N%C3%A3o+foi+poss%C3%ADvel+resetar+a+senha", status_code=302)


@app.get("/admin/aluno/{matricula}/relatorios", response_class=HTMLResponse)
async def admin_ver_relatorios_aluno(request: Request, matricula: str):
    """Página que mostra os relatórios semestrais de um aluno Infantil."""
    if not check_staff(request):
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
    if not check_admin(request):
        return _redir_login()
    topicos = get_all_topicos()
    return admin_temas_page(topicos, msg=ok, erro=erro)


# ── Tópicos ──────────────────────────────────────────────────────────────────

@app.post("/admin/topicos/novo")
async def criar_topico(request: Request, nome: str = Form(...)):
    if not check_admin(request):
        return _redir_login()
    nome = nome.strip()
    if not nome:
        return RedirectResponse("/admin/temas?erro=Nome+do+t%C3%B3pico+n%C3%A3o+pode+ser+vazio", status_code=302)
    create_topico(nome)
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+criado+com+sucesso", status_code=302)


@app.post("/admin/topicos/{topico_id}/editar")
async def editar_topico(request: Request, topico_id: int, nome: str = Form(...)):
    if not check_admin(request):
        return _redir_login()
    update_topico(topico_id, nome.strip())
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+atualizado", status_code=302)


@app.post("/admin/topicos/{topico_id}/excluir")
async def excluir_topico(request: Request, topico_id: int):
    if not check_admin(request):
        return _redir_login()
    delete_topico(topico_id)
    return RedirectResponse("/admin/temas?ok=T%C3%B3pico+removido", status_code=302)


# ── Temas ─────────────────────────────────────────────────────────────────────

@app.post("/admin/temas/novo")
async def criar_tema(request: Request):
    if not check_admin(request):
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
    if not check_admin(request):
        return _redir_login()
    update_tema(tema_id, nome.strip())
    return RedirectResponse("/admin/temas?ok=Tema+atualizado", status_code=302)


@app.post("/admin/temas/{tema_id}/excluir")
async def excluir_tema(request: Request, tema_id: int):
    if not check_admin(request):
        return _redir_login()
    delete_tema(tema_id)
    return RedirectResponse("/admin/temas?ok=Tema+removido", status_code=302)


@app.post("/admin/temas/{tema_id}/subtema")
async def criar_subtema(request: Request, tema_id: int, descricao: str = Form(...)):
    if not check_admin(request):
        return _redir_login()
    descricao = descricao.strip()
    if not descricao:
        return RedirectResponse("/admin/temas?erro=Descri%C3%A7%C3%A3o+do+subtema+n%C3%A3o+pode+ser+vazia", status_code=302)
    create_subtema(tema_id, descricao)
    return RedirectResponse("/admin/temas?ok=Subtema+adicionado", status_code=302)


@app.post("/admin/subtemas/{subtema_id}/editar")
async def editar_subtema(request: Request, subtema_id: int, descricao: str = Form(...)):
    if not check_admin(request):
        return _redir_login()
    descricao = descricao.strip()
    if not descricao:
        return RedirectResponse("/admin/temas?erro=Descri%C3%A7%C3%A3o+do+subtema+n%C3%A3o+pode+ser+vazia", status_code=302)
    update_subtema(subtema_id, descricao)
    return RedirectResponse("/admin/temas?ok=Subtema+atualizado", status_code=302)


@app.post("/admin/subtemas/{subtema_id}/excluir")
async def excluir_subtema(request: Request, subtema_id: int):
    if not check_admin(request):
        return _redir_login()
    delete_subtema(subtema_id)
    return RedirectResponse("/admin/temas?ok=Subtema+removido", status_code=302)


@app.post("/admin/topicos/{topico_id}/turmas")
async def salvar_turmas_topico(request: Request, topico_id: int):
    if not check_admin(request):
        return _redir_login()
    form = await request.form()
    turmas = list(form.getlist("turma"))
    update_topico_turmas(topico_id, turmas)
    return RedirectResponse("/admin/temas?ok=Turmas+do+t%C3%B3pico+salvas", status_code=302)


@app.post("/admin/temas/{tema_id}/turmas")
async def salvar_turmas_tema(request: Request, tema_id: int):
    if not check_admin(request):
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
    return professora_login_page(erro="1" in erro, bloqueado="bloqueado" in erro)


@app.post("/professora/login")
async def prof_post_login(
    request: Request,
    usuario: str = Form(...),
    senha:   str = Form(...),
):
    ip = _client_ip(request)
    if login_bloqueado(ip):
        return RedirectResponse("/professora/login?erro=bloqueado", status_code=302)
    user = authenticate_user(usuario, senha)
    if user and user.get("role") in ("admin", "professora"):
        limpar_falhas_login(ip)
        resp = RedirectResponse("/professora?bemvindo=1", status_code=302)
        resp.set_cookie(COOKIE_NAME, make_session_token(user),
                        max_age=COOKIE_MAX, httponly=True, samesite="lax",
                        secure=COOKIE_SECURE)
        return resp
    registrar_falha_login(ip)
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
    descricao  = sanitizar_html(form.get("descricao_final", "").strip())

    save_respostas(relatorio["id"], respostas)
    update_relatorio(relatorio["id"], "em_andamento", descricao, editado_por=user["nome"])

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
    descricao = sanitizar_html(form.get("descricao_final", "").strip())

    # Validação server-side: todos os subtemas da turma respondidos
    turma = aluno.get("turma", "")
    temas = get_temas_para_turma(turma)
    todos_ids = [st["id"] for t in temas for st in t.get("subtemas", [])]
    faltando  = [sid for sid in todos_ids if sid not in respostas or not respostas[sid]]
    if faltando:
        save_respostas(relatorio["id"], respostas)
        update_relatorio(relatorio["id"], "em_andamento", descricao, editado_por=user["nome"])
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=Preencha+todos+os+{len(todos_ids)}+subtemas+antes+de+confirmar",
            status_code=302,
        )

    if len(descricao) < 10:
        save_respostas(relatorio["id"], respostas)
        update_relatorio(relatorio["id"], "em_andamento", descricao, editado_por=user["nome"])
        return RedirectResponse(
            f"/professora/relatorio/{matricula}/{semestre}?erro=A+descri%C3%A7%C3%A3o+final+%C3%A9+obrigat%C3%B3ria",
            status_code=302,
        )

    save_respostas(relatorio["id"], respostas)
    update_relatorio(relatorio["id"], "concluido", descricao, editado_por=user["nome"])
    _auditar(request, "Confirmar relatório", alvo=matricula,
             detalhe=f"{semestre}º sem · {aluno.get('nome','')}")

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
    cont_s1 = {"pendentes": 0, "andamento": 0, "concluidos": 0}
    cont_s2 = {"pendentes": 0, "andamento": 0, "concluidos": 0}

    def _conta(cont: dict, s: str) -> None:
        if s == "concluido":
            cont["concluidos"] += 1
        elif s == "em_andamento":
            cont["andamento"] += 1
        else:
            cont["pendentes"] += 1

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

        # Contadores por semestre (sem filtro de status)
        _conta(cont_s1, s1)
        _conta(cont_s2, s2)

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
        "pendentes": cont_s1["pendentes"] + cont_s2["pendentes"],
        "andamento": cont_s1["andamento"] + cont_s2["andamento"],
        "concluidos":cont_s1["concluidos"] + cont_s2["concluidos"],
        "s1":        cont_s1,
        "s2":        cont_s2,
    }
    return rows, turmas_inf, contadores


@app.get("/admin/relatorios", response_class=HTMLResponse)
async def admin_relatorios(
    request: Request,
    turma: str = "", semestre: str = "", status: str = "",
    ok: str = "", erro: str = "",
):
    if not check_staff(request):
        return _redir_login()
    rows, turmas_inf, cont = _painel_relatorios_data(turma, semestre, status)
    filtros = {"turma": turma, "semestre": semestre, "status": status}
    is_admin_user = check_admin(request)
    return admin_relatorios_page(rows, turmas_inf, filtros, cont, msg=ok, erro=erro,
                                 staff_only=not is_admin_user, pais_liberado=get_pais_liberado())


@app.post("/admin/visibilidade")
async def admin_visibilidade(request: Request, liberar: str = Form("")):
    """Liga/desliga o acesso dos pais aos boletins e relatórios.
    Disponível para admin e coordenação."""
    if not check_staff(request):
        return _redir_login()
    set_pais_liberado(liberar == "1")
    _auditar(request, "Visibilidade dos pais", detalhe=("liberada" if liberar == "1" else "desativada"))
    msg = ("Área dos pais LIBERADA — os responsáveis já conseguem consultar."
           if liberar == "1" else
           "Área dos pais DESATIVADA — os responsáveis verão a mensagem de atualização.")
    return RedirectResponse(f"/admin/relatorios?ok={quote(msg)}", status_code=302)


# ════════════════════════════════════════════════════════════════════════════
#  AVALIAÇÕES EM PDF (ex.: Avaliação de Inglês) — admin/coordenação + pais
# ════════════════════════════════════════════════════════════════════════════

def _sem_aval(valor) -> int:
    """Normaliza o semestre vindo da requisição (1 ou 2; padrão 1)."""
    return int(valor) if dav.semestre_valido(valor) else dav.SEMESTRE_PADRAO


def _redir_avaliacoes(msg: str = "", erro: str = "", semestre: int = 1):
    qs = [f"semestre={semestre}"]
    if msg:
        qs.append(f"ok={quote(msg)}")
    if erro:
        qs.append(f"erro={quote(erro)}")
    return RedirectResponse(f"/admin/avaliacoes?{'&'.join(qs)}", status_code=302)


@app.get("/admin/avaliacoes", response_class=HTMLResponse)
async def admin_avaliacoes(request: Request, semestre: str = "1", ok: str = "", erro: str = ""):
    if not check_staff(request):
        return _redir_login()
    sem = _sem_aval(semestre)
    alunos = get_all_alunos()
    vinculos = dav.get_avaliacoes_map(semestre=sem)
    arquivos = dav.listar_arquivos()
    # Sugestão automática só faz sentido p/ o 1º semestre (arquivos atuais).
    sugestoes = dav.sugerir_vinculos(alunos) if sem == 1 else {}
    return admin_avaliacoes_page(alunos, vinculos, arquivos, sugestoes, semestre=sem,
                                 msg=ok, erro=erro, staff_only=not check_admin(request))


@app.post("/admin/avaliacoes/associar")
async def admin_avaliacoes_associar(
    request: Request, matricula: str = Form(...), arquivo: str = Form(...),
    semestre: str = Form("1"),
):
    if not check_staff(request):
        return _redir_login()
    sem = _sem_aval(semestre)
    if not get_aluno(matricula):
        return _redir_avaliacoes(erro="Aluno não encontrado.", semestre=sem)
    if dav.resolver_caminho(dav.DISCIPLINA_PADRAO, arquivo) is None:
        return _redir_avaliacoes(erro="Arquivo selecionado é inválido ou não foi encontrado.", semestre=sem)
    user = get_session_user(request) or {}
    dav.set_avaliacao(matricula, arquivo, arquivo, user.get("nome", ""), semestre=sem)
    _auditar(request, "Vincular avaliação de inglês", alvo=matricula, detalhe=f"{sem}º sem · {arquivo}")
    return _redir_avaliacoes(msg="Avaliação vinculada com sucesso.", semestre=sem)


@app.post("/admin/avaliacoes/auto")
async def admin_avaliacoes_auto(request: Request, semestre: str = Form("1")):
    """Vincula automaticamente todas as sugestões de alto grau de certeza
    (nome do arquivo == nome do aluno) que ainda não possuem vínculo."""
    if not check_staff(request):
        return _redir_login()
    sem = _sem_aval(semestre)
    alunos = get_all_alunos()
    vinculos = dav.get_avaliacoes_map(semestre=sem)
    sugestoes = dav.sugerir_vinculos(alunos)
    user = get_session_user(request) or {}
    n = 0
    for mat, arq in sugestoes.items():
        if mat not in vinculos:
            dav.set_avaliacao(mat, arq, arq, user.get("nome", ""), semestre=sem)
            n += 1
    if n:
        _auditar(request, "Vínculo automático de avaliações", detalhe=f"{sem}º sem · {n} aluno(s)")
        return _redir_avaliacoes(msg=f"{n} avaliação(ões) vinculada(s) automaticamente.", semestre=sem)
    return _redir_avaliacoes(msg="Nenhuma sugestão nova para vincular.", semestre=sem)


@app.post("/admin/avaliacoes/upload")
async def admin_avaliacoes_upload(
    request: Request, matricula: str = Form(...), pdf: UploadFile = File(...),
    semestre: str = Form("1"),
):
    if not check_staff(request):
        return _redir_login()
    sem = _sem_aval(semestre)
    if not get_aluno(matricula):
        return _redir_avaliacoes(erro="Aluno não encontrado.", semestre=sem)

    nome = pdf.filename or ""
    if not nome.lower().endswith(".pdf"):
        return _redir_avaliacoes(erro="Envie um arquivo no formato PDF.", semestre=sem)
    conteudo = await pdf.read()
    if not conteudo:
        return _redir_avaliacoes(erro="O arquivo está vazio ou corrompido.", semestre=sem)
    if len(conteudo) > dav.MAX_UPLOAD_BYTES:
        return _redir_avaliacoes(erro="Arquivo muito grande (máximo 15 MB).", semestre=sem)
    if not conteudo[:5].startswith(b"%PDF-"):
        return _redir_avaliacoes(erro="Arquivo inválido: não é um PDF válido.", semestre=sem)

    try:
        arquivo = dav.salvar_upload(dav.DISCIPLINA_PADRAO, conteudo, nome)
    except OSError:
        return _redir_avaliacoes(erro="Falha ao salvar o arquivo. Tente novamente.", semestre=sem)
    user = get_session_user(request) or {}
    dav.set_avaliacao(matricula, arquivo, nome, user.get("nome", ""), semestre=sem)
    _auditar(request, "Upload de avaliação de inglês", alvo=matricula, detalhe=f"{sem}º sem · {arquivo}")
    return _redir_avaliacoes(msg="PDF enviado e vinculado com sucesso.", semestre=sem)


@app.post("/admin/avaliacoes/remover")
async def admin_avaliacoes_remover(request: Request, matricula: str = Form(...),
                                   semestre: str = Form("1")):
    if not check_staff(request):
        return _redir_login()
    sem = _sem_aval(semestre)
    dav.remover_avaliacao(matricula, semestre=sem)
    _auditar(request, "Remover vínculo de avaliação", alvo=matricula, detalhe=f"{sem}º sem")
    return _redir_avaliacoes(msg="Vínculo removido. (O arquivo PDF foi mantido na pasta.)", semestre=sem)


@app.get("/admin/avaliacao/{matricula}/{semestre}/ver")
async def admin_ver_avaliacao(request: Request, matricula: str, semestre: int):
    """Visualização da avaliação pelo admin/coordenação (qualquer aluno)."""
    if not check_staff(request):
        return _redir_login()
    return _entregar_avaliacao_pdf(matricula, _sem_aval(semestre))


@app.get("/avaliacao-ingles/{matricula}")
async def ver_avaliacao_responsavel_compat(request: Request, matricula: str):
    """Compatibilidade: link antigo sem semestre -> 1º semestre."""
    return await ver_avaliacao_responsavel(request, matricula, 1)


@app.get("/avaliacao-ingles/{matricula}/{semestre}")
async def ver_avaliacao_responsavel(request: Request, matricula: str, semestre: int):
    """Visualização pelo responsável — apenas a avaliação do próprio filho,
    identificado pela matrícula. Respeita o controle de visibilidade dos pais."""
    if _pais_bloqueado(request):
        return HTMLResponse(MANUTENCAO_HTML)
    mat_clean = re.sub(r'\D', '', matricula)
    bloq = _consulta_bloqueada_resp(request, mat_clean)
    if bloq:
        return bloq
    sem = _sem_aval(semestre)
    aluno = get_aluno(mat_clean) if mat_clean else None
    if aluno and dav.get_avaliacao(mat_clean, semestre=sem):
        _registrar_acesso_pai(request, aluno, mat_clean, "avaliacao_ingles")
    return _entregar_avaliacao_pdf(matricula, sem)


def _entregar_avaliacao_pdf(matricula: str, semestre: int = 1):
    """Resolve e entrega o PDF vinculado ao aluno, aberto no navegador (inline).
    Retorna 404 amigável quando não há vínculo ou o arquivo sumiu do disco."""
    mat_clean = re.sub(r'\D', '', matricula)
    aval = dav.get_avaliacao(mat_clean, semestre=semestre) if mat_clean else None
    if not aval:
        return HTMLResponse(_PDF_NAO_ENCONTRADO, status_code=404)
    caminho = dav.resolver_caminho(aval.get("disciplina", dav.DISCIPLINA_PADRAO), aval["arquivo"])
    if not caminho:
        return HTMLResponse(_PDF_NAO_ENCONTRADO, status_code=404)
    aluno = get_aluno(mat_clean) or {}
    # Nome ASCII-safe: o header Content-Disposition não aceita acentos/UTF-8.
    nome_ascii = unicodedata.normalize("NFKD", aluno.get("nome", "avaliacao")).encode("ascii", "ignore").decode()
    nome_aluno = re.sub(r'[^A-Za-z0-9\- ]', '', nome_ascii).strip() or "avaliacao"
    download_nome = f"Avaliacao de Ingles {semestre}o sem - {nome_aluno}.pdf"
    return FileResponse(
        caminho, media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{download_nome}"'},
    )


_PDF_NAO_ENCONTRADO = """<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Avaliação indisponível</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
<style>body{font-family:'Nunito',system-ui,sans-serif;background:linear-gradient(160deg,#1a2570,#1a5fa8);
min-height:100vh;display:flex;align-items:center;justify-content:center;margin:0;padding:24px;}
.c{background:#fff;border-radius:22px;padding:38px 34px;max-width:420px;text-align:center;
box-shadow:0 20px 60px rgba(10,15,50,.35);}h1{font-size:20px;color:#1a2570;margin:10px 0;}
p{font-size:14px;color:#555;line-height:1.6;}a{display:inline-block;margin-top:22px;text-decoration:none;
background:#2b3990;color:#fff;font-weight:800;padding:12px 26px;border-radius:999px;font-size:14px;}</style>
</head><body><div class="c"><div style="font-size:44px;">📄</div>
<h1>Avaliação indisponível</h1>
<p>A avaliação solicitada ainda não está disponível ou foi removida. Caso o problema continue, fale com a coordenação da escola.</p>
<a href="/">Voltar ao início</a></div></body></html>"""


# ════════════════════════════════════════════════════════════════════════════
#  CONTROLE DE ACESSOS DOS RESPONSÁVEIS — admin/coordenação
# ════════════════════════════════════════════════════════════════════════════

@app.get("/admin/auditoria", response_class=HTMLResponse)
async def admin_auditoria(request: Request):
    if not check_admin(request):
        return _redir_login()
    return admin_auditoria_page(daud.listar(500))


@app.get("/admin/acessos", response_class=HTMLResponse)
async def admin_acessos(request: Request):
    if not check_staff(request):
        return _redir_login()
    alunos = get_all_alunos()
    rows = dac.listar_acessos()
    agg = dac.agregar_por_aluno_documento(rows)
    return admin_acessos_page(
        alunos, list(agg.values()), total_acessos=len(rows),
        staff_only=not check_admin(request),
    )


def _get_or_create_relatorio(matricula: str, semestre: int) -> dict | None:
    """Retorna o relatório do aluno/semestre, criando-o (sem respostas) se ainda
    não existir — necessário para o admin poder trancar antes da professora abrir."""
    aluno = get_aluno(matricula)
    if not aluno:
        return None
    nome_prof = aluno.get("professora", "").strip()
    professora = next(
        (u for u in get_all_usuarios() if u.get("nome", "").strip() == nome_prof),
        None,
    )
    professora_id = professora["id"] if professora else None
    ano = aluno.get("ano_letivo", "2026")
    return upsert_relatorio(matricula, semestre, professora_id, ano)


@app.get("/admin/relatorio/aluno/{matricula}/{semestre}")
async def admin_abrir_relatorio(request: Request, matricula: str, semestre: int):
    """Abre (criando se necessário) o relatório de um aluno/semestre — usado quando
    a professora ainda não preencheu nada e o relatório não existe no banco."""
    if not check_staff(request):
        return _redir_login()
    relatorio = _get_or_create_relatorio(matricula, semestre)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)
    return RedirectResponse(f"/admin/relatorio/{relatorio['id']}", status_code=302)


@app.post("/admin/relatorio/aluno/{matricula}/{semestre}/trancar")
async def admin_trancar_por_aluno(
    request: Request, matricula: str, semestre: int,
    turma: str = Form(""), semestre_filtro: str = Form(""), status: str = Form(""),
):
    if not check_staff(request):
        return _redir_login()
    relatorio = _get_or_create_relatorio(matricula, semestre)
    if relatorio:
        set_relatorio_trancado(relatorio["id"], True)
    qs = f"turma={quote(turma)}&semestre={quote(semestre_filtro)}&status={quote(status)}"
    return RedirectResponse(f"/admin/relatorios?{qs}", status_code=302)


@app.post("/admin/relatorio/aluno/{matricula}/{semestre}/destrancar")
async def admin_destrancar_por_aluno(
    request: Request, matricula: str, semestre: int,
    turma: str = Form(""), semestre_filtro: str = Form(""), status: str = Form(""),
):
    if not check_staff(request):
        return _redir_login()
    relatorio = _get_or_create_relatorio(matricula, semestre)
    if relatorio:
        set_relatorio_trancado(relatorio["id"], False)
    qs = f"turma={quote(turma)}&semestre={quote(semestre_filtro)}&status={quote(status)}"
    return RedirectResponse(f"/admin/relatorios?{qs}", status_code=302)


@app.post("/admin/relatorios/trancar-semestre")
async def admin_trancar_semestre_inteiro(
    request: Request,
    semestre: int = Form(...),
    acao: str = Form(...),       # "trancar" ou "destrancar"
    turma: str = Form(""),
    status: str = Form(""),
):
    """Tranca/destranca de uma vez todos os relatórios de um semestre
    (de Ed. Infantil), criando os que ainda não existem. Respeita o
    filtro de turma atual, se houver."""
    if not check_staff(request):
        return _redir_login()
    if semestre not in (1, 2):
        return RedirectResponse("/admin/relatorios", status_code=302)

    trancar = (acao == "trancar")
    afetados = 0
    for mat, al in get_all_alunos().items():
        t = al.get("turma", "")
        if not is_infantil(t):
            continue
        if turma and t != turma:
            continue
        relatorio = _get_or_create_relatorio(mat, semestre)
        if relatorio:
            set_relatorio_trancado(relatorio["id"], trancar)
            afetados += 1

    verbo = "trancados" if trancar else "destrancados"
    msg = quote(f"{afetados} relatórios do {semestre}º semestre foram {verbo}")
    qs = f"turma={quote(turma)}&semestre={quote(str(semestre))}&status={quote(status)}&ok={msg}"
    return RedirectResponse(f"/admin/relatorios?{qs}", status_code=302)


@app.get("/admin/relatorio/{rel_id}", response_class=HTMLResponse)
async def admin_ver_relatorio(request: Request, rel_id: int, msg: str = "", erro: str = ""):
    if not check_staff(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    aluno = get_aluno(relatorio["matricula"])
    if not aluno:
        return RedirectResponse("/admin/relatorios", status_code=302)

    temas    = get_temas_para_turma(aluno.get("turma", ""))
    respostas = get_respostas(rel_id)
    user_admin = get_session_user(request)
    prefix   = f"/admin/relatorio/{rel_id}"

    return relatorio_form_page(
        user_admin, aluno, relatorio["matricula"], relatorio["semestre"],
        relatorio, temas, respostas, msg=msg, erro=erro, form_prefix=prefix,
    )


@app.post("/admin/relatorio/{rel_id}/salvar")
async def admin_salvar_relatorio(request: Request, rel_id: int):
    if not check_staff(request):
        return _redir_login()
    user_staff = get_session_user(request)

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    form      = dict(await request.form())
    respostas = _parse_respostas(form)
    descricao = sanitizar_html(form.get("descricao_final", "").strip())
    novo_status = "em_andamento" if relatorio["status"] == "pendente" else relatorio["status"]

    save_respostas(rel_id, respostas)
    update_relatorio(rel_id, novo_status, descricao, editado_por=user_staff["nome"])

    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Alterações+salvas+com+sucesso", status_code=302)


@app.post("/admin/relatorio/{rel_id}/confirmar")
async def admin_confirmar_relatorio(request: Request, rel_id: int):
    if not check_staff(request):
        return _redir_login()
    user_staff = get_session_user(request)

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    form      = dict(await request.form())
    respostas = _parse_respostas(form)
    descricao = sanitizar_html(form.get("descricao_final", "").strip())

    aluno_rel = get_aluno(relatorio["matricula"])
    turma_rel = aluno_rel.get("turma", "") if aluno_rel else ""
    temas    = get_temas_para_turma(turma_rel)
    todos_ids = [st["id"] for t in temas for st in t.get("subtemas", [])]
    faltando  = [sid for sid in todos_ids if sid not in respostas]

    if faltando:
        save_respostas(rel_id, respostas)
        update_relatorio(rel_id, "em_andamento", descricao, editado_por=user_staff["nome"])
        return RedirectResponse(
            f"/admin/relatorio/{rel_id}?erro=Preencha+todos+os+subtemas+antes+de+confirmar",
            status_code=302,
        )

    save_respostas(rel_id, respostas)
    update_relatorio(rel_id, "concluido", descricao, editado_por=user_staff["nome"])
    _auditar(request, "Confirmar relatório", alvo=relatorio.get("matricula", str(rel_id)))
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+confirmado+com+sucesso", status_code=302)


@app.post("/admin/relatorio/{rel_id}/trancar")
async def admin_trancar_relatorio(request: Request, rel_id: int):
    if not check_staff(request):
        return _redir_login()
    set_relatorio_trancado(rel_id, True)
    _auditar(request, "Trancar relatório", alvo=str(rel_id))
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+trancado", status_code=302)


@app.post("/admin/relatorio/{rel_id}/destrancar")
async def admin_destrancar_relatorio(request: Request, rel_id: int):
    if not check_staff(request):
        return _redir_login()
    set_relatorio_trancado(rel_id, False)
    _auditar(request, "Destrancar relatório", alvo=str(rel_id))
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+destrancado", status_code=302)


@app.post("/admin/relatorio/{rel_id}/reabrir")
async def admin_reabrir_relatorio(request: Request, rel_id: int):
    """Reabre um relatório já concluído, devolvendo o acesso de edição à professora."""
    if not check_staff(request):
        return _redir_login()
    reabrir_relatorio(rel_id)
    _auditar(request, "Reabrir relatório", alvo=str(rel_id))
    return RedirectResponse(f"/admin/relatorio/{rel_id}?msg=Relatório+reaberto+para+a+professora+preencher+novamente", status_code=302)


@app.get("/admin/relatorio/{rel_id}/imprimir", response_class=HTMLResponse)
async def admin_imprimir_relatorio(request: Request, rel_id: int):
    if not check_staff(request):
        return _redir_login()

    relatorio = get_relatorio_by_id(rel_id)
    if not relatorio:
        return RedirectResponse("/admin/relatorios", status_code=302)

    aluno    = get_aluno(relatorio["matricula"])
    temas    = get_temas_para_turma(aluno.get("turma", "") if aluno else "")
    respostas = get_respostas(rel_id)

    return HTMLResponse(gerar_relatorio_print_html(
        aluno, relatorio["matricula"], relatorio["semestre"],
        relatorio, temas, respostas,
    ))


@app.get("/admin/relatorios/imprimir", response_class=HTMLResponse)
async def admin_imprimir_relatorios_lote(request: Request, semestre: int, turma: str = ""):
    """Impressão em lote de todos os relatórios de um semestre (Ed. Infantil),
    opcionalmente filtrados por turma."""
    if not check_staff(request):
        return _redir_login()
    if semestre not in (1, 2):
        return RedirectResponse("/admin/relatorios", status_code=302)

    itens = []
    for mat, al in sorted(get_all_alunos().items(), key=lambda x: (x[1].get("turma", ""), x[1].get("nome", ""))):
        t = al.get("turma", "")
        if not is_infantil(t):
            continue
        if turma and t != turma:
            continue
        relatorio = get_relatorio(mat, semestre, al.get("ano_letivo", "2026"))
        if not relatorio:
            continue
        temas = get_temas_para_turma(t)
        respostas = get_respostas(relatorio["id"])
        itens.append((al, mat, relatorio, temas, respostas))

    return HTMLResponse(gerar_relatorios_print_html_multiplos(itens, semestre))

