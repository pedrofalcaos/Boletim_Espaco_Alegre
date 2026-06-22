"""Formulário de preenchimento e visualização do Relatório Semestral da Ed. Infantil."""
from templates import page_shell

_OPCOES = ["CA", "CC", "ED"]

_LEGENDA = {
    "CA": "Com Autonomia",
    "CC": "Com Colaboração",
    "ED": "Em Desenvolvimento",
}

_COR_OPCAO = {
    "CA": ("#0a7c3e", "#e3f5ec", "#a8ddc0"),
    "CC": ("#2b3990", "#e8eaf8", "#b0b8e8"),
    "ED": ("#c25b0d", "#fef0e4", "#f8d4a8"),
}

_STATUS_LABEL = {
    "pendente":     ("🔴", "#b52222", "#fef2f2", "Pendente"),
    "em_andamento": ("🟡", "#c25b0d", "#fef0e4", "Em andamento"),
    "concluido":    ("🟢", "#0a7c3e", "#e3f5ec", "Concluído"),
}


def _badge_status(status: str) -> str:
    ico, cor, bg, label = _STATUS_LABEL.get(status, _STATUS_LABEL["pendente"])
    return (f'<span style="background:{bg};color:{cor};font-size:11px;font-weight:800;'
            f'padding:3px 12px;border-radius:20px;border:1px solid {cor}30;">'
            f'{ico} {label}</span>')


def _badge_resposta(resp: str) -> str:
    if not resp:
        return '<span style="color:#ccc;font-size:12px;">— não respondido</span>'
    cor, bg, borda = _COR_OPCAO.get(resp, ("#888", "#f5f5f5", "#ddd"))
    label = _LEGENDA.get(resp, resp)
    return (f'<span style="background:{bg};color:{cor};border:1px solid {borda};'
            f'font-size:12px;font-weight:800;padding:3px 12px;border-radius:20px;">'
            f'{resp} — {label}</span>')


# ════════════════════════════════════════════════════════════════════════
#  FORMULÁRIO PRINCIPAL
# ════════════════════════════════════════════════════════════════════════

def relatorio_form_page(
    user: dict,
    aluno: dict,
    matricula: str,
    semestre: int,
    relatorio: dict,
    temas: list,
    respostas: dict,     # {subtema_id: resposta_str}
    msg: str = "",
    erro: str = "",
    form_prefix: str = None,   # ex: "/admin/relatorio/42" para rotas do admin
) -> str:
    nome_aluno   = aluno.get("nome", "")
    turma        = aluno.get("turma", "")
    periodo      = aluno.get("periodo", "")
    ano          = aluno.get("ano_letivo", "2026")
    status       = relatorio.get("status", "pendente")
    descricao    = relatorio.get("descricao_final", "")
    rel_id       = relatorio.get("id")
    trancado     = bool(relatorio.get("trancado"))
    sem_label    = "1º Semestre" if semestre == 1 else "2º Semestre"

    is_staff     = user.get("role") in ("admin", "coordenacao")
    is_readonly  = (status == "concluido" or trancado) and not is_staff
    nome_prof    = user.get("nome", "")
    editado_por  = relatorio.get("editado_por_nome", "")
    atualizado_em = relatorio.get("atualizado_em", "")
    prefix       = form_prefix or f"/professora/relatorio/{matricula}/{semestre}"

    # temas é agora lista de tópicos: [{id, nome, temas:[{id, nome, subtemas:[...]}]}]
    total_subtemas = sum(
        len(t.get("subtemas", []))
        for tp in temas for t in tp.get("temas", [])
    )
    respondidos    = sum(1 for sid in respostas if respostas[sid])
    pct            = int(respondidos / total_subtemas * 100) if total_subtemas else 0

    # ── Mensagens ──
    aviso = ""
    if msg:
        aviso = f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:18px;font-size:13px;color:#0a7c3e;font-weight:700;">✔ {msg}</div>'
    elif erro:
        aviso = f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:11px 16px;margin-bottom:18px;font-size:13px;color:#b52222;font-weight:700;">✖ {erro}</div>'

    # ── Legenda de avaliação ──
    legenda_html = """
<div style="background:#fff;border-radius:12px;padding:14px 20px;margin-bottom:16px;
            box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
  <span style="font-size:11px;font-weight:800;color:#aaa;text-transform:uppercase;
               letter-spacing:.5px;white-space:nowrap;margin-right:4px;">Legenda:</span>
  <span style="background:#e3f5ec;color:#0a7c3e;border:1px solid #a8ddc0;
               font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;white-space:nowrap;">
    CA — Com Autonomia
  </span>
  <span style="background:#e8eaf8;color:#2b3990;border:1px solid #b0b8e8;
               font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;white-space:nowrap;">
    CC — Com Colaboração
  </span>
  <span style="background:#fef0e4;color:#c25b0d;border:1px solid #f8d4a8;
               font-size:12px;font-weight:800;padding:4px 14px;border-radius:20px;white-space:nowrap;">
    ED — Em Desenvolvimento
  </span>
</div>"""

    # ── Barra de progresso ──
    cor_barra = "#0a7c3e" if pct == 100 else ("#c25b0d" if pct > 0 else "#dcdcd8")
    barra_html = f"""
<div style="background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.07);">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
    <span style="font-family:'Fredoka One',cursive;font-size:14px;color:#2b3990;">Progresso de preenchimento</span>
    <span style="font-size:13px;font-weight:800;color:{cor_barra};">{respondidos} / {total_subtemas} subtemas</span>
  </div>
  <div style="background:#f0f0ee;border-radius:8px;height:12px;overflow:hidden;">
    <div id="barra-prog" style="height:100%;width:{pct}%;background:{cor_barra};border-radius:8px;transition:width .4s;"></div>
  </div>
  <div style="display:flex;justify-content:space-between;margin-top:6px;">
    <span style="font-size:11px;color:#aaa;" id="txt-prog">{pct}% concluído</span>
    {"<span style='font-size:11px;color:#0a7c3e;font-weight:700;'>✔ Todos os subtemas respondidos!</span>" if pct == 100 else ""}
  </div>
</div>"""

    # ── Campo de observações — sempre visível ──
    if is_readonly:
        obs_html = f"""
<div style="background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;
              margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #f7d800;">
    📝 Observações Pedagógicas
  </div>
  <div style="font-size:13px;color:#4a4a4a;line-height:1.7;">{descricao or '—'}</div>
</div>"""
    else:
        _TB_BTN = ("font-family:'Nunito',sans-serif;background:#fff;border:1px solid #dcdcd8;"
                   "border-radius:6px;padding:5px 9px;cursor:pointer;font-size:13px;color:#444;"
                   "min-width:30px;line-height:1;")
        toolbar = f"""
<div style="display:flex;gap:5px;flex-wrap:wrap;align-items:center;background:#f7f7f5;
            border:1.5px solid #dcdcd8;border-bottom:none;border-radius:9px 9px 0 0;padding:7px 9px;">
  <button type="button" title="Negrito" style="{_TB_BTN}font-weight:900;"
    onmousedown="event.preventDefault()" onclick="fmtDoc('bold')">B</button>
  <button type="button" title="Itálico" style="{_TB_BTN}font-style:italic;"
    onmousedown="event.preventDefault()" onclick="fmtDoc('italic')">I</button>
  <button type="button" title="Sublinhado" style="{_TB_BTN}text-decoration:underline;"
    onmousedown="event.preventDefault()" onclick="fmtDoc('underline')">U</button>
  <input type="color" title="Cor do texto" value="#2b3990"
    style="width:30px;height:30px;border:1px solid #dcdcd8;border-radius:6px;padding:2px;cursor:pointer;"
    onmousedown="saveSel()" onchange="fmtDoc('foreColor', this.value)">
  <span style="width:1px;height:22px;background:#dcdcd8;margin:0 2px;"></span>
  <button type="button" title="Justificar" style="{_TB_BTN}"
    onmousedown="event.preventDefault()" onclick="fmtDoc('justifyFull')">≡</button>
  <button type="button" title="Lista numerada" style="{_TB_BTN}"
    onmousedown="event.preventDefault()" onclick="fmtDoc('insertOrderedList')">1.</button>
  <button type="button" title="Lista com marcadores" style="{_TB_BTN}"
    onmousedown="event.preventDefault()" onclick="fmtDoc('insertUnorderedList')">•≡</button>
  <span style="width:1px;height:22px;background:#dcdcd8;margin:0 2px;"></span>
  <button type="button" title="Inserir link" style="{_TB_BTN}"
    onmousedown="event.preventDefault()" onclick="fmtLink()">🔗</button>
  <button type="button" title="Inserir imagem" style="{_TB_BTN}"
    onmousedown="event.preventDefault()" onclick="fmtImagem()">🖼️</button>
</div>"""
        _editor_style = ("width:100%;min-height:140px;font-family:'Nunito',sans-serif;font-size:13px;"
                          "color:#4a4a4a;padding:12px 14px;border:1.5px solid #dcdcd8;"
                          "border-radius:0 0 9px 9px;outline:none;line-height:1.6;overflow-y:auto;")
        obs_html = f"""
<div style="background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:18px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;
              margin-bottom:10px;padding-bottom:8px;border-bottom:2px solid #f7d800;">
    📝 Observações Pedagógicas
    <span style="font-size:10px;font-weight:700;color:#aaa;margin-left:8px;">obrigatória para confirmar</span>
  </div>
  {toolbar}
  <div id="descricao_editor" contenteditable="true"
    data-placeholder="Descreva o desenvolvimento do aluno: pontos fortes, áreas a desenvolver, comportamento, socialização, conquistas do semestre..."
    style="{_editor_style}"
    oninput="syncDescricao()"
    onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#dcdcd8'">{descricao}</div>
  <textarea id="descricao_final" name="descricao_final" style="display:none;">{descricao}</textarea>
</div>"""

    _btn_salvar = """
<button type="submit"
  style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
         background:#f7f7f5;color:#2b3990;border:2px solid #2b3990;
         border-radius:10px;padding:12px 28px;cursor:pointer;">
  💾 Salvar Rascunho
</button>"""

    # ── Rodapé interno: quem editou por último (visível só para admin/coordenação) ──
    footer_editor_html = ""
    if is_staff and editado_por:
        quando = ""
        if atualizado_em:
            try:
                from datetime import datetime as _dt
                dt = atualizado_em if hasattr(atualizado_em, "strftime") else _dt.fromisoformat(str(atualizado_em))
                quando = f" em {dt.strftime('%d/%m/%Y às %H:%M')}"
            except (ValueError, TypeError):
                quando = ""
        footer_editor_html = f"""
<div style="margin-top:18px;padding-top:12px;border-top:1px solid #f0f0ee;text-align:right;">
  <span style="font-size:11px;color:#aaa;font-style:italic;">
    🖊️ Última edição por <b>{editado_por}</b>{quando}
  </span>
</div>"""

    # ── Sem temas configurados ──
    if not temas:
        aviso_temas = """
<div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:12px;padding:18px;
            margin-bottom:16px;color:#c25b0d;font-size:13px;font-weight:700;">
  ⚠️ Nenhum tema avaliativo configurado para esta turma ainda.<br>
  <span style="font-size:11px;font-weight:600;">O administrador precisa cadastrar os temas e configurar as turmas.</span>
</div>"""
        if is_readonly:
            corpo  = aviso_temas
            botoes = ""
        else:
            corpo  = f'<form id="frm-relatorio" method="POST" action="{prefix}/salvar">\n{aviso_temas}'
            botoes = f'<div style="display:flex;gap:12px;padding-bottom:32px;">{_btn_salvar}</div>\n</form>'
    elif is_readonly:
        # ── Modo leitura (concluido + professora) ──
        corpo  = _render_readonly(temas, respostas)
        botoes = ""
    else:
        corpo, botoes = _render_form(prefix, temas, respostas, status, is_staff)

    # ── Banner read-only ──
    banner_concluido = ""
    if trancado and not is_staff:
        banner_concluido = """
<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:10px;padding:12px 18px;
            margin-bottom:18px;display:flex;align-items:center;gap:10px;">
  <span style="font-size:20px;">🔒</span>
  <div>
    <div style="font-weight:800;color:#b52222;font-size:13px;">Relatório trancado pelo administrador</div>
    <div style="font-size:11px;color:#c25b5b;">Este relatório está temporariamente bloqueado para edição. Fale com a administração caso precise alterá-lo.</div>
  </div>
</div>"""
    elif is_readonly:
        banner_concluido = """
<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:12px 18px;
            margin-bottom:18px;display:flex;align-items:center;gap:10px;">
  <span style="font-size:20px;">🟢</span>
  <div>
    <div style="font-weight:800;color:#0a7c3e;font-size:13px;">Relatório confirmado</div>
    <div style="font-size:11px;color:#5a9a74;">Este relatório foi confirmado e não pode mais ser editado pela professora.</div>
  </div>
</div>"""
    elif is_staff and status == "concluido":
        banner_concluido = """
<div style="background:#e8eaf8;border:1px solid #b0b8e8;border-radius:10px;padding:12px 18px;
            margin-bottom:18px;display:flex;align-items:center;gap:10px;">
  <span style="font-size:20px;">🔧</span>
  <div>
    <div style="font-weight:800;color:#2b3990;font-size:13px;">Modo administração — edição após confirmação</div>
    <div style="font-size:11px;color:#666;">Como admin/coordenação, você pode editar mesmo após a confirmação.</div>
  </div>
</div>"""

    # ── Reabrir relatório concluído (admin e coordenação) ──
    reabrir_html = ""
    if is_staff and rel_id and status == "concluido":
        reabrir_html = f"""
<form method="POST" action="/admin/relatorio/{rel_id}/reabrir" style="display:inline;"
      onsubmit="return confirm('Reabrir este relatório para a professora preencher novamente?\\n\\nO status voltará para \\'Em andamento\\' e ela poderá editar as respostas.');">
  <button type="submit"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
           background:#fffbe6;color:#a67c00;border:1.5px solid #f7d800;
           border-radius:9px;padding:8px 14px;cursor:pointer;white-space:nowrap;">
    🔄 Liberar para a professora preencher novamente
  </button>
</form>"""

    # ── Controle de trava (admin e coordenação) ──
    trava_html = ""
    if is_staff and rel_id:
        if trancado:
            trava_html = f"""
<form method="POST" action="/admin/relatorio/{rel_id}/destrancar" style="display:inline;">
  <button type="submit"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
           background:#fef2f2;color:#b52222;border:1.5px solid #fecaca;
           border-radius:9px;padding:8px 14px;cursor:pointer;white-space:nowrap;">
    🔓 Destrancar relatório
  </button>
</form>"""
        else:
            trava_html = f"""
<form method="POST" action="/admin/relatorio/{rel_id}/trancar" style="display:inline;"
      onsubmit="return confirm('Trancar este relatório? A professora não poderá mais editá-lo até você destrancar.');">
  <button type="submit"
    style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:800;
           background:#f7f7f5;color:#2b3990;border:1.5px solid #b0b8e8;
           border-radius:9px;padding:8px 14px;cursor:pointer;white-space:nowrap;">
    🔒 Trancar relatório
  </button>
</form>"""

    back_url = "/professora" if not is_staff else "/admin/relatorios"
    back_label = "← Minhas Turmas" if not is_staff else "← Relatórios"

    body = f"""
<div style="max-width:820px;margin:0 auto;padding:24px 16px;">

  <!-- Header -->
  <div style="display:flex;align-items:flex-start;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="{back_url}"
       style="background:#e8eaf8;color:#2b3990;font-family:'Nunito',sans-serif;font-weight:800;
              font-size:12px;padding:8px 14px;border-radius:8px;white-space:nowrap;margin-top:2px;">
      {back_label}
    </a>
    <div style="flex:1;min-width:200px;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:19px;color:#2b3990;line-height:1.2;">
        {nome_aluno}
      </h1>
      <div style="font-size:12px;color:#aaa;margin-top:3px;">
        {turma} &nbsp;·&nbsp; {periodo} &nbsp;·&nbsp; {sem_label} &nbsp;·&nbsp; {ano}
        {"&nbsp;·&nbsp; Profª " + nome_prof if not is_staff else ""}
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
      {_badge_status(status)}
      {reabrir_html}
      {trava_html}
      <a href="/{'admin/logout' if is_staff else 'professora/logout'}"
         style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;
                font-size:12px;padding:8px 14px;border-radius:9px;border:1px solid #dcdcd8;">
        Sair
      </a>
    </div>
  </div>

  {aviso}
  {banner_concluido}
  {legenda_html}
  {barra_html if not is_readonly else ""}
  {corpo}
  {obs_html}
  {botoes}
  {footer_editor_html}

</div>

<script>
var total = {total_subtemas};
function updateProgress() {{
  if (total === 0) return;
  var names = {{}};
  document.querySelectorAll('input[type=radio]').forEach(function(r) {{ names[r.name] = true; }});
  var totalGrupos = Object.keys(names).filter(function(n){{return n.startsWith('resposta_');}}).length;
  var respondidos = 0;
  Object.keys(names).filter(function(n){{return n.startsWith('resposta_');}}).forEach(function(n) {{
    if (document.querySelector('input[name="'+n+'"]:checked')) respondidos++;
  }});
  var pct = totalGrupos > 0 ? Math.round(respondidos / totalGrupos * 100) : 0;
  var barra = document.getElementById('barra-prog');
  var txt   = document.getElementById('txt-prog');
  var cor   = pct === 100 ? '#0a7c3e' : (pct > 0 ? '#c25b0d' : '#dcdcd8');
  if (barra) {{ barra.style.width = pct + '%'; barra.style.background = cor; }}
  if (txt)   {{ txt.textContent = pct + '% concluído'; txt.style.color = cor; }}
}}
document.addEventListener('DOMContentLoaded', function() {{
  document.querySelectorAll('input[type=radio]').forEach(function(r) {{
    r.addEventListener('change', updateProgress);
  }});
  updateProgress();
  var frmEl = document.getElementById('frm-relatorio');
  if (frmEl) {{ frmEl.addEventListener('submit', function() {{ syncDescricao(); }}); }}
}});
var _savedSel = null;
function saveSel() {{
  var sel = window.getSelection();
  if (sel && sel.rangeCount > 0) {{ _savedSel = sel.getRangeAt(0); }}
}}
function fmtDoc(cmd, value) {{
  var ed = document.getElementById('descricao_editor');
  if (!ed) return;
  ed.focus();
  if (_savedSel) {{
    var sel = window.getSelection();
    sel.removeAllRanges();
    sel.addRange(_savedSel);
  }}
  document.execCommand(cmd, false, value || null);
  syncDescricao();
}}
function fmtLink() {{
  var url = prompt('Endereço do link (https://...)');
  if (url) {{ fmtDoc('createLink', url); }}
}}
function fmtImagem() {{
  var url = prompt('Endereço da imagem (https://...)');
  if (url) {{ fmtDoc('insertImage', url); }}
}}
function syncDescricao() {{
  var ed = document.getElementById('descricao_editor');
  var hid = document.getElementById('descricao_final');
  if (ed && hid) {{ hid.value = ed.innerHTML; }}
}}
function confirmar() {{
  // Valida no client antes de submeter
  var names = {{}};
  document.querySelectorAll('input[type=radio]').forEach(function(r) {{ names[r.name] = true; }});
  var grupos = Object.keys(names).filter(function(n){{return n.startsWith('resposta_');}});
  var naoRespondidos = grupos.filter(function(n) {{
    return !document.querySelector('input[name="'+n+'"]:checked');
  }});
  if (naoRespondidos.length > 0) {{
    alert('Por favor, responda todos os ' + grupos.length + ' subtemas antes de confirmar. Faltam ' + naoRespondidos.length + '.');
    return;
  }}
  syncDescricao();
  var desc = document.getElementById('descricao_final');
  if (desc) {{
    var textoPuro = desc.value.replace(/<[^>]*>/g, '').trim();
    if (textoPuro.length < 10) {{
      alert('A descrição final deve ter pelo menos 10 caracteres.');
      var ed = document.getElementById('descricao_editor');
      if (ed) ed.focus();
      return;
    }}
  }}
  if (!confirm('Confirmar o relatório de {nome_aluno}?\\n\\nApós confirmar, você não poderá mais editar.')) return;
  var frm = document.getElementById('frm-relatorio');
  frm.action = '{prefix}/confirmar';
  frm.submit();
}}
</script>"""
    return page_shell(f"Relatório — {nome_aluno} — {sem_label}", body)


# ── Modo leitura ──────────────────────────────────────────────────────────────

def _render_readonly(temas: list, respostas: dict) -> str:
    """Renderiza Tópico→Tema→Subtema em modo leitura. temas é lista de tópicos."""
    secoes = ""
    for topico in temas:
        temas_html = ""
        for tema in topico.get("temas", []):
            linhas = ""
            for st in tema.get("subtemas", []):
                resp = respostas.get(st["id"], "")
                linhas += f"""
<div style="display:flex;align-items:center;gap:12px;padding:9px 0;border-bottom:.5px solid #f5f5f5;">
  <span style="flex:1;font-size:13px;color:#4a4a4a;">{st['descricao']}</span>
  {_badge_resposta(resp)}
</div>"""
            temas_html += f"""
<div style="margin-bottom:10px;border-left:3px solid #f7d800;padding-left:12px;">
  <div style="font-family:'Fredoka One',cursive;font-size:13px;color:#2b3990;margin-bottom:6px;">
    🏷️ {tema['nome']}
  </div>
  {linhas}
</div>"""
        secoes += f"""
<div style="background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:16px;color:#2b3990;
              margin-bottom:14px;padding-bottom:8px;border-bottom:3px solid #f7d800;">
    📂 {topico['nome']}
  </div>
  {temas_html}
</div>"""
    return secoes


# ── Modo edição ───────────────────────────────────────────────────────────────

def _render_form(prefix, temas, respostas, status, is_staff):
    """temas é lista de tópicos: [{id, nome, temas:[{id, nome, subtemas:[...]}]}]"""
    _INP_RD = ("position:absolute;opacity:0;width:0;height:0;")

    def _opcao(subtema_id: int, valor: str, resp_atual: str) -> str:
        checked = "checked" if resp_atual == valor else ""
        cor, bg, borda = _COR_OPCAO[valor]
        nome_campo = f"resposta_{subtema_id}"
        base = (f"display:inline-block;font-size:12px;font-weight:800;padding:6px 14px;"
                f"border-radius:20px;cursor:pointer;border:2px solid;transition:all .15s;"
                f"border-color:{borda};background:#f9f9f9;color:#aaa;")
        ativo = (f"display:inline-block;font-size:12px;font-weight:800;padding:6px 14px;"
                 f"border-radius:20px;cursor:pointer;border:2px solid;transition:all .15s;"
                 f"border-color:{cor};background:{bg};color:{cor};")
        span_id = f"pill_{subtema_id}_{valor.replace(' ','_')}"
        titulo  = _LEGENDA.get(valor, valor)
        return f"""<label style="cursor:pointer;" title="{titulo}">
  <input type="radio" name="{nome_campo}" value="{valor}" {checked}
         style="{_INP_RD}"
         onchange="updatePills({subtema_id}); updateProgress();">
  <span id="{span_id}" style="{ativo if checked else base}">{valor}</span>
</label>"""

    secoes = ""
    for topico in temas:
        temas_html = ""
        for tema in topico.get("temas", []):
            linhas = ""
            for st in tema.get("subtemas", []):
                sid = st["id"]
                resp_atual = respostas.get(sid, "")
                opcoes_html = "".join(_opcao(sid, v, resp_atual) for v in _OPCOES)
                linhas += f"""
<div style="padding:10px 0;border-bottom:.5px solid #f5f5f5;">
  <div style="font-size:13px;color:#4a4a4a;margin-bottom:8px;font-weight:600;">{st['descricao']}</div>
  <div style="display:flex;gap:8px;flex-wrap:wrap;">{opcoes_html}</div>
</div>"""
            temas_html += f"""
<div style="margin-bottom:10px;border-left:3px solid #f7d800;padding-left:12px;">
  <div style="font-family:'Fredoka One',cursive;font-size:13px;color:#2b3990;margin-bottom:6px;">
    🏷️ {tema['nome']}
  </div>
  {linhas}
</div>"""

        secoes += f"""
<div style="background:#fff;border-radius:12px;padding:18px 22px;margin-bottom:14px;box-shadow:0 2px 8px rgba(0,0,0,.06);">
  <div style="font-family:'Fredoka One',cursive;font-size:16px;color:#2b3990;
              margin-bottom:14px;padding-bottom:8px;border-bottom:3px solid #f7d800;">
    📂 {topico['nome']}
  </div>
  {temas_html}
</div>"""

    form_html = f"""<form id="frm-relatorio" method="POST" action="{prefix}/salvar">
{secoes}"""

    botoes = f"""
<div style="display:flex;gap:12px;flex-wrap:wrap;padding-bottom:32px;">
  <button type="submit"
    style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
           background:#f7f7f5;color:#2b3990;border:2px solid #2b3990;
           border-radius:10px;padding:12px 28px;cursor:pointer;">
    💾 Salvar Rascunho
  </button>
  {"" if not is_staff and status == "concluido" else f'''
  <button type="button" onclick="confirmar()"
    style="font-family:\'Nunito\',sans-serif;font-size:14px;font-weight:900;
           background:#2b3990;color:#fff;border:none;
           border-radius:10px;padding:12px 28px;cursor:pointer;">
    ✅ {"Atualizar e Confirmar" if status == "concluido" else "Confirmar Relatório"}
  </button>'''}
</div>
</form>"""

    ids_subtemas = [st["id"] for tp in temas for t in tp.get("temas", []) for st in t.get("subtemas", [])]
    pill_js_vals = '["' + '","'.join(_OPCOES) + '"]'
    pill_js = f"""
<script>
var _opcoes = {pill_js_vals};
var _corAtivo = {{"CA":"#0a7c3e","CC":"#2b3990","ED":"#c25b0d"}};
var _bgAtivo  = {{"CA":"#e3f5ec","CC":"#e8eaf8","ED":"#fef0e4"}};
var _bdAtivo  = {{"CA":"#a8ddc0","CC":"#b0b8e8","ED":"#f8d4a8"}};
function updatePills(sid) {{
  _opcoes.forEach(function(v) {{
    var key = v.replace(/ /g,'_');
    var el  = document.getElementById('pill_' + sid + '_' + key);
    var inp = document.querySelector('input[name="resposta_'+sid+'"][value="'+v+'"]:checked');
    if (!el) return;
    if (inp) {{
      el.style.background    = _bgAtivo[v];
      el.style.color         = _corAtivo[v];
      el.style.borderColor   = _bdAtivo[v];
    }} else {{
      el.style.background    = '#f9f9f9';
      el.style.color         = '#aaa';
      el.style.borderColor   = '#ddd';
    }}
  }});
}}
document.addEventListener('DOMContentLoaded', function() {{
  var ids = [{','.join(str(i) for i in ids_subtemas)}];
  ids.forEach(function(sid) {{ updatePills(sid); }});
}});
</script>"""

    return form_html + pill_js, botoes
