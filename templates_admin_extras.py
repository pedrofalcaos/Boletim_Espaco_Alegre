"""Páginas extras do painel admin: professoras e temas avaliativos."""
from urllib.parse import quote
from datetime import date
from templates import page_shell, admin_nav
from design_system import avatar_iniciais, avatar

# O pop-up de festas (São João / férias) some sozinho após esta data.
FESTAS_ATE = date(2026, 7, 31)
from icons import (ICON_EDIT, ICON_CLIPBOARD, ICON_PRINTER, ICON_LOCK, ICON_UNLOCK,
                    ICON_REFRESH, ICON_KEY, ICON_PLUS, ICON_TRASH, dot)

# Todas as turmas disponíveis (para seleção na criação/edição da professora)
_TODAS_TURMAS = [
    "Infantil 1 – A", "Infantil 1 – B",
    "Infantil 2 – A", "Infantil 2 – B",
    "Infantil 3 – A", "Infantil 3 – B",
    "Infantil 4 – A", "Infantil 4 – B",
    "Infantil 5 – A",
    "1º Ano A", "1º Ano B", "2º Ano A", "2º Ano B",
    "3º Ano A", "3º Ano B", "4º Ano A", "4º Ano B",
    "5º Ano A", "5º Ano B",
]

_ST_COR = {"pendente":"#b52222","em_andamento":"#c25b0d","concluido":"#0a7c3e"}
_ST_BG  = {"pendente":"#fef2f2","em_andamento":"#fef0e4","concluido":"#e3f5ec"}
_ST_BD  = {"pendente":"#fecaca","em_andamento":"#f8d4a8","concluido":"#a8ddc0"}
_ST_LAB = {"pendente":"Não preenchido","em_andamento":"Em preenchimento","concluido":"Preenchido"}


# ── Utilitários ───────────────────────────────────────────────────────────────
def _msg_ok(texto: str) -> str:
    return f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:13px;color:#0a7c3e;font-weight:700;">✔ {texto}</div>'

def _msg_erro(texto: str) -> str:
    return f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:13px;color:#b52222;font-weight:700;">✖ {texto}</div>'

def _card(conteudo: str) -> str:
    return f'<div class="gcard">{conteudo}</div>'

def _secao(titulo: str) -> str:
    return f'<div style="font-family:\'Fredoka One\',cursive;font-size:16px;color:#2b3990;margin-bottom:16px;border-bottom:2px solid #f7d800;padding-bottom:6px;">{titulo}</div>'

_INP = ("width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;"
        "color:#2b3990;padding:9px 13px;border:1.5px solid #c8c8c4;border-radius:9px;outline:none;")
_BTN_AZ = ("font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;"
            "background:#2b3990;color:#fff;border:none;border-radius:9px;padding:9px 22px;cursor:pointer;")
_BTN_VM = ("font-family:'Nunito',sans-serif;font-size:11px;font-weight:800;"
            "background:#fef2f2;color:#b52222;border:1px solid #fecaca;border-radius:7px;padding:4px 12px;cursor:pointer;")
_BTN_CINZA = ("font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;"
               "background:#f7f7f5;color:#888;border:1px solid #dcdcd8;border-radius:9px;padding:9px 20px;cursor:pointer;display:inline-block;text-decoration:none;")


# ════════════════════════════════════════════════════════════════════════
#  PROFESSORAS
# ════════════════════════════════════════════════════════════════════════

def admin_professoras_page(professoras: list, alunos_por_prof: dict, msg: str = "", erro: str = "",
                            senha_gerada: str = "", coordenadoras: list | None = None) -> str:
    """
    professoras: lista de dicts do db (id, username, nome, role, ativo, senha_temporaria)
    alunos_por_prof: {professora_nome: [lista de turmas]}
    coordenadoras: lista de dicts do db com role == "coordenacao"
    """
    coordenadoras = coordenadoras or []
    nav = admin_nav("professoras")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

    senha_box = ""
    if senha_gerada:
        senha_box = f"""
<div style="background:#fffbe6;border:2px solid #f7d800;border-radius:10px;padding:14px 18px;margin-bottom:20px;">
  <div style="font-size:11px;font-weight:800;color:#a67c00;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">
    {ICON_KEY}Nova senha temporária gerada
  </div>
  <div style="font-family:monospace;font-size:20px;font-weight:900;color:#2b3990;background:#fff;
              border:1px dashed #ccc;border-radius:7px;padding:8px 16px;display:inline-block;letter-spacing:2px;">
    {senha_gerada}
  </div>
  <div style="font-size:11px;color:#888;margin-top:8px;">
    Repasse esta senha à professora — ela não será exibida novamente. No próximo acesso,
    será solicitado que ela cadastre uma nova senha pessoal.
  </div>
</div>"""

    def _turmas_chips(turmas_conf, turmas_alunos):
        """Mostra turmas configuradas (azul escuro) e as do aluno mas não configuradas (cinza)."""
        conf_set = set(turmas_conf or [])
        todas = sorted(set(list(conf_set) + list(turmas_alunos or [])))
        if not todas:
            return '<span style="color:#ccc;font-size:12px;">nenhuma turma vinculada</span>'
        return " ".join(
            f'<span style="background:{"#2b3990" if t in conf_set else "#e8eaf8"};'
            f'color:{"#fff" if t in conf_set else "#2b3990"};font-size:10px;font-weight:800;'
            f'padding:2px 9px;border-radius:20px;">{t}</span>'
            for t in todas
        )

    def _turma_checkboxes(conf, prefix_id):
        html = '<div style="display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;">'
        for t in _TODAS_TURMAS:
            chk = "checked" if t in (conf or []) else ""
            html += (f'<label style="display:flex;align-items:center;gap:4px;font-size:11px;'
                     f'font-weight:700;color:#555;cursor:pointer;background:#f7f7f5;'
                     f'border:1.5px solid #ddd;border-radius:7px;padding:3px 9px;">'
                     f'<input type="checkbox" name="turma" value="{t}" {chk}> {t}</label>')
        html += '</div>'
        return html

    def _foto_box(uid, foto_url):
        remover = (f'<form method="POST" action="/admin/usuario/{uid}/foto/remover" style="display:inline;" '
                   f'onsubmit="return confirm(\'Remover a foto?\');">'
                   f'<button type="submit" style="{_BTN_VM}">Remover foto</button></form>') if foto_url else ""
        return f"""
  <div id="foto-form-{uid}" style="display:none;margin-top:11px;border-top:1px solid #f0f0ee;padding-top:11px;">
    <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
      <label style="{_BTN_AZ}padding:7px 16px;font-size:12px;cursor:pointer;display:inline-block;">
        📷 Escolher foto
        <input type="file" accept="image/jpeg,image/png,image/webp" data-action="/admin/usuario/{uid}/foto" onchange="abrirCropper(this)" style="display:none;">
      </label>
      {remover}
    </div>
    <div style="font-size:10px;color:#aaa;margin-top:5px;">JPG, PNG ou WEBP · até 8 MB · recortada em quadrado automaticamente.</div>
  </div>"""

    if professoras:
        cards = ""
        for p in professoras:
            pid = p["id"]
            conf_turmas = p.get("turmas") or []
            aluno_turmas = alunos_por_prof.get(p["nome"], [])
            chips = _turmas_chips(conf_turmas, aluno_turmas)
            checkboxes = _turma_checkboxes(conf_turmas, pid)

            pendente_badge = ""
            if p.get("senha_temporaria"):
                pendente_badge = ('<span style="background:#fef0e4;color:#c25b0d;font-size:10px;font-weight:800;'
                                   'padding:2px 9px;border-radius:20px;margin-left:8px;white-space:nowrap;">'
                                   '⏳ Aguardando troca de senha</span>')

            cards += f"""
<div style="background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
    {avatar(p["nome"], p.get("foto_url"), size=44)}
    <div style="flex:1;">
      <div style="font-weight:800;color:#2b3990;font-size:14px;">{p["nome"]}{pendente_badge}</div>
      <div style="font-size:11px;color:#aaa;margin-top:2px;">{p["username"]}</div>
    </div>
    <button type="button" onclick="toggleFoto({pid})" style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">📷 Foto</button>
    <button type="button" onclick="toggleTurmas({pid})"
      style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">
      {ICON_EDIT}Editar turmas
    </button>
    <form method="POST" action="/admin/professoras/{pid}/resetar-senha"
          onsubmit="return confirm('Gerar uma nova senha temporária para {p["nome"]}?\\n\\nA senha atual deixará de funcionar e ela precisará trocá-la no próximo acesso.');">
      <button type="submit" style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">{ICON_KEY}Resetar senha</button>
    </form>
    <form method="POST" action="/admin/professoras/{pid}/excluir"
          onsubmit="return confirm('Excluir {p["nome"]}? Os alunos não são apagados.');">
      <button type="submit" style="{_BTN_VM}">{ICON_TRASH}</button>
    </form>
  </div>
  <div style="margin-top:10px;">{chips}</div>
  {_foto_box(pid, p.get("foto_url"))}
  <div id="turmas-form-{pid}" style="display:none;margin-top:12px;border-top:1px solid #f0f0ee;padding-top:12px;">
    <form method="POST" action="/admin/professoras/{pid}/turmas">
      <div style="font-size:11px;font-weight:800;color:#aaa;margin-bottom:4px;text-transform:uppercase;letter-spacing:.5px;">
        Selecione as turmas desta professora:
      </div>
      {checkboxes}
      <button type="submit" style="{_BTN_AZ}padding:7px 18px;font-size:12px;margin-top:10px;">
        Salvar turmas
      </button>
    </form>
  </div>
</div>"""
        tabela = cards
    else:
        tabela = '<p style="color:#aaa;font-size:13px;text-align:center;padding:20px 0;">Nenhuma professora cadastrada ainda.</p>'

    lista_card = _card(_secao("👩‍🏫 Professoras cadastradas") + tabela)

    # ── Corrigir nome de professora (propaga p/ alunos e relatórios) ──
    nomes_distintos = sorted({n for n in alunos_por_prof.keys() if n})
    opts_nomes = "".join(f'<option value="{n}">{n}</option>' for n in nomes_distintos)
    renomear_card = _card(f"""
{_secao(f"{ICON_EDIT}Corrigir nome de professora")}
<p style="font-size:12px;color:#888;margin-bottom:14px;">
  Escreveu o nome errado? Corrija aqui e a mudança vai automaticamente para
  <strong>todos os alunos vinculados</strong> e seus <strong>boletins e relatórios</strong>
  (e também para a conta de login, se existir uma com esse nome).
</p>
<form method="POST" action="/admin/professoras/renomear"
      onsubmit="return confirm('Corrigir o nome em todos os alunos vinculados?');">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px;">
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome atual (como está hoje)</label>
      <select name="antigo" required style="{_INP}background:#fff;">
        <option value="">— selecione —</option>
        {opts_nomes}
      </select>
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome corrigido</label>
      <input name="novo" required placeholder="Ex: Vanessa Silva" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
  </div>
  <button type="submit" style="{_BTN_AZ}">Corrigir nome →</button>
</form>""")

    # Seleção de turmas para nova professora
    nova_checkboxes = _turma_checkboxes([], "nova")

    nova_card = _card(f"""
{_secao(f"{ICON_PLUS}Nova Professora")}
<form method="POST" action="/admin/professoras/nova">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:16px;">
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome completo</label>
      <input name="nome" required placeholder="Ex: Vanessa" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Usuário de login</label>
      <input name="username" required placeholder="Ex: vanessa@escola.com" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Senha inicial</label>
      <input name="senha" type="password" required placeholder="Mínimo 6 caracteres" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
  </div>
  <div style="margin-bottom:12px;">
    <div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;margin-bottom:4px;">
      Turmas sob responsabilidade:
    </div>
    {nova_checkboxes}
  </div>
  <div style="font-size:11px;color:#aaa;margin-bottom:14px;">
    💡 O nome deve ser idêntico ao campo <strong>Professor(a)</strong> nos alunos para que o vínculo funcione.
  </div>
  <button type="submit" style="{_BTN_AZ}">Cadastrar professora →</button>
</form>""")

    # ── Coordenadoras ──
    if coordenadoras:
        coord_cards = ""
        for c in coordenadoras:
            cid = c["id"]
            pendente_badge = ""
            if c.get("senha_temporaria"):
                pendente_badge = ('<span style="background:#fef0e4;color:#c25b0d;font-size:10px;font-weight:800;'
                                   'padding:2px 9px;border-radius:20px;margin-left:8px;white-space:nowrap;">'
                                   '⏳ Aguardando troca de senha</span>')
            coord_cards += f"""
<div style="background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
    {avatar(c["nome"], c.get("foto_url"), size=44)}
    <div style="flex:1;">
      <div style="font-weight:800;color:#2b3990;font-size:14px;">{c["nome"]}{pendente_badge}</div>
      <div style="font-size:11px;color:#aaa;margin-top:2px;">{c["username"]} · coordenação</div>
    </div>
    <button type="button" onclick="toggleFoto({cid})" style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">📷 Foto</button>
    <form method="POST" action="/admin/professoras/{cid}/resetar-senha"
          onsubmit="return confirm('Gerar uma nova senha temporária para {c["nome"]}?\\n\\nA senha atual deixará de funcionar e ela precisará trocá-la no próximo acesso.');">
      <button type="submit" style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">{ICON_KEY}Resetar senha</button>
    </form>
    <form method="POST" action="/admin/professoras/{cid}/excluir"
          onsubmit="return confirm('Excluir {c["nome"]}?');">
      <button type="submit" style="{_BTN_VM}">{ICON_TRASH}</button>
    </form>
  </div>
  {_foto_box(cid, c.get("foto_url"))}
</div>"""
        coord_lista = coord_cards
    else:
        coord_lista = '<p style="color:#aaa;font-size:13px;text-align:center;padding:20px 0;">Nenhuma coordenadora cadastrada ainda.</p>'

    coord_lista_card = _card(_secao("🧑‍💼 Coordenação cadastrada") + coord_lista)

    coord_nova_card = _card(f"""
{_secao(f"{ICON_PLUS}Nova Coordenadora")}
<form method="POST" action="/admin/coordenacao/nova">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:16px;">
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome completo</label>
      <input name="nome" required placeholder="Ex: Cristiane Dantas" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Usuário de login</label>
      <input name="username" required placeholder="Ex: cristiane.dantas" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Senha inicial</label>
      <input name="senha" type="password" required placeholder="Mínimo 6 caracteres" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
  </div>
  <div style="font-size:11px;color:#aaa;margin-bottom:14px;">
    💡 Coordenadoras podem visualizar, editar e imprimir relatórios de qualquer turma, mas não gerenciam alunos, professoras ou a estrutura avaliativa.
  </div>
  <button type="submit" style="{_BTN_AZ}">Cadastrar coordenadora →</button>
</form>""")

    js_toggle = """
<script>
function toggleTurmas(id) {
  var el = document.getElementById('turmas-form-' + id);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
function toggleFoto(id) {
  var el = document.getElementById('foto-form-' + id);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
</script>"""

    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Colaboradoras</h1>
      <p style="font-size:12px;color:#888;">{len(professoras)} professora(s) · {len(coordenadoras)} coordenadora(s) cadastrada(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {senha_box}
  {lista_card}
  {renomear_card}
  {nova_card}
  {coord_lista_card}
  {coord_nova_card}
  {js_toggle}
</div>"""
    return page_shell("Colaboradoras — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  TEMAS AVALIATIVOS  (com matrix turma × subtema)
# ════════════════════════════════════════════════════════════════════════

# Rótulos curtos para as colunas da matrix
_TURMAS_INF = [
    ("Infantil 1 – A", "1A"), ("Infantil 1 – B", "1B"),
    ("Infantil 2 – A", "2A"), ("Infantil 2 – B", "2B"),
    ("Infantil 3 – A", "3A"), ("Infantil 3 – B", "3B"),
    ("Infantil 4 – A", "4A"), ("Infantil 4 – B", "4B"),
    ("Infantil 5 – A", "5A"),
]


def _turma_checkboxes(todas_turmas, turmas_selecionadas, turmas_permitidas=None, prefixo="turma") -> str:
    """Renderiza checkboxes de turmas em grade. turmas_permitidas=None significa todas liberadas."""
    html = '<div style="display:flex;flex-wrap:wrap;gap:6px 10px;margin:10px 0;">'
    for nome, label in _TURMAS_INF:
        checked   = "checked" if nome in turmas_selecionadas else ""
        disabled  = ""
        estilo_cb = "cursor:pointer;"
        estilo_lb = "font-size:12px;font-weight:700;cursor:pointer;"
        if turmas_permitidas is not None and nome not in turmas_permitidas:
            disabled  = "disabled"
            estilo_cb = "cursor:not-allowed;opacity:.35;"
            estilo_lb = "font-size:12px;font-weight:700;color:#bbb;cursor:not-allowed;"
        uid = f"{prefixo}_{nome.replace(' ','_').replace('–','_')}"
        html += (f'<label for="{uid}" style="display:flex;align-items:center;gap:4px;{estilo_lb}">'
                 f'<input type="checkbox" id="{uid}" name="turma" value="{nome}" {checked} {disabled}'
                 f' style="{estilo_cb}">'
                 f'{label}</label>')
    html += '</div>'
    return html


def admin_temas_page(topicos: list, msg: str = "", erro: str = "") -> str:
    nav   = admin_nav("temas")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")
    total_temas    = sum(len(tp.get("temas", [])) for tp in topicos)
    total_subtemas = sum(len(t.get("subtemas", [])) for tp in topicos for t in tp.get("temas", []))

    def _render_tema(tema: dict, tp_turmas_permitidas: list) -> str:
        """Card de Tema: seleção de turmas (restrita ao tópico) + lista de subtemas."""
        subtemas   = tema.get("subtemas", [])
        tid        = tema["id"]
        t_turmas   = tema.get("turmas") or []

        # checkboxes de turmas (somente as que o tópico permite)
        turmas_sel = t_turmas if t_turmas else [n for n, _ in _TURMAS_INF]
        cbs_turmas = _turma_checkboxes(
            _TURMAS_INF, turmas_sel,
            turmas_permitidas=tp_turmas_permitidas if tp_turmas_permitidas else None,
            prefixo=f"tema_{tid}"
        )

        form_nome_turmas = f"""
<div style="display:flex;gap:8px;margin-bottom:10px;align-items:center;">
  <form method="POST" action="/admin/temas/{tid}/editar"
        style="display:flex;gap:8px;flex:1;">
    <input name="nome" value="{tema['nome']}" required
           style="{_INP}flex:1;font-size:13px;font-weight:800;color:#2b3990;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:7px 12px;font-size:11px;">Salvar nome</button>
  </form>
  <form method="POST" action="/admin/temas/{tid}/excluir"
        onsubmit="return confirm('Excluir este tema e todos os subtemas?');">
    <button type="submit" style="{_BTN_VM}">{ICON_TRASH}Excluir</button>
  </form>
</div>
<form method="POST" action="/admin/temas/{tid}/turmas">
  <div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
              color:#aaa;margin-bottom:4px;">Turmas que avaliam este tema</div>
  {cbs_turmas}
  <button type="submit" style="{_BTN_AZ}padding:6px 16px;font-size:11px;margin-top:4px;">
    💾 Salvar turmas do tema
  </button>
  <span style="font-size:10px;color:#aaa;margin-left:8px;">
    Apenas turmas habilitadas pelo tópico podem ser selecionadas
  </span>
</form>"""

        # Lista de subtemas
        if subtemas:
            lista_st = ""
            for i, st in enumerate(subtemas, 1):
                sid = st["id"]
                desc_attr = st["descricao"].replace('"', "&quot;")
                lista_st += f"""
<div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:.5px solid #f0f0ee;">
  <span style="font-size:12px;color:#aaa;white-space:nowrap;">{i}.</span>
  <form method="POST" action="/admin/subtemas/{sid}/editar" style="display:flex;gap:6px;flex:1;">
    <input name="descricao" value="{desc_attr}" required
           style="{_INP}flex:1;font-size:12px;padding:6px 10px;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:6px 12px;font-size:11px;">💾 Salvar</button>
  </form>
  <form id="del-st-{sid}" method="POST" action="/admin/subtemas/{sid}/excluir" style="display:none;"></form>
  <button type="button"
    onclick="if(confirm('Excluir subtema?'))document.getElementById('del-st-{sid}').submit()"
    style="{_BTN_VM}">✕ Excluir</button>
</div>"""
            subtemas_html = f'<div style="margin:12px 0 4px;">{lista_st}</div>'
        else:
            subtemas_html = '<p style="color:#ccc;font-size:12px;margin:10px 0 4px;">Nenhum subtema ainda.</p>'

        form_novo_st = f"""
<div style="margin-top:10px;padding-top:10px;border-top:.5px dashed #e8e8e4;">
  <form method="POST" action="/admin/temas/{tid}/subtema" style="display:flex;gap:8px;">
    <input name="descricao" required placeholder="Descrição do novo subtema..."
           style="{_INP}flex:1;font-size:12px;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:8px 14px;font-size:12px;">+ Subtema</button>
  </form>
</div>"""

        badge = (f'<span style="background:#e8eaf8;color:#2b3990;font-size:10px;font-weight:800;'
                 f'padding:2px 9px;border-radius:20px;">{len(subtemas)} subtema(s)</span>')

        turmas_badge = ""
        if t_turmas:
            labels = [lb for nm, lb in _TURMAS_INF if nm in t_turmas]
            turmas_badge = (f' <span style="background:#e3f5ec;color:#0a7c3e;font-size:10px;'
                            f'font-weight:800;padding:2px 9px;border-radius:20px;">'
                            f'{", ".join(labels)}</span>')

        return f"""
<div style="background:#f9f9f7;border:1px solid #e8e8e4;border-radius:10px;
            padding:14px 18px;margin-bottom:10px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:12px;
              border-bottom:1.5px solid #f0f0ee;padding-bottom:8px;">
    <span style="font-family:'Fredoka One',cursive;font-size:13px;color:#2b3990;flex:1;">
      🏷️ Tema {turmas_badge}
    </span>
    {badge}
  </div>
  {form_nome_turmas}
  {subtemas_html}
  {form_novo_st}
</div>"""

    # ── Renderiza cada Tópico ──
    topicos_html = ""
    for tp in topicos:
        tp_id   = tp.get("id")
        tp_nome = tp.get("nome", "Sem tópico")
        temas   = tp.get("temas", [])
        tp_turmas = tp.get("turmas") or []

        # Determina turmas permitidas para os temas deste tópico
        tp_turmas_permitidas = tp_turmas if tp_turmas else [n for n, _ in _TURMAS_INF]

        temas_html = "".join(_render_tema(t, tp_turmas_permitidas) for t in temas)

        if tp_id is not None:
            # Contagens para o aviso de exclusão
            n_temas    = len(temas)
            n_subtemas = sum(len(t.get("subtemas", [])) for t in temas)
            aviso_excluir = (
                f"⚠️ ATENÇÃO — Excluir o tópico \"{tp_nome}\"?\\n\\n"
                f"Esta ação irá remover permanentemente:\\n"
                f"  • {n_temas} tema(s)\\n"
                f"  • {n_subtemas} subtema(s)\\n\\n"
                f"Essa operação NÃO pode ser desfeita."
            )

            # Checkboxes de turmas do tópico (todas disponíveis)
            cbs_tp = _turma_checkboxes(
                _TURMAS_INF,
                tp_turmas if tp_turmas else [n for n, _ in _TURMAS_INF],
                prefixo=f"tp_{tp_id}"
            )
            header_controls = f"""
<div style="display:flex;gap:8px;margin-bottom:12px;align-items:center;">
  <form method="POST" action="/admin/topicos/{tp_id}/editar"
        style="display:flex;gap:8px;flex:1;">
    <input name="nome" value="{tp_nome}" required
           style="{_INP}flex:1;font-size:15px;font-weight:900;color:#2b3990;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:8px 14px;">Salvar nome</button>
  </form>
  <form method="POST" action="/admin/topicos/{tp_id}/excluir"
        onsubmit="return confirm('{aviso_excluir}');">
    <button type="submit" style="{_BTN_VM}">{ICON_TRASH}Excluir tópico</button>
  </form>
</div>
<div style="background:#f0f4ff;border-radius:9px;padding:12px 14px;margin-bottom:14px;">
  <div style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
              color:#2b3990;margin-bottom:4px;">📌 Turmas deste tópico</div>
  <p style="font-size:11px;color:#666;margin-bottom:6px;">
    Selecione as turmas que terão acesso a este tópico. Os temas herdam essas turmas.
  </p>
  <form method="POST" action="/admin/topicos/{tp_id}/turmas">
    {cbs_tp}
    <button type="submit" style="{_BTN_AZ}padding:6px 18px;font-size:12px;margin-top:6px;">
      💾 Salvar turmas do tópico
    </button>
  </form>
</div>"""
            novo_tema_neste = f"""
<div style="border-top:1.5px dashed #e0e0da;padding-top:14px;margin-top:8px;">
  <p style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;
             letter-spacing:.5px;margin-bottom:8px;">➕ Novo Tema neste Tópico</p>
  <form method="POST" action="/admin/temas/novo" style="display:flex;gap:8px;">
    <input type="hidden" name="topico_id" value="{tp_id}">
    <input name="nome" required placeholder="Nome do tema..."
           style="{_INP}flex:1;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:9px 16px;">Criar tema →</button>
  </form>
</div>"""
        else:
            header_controls = ""
            novo_tema_neste = ""

        # Badge de turmas do tópico
        if tp_turmas:
            labels_tp = [lb for nm, lb in _TURMAS_INF if nm in tp_turmas]
            turmas_tp_badge = (f'<span style="background:#e8eaf8;color:#2b3990;font-size:11px;'
                               f'font-weight:800;padding:3px 10px;border-radius:20px;">'
                               f'Turmas: {", ".join(labels_tp)}</span>')
        else:
            turmas_tp_badge = (f'<span style="background:#f7f7f5;color:#aaa;font-size:11px;'
                               f'font-weight:700;padding:3px 10px;border-radius:20px;">'
                               f'Todas as turmas</span>')

        badge_tp = (f'<span style="background:#2b3990;color:#f7d800;font-size:11px;font-weight:800;'
                    f'padding:3px 12px;border-radius:20px;">{len(temas)} tema(s)</span>')

        topicos_html += _card(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;
            border-bottom:3px solid #f7d800;padding-bottom:10px;flex-wrap:wrap;">
  <span style="font-family:'Fredoka One',cursive;font-size:18px;color:#2b3990;flex:1;">
    📂 {tp_nome}
  </span>
  {turmas_tp_badge}
  {badge_tp}
</div>
{header_controls}
{temas_html if temas_html else '<p style="color:#ccc;font-size:12px;padding:8px 0;">Nenhum tema. Use o formulário abaixo para criar.</p>'}
{novo_tema_neste}""")

    if not topicos_html:
        topicos_html = _card('<p style="color:#aaa;text-align:center;padding:20px 0;">Nenhum tópico cadastrado. Crie um tópico para começar.</p>')

    # ── Formulário de novo Tópico ──
    novo_topico_card = _card(f"""
{_secao("📂 Novo Tópico")}
<form method="POST" action="/admin/topicos/novo" style="display:flex;gap:10px;align-items:flex-end;">
  <div style="flex:1;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;
                  color:#aaa;display:block;margin-bottom:4px;">Nome do tópico</label>
    <input name="nome" required placeholder="Ex: Desenvolvimento Cognitivo" style="{_INP}"
      onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  </div>
  <button type="submit" style="{_BTN_AZ}">Criar tópico →</button>
</form>
<p style="font-size:11px;color:#aaa;margin-top:10px;">
  Após criar o tópico, selecione as turmas e adicione os temas.
</p>
<div style="border-top:1.5px dashed #e0e0da;padding-top:14px;margin-top:14px;display:flex;flex-direction:column;gap:10px;">
  <form method="POST" action="/admin/seed-estrutura-avaliativa"
        onsubmit="return confirm('Importar a estrutura avaliativa padrão da Ed. Infantil (5 tópicos, tema Habilidade e 10 subtemas cada, aplicados a todas as turmas de Infantil)? Tópicos/temas/subtemas já existentes não serão duplicados.');">
    <button type="submit"
      style="{_BTN_AZ}background:#2b3990;">
      📥 Importar estrutura avaliativa padrão (Ed. Infantil)
    </button>
  </form>
  <form method="POST" action="/admin/seed-estrutura-infantil3"
        onsubmit="return confirm('Importar a estrutura avaliativa específica do Infantil 3 (A e B) — 5 tópicos com tema Conteúdos e Habilidades, aplicados apenas a essas turmas? Tópicos/temas/subtemas já existentes não serão duplicados.');">
    <button type="submit"
      style="{_BTN_AZ}background:#2b3990;">
      📥 Importar estrutura avaliativa — Infantil 3 (A e B)
    </button>
  </form>
  <form method="POST" action="/admin/seed-estrutura-infantil4"
        onsubmit="return confirm('Importar a estrutura avaliativa específica do Infantil 4 (A e B) — 5 tópicos com tema Conteúdos e Habilidades, aplicados apenas a essas turmas? Tópicos/temas/subtemas já existentes não serão duplicados.');">
    <button type="submit"
      style="{_BTN_AZ}background:#2b3990;">
      📥 Importar estrutura avaliativa — Infantil 4 (A e B)
    </button>
  </form>
  <form method="POST" action="/admin/seed-estrutura-infantil5"
        onsubmit="return confirm('Importar a estrutura avaliativa específica do Infantil 5 (A) — 5 tópicos com tema Conteúdos e Habilidades, aplicados apenas a essa turma? Tópicos/temas/subtemas já existentes não serão duplicados.');">
    <button type="submit"
      style="{_BTN_AZ}background:#2b3990;">
      📥 Importar estrutura avaliativa — Infantil 5 (A)
    </button>
  </form>
</div>""")

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Estrutura Avaliativa</h1>
      <p style="font-size:12px;color:#888;">{len(topicos)} tópico(s) · {total_temas} tema(s) · {total_subtemas} subtema(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;
       font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {novo_topico_card}
  {topicos_html}
</div>"""
    return page_shell("Estrutura Avaliativa — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  PAINEL DE RELATÓRIOS SEMESTRAIS (ADMIN)
# ════════════════════════════════════════════════════════════════════════

_ST = {
    "pendente":     ("#b52222", "#fef2f2", "#fecaca", "Pendente"),
    "em_andamento": ("#c25b0d", "#fef0e4", "#f8d4a8", "Em andamento"),
    "concluido":    ("#0a7c3e", "#e3f5ec", "#a8ddc0", "Concluído"),
}

def _pill_status(status: str, rel_id: int | None = None, trancado: bool = False,
                  abrir_href: str | None = None) -> str:
    cor, bg, bd, label = _ST.get(status, _ST["pendente"])
    cadeado = f' <span title="Trancado pelo administrador" style="color:{cor};">{ICON_LOCK}</span>' if trancado else ""
    return (f'<span style="background:{bg};border:1px solid {bd};color:{cor};'
            f'font-size:10px;font-weight:800;padding:2px 10px;border-radius:20px;'
            f'white-space:nowrap;">{dot(cor)}{label}{cadeado}</span>')


def _btn_abrir(status: str, rel_id: int | None, abrir_href: str | None) -> str:
    """Botão explícito para abrir/editar o relatório — visível independente do status,
    já que clicar apenas na pill de status não é intuitivo o suficiente."""
    href = f"/admin/relatorio/{rel_id}" if rel_id else abrir_href
    if not href:
        return ""
    label = f"{ICON_EDIT}Editar" if status == "concluido" else f"{ICON_CLIPBOARD}Abrir"
    return (f'<a href="{href}" style="font-family:\'Nunito\',sans-serif;font-size:10px;font-weight:800;'
            f'background:#e8eaf8;color:#2b3990;border:1px solid #b0b8e8;border-radius:7px;'
            f'padding:3px 9px;text-decoration:none;white-space:nowrap;">{label}</a>')


def _btn_trancar(matricula: str, semestre: int, trancado: bool, filtros: dict) -> str:
    acao = "destrancar" if trancado else "trancar"
    icone = ICON_UNLOCK if trancado else ICON_LOCK
    titulo = "Destrancar relatório" if trancado else "Trancar relatório (impede edição da professora)"
    confirma = "" if trancado else (
        " onsubmit=\"return confirm('Trancar este relatório? A professora não poderá mais editá-lo até você destrancar.');\""
    )
    return f"""<form method="POST" action="/admin/relatorio/aluno/{matricula}/{semestre}/{acao}"
      style="display:inline;"{confirma}>
  <input type="hidden" name="turma" value="{filtros.get('turma','')}">
  <input type="hidden" name="semestre_filtro" value="{filtros.get('semestre','')}">
  <input type="hidden" name="status" value="{filtros.get('status','')}">
  <button type="submit" title="{titulo}"
    style="background:none;border:none;cursor:pointer;font-size:12px;">{icone}</button>
</form>"""


def admin_relatorios_page(
    rows: list,           # lista de dicts: nome, turma, professora, s1_status, s1_id, s2_status, s2_id
    turmas_disponiveis: list,
    filtros: dict,        # {turma, semestre, status}
    contadores: dict,     # {total, pendentes, andamento, concluidos}
    msg: str = "",
    erro: str = "",
    staff_only: bool = False,
    pais_liberado: bool = True,
) -> str:
    nav   = admin_nav("relatorios", staff_only=staff_only)
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

    # ── Controle de visibilidade para os pais (admin + coordenação) ──
    if pais_liberado:
        vis_cor, vis_bg, vis_bd = "#0a7c3e", "#e3f5ec", "#a8ddc0"
        vis_ico   = "🟢"
        vis_titulo = "Área dos pais LIBERADA"
        vis_texto  = "Os responsáveis conseguem consultar os boletins e relatórios neste momento."
        vis_btn_lbl = "Desativar para os pais"
        vis_btn_val = "0"
        vis_btn_bg, vis_btn_cor, vis_btn_bd = "#fef2f2", "#b52222", "#fecaca"
        vis_confirma = ("return confirm('Desativar o acesso dos pais? Eles passarão a ver a "
                        "mensagem de que o site está em atualização.');")
    else:
        vis_cor, vis_bg, vis_bd = "#c25b0d", "#fef0e4", "#f8d4a8"
        vis_ico   = "🟠"
        vis_titulo = "Área dos pais DESATIVADA"
        vis_texto  = ("Os responsáveis veem a mensagem de \"site em atualização\". "
                      "Ative quando terminar de lançar as informações.")
        vis_btn_lbl = "Liberar para os pais"
        vis_btn_val = "1"
        vis_btn_bg, vis_btn_cor, vis_btn_bd = "#e3f5ec", "#0a7c3e", "#a8ddc0"
        vis_confirma = "return confirm('Liberar a consulta para todos os pais agora?');"

    visibilidade_card = _card(f"""
<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  <div style="flex:1;min-width:240px;">
    <div style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;">
      Visibilidade dos pais
    </div>
    <div style="display:inline-flex;align-items:center;gap:8px;background:{vis_bg};border:1.5px solid {vis_bd};
                color:{vis_cor};font-weight:900;font-size:13px;padding:6px 14px;border-radius:20px;">
      {vis_ico} {vis_titulo}
    </div>
    <p style="font-size:12px;color:#777;margin-top:8px;line-height:1.5;max-width:520px;">{vis_texto}</p>
  </div>
  <form method="POST" action="/admin/visibilidade" onsubmit="{vis_confirma}">
    <input type="hidden" name="liberar" value="{vis_btn_val}">
    <button type="submit"
      style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;
             background:{vis_btn_bg};color:{vis_btn_cor};border:1.5px solid {vis_btn_bd};
             border-radius:10px;padding:11px 22px;cursor:pointer;white-space:nowrap;">
      {vis_btn_lbl}
    </button>
  </form>
</div>""")

    # ── Cards de resumo (totais + divisão por semestre) ──
    def _cards_semestre(label: str, c: dict) -> str:
        return f"""
<div style="flex:1;min-width:260px;">
  <div style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px;">{label}</div>
  <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;">
    <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:12px 14px;text-align:center;">
      <div style="font-size:22px;font-weight:900;color:#b52222;">{c['pendentes']}</div>
      <div style="font-size:10px;color:#b52222;font-weight:700;margin-top:2px;">{dot("#b52222")}Pendentes</div>
    </div>
    <div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:12px;padding:12px 14px;text-align:center;">
      <div style="font-size:22px;font-weight:900;color:#c25b0d;">{c['andamento']}</div>
      <div style="font-size:10px;color:#c25b0d;font-weight:700;margin-top:2px;">{dot("#c25b0d")}Andamento</div>
    </div>
    <div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:12px;padding:12px 14px;text-align:center;">
      <div style="font-size:22px;font-weight:900;color:#0a7c3e;">{c['concluidos']}</div>
      <div style="font-size:10px;color:#0a7c3e;font-weight:700;margin-top:2px;">{dot("#0a7c3e")}Concluídos</div>
    </div>
  </div>
</div>"""

    resumo = f"""
<div style="background:#fff;border-radius:12px;padding:16px 18px;box-shadow:0 2px 8px rgba(0,0,0,.07);
            text-align:center;margin-bottom:12px;max-width:220px;">
  <div style="font-size:28px;font-weight:900;color:#2b3990;">{contadores['total']}</div>
  <div style="font-size:11px;color:#aaa;font-weight:700;margin-top:2px;">Total de alunos</div>
</div>
<div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:20px;">
  {_cards_semestre("1º Semestre", contadores['s1'])}
  {_cards_semestre("2º Semestre", contadores['s2'])}
</div>"""

    # ── Filtros ──
    def _opt_turma(val, label):
        sel = "selected" if filtros.get("turma","") == val else ""
        return f'<option value="{val}" {sel}>{label}</option>'

    def _opt_sem(val, label):
        sel = "selected" if str(filtros.get("semestre","")) == str(val) else ""
        return f'<option value="{val}" {sel}>{label}</option>'

    def _opt_st(val, label):
        sel = "selected" if filtros.get("status","") == val else ""
        return f'<option value="{val}" {sel}>{label}</option>'

    opts_turma = _opt_turma("", "Todas as turmas") + "".join(_opt_turma(t, t) for t in turmas_disponiveis)
    opts_sem   = _opt_sem("", "1º e 2º Sem.") + _opt_sem("1", "1º Semestre") + _opt_sem("2", "2º Semestre")
    opts_st    = (_opt_st("", "Todos os status") + _opt_st("pendente", "🔴 Pendente")
                  + _opt_st("em_andamento", "🟡 Em andamento") + _opt_st("concluido", "🟢 Concluído"))

    filtros_card = _card(f"""
<form method="GET" action="/admin/relatorios"
      style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;">
  <div style="flex:1;min-width:180px;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;display:block;margin-bottom:4px;">Turma</label>
    <select name="turma" style="{_INP}background:#fff;">
      {opts_turma}
    </select>
  </div>
  <div style="min-width:140px;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;display:block;margin-bottom:4px;">Semestre</label>
    <select name="semestre" style="{_INP}background:#fff;">
      {opts_sem}
    </select>
  </div>
  <div style="min-width:160px;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;display:block;margin-bottom:4px;">Status</label>
    <select name="status" style="{_INP}background:#fff;">
      {opts_st}
    </select>
  </div>
  <button type="submit" style="{_BTN_AZ}">Filtrar</button>
  <a href="/admin/relatorios" style="{_BTN_CINZA}">Limpar</a>
</form>""")

    # ── Trava em massa por semestre ──
    turma_atual = filtros.get("turma", "")
    escopo_label = f"da turma {turma_atual}" if turma_atual else "de todas as turmas"

    def _form_massa(semestre: int, acao: str) -> str:
        trancar = acao == "trancar"
        cor = "#b52222" if trancar else "#0a7c3e"
        bg  = "#fef2f2" if trancar else "#e3f5ec"
        bd  = "#fecaca" if trancar else "#a8ddc0"
        icone = ICON_LOCK if trancar else ICON_UNLOCK
        label = f"{icone}{'Trancar' if trancar else 'Destrancar'} {semestre}º Semestre"
        confirma = (f"return confirm('{'Trancar' if trancar else 'Destrancar'} TODOS os relatórios "
                    f"do {semestre}º semestre {escopo_label}?');")
        return f"""
<form method="POST" action="/admin/relatorios/trancar-semestre" style="display:inline;"
      onsubmit="{confirma}">
  <input type="hidden" name="semestre" value="{semestre}">
  <input type="hidden" name="acao" value="{acao}">
  <input type="hidden" name="turma" value="{turma_atual}">
  <input type="hidden" name="status" value="{filtros.get('status','')}">
  <button type="submit"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
           background:{bg};color:{cor};border:1.5px solid {bd};
           border-radius:9px;padding:9px 16px;cursor:pointer;white-space:nowrap;">
    {label}
  </button>
</form>"""

    trava_massa_card = _card(f"""
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
  <span style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;">
    Trava em massa ({escopo_label}):
  </span>
  {_form_massa(1, "trancar")}
  {_form_massa(1, "destrancar")}
  <span style="width:1px;height:24px;background:#e8e8e4;"></span>
  {_form_massa(2, "trancar")}
  {_form_massa(2, "destrancar")}
</div>""")

    imp_lote_card = _card(f"""
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
  <span style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;">
    Impressão em lote ({escopo_label}):
  </span>
  <a href="/admin/relatorios/imprimir?semestre=1&turma={quote(turma_atual)}" target="_blank"
     style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
            background:#e8eaf8;color:#2b3990;border:1.5px solid #b0b8e8;
            border-radius:9px;padding:9px 16px;cursor:pointer;white-space:nowrap;text-decoration:none;">
    {ICON_PRINTER}Imprimir todos — 1º Semestre
  </a>
  <a href="/admin/relatorios/imprimir?semestre=2&turma={quote(turma_atual)}" target="_blank"
     style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
            background:#e8eaf8;color:#2b3990;border:1.5px solid #b0b8e8;
            border-radius:9px;padding:9px 16px;cursor:pointer;white-space:nowrap;text-decoration:none;">
    {ICON_PRINTER}Imprimir todos — 2º Semestre
  </a>
  <span style="font-size:10px;color:#aaa;">💡 Use o filtro de turma acima para restringir a impressão a uma turma.</span>
</div>""")

    imp_selecionados_card = _card(f"""
<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
  <span style="font-size:11px;font-weight:800;color:#0a7c3e;text-transform:uppercase;letter-spacing:.5px;white-space:nowrap;">
    Imprimir selecionados:
  </span>
  <span id="sel-contador" style="font-size:12px;font-weight:800;color:#2b3990;min-width:80px;">nenhum marcado</span>
  <button type="button" onclick="imprimirSelecionados(1)"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;background:#e3f5ec;color:#0a7c3e;
           border:1.5px solid #a8ddc0;border-radius:9px;padding:9px 16px;cursor:pointer;white-space:nowrap;">
    {ICON_PRINTER}Imprimir selecionados — 1º Semestre
  </button>
  <button type="button" onclick="imprimirSelecionados(2)"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;background:#e3f5ec;color:#0a7c3e;
           border:1.5px solid #a8ddc0;border-radius:9px;padding:9px 16px;cursor:pointer;white-space:nowrap;">
    {ICON_PRINTER}Imprimir selecionados — 2º Semestre
  </button>
  <span style="font-size:10px;color:#aaa;">💡 Marque os alunos na tabela e clique no semestre desejado.</span>
</div>""")

    sel_script = """
<script>
function atualizaContadorSel(){
  var n=document.querySelectorAll('.sel-rel:checked').length;
  var el=document.getElementById('sel-contador');
  if(el)el.textContent=n>0?(n+' aluno(s) marcado(s)'):'nenhum marcado';
}
function selTodosRel(master){
  document.querySelectorAll('.sel-rel').forEach(function(c){c.checked=master.checked;});
  atualizaContadorSel();
}
function imprimirSelecionados(sem){
  var mats=[];
  document.querySelectorAll('.sel-rel:checked').forEach(function(c){mats.push(c.value);});
  if(mats.length===0){alert('Marque ao menos um aluno na tabela para imprimir.');return;}
  window.open('/admin/relatorios/imprimir-selecionados?semestre='+sem+'&matriculas='+mats.join(','),'_blank');
}
</script>"""

    # ── Tabela de alunos ──
    sem_filtro = str(filtros.get("semestre", ""))
    mostrar_s1 = sem_filtro in ("", "1")
    mostrar_s2 = sem_filtro in ("", "2")

    if rows:
        th_s1 = '<th style="padding:9px 12px;text-align:center;">1º Semestre</th>' if mostrar_s1 else ""
        th_s2 = '<th style="padding:9px 12px;text-align:center;">2º Semestre</th>' if mostrar_s2 else ""

        linhas = ""
        for r in rows:
            td_s1 = ""
            td_s2 = ""
            if mostrar_s1:
                pill = _pill_status(r["s1_status"], r.get("s1_id"), r.get("s1_trancado", False))
                abrir = _btn_abrir(r["s1_status"], r.get("s1_id"), abrir_href=f'/admin/relatorio/aluno/{r["matricula"]}/1')
                imp  = f'<a href="/admin/relatorio/{r["s1_id"]}/imprimir" target="_blank" title="Imprimir" style="color:#2b3990;">{ICON_PRINTER}</a>' if r.get("s1_id") else ""
                trv  = _btn_trancar(r["matricula"], 1, r.get("s1_trancado", False), filtros)
                td_s1 = (f'<td style="padding:9px 12px;text-align:center;">'
                         f'<div style="display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:4px;">'
                         f'{pill}{abrir}{imp}{trv}</div></td>')
            if mostrar_s2:
                pill = _pill_status(r["s2_status"], r.get("s2_id"), r.get("s2_trancado", False))
                abrir = _btn_abrir(r["s2_status"], r.get("s2_id"), abrir_href=f'/admin/relatorio/aluno/{r["matricula"]}/2')
                imp  = f'<a href="/admin/relatorio/{r["s2_id"]}/imprimir" target="_blank" title="Imprimir" style="color:#2b3990;">{ICON_PRINTER}</a>' if r.get("s2_id") else ""
                trv  = _btn_trancar(r["matricula"], 2, r.get("s2_trancado", False), filtros)
                td_s2 = (f'<td style="padding:9px 12px;text-align:center;">'
                         f'<div style="display:flex;align-items:center;justify-content:center;flex-wrap:wrap;gap:4px;">'
                         f'{pill}{abrir}{imp}{trv}</div></td>')

            linhas += f"""
<tr style="border-bottom:.5px solid #f0f0ee;">
  <td style="padding:9px 12px;text-align:center;"><input type="checkbox" class="sel-rel" value="{r['matricula']}" onchange="atualizaContadorSel()" style="width:16px;height:16px;cursor:pointer;"></td>
  <td style="padding:9px 12px;font-weight:800;color:#2b3990;">{r['nome']}</td>
  <td style="padding:9px 12px;font-size:12px;color:#555;">{r['turma']}</td>
  <td style="padding:9px 12px;font-size:12px;color:#888;">{r['professora']}</td>
  {td_s1}
  {td_s2}
</tr>"""

        tabela_html = _card(f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;text-align:center;"><input type="checkbox" onclick="selTodosRel(this)" title="Selecionar todos" style="width:16px;height:16px;cursor:pointer;"></th>
      <th style="padding:9px 12px;text-align:left;">Aluno</th>
      <th style="padding:9px 12px;text-align:left;">Turma</th>
      <th style="padding:9px 12px;text-align:left;">Professora</th>
      {th_s1}
      {th_s2}
    </tr>
  </thead>
  <tbody>{linhas}</tbody>
</table>
</div>""")
    else:
        tabela_html = _card('<p style="text-align:center;color:#aaa;padding:24px;">Nenhum aluno de Ed. Infantil encontrado com esses filtros.</p>')

    body = f"""
<div style="max-width:1000px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Relatórios Semestrais</h1>
      <p style="font-size:12px;color:#888;">Ed. Infantil — {contadores['total']} aluno(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {visibilidade_card}
  {resumo}
  {filtros_card}
  {trava_massa_card}
  {imp_lote_card}
  {imp_selecionados_card}
  {tabela_html}
</div>
{sel_script}"""
    return page_shell("Relatórios Semestrais — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  PÁGINA DE RELATÓRIOS DE UM ALUNO (admin)
# ════════════════════════════════════════════════════════════════════════

def admin_aluno_relatorios_page(aluno: dict, matricula: str, rel1: dict | None, rel2: dict | None) -> str:
    """
    Mostra os dois relatórios semestrais de um aluno da Ed. Infantil.
    rel1/rel2: dict do relatório ou None (não existe ainda).
    """
    nome      = aluno.get("nome", "")
    turma     = aluno.get("turma", "")
    periodo   = aluno.get("periodo", "")
    professora= aluno.get("professora", "")
    ano       = aluno.get("ano_letivo", "2026")

    def _sem_card(sem: int, rel: dict | None) -> str:
        sem_label = f"{sem}º Semestre"
        if rel is None:
            status_html = (
                f'<span style="background:#fef2f2;border:1px solid #fecaca;color:#b52222;'
                f'font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;">{dot("#b52222")}Não preenchido</span>'
            )
            btn = (f'<a href="/admin/relatorio/aluno/{matricula}/{sem}" '
                   f'style="background:#2b3990;color:#fff;font-family:\'Nunito\',sans-serif;'
                   f'font-weight:800;font-size:13px;padding:9px 20px;border-radius:9px;'
                   f'text-decoration:none;">{ICON_EDIT}Iniciar relatório</a>')
            impressao = ""
        else:
            s = rel.get("status", "pendente")
            cor, bg, bd = _ST_COR[s], _ST_BG[s], _ST_BD[s]
            status_html = (
                f'<span style="background:{bg};border:1px solid {bd};color:{cor};'
                f'font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;">'
                f'{dot(cor)}{_ST_LAB[s]}</span>'
            )
            btn = (f'<a href="/admin/relatorio/{rel["id"]}" '
                   f'style="background:#2b3990;color:#fff;font-family:\'Nunito\',sans-serif;'
                   f'font-weight:800;font-size:13px;padding:9px 20px;border-radius:9px;'
                   f'text-decoration:none;">{ICON_EDIT}Ver / Editar</a>')
            impressao = (f' &nbsp;<a href="/admin/relatorio/{rel["id"]}/imprimir" target="_blank"'
                         f' style="background:#e8eaf8;color:#2b3990;font-family:\'Nunito\',sans-serif;'
                         f'font-weight:800;font-size:13px;padding:9px 18px;border-radius:9px;'
                         f'text-decoration:none;">{ICON_PRINTER}Imprimir</a>')

        return f"""
<div style="background:#fff;border-radius:12px;padding:20px 24px;margin-bottom:14px;
            box-shadow:0 2px 10px rgba(0,0,0,.07);">
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
    <div style="font-family:'Fredoka One',cursive;font-size:17px;color:#2b3990;flex:1;">
      {sem_label} / {ano}
    </div>
    {status_html}
  </div>
  <div style="margin-top:14px;display:flex;gap:8px;flex-wrap:wrap;">
    {btn}{impressao}
  </div>
</div>"""

    body = f"""
<div style="max-width:820px;margin:0 auto;padding:24px 16px;">
  <!-- Header -->
  <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="/admin" style="background:#e8eaf8;color:#2b3990;font-family:'Nunito',sans-serif;
       font-weight:800;font-size:12px;padding:8px 14px;border-radius:8px;margin-top:2px;">
      ← Painel
    </a>
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#2b3990;">{nome}</h1>
      <div style="font-size:12px;color:#aaa;margin-top:3px;">
        {turma} &nbsp;·&nbsp; {periodo} &nbsp;·&nbsp; Profª {professora} &nbsp;·&nbsp; Matrícula {matricula}
      </div>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;
       font-weight:700;font-size:12px;padding:8px 14px;border-radius:9px;border:1px solid #dcdcd8;">
      Sair
    </a>
  </div>

  <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;margin-bottom:14px;">
    {ICON_CLIPBOARD}Relatórios Semestrais
  </div>

  {_sem_card(1, rel1)}
  {_sem_card(2, rel2)}
</div>"""
    return page_shell(f"Relatórios — {nome}", body)


# ════════════════════════════════════════════════════════════════════════
#  PÁGINA DE EDIÇÃO DO ALUNO INFANTIL (admin)
# ════════════════════════════════════════════════════════════════════════

def aluno_infantil_form(matricula: str, aluno: dict, temas: list, msg: str = "") -> str:
    nome      = aluno.get("nome", "")
    turma     = aluno.get("turma", "")
    periodo   = aluno.get("periodo", "")
    professora= aluno.get("professora", "")
    ano       = aluno.get("ano_letivo", "2026")
    obs       = aluno.get("observacoes", "")

    msg_html = _msg_ok(msg) if msg else ""

    # ── Subtemas por tópico → tema (temas é lista de tópicos: get_temas_para_turma) ──
    total_subtemas_turma = sum(
        len(t.get("subtemas", [])) for tp in temas for t in tp.get("temas", [])
    )
    if not temas or total_subtemas_turma == 0:
        subtemas_html = """
<div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:12px;padding:20px;
            color:#c25b0d;font-size:13px;font-weight:700;text-align:center;">
  ⚠️ Nenhum tema cadastrado para esta turma.<br>
  <span style="font-size:11px;font-weight:600;">Acesse <strong>Temas Avaliativos</strong> no menu para configurar.</span>
</div>"""
    else:
        secoes = ""
        for topico in temas:
            for tema in topico.get("temas", []):
                linhas = ""
                for st in tema.get("subtemas", []):
                    linhas += f"""
<div style="padding:8px 0;border-bottom:.5px solid #f0f0ee;font-size:13px;color:#4a4a4a;">
  • {st['descricao']}
</div>"""
                secoes += f"""
<div style="background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:14px;color:#2b3990;
              margin-bottom:10px;padding-bottom:7px;border-bottom:2px solid #f7d800;">
    📂 {topico['nome']} <span style="font-weight:400;">— 🏷️ {tema['nome']}</span>
    <span style="font-size:11px;font-family:'Nunito',sans-serif;font-weight:700;color:#aaa;margin-left:6px;">
      ({len(tema.get('subtemas',[]))} subtemas)
    </span>
  </div>
  {linhas}
</div>"""
        subtemas_html = secoes

    # ── Campo de observações ──
    inp_s = ("width:100%;font-family:'Nunito',sans-serif;font-size:13px;color:#4a4a4a;"
             "padding:12px 14px;border:1.5px solid #dcdcd8;border-radius:9px;outline:none;"
             "resize:vertical;line-height:1.6;")
    obs_html = f"""
<div style="background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:18px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;
              margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #f7d800;">
    📝 Observações
    <span style="font-size:10px;font-weight:700;color:#aaa;margin-left:8px;">
      anotações livres durante o semestre
    </span>
  </div>
  <textarea name="observacoes" rows="6"
    placeholder="Anote o desenvolvimento do aluno, conquistas, pontos de atenção..."
    style="{inp_s}"
    onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#dcdcd8'">{obs}</textarea>
</div>"""

    _foto = aluno.get("foto_url")
    _rem_foto = (f'<form method="POST" action="/admin/aluno/{matricula}/foto/remover" '
                 f'onsubmit="return confirm(\'Remover a foto?\');"><button type="submit" '
                 f'style="{_BTN_VM}">Remover</button></form>') if _foto else ""
    foto_card = f"""
<div style="background:#fff;border-radius:12px;padding:16px 22px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  {avatar(nome, _foto, size=60)}
  <div style="flex:1;min-width:200px;">
    <div style="font-family:'Fredoka One',cursive;font-size:14px;color:#2b3990;">📷 Foto do aluno</div>
    <div style="font-size:11px;color:#888;margin-top:2px;">JPG, PNG ou WEBP · até 8 MB · recortada em quadrado automaticamente.</div>
  </div>
  <label style="{_BTN_AZ}padding:9px 18px;font-size:12px;cursor:pointer;display:inline-block;">
    📷 Escolher foto
    <input type="file" accept="image/jpeg,image/png,image/webp" data-action="/admin/aluno/{matricula}/foto" onchange="abrirCropper(this)" style="display:none;">
  </label>
  {_rem_foto}
</div>"""

    body = f"""
<div style="max-width:820px;margin:0 auto;padding:24px 16px;">

  <!-- Header -->
  <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="/admin" style="background:#e8eaf8;color:#2b3990;font-family:'Nunito',sans-serif;
       font-weight:800;font-size:12px;padding:8px 14px;border-radius:8px;margin-top:2px;">
      ← Painel
    </a>
    {avatar(nome, aluno.get("foto_url"), size=48)}
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#2b3990;">{nome}</h1>
      <div style="font-size:12px;color:#aaa;margin-top:3px;">
        {turma} &nbsp;·&nbsp; {periodo} &nbsp;·&nbsp; Profª {professora}
        &nbsp;·&nbsp; Matrícula {matricula} &nbsp;·&nbsp; {ano}
      </div>
    </div>
    <div style="display:flex;gap:8px;">
      <a href="/admin/aluno/{matricula}/relatorios"
         style="background:#e3f5ec;color:#0a7c3e;font-family:'Nunito',sans-serif;
                font-weight:800;font-size:12px;padding:8px 14px;border-radius:8px;white-space:nowrap;">
        📋 Relatórios
      </a>
      <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;
         font-weight:700;font-size:12px;padding:8px 14px;border-radius:9px;border:1px solid #dcdcd8;">
        Sair
      </a>
    </div>
  </div>

  {msg_html}
  {foto_card}

  <!-- Subtemas -->
  <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;
              margin-bottom:12px;">
    🏷️ Temas e Subtemas da Turma
  </div>
  {subtemas_html}

  <!-- Observações (sempre aberto) -->
  <div style="margin-top:20px;">
    <form method="POST" action="/admin/aluno/{matricula}/editar-infantil/salvar">
      {obs_html}
      <button type="submit"
        style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
               background:#2b3990;color:#fff;border:none;border-radius:10px;
               padding:12px 32px;cursor:pointer;">
        💾 Salvar Observações
      </button>
    </form>
  </div>

</div>"""
    return page_shell(f"Editar — {nome}", body)


# ════════════════════════════════════════════════════════════════════════
#  AVALIAÇÃO DE INGLÊS (PDF)
# ════════════════════════════════════════════════════════════════════════

def banner_festas_pais() -> str:
    """Pop-up animado de São João / boas férias exibido ao responsável ao abrir
    o boletim ou relatório. O pai fecha antes de visualizar o documento.
    Aparece já visível (não depende de JS para abrir) e some ao fechar.
    Expira automaticamente após FESTAS_ATE. Não aparece na impressão (.no-print)."""
    if date.today() > FESTAS_ATE:
        return ""
    return """
<div id="festa-pop" class="no-print" onclick="if(event.target===this)this.style.display='none'"
     style="position:fixed;inset:0;z-index:2000;display:flex;align-items:center;justify-content:center;
            padding:18px;background:rgba(18,24,70,.55);-webkit-backdrop-filter:blur(4px);backdrop-filter:blur(4px);">
  <style>
    @keyframes fpPop{0%{transform:scale(.55) translateY(40px);opacity:0;}
      60%{transform:scale(1.05) translateY(-6px);opacity:1;}100%{transform:scale(1) translateY(0);}}
    @keyframes fpFloat{0%,100%{transform:translateY(0) rotate(-4deg);}50%{transform:translateY(-9px) rotate(4deg);}}
    @keyframes fpFlags{0%{background-position:0 0;}100%{background-position:72px 0;}}
    #festa-pop .fp-card{animation:fpPop .6s cubic-bezier(.2,.9,.3,1.35) both;}
    #festa-pop .fp-flags{animation:fpFlags 3s linear infinite;}
    #festa-pop .fp-emoji{display:inline-block;animation:fpFloat 3s ease-in-out infinite;}
    @media(prefers-reduced-motion:reduce){#festa-pop .fp-card,#festa-pop .fp-flags,#festa-pop .fp-emoji{animation:none!important;}}
  </style>
  <div class="fp-card" style="position:relative;max-width:430px;width:100%;background:#fff;border-radius:24px;
       overflow:hidden;box-shadow:0 26px 72px rgba(10,15,50,.5);">
    <div class="fp-flags" style="height:12px;
         background:repeating-linear-gradient(45deg,#f7d800 0 18px,#ff5a5f 18px 36px,#19c7b4 36px 54px,#ff9f1c 54px 72px);"></div>
    <button onclick="document.getElementById('festa-pop').style.display='none'" aria-label="Fechar"
      style="position:absolute;top:16px;right:16px;width:34px;height:34px;border:none;border-radius:50%;
             background:rgba(43,57,144,.10);color:#2b3990;font-size:16px;font-weight:900;cursor:pointer;line-height:1;">✕</button>
    <div style="padding:28px 28px 26px;text-align:center;">
      <div style="font-size:40px;line-height:1;margin-bottom:10px;">
        <span class="fp-emoji">🎉</span>
        <span class="fp-emoji" style="animation-delay:.3s;">🌽</span>
        <span class="fp-emoji" style="animation-delay:.6s;">🔥</span>
        <span class="fp-emoji" style="animation-delay:.9s;">🎈</span>
      </div>
      <div style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;margin-bottom:10px;line-height:1.25;">
        Feliz São João e boas férias! 💛
      </div>
      <p style="font-size:13.5px;line-height:1.7;color:#41476b;font-weight:600;max-width:340px;margin:0 auto;">
        Chegamos ao fim de mais um semestre cheio de descobertas, sorrisos e conquistas.
        Obrigado, família, por caminhar lado a lado com a gente em cada passo do seu pequeno.
        Que estas férias sejam de muito descanso, brincadeiras ao pé da fogueira e momentos
        especiais juntos — e que voltem com o coração quentinho para a próxima etapa! 🌻
      </p>
      <div style="margin-top:14px;font-size:12px;color:#8a8fb0;font-weight:700;">
        Com carinho, Equipe Escola Espaço Alegre
      </div>
      <button onclick="document.getElementById('festa-pop').style.display='none'"
        style="margin-top:20px;background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;border:none;
               border-radius:999px;padding:13px 34px;font-family:'Plus Jakarta Sans','Nunito',sans-serif;
               font-weight:800;font-size:14px;cursor:pointer;box-shadow:0 8px 22px rgba(26,37,112,.4);">
        Continuar →
      </button>
    </div>
  </div>
</div>"""


def card_avaliacao_pais(matricula: str, semestres: list) -> str:
    """Card discreto exibido na área do responsável quando há PDF vinculado.
    Mostra um botão por semestre disponível. Abre o PDF em nova aba.
    Some por completo na impressão (.no-print)."""
    if not semestres:
        return ""
    botoes = ""
    for sem in semestres:
        botoes += f"""
    <a href="/avaliacao-ingles/{quote(matricula)}/{sem}" target="_blank" rel="noopener"
       style="display:inline-flex;align-items:center;gap:8px;text-decoration:none;
              background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;font-weight:800;
              font-size:13px;padding:10px 20px;border-radius:999px;white-space:nowrap;
              box-shadow:0 6px 16px rgba(26,37,112,.3);">{sem}º Semestre →</a>"""
    return f"""
<div class="no-print" style="max-width:750px;margin:0 auto 18px;padding:0 16px;position:relative;z-index:1;">
  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;
              background:rgba(255,255,255,.66);backdrop-filter:blur(20px) saturate(180%);
              -webkit-backdrop-filter:blur(20px) saturate(180%);
              border:1px solid rgba(255,255,255,.55);border-radius:16px;padding:15px 20px;
              box-shadow:0 10px 30px rgba(43,57,144,.16);">
    <span style="font-size:28px;line-height:1;">📄</span>
    <span style="flex:1;min-width:160px;">
      <span style="display:block;font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;">Avaliação de Inglês</span>
      <span style="display:block;font-size:12px;color:#5a6079;margin-top:2px;">
        Clique no semestre para visualizar ou baixar o PDF.
      </span>
    </span>
    <span style="display:flex;gap:8px;flex-wrap:wrap;">{botoes}</span>
  </div>
</div>"""


def admin_avaliacoes_page(
    alunos: dict,        # {matricula: {nome, turma, ...}}
    vinculos: dict,      # {matricula: {arquivo, nome_original, atualizado_em, ...}}
    arquivos: list,      # nomes de PDFs disponíveis na pasta
    sugestoes: dict,     # {matricula: arquivo_sugerido}
    semestre: int = 1,   # semestre que está sendo gerenciado (1 ou 2)
    msg: str = "",
    erro: str = "",
    staff_only: bool = False,
) -> str:
    nav   = admin_nav("avaliacoes", staff_only=staff_only)
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

    # ── Abas de semestre ──
    def _aba(sem: int, label: str) -> str:
        ativa = sem == semestre
        estilo = ("background:#2b3990;color:#fff;" if ativa
                  else "background:#fff;color:#2b3990;border:1.5px solid #b0b8e8;")
        return (f'<a href="/admin/avaliacoes?semestre={sem}" '
                f'style="{estilo}font-family:\'Nunito\',sans-serif;font-weight:900;font-size:13px;'
                f'padding:9px 22px;border-radius:10px;text-decoration:none;white-space:nowrap;">{label}</a>')
    abas = (f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:18px;">'
            f'{_aba(1, "1º Semestre")}{_aba(2, "2º Semestre")}</div>')

    # ordena alunos por turma e nome (mesmo critério das demais telas)
    ordenados = sorted(alunos.items(), key=lambda kv: (kv[1].get("turma", ""), kv[1].get("nome", "")))

    total_vinc = sum(1 for m in alunos if m in vinculos)
    sugest_novas = sum(1 for m, a in sugestoes.items() if m not in vinculos)

    def _options(selecionado: str) -> str:
        opts = ['<option value="">— selecione um arquivo —</option>']
        for a in arquivos:
            sel = "selected" if a == selecionado else ""
            opts.append(f'<option value="{a}" {sel}>{a}</option>')
        return "".join(opts)

    # ── Barra de resumo / ações em massa ──
    auto_btn = ""
    if sugest_novas:
        auto_btn = f"""
<form method="POST" action="/admin/avaliacoes/auto" style="display:inline;"
      onsubmit="return confirm('Vincular automaticamente {sugest_novas} avaliação(ões) sugerida(s) pelo nome do arquivo?');">
  <input type="hidden" name="semestre" value="{semestre}">
  <button type="submit" style="{_BTN_AZ}">✨ Vincular sugestões automáticas ({sugest_novas})</button>
</form>"""

    resumo_card = _card(f"""
<div style="display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
  <div style="flex:1;min-width:240px;">
    <div style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;letter-spacing:.5px;margin-bottom:6px;">
      Resumo
    </div>
    <p style="font-size:13px;color:#555;line-height:1.6;">
      <strong style="color:#2b3990;">{total_vinc}</strong> de <strong>{len(alunos)}</strong> aluno(s) com avaliação vinculada
      &nbsp;·&nbsp; <strong style="color:#2b3990;">{len(arquivos)}</strong> PDF(s) disponíveis na pasta.
    </p>
    <p style="font-size:11px;color:#aaa;margin-top:6px;">
      💡 As sugestões automáticas casam o nome do arquivo com o nome do aluno (ex.: <em>João Pedro - INFANTIL 4A.pdf</em>).
    </p>
  </div>
  {auto_btn}
</div>""")

    # ── Linhas da tabela ──
    linhas = ""
    for mat, al in ordenados:
        nome  = al.get("nome", "")
        turma = al.get("turma", "")
        v     = vinculos.get(mat)
        sugerido = sugestoes.get(mat, "")

        if v:
            data = (v.get("atualizado_em") or v.get("criado_em") or "")[:10]
            vinc_html = f"""
<div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
  <span style="background:#e3f5ec;border:1px solid #a8ddc0;color:#0a7c3e;font-size:11px;font-weight:800;
               padding:3px 10px;border-radius:20px;">📄 Vinculado</span>
  <a href="/admin/avaliacao/{quote(mat)}/{semestre}/ver" target="_blank" rel="noopener"
     style="color:#2b3990;font-weight:800;font-size:12px;text-decoration:underline;word-break:break-all;">{v.get('arquivo','')}</a>
</div>
<div style="font-size:10px;color:#aaa;margin-top:3px;">Atualizado em {data}</div>"""
            acao_links = f"""
<a href="/admin/avaliacao/{quote(mat)}/{semestre}/ver" target="_blank" rel="noopener"
   style="font-family:'Nunito',sans-serif;font-size:11px;font-weight:800;background:#e8eaf8;color:#2b3990;
          border:1px solid #b0b8e8;border-radius:7px;padding:5px 12px;text-decoration:none;white-space:nowrap;">👁 Visualizar</a>
<form method="POST" action="/admin/avaliacoes/remover" style="display:inline;"
      onsubmit="return confirm('Remover o vínculo da avaliação de {nome}? O arquivo PDF será mantido na pasta.');">
  <input type="hidden" name="matricula" value="{mat}">
  <input type="hidden" name="semestre" value="{semestre}">
  <button type="submit" style="{_BTN_VM}">🗑 Remover vínculo</button>
</form>"""
            label_associar = "🔁 Trocar arquivo"
            preselect = v.get("arquivo", "")
        else:
            vinc_html = '<span style="color:#bbb;font-size:12px;">— Sem avaliação vinculada</span>'
            if sugerido:
                vinc_html += f'<div style="font-size:10px;color:#c25b0d;margin-top:3px;">Sugestão: {sugerido}</div>'
            acao_links = ""
            label_associar = "🔗 Vincular"
            preselect = sugerido

        status_attr = "vinc" if v else "sem"
        linhas += f"""
<tr class="av-row" data-nome="{nome}" data-turma="{turma}" data-status="{status_attr}"
    style="border-bottom:.5px solid #f0f0ee;vertical-align:top;">
  <td style="padding:11px 12px;">
    <div style="font-weight:800;color:#2b3990;font-size:13px;">{nome}</div>
    <div style="font-size:11px;color:#888;">{turma}</div>
  </td>
  <td style="padding:11px 12px;min-width:200px;">{vinc_html}<div style="margin-top:7px;display:flex;gap:6px;flex-wrap:wrap;">{acao_links}</div></td>
  <td style="padding:11px 12px;min-width:260px;">
    <form method="POST" action="/admin/avaliacoes/associar" style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;margin-bottom:8px;">
      <input type="hidden" name="matricula" value="{mat}">
      <input type="hidden" name="semestre" value="{semestre}">
      <select name="arquivo" required style="{_INP}background:#fff;max-width:230px;">{_options(preselect)}</select>
      <button type="submit" style="{_BTN_AZ}padding:8px 16px;font-size:12px;">{label_associar}</button>
    </form>
    <form method="POST" action="/admin/avaliacoes/upload" enctype="multipart/form-data"
          style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
      <input type="hidden" name="matricula" value="{mat}">
      <input type="hidden" name="semestre" value="{semestre}">
      <input type="file" name="pdf" accept="application/pdf,.pdf" required
             style="font-family:'Nunito',sans-serif;font-size:11px;color:#555;max-width:200px;">
      <button type="submit" style="{_BTN_CINZA}padding:8px 16px;font-size:12px;">⬆ Enviar novo PDF</button>
    </form>
  </td>
</tr>"""

    # ── Card de filtro (busca instantânea, sem recarregar) ──
    turmas_distintas = sorted({al.get("turma", "") for al in alunos.values() if al.get("turma")})
    opts_turma = "".join(f'<option value="{t}">{t}</option>' for t in turmas_distintas)
    _lbl = ("font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;"
            "color:#aaa;display:block;margin-bottom:4px;")
    filtro_card = _card(f"""
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;">
  <div style="flex:1;min-width:200px;">
    <label style="{_lbl}">Buscar por nome</label>
    <input id="f-nome" type="text" oninput="filtrarAval()" autocomplete="off"
           placeholder="Digite o nome do aluno…" style="{_INP}background:#fff;">
  </div>
  <div style="min-width:170px;">
    <label style="{_lbl}">Turma</label>
    <select id="f-turma" onchange="filtrarAval()" style="{_INP}background:#fff;">
      <option value="">Todas as turmas</option>
      {opts_turma}
    </select>
  </div>
  <div style="min-width:170px;">
    <label style="{_lbl}">Situação</label>
    <select id="f-status" onchange="filtrarAval()" style="{_INP}background:#fff;">
      <option value="">Todas</option>
      <option value="vinc">✅ Vinculadas</option>
      <option value="sem">⬜ Sem vínculo</option>
    </select>
  </div>
  <button type="button" onclick="limparFiltroAval()" style="{_BTN_CINZA}">Limpar</button>
</div>
<div id="f-contador" style="font-size:12px;color:#888;margin-top:12px;font-weight:700;"></div>""")

    tabela = _card(f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;text-align:left;">Aluno</th>
      <th style="padding:9px 12px;text-align:left;">Avaliação vinculada</th>
      <th style="padding:9px 12px;text-align:left;">Associar / Enviar</th>
    </tr>
  </thead>
  <tbody>{linhas}</tbody>
</table>
<div id="av-vazio" style="display:none;text-align:center;color:#aaa;padding:26px;font-size:13px;">
  Nenhum aluno encontrado com esses filtros.
</div>
</div>""")

    script = """
<script>
function _normAval(s){return (s||'').toString().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function filtrarAval(){
  var nome=_normAval(document.getElementById('f-nome').value.trim());
  var turma=document.getElementById('f-turma').value;
  var status=document.getElementById('f-status').value;
  var rows=document.querySelectorAll('tr.av-row');
  var vis=0;
  rows.forEach(function(r){
    var okNome=!nome||_normAval(r.dataset.nome).indexOf(nome)!==-1;
    var okTurma=!turma||r.dataset.turma===turma;
    var okStatus=!status||r.dataset.status===status;
    var show=okNome&&okTurma&&okStatus;
    r.style.display=show?'':'none';
    if(show)vis++;
  });
  document.getElementById('f-contador').textContent='Mostrando '+vis+' de '+rows.length+' aluno(s)';
  document.getElementById('av-vazio').style.display=vis===0?'block':'none';
}
function limparFiltroAval(){
  document.getElementById('f-nome').value='';
  document.getElementById('f-turma').value='';
  document.getElementById('f-status').value='';
  filtrarAval();
}
document.addEventListener('DOMContentLoaded',filtrarAval);
</script>"""

    body = f"""
<div style="max-width:1000px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Avaliação de Inglês</h1>
      <p style="font-size:12px;color:#888;">Gerenciando o <strong style="color:#2b3990;">{semestre}º semestre</strong> — vincule o PDF a cada aluno; os responsáveis verão o botão na área deles.</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {abas}
  {aviso}
  {resumo_card}
  {filtro_card}
  {tabela}
</div>
{script}"""
    return page_shell("Avaliação de Inglês — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  CONTROLE DE ACESSOS DOS RESPONSÁVEIS
# ════════════════════════════════════════════════════════════════════════

_DOC_LABEL = {
    "boletim": "Boletim",
    "relatorio": "Relatório Semestral",
    "avaliacao_ingles": "Avaliação de Inglês",
}
_DISP_LABEL = {"web": "💻 Web", "mobile": "📱 Celular", "tablet": "📲 Tablet"}


def _fmt_dt(s: str) -> str:
    """'2026-06-25 14:30:00' -> '25/06/2026 14:30'."""
    if not s:
        return ""
    d, h = s[:10], s[11:16]
    return f"{d[8:10]}/{d[5:7]}/{d[0:4]} {h}" if len(d) == 10 else s


def admin_acessos_page(
    alunos: dict,          # {matricula: {nome, turma, professora, ...}}
    acessos_agg: list,     # [{matricula, nome_aluno, turma, documento, qtd, ultimo, dispositivo, ip}]
    total_acessos: int = 0,
    staff_only: bool = False,
) -> str:
    nav = admin_nav("acessos", staff_only=staff_only)

    # ── Métricas dos cards ──
    matriculas_acessaram = {a["matricula"] for a in acessos_agg if a["matricula"] in alunos}
    n_acessaram   = len(matriculas_acessaram)
    n_nao         = max(len(alunos) - n_acessaram, 0)
    ultimo_global = max((a["ultimo"] for a in acessos_agg), default="")
    ultimo_aluno  = ""
    if ultimo_global:
        for a in acessos_agg:
            if a["ultimo"] == ultimo_global:
                ultimo_aluno = a["nome_aluno"] or alunos.get(a["matricula"], {}).get("nome", "")
                break

    def _metric(valor, rotulo, cor, bg, bd):
        return f"""
<div style="flex:1;min-width:170px;background:{bg};border:1px solid {bd};border-radius:14px;padding:16px 18px;">
  <div style="font-size:28px;font-weight:900;color:{cor};line-height:1;">{valor}</div>
  <div style="font-size:11px;color:{cor};font-weight:700;margin-top:6px;">{rotulo}</div>
</div>"""

    ultimo_card = f"""
<div style="flex:1;min-width:200px;background:#e8eaf8;border:1px solid #b0b8e8;border-radius:14px;padding:16px 18px;">
  <div style="font-size:14px;font-weight:900;color:#2b3990;line-height:1.2;">{_fmt_dt(ultimo_global) or '—'}</div>
  <div style="font-size:11px;color:#2b3990;font-weight:700;margin-top:6px;">Último acesso{(' · ' + ultimo_aluno) if ultimo_aluno else ''}</div>
</div>"""

    cards = f"""
<div style="display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px;">
  {_metric(n_acessaram, "Responsáveis que acessaram", "#0a7c3e", "#e3f5ec", "#a8ddc0")}
  {_metric(n_nao, "Ainda não acessaram", "#b52222", "#fef2f2", "#fecaca")}
  {_metric(total_acessos, "Total de acessos registrados", "#2b3990", "#e8eaf8", "#b0b8e8")}
  {ultimo_card}
</div>"""

    # ── Linhas: acessos agregados + alunos que nunca acessaram ──
    turmas_distintas = sorted({al.get("turma", "") for al in alunos.values() if al.get("turma")})

    linhas = ""
    # 1) quem acessou (uma linha por aluno+documento)
    for a in sorted(acessos_agg, key=lambda x: x["ultimo"], reverse=True):
        mat = a["matricula"]
        al  = alunos.get(mat, {})
        nome  = a["nome_aluno"] or al.get("nome", "")
        turma = a["turma"] or al.get("turma", "")
        prof  = al.get("professora", "")
        doc   = _DOC_LABEL.get(a["documento"], a["documento"])
        disp  = _DISP_LABEL.get(a["dispositivo"], a["dispositivo"])
        linhas += f"""
<tr class="ac-row" data-nome="{nome}" data-turma="{turma}" data-doc="{a['documento']}" data-status="sim" data-data="{a['ultimo'][:10]}"
    style="border-bottom:.5px solid #f0f0ee;">
  <td style="padding:10px 12px;font-weight:800;color:#2b3990;">{nome}</td>
  <td style="padding:10px 12px;font-size:12px;color:#555;">{turma}</td>
  <td style="padding:10px 12px;font-size:12px;color:#888;">{prof}</td>
  <td style="padding:10px 12px;font-size:12px;color:#333;">{doc}</td>
  <td style="padding:10px 12px;text-align:center;font-weight:900;color:#2b3990;">{a['qtd']}</td>
  <td style="padding:10px 12px;font-size:12px;color:#333;white-space:nowrap;">{_fmt_dt(a['ultimo'])}</td>
  <td style="padding:10px 12px;font-size:12px;color:#555;white-space:nowrap;">{disp}</td>
  <td style="padding:10px 12px;text-align:center;">
    <span style="background:#e3f5ec;border:1px solid #a8ddc0;color:#0a7c3e;font-size:11px;font-weight:800;padding:3px 10px;border-radius:20px;white-space:nowrap;">Acessou</span>
  </td>
</tr>"""

    # 2) quem nunca acessou (uma linha por aluno)
    for mat, al in sorted(alunos.items(), key=lambda kv: (kv[1].get("turma", ""), kv[1].get("nome", ""))):
        if mat in matriculas_acessaram:
            continue
        nome  = al.get("nome", "")
        turma = al.get("turma", "")
        prof  = al.get("professora", "")
        linhas += f"""
<tr class="ac-row" data-nome="{nome}" data-turma="{turma}" data-doc="nenhum" data-status="nao" data-data=""
    style="border-bottom:.5px solid #f0f0ee;background:#fffdfa;">
  <td style="padding:10px 12px;font-weight:800;color:#2b3990;">{nome}</td>
  <td style="padding:10px 12px;font-size:12px;color:#555;">{turma}</td>
  <td style="padding:10px 12px;font-size:12px;color:#888;">{prof}</td>
  <td style="padding:10px 12px;font-size:12px;color:#bbb;">—</td>
  <td style="padding:10px 12px;text-align:center;color:#bbb;">0</td>
  <td style="padding:10px 12px;font-size:12px;color:#bbb;">Nunca acessou</td>
  <td style="padding:10px 12px;font-size:12px;color:#bbb;">—</td>
  <td style="padding:10px 12px;text-align:center;">
    <span style="background:#fef2f2;border:1px solid #fecaca;color:#b52222;font-size:11px;font-weight:800;padding:3px 10px;border-radius:20px;white-space:nowrap;">Não acessado</span>
  </td>
</tr>"""

    opts_turma = "".join(f'<option value="{t}">{t}</option>' for t in turmas_distintas)
    _lbl = ("font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;"
            "color:#aaa;display:block;margin-bottom:4px;")

    filtro_card = _card(f"""
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;">
  <div style="flex:1;min-width:170px;">
    <label style="{_lbl}">Buscar por aluno</label>
    <input id="ac-nome" type="text" oninput="filtrarAcessos()" autocomplete="off"
           placeholder="Nome do aluno…" style="{_INP}background:#fff;">
  </div>
  <div style="min-width:150px;">
    <label style="{_lbl}">Turma</label>
    <select id="ac-turma" onchange="filtrarAcessos()" style="{_INP}background:#fff;">
      <option value="">Todas</option>{opts_turma}
    </select>
  </div>
  <div style="min-width:150px;">
    <label style="{_lbl}">Documento</label>
    <select id="ac-doc" onchange="filtrarAcessos()" style="{_INP}background:#fff;">
      <option value="">Todos</option>
      <option value="boletim">Boletim</option>
      <option value="relatorio">Relatório Semestral</option>
      <option value="avaliacao_ingles">Avaliação de Inglês</option>
    </select>
  </div>
  <div style="min-width:150px;">
    <label style="{_lbl}">Situação</label>
    <select id="ac-status" onchange="filtrarAcessos()" style="{_INP}background:#fff;">
      <option value="">Todas</option>
      <option value="sim">✅ Acessou</option>
      <option value="nao">⬜ Não acessou</option>
    </select>
  </div>
  <div style="min-width:140px;">
    <label style="{_lbl}">De</label>
    <input id="ac-de" type="date" onchange="filtrarAcessos()" style="{_INP}background:#fff;">
  </div>
  <div style="min-width:140px;">
    <label style="{_lbl}">Até</label>
    <input id="ac-ate" type="date" onchange="filtrarAcessos()" style="{_INP}background:#fff;">
  </div>
  <button type="button" onclick="limparFiltroAcessos()" style="{_BTN_CINZA}">Limpar</button>
</div>
<div id="ac-contador" style="font-size:12px;color:#888;margin-top:12px;font-weight:700;"></div>""")

    if linhas:
        tabela = _card(f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;text-align:left;">Aluno</th>
      <th style="padding:9px 12px;text-align:left;">Turma</th>
      <th style="padding:9px 12px;text-align:left;">Professora</th>
      <th style="padding:9px 12px;text-align:left;">Documento</th>
      <th style="padding:9px 12px;text-align:center;">Acessos</th>
      <th style="padding:9px 12px;text-align:left;">Último acesso</th>
      <th style="padding:9px 12px;text-align:left;">Dispositivo</th>
      <th style="padding:9px 12px;text-align:center;">Situação</th>
    </tr>
  </thead>
  <tbody>{linhas}</tbody>
</table>
<div id="ac-vazio" style="display:none;text-align:center;color:#aaa;padding:26px;font-size:13px;">
  Nenhum registro encontrado com esses filtros.
</div>
</div>""")
    else:
        tabela = _card('<p style="text-align:center;color:#aaa;padding:24px;">Nenhum aluno cadastrado ainda.</p>')

    nota = _card("""
<p style="font-size:12px;color:#888;line-height:1.6;margin:0;">
  ℹ️ Os pais acessam por matrícula (sem login individual), por isso o registro é por
  <strong>aluno e documento</strong>. Mostramos a <strong>professora</strong> como referência de contato interno.
  Recarregamentos rápidos da mesma página não geram acessos duplicados.
</p>""")

    script = """
<script>
function _normAc(s){return (s||'').toString().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function filtrarAcessos(){
  var nome=_normAc(document.getElementById('ac-nome').value.trim());
  var turma=document.getElementById('ac-turma').value;
  var doc=document.getElementById('ac-doc').value;
  var status=document.getElementById('ac-status').value;
  var de=document.getElementById('ac-de').value;
  var ate=document.getElementById('ac-ate').value;
  var rows=document.querySelectorAll('tr.ac-row');
  var vis=0;
  rows.forEach(function(r){
    var d=r.dataset;
    var ok=(!nome||_normAc(d.nome).indexOf(nome)!==-1)
        && (!turma||d.turma===turma)
        && (!doc||d.doc===doc)
        && (!status||d.status===status);
    if(ok && (de||ate)){
      if(!d.data){ ok=false; }
      else{ if(de && d.data<de) ok=false; if(ate && d.data>ate) ok=false; }
    }
    r.style.display=ok?'':'none';
    if(ok)vis++;
  });
  document.getElementById('ac-contador').textContent='Mostrando '+vis+' de '+rows.length+' registro(s)';
  document.getElementById('ac-vazio').style.display=vis===0?'block':'none';
}
function limparFiltroAcessos(){
  ['ac-nome','ac-turma','ac-doc','ac-status','ac-de','ac-ate'].forEach(function(id){document.getElementById(id).value='';});
  filtrarAcessos();
}
document.addEventListener('DOMContentLoaded',filtrarAcessos);
</script>"""

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Controle de Acessos dos Responsáveis</h1>
      <p style="font-size:12px;color:#888;">Histórico de quem visualizou os documentos dos alunos.</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {cards}
  {filtro_card}
  {tabela}
  {nota}
</div>
{script}"""
    return page_shell("Controle de Acessos — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  AUDITORIA — trilha de alterações da equipe
# ════════════════════════════════════════════════════════════════════════

_ROLE_BADGE = {
    "admin":       ("#2b3990", "#e8eaf8", "#b0b8e8"),
    "coordenacao": ("#6a1a8a", "#f5eafc", "#e0c8f0"),
    "professora":  ("#0a7c3e", "#e3f5ec", "#a8ddc0"),
}


def admin_auditoria_page(registros: list) -> str:
    """Lista a trilha de auditoria (mais recentes primeiro). Apenas admin."""
    nav = admin_nav("auditoria")

    linhas = ""
    for r in registros:
        cor, bg, bd = _ROLE_BADGE.get(r.get("role", ""), ("#888", "#f0f0ee", "#ddd"))
        role = r.get("role", "") or "—"
        linhas += f"""
<tr class="aud-row" data-busca="{(r.get('usuario','') + ' ' + r.get('acao','') + ' ' + r.get('alvo','') + ' ' + r.get('detalhe','')).lower()}"
    style="border-bottom:.5px solid #f0f0ee;">
  <td style="padding:9px 12px;font-size:12px;color:#333;white-space:nowrap;">{_fmt_dt(r.get('criado_em',''))}</td>
  <td style="padding:9px 12px;">
    <span style="font-weight:800;color:#2b3990;font-size:13px;">{r.get('usuario','?')}</span>
    <span style="background:{bg};border:1px solid {bd};color:{cor};font-size:9px;font-weight:800;
                 padding:1px 7px;border-radius:10px;margin-left:6px;white-space:nowrap;">{role}</span>
  </td>
  <td style="padding:9px 12px;font-size:12px;color:#333;font-weight:700;">{r.get('acao','')}</td>
  <td style="padding:9px 12px;font-size:12px;color:#555;">{r.get('alvo','') or '—'}</td>
  <td style="padding:9px 12px;font-size:12px;color:#888;">{r.get('detalhe','') or '—'}</td>
</tr>"""

    if registros:
        tabela = _card(f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;text-align:left;">Data/hora</th>
      <th style="padding:9px 12px;text-align:left;">Quem</th>
      <th style="padding:9px 12px;text-align:left;">Ação</th>
      <th style="padding:9px 12px;text-align:left;">Alvo</th>
      <th style="padding:9px 12px;text-align:left;">Detalhe</th>
    </tr>
  </thead>
  <tbody>{linhas}</tbody>
</table>
<div id="aud-vazio" style="display:none;text-align:center;color:#aaa;padding:26px;font-size:13px;">
  Nenhum registro encontrado.
</div>
</div>""")
    else:
        tabela = _card('<p style="text-align:center;color:#aaa;padding:24px;">Nenhuma alteração registrada ainda.</p>')

    _lbl = ("font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;"
            "color:#aaa;display:block;margin-bottom:4px;")
    filtro_card = _card(f"""
<div style="display:flex;gap:10px;flex-wrap:wrap;align-items:flex-end;">
  <div style="flex:1;min-width:220px;">
    <label style="{_lbl}">Buscar (usuário, ação, aluno…)</label>
    <input id="aud-busca" type="text" oninput="filtrarAud()" autocomplete="off"
           placeholder="Digite para filtrar…" style="{_INP}background:#fff;">
  </div>
  <button type="button" onclick="document.getElementById('aud-busca').value='';filtrarAud()" style="{_BTN_CINZA}">Limpar</button>
</div>
<div id="aud-contador" style="font-size:12px;color:#888;margin-top:12px;font-weight:700;"></div>""")

    script = """
<script>
function _normAud(s){return (s||'').toString().toLowerCase().normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
function filtrarAud(){
  var q=_normAud(document.getElementById('aud-busca').value.trim());
  var rows=document.querySelectorAll('tr.aud-row');var vis=0;
  rows.forEach(function(r){
    var show=!q||_normAud(r.dataset.busca).indexOf(q)!==-1;
    r.style.display=show?'':'none';if(show)vis++;
  });
  document.getElementById('aud-contador').textContent='Mostrando '+vis+' de '+rows.length+' registro(s)';
  var v=document.getElementById('aud-vazio');if(v)v.style.display=vis===0?'block':'none';
}
document.addEventListener('DOMContentLoaded',filtrarAud);
</script>"""

    nota = _card("""
<p style="font-size:12px;color:#888;line-height:1.6;margin:0;">
  🔎 Registro interno das alterações feitas pela equipe (cadastros, edições, confirmações de
  relatório, vínculos de avaliação, visibilidade dos pais, etc.). Mostra as 500 ações mais recentes.
  Visível apenas para a administração.
</p>""")

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.png" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Auditoria</h1>
      <p style="font-size:12px;color:#888;">Histórico de alterações feitas pela equipe.</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {filtro_card}
  {tabela}
  {nota}
</div>
{script}"""
    return page_shell("Auditoria — Escola Espaço Alegre", body)
