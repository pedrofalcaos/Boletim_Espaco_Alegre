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
#  TEMAS AVALIATIVOS
# ════════════════════════════════════════════════════════════════════════

def admin_temas_page(temas: list, msg: str = "", erro: str = "") -> str:
    """
    temas: lista de dicts com campo 'subtemas' (lista de dicts)
    """
    nav = admin_nav("temas")
    aviso = _msg_ok(msg) if msg else (_msg_erro(erro) if erro else "")

    total_subtemas = sum(len(t.get("subtemas", [])) for t in temas)

    # ── Cards de cada tema ──
    temas_html = ""
    for tema in temas:
        subtemas = tema.get("subtemas", [])

        # Linhas de subtemas existentes
        if subtemas:
            linhas_st = ""
            for i, st in enumerate(subtemas, 1):
                linhas_st += f"""
<div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:.5px solid #f0f0ee;">
  <span style="color:#aaa;font-size:11px;font-weight:700;min-width:22px;">{i}.</span>
  <span style="flex:1;font-size:13px;color:#4a4a4a;">{st['descricao']}</span>
  <form method="POST" action="/admin/subtemas/{st['id']}/excluir" style="margin:0;"
        onsubmit="return confirm('Excluir subtema?');">
    <button type="submit" style="{_BTN_VM}">✕</button>
  </form>
</div>"""
        else:
            linhas_st = '<p style="color:#ccc;font-size:12px;padding:8px 0;">Nenhum subtema ainda.</p>'

        # Form inline para novo subtema
        form_st = f"""
<form method="POST" action="/admin/temas/{tema['id']}/subtema" style="display:flex;gap:8px;margin-top:12px;">
  <input name="descricao" required placeholder="Novo subtema..." style="{_INP}flex:1;"
    onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  <button type="submit" style="{_BTN_AZ}padding:9px 16px;">+ Adicionar</button>
</form>"""

        # Form de edição do nome do tema
        form_edit = f"""
<form method="POST" action="/admin/temas/{tema['id']}/editar" style="display:flex;gap:8px;margin-bottom:12px;">
  <input name="nome" value="{tema['nome']}" required style="{_INP}flex:1;font-size:14px;font-weight:800;color:#2b3990;"
    onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  <button type="submit" style="{_BTN_AZ}padding:9px 14px;font-size:12px;">Salvar</button>
  <form method="POST" action="/admin/temas/{tema['id']}/excluir" style="margin:0;"
        onsubmit="return confirm('Excluir o tema e todos os subtemas?');">
    <button type="submit" style="{_BTN_VM}padding:9px 12px;">🗑</button>
  </form>
</form>"""

        badge = f'<span style="background:#e8eaf8;color:#2b3990;font-size:11px;font-weight:800;padding:2px 10px;border-radius:20px;">{len(subtemas)} subtema(s)</span>'

        temas_html += _card(f"""
<div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;border-bottom:2px solid #f7d800;padding-bottom:8px;">
  <span style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;flex:1;">🏷️ Tema</span>
  {badge}
</div>
{form_edit}
<div style="padding:0 0 4px 0;">{linhas_st}</div>
{form_st}""")

    if not temas_html:
        temas_html = _card('<p style="color:#aaa;text-align:center;padding:20px 0;">Nenhum tema cadastrado ainda.</p>')

    # ── Form novo tema ──
    novo_tema_card = _card(f"""
{_secao("➕ Novo Tema Principal")}
<form method="POST" action="/admin/temas/novo" style="display:flex;gap:10px;align-items:flex-end;">
  <div style="flex:1;">
    <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome do tema</label>
    <input name="nome" required placeholder="Ex: O eu, o outro e o nós" style="{_INP}"
      onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#c8c8c4'">
  </div>
  <button type="submit" style="{_BTN_AZ}">Criar tema →</button>
</form>
<p style="font-size:11px;color:#aaa;margin-top:10px;">Após criar o tema, adicione os subtemas avaliativos dentro do card gerado acima.</p>""")

    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:44px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:#2b3990;">Temas Avaliativos</h1>
      <p style="font-size:12px;color:#888;">{len(temas)} tema(s) · {total_subtemas} subtema(s) cadastrado(s)</p>
    </div>
    <a href="/admin/logout" style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;font-size:12px;padding:9px 16px;border-radius:10px;border:1px solid #dcdcd8;">Sair</a>
  </div>

  {nav}
  {aviso}
  {novo_tema_card}
  {temas_html}
</div>"""
    return page_shell("Temas Avaliativos — Escola Espaço Alegre", body)
