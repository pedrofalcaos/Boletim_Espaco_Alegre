"""Páginas extras do painel admin: professoras e temas avaliativos."""
from templates import page_shell, admin_nav


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

    if professoras:
        rows = ""
        for p in professoras:
            turmas = alunos_por_prof.get(p["nome"], [])
            turmas_html = " ".join(
                f'<span style="background:#e8eaf8;color:#2b3990;font-size:10px;font-weight:800;padding:2px 9px;border-radius:20px;">{t}</span>'
                for t in turmas
            ) or '<span style="color:#ccc;font-size:12px;">nenhuma turma vinculada</span>'

            rows += f"""
<tr style="border-bottom:.5px solid #dcdcd8;">
  <td style="padding:10px 14px;font-weight:800;color:#2b3990;">{p["nome"]}</td>
  <td style="padding:10px 14px;font-size:12px;color:#888;">{p["username"]}</td>
  <td style="padding:10px 14px;">{turmas_html}</td>
  <td style="padding:10px 14px;text-align:center;">
    <form method="POST" action="/admin/professoras/{p['id']}/excluir"
          onsubmit="return confirm('Excluir {p['nome']}? Isso não apaga os alunos.');">
      <button type="submit" style="{_BTN_VM}">🗑 Excluir</button>
    </form>
  </td>
</tr>"""

        tabela = f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 14px;text-align:left;">Nome</th>
      <th style="padding:9px 14px;text-align:left;">Usuário</th>
      <th style="padding:9px 14px;text-align:left;">Turmas vinculadas</th>
      <th style="padding:9px 14px;text-align:center;">Ação</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>"""
    else:
        tabela = '<p style="color:#aaa;font-size:13px;text-align:center;padding:20px 0;">Nenhuma professora cadastrada ainda.</p>'

    lista_card = _card(_secao("👩‍🏫 Professoras cadastradas") + tabela)

    nova_card = _card(f"""
{_secao("➕ Nova Professora")}
<form method="POST" action="/admin/professoras/nova">
  <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px;margin-bottom:14px;">
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome completo</label>
      <input name="nome" required placeholder="Ex: Maria Luiza" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Usuário de login</label>
      <input name="username" required placeholder="Ex: maria.luiza" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
    <div>
      <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Senha inicial</label>
      <input name="senha" type="password" required placeholder="Mínimo 6 caracteres" style="{_INP}"
        onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    </div>
  </div>
  <div style="font-size:11px;color:#aaa;margin-bottom:14px;">
    💡 O nome deve ser idêntico ao campo <strong>Professor(a)</strong> cadastrado nos alunos para que o vínculo funcione.
  </div>
  <button type="submit" style="{_BTN_AZ}">Cadastrar professora →</button>
</form>""")

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


def admin_temas_page(temas: list, msg: str = "", erro: str = "") -> str:
    nav   = admin_nav("temas")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")
    total_subtemas = sum(len(t.get("subtemas", [])) for t in temas)

    # ── Cabeçalho das colunas (turmas) ──
    th_turmas = "".join(
        f'<th style="padding:6px 4px;text-align:center;font-size:10px;font-weight:800;'
        f'color:#2b3990;white-space:nowrap;min-width:32px;">{label}</th>'
        for _, label in _TURMAS_INF
    )

    temas_html = ""
    for tema in temas:
        subtemas = tema.get("subtemas", [])

        # ── Edição do nome do tema ──
        form_nome = f"""
<div style="display:flex;gap:8px;margin-bottom:14px;align-items:center;">
  <form method="POST" action="/admin/temas/{tema['id']}/editar"
        style="display:flex;gap:8px;flex:1;">
    <input name="nome" value="{tema['nome']}" required
           style="{_INP}flex:1;font-size:15px;font-weight:800;color:#2b3990;"
           onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
    <button type="submit" style="{_BTN_AZ}padding:9px 14px;font-size:12px;">Salvar nome</button>
  </form>
  <form method="POST" action="/admin/temas/{tema['id']}/excluir"
        onsubmit="return confirm('Excluir o tema e todos os subtemas?');">
    <button type="submit" style="{_BTN_VM}padding:9px 12px;">🗑</button>
  </form>
</div>"""

        if not subtemas:
            corpo_matrix = '<p style="color:#ccc;font-size:12px;padding:8px 0 4px;">Nenhum subtema ainda.</p>'
            form_salvar  = ""
        else:
            # ── Matrix: linhas=subtemas, colunas=turmas ──
            linhas = ""
            for i, st in enumerate(subtemas, 1):
                turmas_conf = st.get("turmas", [])
                todas = not turmas_conf  # lista vazia = todas as turmas

                cells = "".join(
                    f'<td style="text-align:center;padding:4px 2px;">'
                    f'<input type="checkbox" name="st_{st["id"]}" value="{turma}"'
                    f'{"checked" if todas or turma in turmas_conf else ""}>'
                    f'</td>'
                    for turma, _ in _TURMAS_INF
                )

                # pré-computa id para evitar backslash dentro de {}
                sid = st["id"]

                btn_todas = (
                    f'<button type="button" onclick="toggleAll(this,\'st_{sid}\')"'
                    f' style="font-size:10px;font-weight:800;background:#e8eaf8;color:#2b3990;'
                    f'border:none;border-radius:5px;padding:3px 7px;cursor:pointer;white-space:nowrap;"'
                    f' title="Marcar/desmarcar todas as turmas">±</button>'
                )

                del_form = (
                    f'<form id="del-st-{sid}" method="POST"'
                    f' action="/admin/subtemas/{sid}/excluir" style="display:none;"></form>'
                    f'<button type="button"'
                    f' onclick="if(confirm(\'Excluir subtema?\'))document.getElementById(\'del-st-{sid}\').submit()"'
                    f' style="{_BTN_VM}padding:3px 8px;">✕</button>'
                )

                linhas += f"""
<tr style="border-bottom:.5px solid #f5f5f5;">
  <td style="padding:7px 10px;font-size:12px;color:#4a4a4a;font-weight:600;">{i}. {st['descricao']}</td>
  {cells}
  <td style="text-align:center;padding:4px 6px;">{btn_todas}</td>
  <td style="text-align:center;padding:4px 6px;">{del_form}</td>
</tr>"""

            corpo_matrix = f"""
<div style="overflow-x:auto;margin-bottom:10px;">
<table style="width:100%;border-collapse:collapse;font-size:12px;">
  <thead>
    <tr style="background:#f7f7f5;">
      <th style="padding:8px 10px;text-align:left;font-size:10px;font-weight:800;
                 text-transform:uppercase;letter-spacing:.4px;color:#aaa;min-width:200px;">Subtema</th>
      {th_turmas}
      <th style="padding:6px 6px;font-size:10px;color:#aaa;text-align:center;white-space:nowrap;">±All</th>
      <th style="padding:6px 6px;font-size:10px;color:#aaa;text-align:center;">Del</th>
    </tr>
  </thead>
  <tbody>{linhas}</tbody>
</table>
</div>"""

            form_salvar = f"""
<button type="submit"
   style="{_BTN_AZ}padding:8px 20px;font-size:12px;margin-bottom:4px;">
  💾 Salvar turmas desta configuração
</button>
<p style="font-size:10px;color:#aaa;margin-top:4px;">
  ✔ Marcado = subtema avaliado naquela turma &nbsp;|&nbsp;
  Se nenhuma turma marcada, o subtema não aparecerá para nenhuma professora.
</p>"""

        # ── Form de novo subtema ──
        form_novo_st = f"""
<div style="margin-top:14px;border-top:.5px solid #f0f0ee;padding-top:12px;">
<form method="POST" action="/admin/temas/{tema['id']}/subtema"
      style="display:flex;gap:8px;">
  <input name="descricao" required placeholder="Novo subtema..."
         style="{_INP}flex:1;"
         onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  <button type="submit" style="{_BTN_AZ}padding:9px 16px;">+ Adicionar</button>
</form>
</div>"""

        badge = (f'<span style="background:#e8eaf8;color:#2b3990;font-size:11px;font-weight:800;'
                 f'padding:2px 10px;border-radius:20px;">{len(subtemas)} subtema(s)</span>')

        # Formulário principal da matrix POST para /admin/temas/{id}/turmas
        form_open  = f'<form method="POST" action="/admin/temas/{tema["id"]}/turmas">'
        form_close = "</form>"

        temas_html += _card(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;
            border-bottom:2px solid #f7d800;padding-bottom:8px;">
  <span style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;flex:1;">🏷️ Tema</span>
  {badge}
</div>
{form_nome}
{form_open}
{corpo_matrix}
{form_salvar}
{form_close}
{form_novo_st}""")

    if not temas_html:
        temas_html = _card('<p style="color:#aaa;text-align:center;padding:20px 0;">Nenhum tema cadastrado ainda.</p>')

    # ── Form novo tema ──
    novo_tema_card = _card(f"""
{_secao("➕ Novo Tema Principal")}
<form method="POST" action="/admin/temas/novo" style="display:flex;gap:10px;align-items:flex-end;">
  <div style="flex:1;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;
                  color:#aaa;display:block;margin-bottom:4px;">Nome do tema</label>
    <input name="nome" required placeholder="Ex: O eu, o outro e o nós" style="{_INP}"
      onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  </div>
  <button type="submit" style="{_BTN_AZ}">Criar tema →</button>
</form>
<p style="font-size:11px;color:#aaa;margin-top:10px;">
  Após criar o tema, adicione os subtemas e configure quais turmas cada um avalia.
</p>""")

    # JS para o botão ± (marcar/desmarcar todas da linha)
    js = """
<script>
function toggleAll(btn, name) {
  var boxes = document.querySelectorAll('input[name="' + name + '"]');
  var allChecked = Array.from(boxes).every(function(b){ return b.checked; });
  boxes.forEach(function(b){ b.checked = !allChecked; });
}
</script>"""

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Temas Avaliativos</h1>
      <p style="font-size:12px;color:#888;">{len(temas)} tema(s) · {total_subtemas} subtema(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;
       font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {novo_tema_card}
  {temas_html}
  {js}
</div>"""
    return page_shell("Temas Avaliativos — Escola Espaço Alegre", body)


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
