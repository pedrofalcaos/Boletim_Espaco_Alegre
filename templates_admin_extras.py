"""Páginas extras do painel admin: professoras e temas avaliativos."""
from templates import page_shell, admin_nav

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
_ST_ICO = {"pendente":"🔴","em_andamento":"🟡","concluido":"🟢"}
_ST_LAB = {"pendente":"Não preenchido","em_andamento":"Em preenchimento","concluido":"Preenchido"}


# ── Utilitários ───────────────────────────────────────────────────────────────
def _msg_ok(texto: str) -> str:
    return f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:13px;color:#0a7c3e;font-weight:700;">✔ {texto}</div>'

def _msg_erro(texto: str) -> str:
    return f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:13px;color:#b52222;font-weight:700;">✖ {texto}</div>'

def _card(conteudo: str) -> str:
    return f'<div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:20px;box-shadow:0 2px 10px rgba(0,0,0,.07);">{conteudo}</div>'

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

def admin_professoras_page(professoras: list, alunos_por_prof: dict, msg: str = "", erro: str = "") -> str:
    """
    professoras: lista de dicts do db (id, username, nome, role, ativo)
    alunos_por_prof: {professora_nome: [lista de turmas]}
    """
    nav = admin_nav("professoras")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

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

    if professoras:
        cards = ""
        for p in professoras:
            pid = p["id"]
            conf_turmas = p.get("turmas") or []
            aluno_turmas = alunos_por_prof.get(p["nome"], [])
            chips = _turmas_chips(conf_turmas, aluno_turmas)
            checkboxes = _turma_checkboxes(conf_turmas, pid)

            cards += f"""
<div style="background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:12px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;">
    <div style="flex:1;">
      <div style="font-weight:800;color:#2b3990;font-size:14px;">{p["nome"]}</div>
      <div style="font-size:11px;color:#aaa;margin-top:2px;">{p["username"]}</div>
    </div>
    <button type="button" onclick="toggleTurmas({pid})"
      style="{_BTN_CINZA}font-size:11px;padding:5px 12px;">
      ✏️ Editar turmas
    </button>
    <form method="POST" action="/admin/professoras/{pid}/excluir"
          onsubmit="return confirm('Excluir {p["nome"]}? Os alunos não são apagados.');">
      <button type="submit" style="{_BTN_VM}">🗑</button>
    </form>
  </div>
  <div style="margin-top:10px;">{chips}</div>
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

    # Seleção de turmas para nova professora
    nova_checkboxes = _turma_checkboxes([], "nova")

    nova_card = _card(f"""
{_secao("➕ Nova Professora")}
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

    js_toggle = """
<script>
function toggleTurmas(id) {
  var el = document.getElementById('turmas-form-' + id);
  el.style.display = el.style.display === 'none' ? 'block' : 'none';
}
</script>"""

    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Professoras</h1>
      <p style="font-size:12px;color:#888;">{len(professoras)} professora(s) cadastrada(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {lista_card}
  {nova_card}
  {js_toggle}
</div>"""
    return page_shell("Professoras — Escola Espaço Alegre", body)


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
    <button type="submit" style="{_BTN_VM}">🗑 Excluir</button>
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
                lista_st += f"""
<div style="display:flex;align-items:center;gap:8px;padding:7px 0;border-bottom:.5px solid #f0f0ee;">
  <span style="flex:1;font-size:12px;color:#4a4a4a;">{i}. {st['descricao']}</span>
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
        onsubmit="return confirm('Excluir o tópico?');">
    <button type="submit" style="{_BTN_VM}">🗑 Excluir</button>
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
</p>""")

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:44px;object-fit:contain;">
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
    "pendente":     ("#b52222", "#fef2f2", "#fecaca", "🔴", "Pendente"),
    "em_andamento": ("#c25b0d", "#fef0e4", "#f8d4a8", "🟡", "Em andamento"),
    "concluido":    ("#0a7c3e", "#e3f5ec", "#a8ddc0", "🟢", "Concluído"),
}

def _pill_status(status: str, rel_id: int | None = None) -> str:
    cor, bg, bd, ico, label = _ST.get(status, _ST["pendente"])
    pill = (f'<span style="background:{bg};border:1px solid {bd};color:{cor};'
            f'font-size:10px;font-weight:800;padding:2px 10px;border-radius:20px;'
            f'white-space:nowrap;">{ico} {label}</span>')
    if rel_id:
        return f'<a href="/admin/relatorio/{rel_id}" style="text-decoration:none;">{pill}</a>'
    return pill


def admin_relatorios_page(
    rows: list,           # lista de dicts: nome, turma, professora, s1_status, s1_id, s2_status, s2_id
    turmas_disponiveis: list,
    filtros: dict,        # {turma, semestre, status}
    contadores: dict,     # {total, pendentes, andamento, concluidos}
    msg: str = "",
    erro: str = "",
) -> str:
    nav   = admin_nav("relatorios")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

    # ── Cards de resumo ──
    resumo = f"""
<div style="display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px;">
  <div style="background:#fff;border-radius:12px;padding:16px 18px;box-shadow:0 2px 8px rgba(0,0,0,.07);text-align:center;">
    <div style="font-size:28px;font-weight:900;color:#2b3990;">{contadores['total']}</div>
    <div style="font-size:11px;color:#aaa;font-weight:700;margin-top:2px;">Total de alunos</div>
  </div>
  <div style="background:#fef2f2;border:1px solid #fecaca;border-radius:12px;padding:16px 18px;text-align:center;">
    <div style="font-size:28px;font-weight:900;color:#b52222;">{contadores['pendentes']}</div>
    <div style="font-size:11px;color:#b52222;font-weight:700;margin-top:2px;">🔴 Pendentes</div>
  </div>
  <div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:12px;padding:16px 18px;text-align:center;">
    <div style="font-size:28px;font-weight:900;color:#c25b0d;">{contadores['andamento']}</div>
    <div style="font-size:11px;color:#c25b0d;font-weight:700;margin-top:2px;">🟡 Em andamento</div>
  </div>
  <div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:12px;padding:16px 18px;text-align:center;">
    <div style="font-size:28px;font-weight:900;color:#0a7c3e;">{contadores['concluidos']}</div>
    <div style="font-size:11px;color:#0a7c3e;font-weight:700;margin-top:2px;">🟢 Concluídos</div>
  </div>
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
                pill = _pill_status(r["s1_status"], r.get("s1_id"))
                imp  = f'<a href="/admin/relatorio/{r["s1_id"]}/imprimir" target="_blank" title="Imprimir" style="font-size:12px;margin-left:6px;">🖨️</a>' if r.get("s1_id") else ""
                td_s1 = f'<td style="padding:9px 12px;text-align:center;">{pill}{imp}</td>'
            if mostrar_s2:
                pill = _pill_status(r["s2_status"], r.get("s2_id"))
                imp  = f'<a href="/admin/relatorio/{r["s2_id"]}/imprimir" target="_blank" title="Imprimir" style="font-size:12px;margin-left:6px;">🖨️</a>' if r.get("s2_id") else ""
                td_s2 = f'<td style="padding:9px 12px;text-align:center;">{pill}{imp}</td>'

            linhas += f"""
<tr style="border-bottom:.5px solid #f0f0ee;">
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
    <img src="/static/logo.jpg" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Relatórios Semestrais</h1>
      <p style="font-size:12px;color:#888;">Ed. Infantil — {contadores['total']} aluno(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {resumo}
  {filtros_card}
  {tabela_html}
</div>"""
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
                f'font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;">🔴 Não preenchido</span>'
            )
            btn = (f'<a href="/admin/relatorio/novo/{matricula}/{sem}" '
                   f'style="background:#2b3990;color:#fff;font-family:\'Nunito\',sans-serif;'
                   f'font-weight:800;font-size:13px;padding:9px 20px;border-radius:9px;'
                   f'text-decoration:none;">✏️ Iniciar relatório</a>')
            impressao = ""
        else:
            s = rel.get("status", "pendente")
            cor, bg, bd = _ST_COR[s], _ST_BG[s], _ST_BD[s]
            status_html = (
                f'<span style="background:{bg};border:1px solid {bd};color:{cor};'
                f'font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;">'
                f'{_ST_ICO[s]} {_ST_LAB[s]}</span>'
            )
            btn = (f'<a href="/admin/relatorio/{rel["id"]}" '
                   f'style="background:#2b3990;color:#fff;font-family:\'Nunito\',sans-serif;'
                   f'font-weight:800;font-size:13px;padding:9px 20px;border-radius:9px;'
                   f'text-decoration:none;">✏️ Ver / Editar</a>')
            impressao = (f' &nbsp;<a href="/admin/relatorio/{rel["id"]}/imprimir" target="_blank"'
                         f' style="background:#e8eaf8;color:#2b3990;font-family:\'Nunito\',sans-serif;'
                         f'font-weight:800;font-size:13px;padding:9px 18px;border-radius:9px;'
                         f'text-decoration:none;">🖨️ Imprimir</a>')

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
    📋 Relatórios Semestrais
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

    # ── Subtemas por tema ──
    if not temas:
        subtemas_html = """
<div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:12px;padding:20px;
            color:#c25b0d;font-size:13px;font-weight:700;text-align:center;">
  ⚠️ Nenhum tema cadastrado para esta turma.<br>
  <span style="font-size:11px;font-weight:600;">Acesse <strong>Temas Avaliativos</strong> no menu para configurar.</span>
</div>"""
    else:
        secoes = ""
        for tema in temas:
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
    🏷️ {tema['nome']}
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
