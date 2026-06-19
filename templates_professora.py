"""Páginas da área da professora."""
from urllib.parse import quote
from templates import page_shell, _ANO_ATUAL

# ── Helpers de status ─────────────────────────────────────────────────────────

_STATUS = {
    "pendente":     ("#b52222", "#fef2f2", "#fecaca", "🔴 Pendente"),
    "em_andamento": ("#c25b0d", "#fef0e4", "#f8d4a8", "🟡 Em andamento"),
    "concluido":    ("#0a7c3e", "#e3f5ec", "#a8ddc0", "🟢 Concluído"),
}

def _badge_status(status: str) -> str:
    cor, bg, borda, label = _STATUS.get(status, _STATUS["pendente"])
    return (f'<span style="background:{bg};border:1px solid {borda};color:{cor};'
            f'font-size:11px;font-weight:800;padding:3px 11px;border-radius:20px;'
            f'white-space:nowrap;">{label}</span>')

def _dot(status: str) -> str:
    cores = {"pendente": "#b52222", "em_andamento": "#c25b0d", "concluido": "#0a7c3e"}
    c = cores.get(status, "#b52222")
    return f'<span style="display:inline-block;width:10px;height:10px;border-radius:50%;background:{c};"></span>'

def is_infantil(turma: str) -> bool:
    return turma.lower().startswith("infantil")


# ════════════════════════════════════════════════════════════════════════
#  LOGIN
# ════════════════════════════════════════════════════════════════════════

def professora_login_page(erro: bool = False) -> str:
    erro_html = '<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#b52222;font-weight:700;text-align:center;">Usuário ou senha incorretos.</div>' if erro else ''
    body = f"""
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px;">
<div style="background:#fff;border-radius:20px;box-shadow:0 8px 48px rgba(0,0,0,.22);width:100%;max-width:400px;overflow:hidden;">
  <div style="background:#2b3990;padding:28px 32px 24px;text-align:center;border-bottom:4px solid #f7d800;">
    <img src="/static/logo.jpg" style="height:56px;object-fit:contain;margin-bottom:10px;" alt="Logo">
    <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#fff;">Área da Professora</h1>
    <p style="font-size:11px;color:#b0b8e8;margin-top:3px;">Relatórios Semestrais — Ed. Infantil</p>
  </div>
  <div style="padding:28px 32px 32px;">
    {erro_html}
    <form method="POST" action="/professora/login">
      <div style="margin-bottom:14px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Usuário</label>
        <input name="usuario" type="text" autocomplete="username"
          style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;
                 padding:11px 14px;border:2px solid #ddd;border-radius:10px;outline:none;color:#2b3990;"
          onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#ddd'">
      </div>
      <div style="margin-bottom:20px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Senha</label>
        <input name="senha" type="password" autocomplete="current-password"
          style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;
                 padding:11px 14px;border:2px solid #ddd;border-radius:10px;outline:none;color:#2b3990;"
          onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#ddd'">
      </div>
      <button type="submit"
        style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
               background:#2b3990;color:#fff;border:none;border-radius:10px;padding:13px;cursor:pointer;">
        Entrar →
      </button>
    </form>
  </div>
  <div style="border-top:1px solid #f0f0ee;padding:12px 32px;text-align:center;font-size:11px;color:#ccc;">
    Escola Espaço Alegre &nbsp;|&nbsp; Ed. Infantil e Fundamental &nbsp;|&nbsp; Bilíngue
  </div>
  <p style="text-align:center;font-size:10px;color:#bbb;padding:0 32px 16px;">
    Desenvolvido por <strong style="color:#888;">Pedro Falcão</strong> © {_ANO_ATUAL}
  </p>
</div>
</div>"""
    return page_shell("Área da Professora — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  TROCAR SENHA
# ════════════════════════════════════════════════════════════════════════

def professora_trocar_senha_page(user: dict, obrigatorio: bool = False, erro: str = "") -> str:
    nome = user.get("nome", "Professora")
    erro_html = f'<div style="background:#fef2f2;border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#b52222;font-weight:700;text-align:center;">{erro}</div>' if erro else ''

    aviso_html = ""
    if obrigatorio:
        aviso_html = """
<div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:#c25b0d;font-weight:700;text-align:center;">
  🔑 Sua senha é temporária. Por segurança, defina uma nova senha para continuar.
</div>"""

    cancelar_html = "" if obrigatorio else """
<a href="/professora" style="display:block;text-align:center;margin-top:14px;font-size:12px;color:#aaa;font-weight:700;text-decoration:none;">
  ← Voltar
</a>"""

    _input = ("width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;"
              "padding:11px 14px;border:2px solid #ddd;border-radius:10px;outline:none;color:#2b3990;")

    body = f"""
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px;">
<div style="background:#fff;border-radius:20px;box-shadow:0 8px 48px rgba(0,0,0,.22);width:100%;max-width:400px;overflow:hidden;">
  <div style="background:#2b3990;padding:28px 32px 24px;text-align:center;border-bottom:4px solid #f7d800;">
    <img src="/static/logo.jpg" style="height:56px;object-fit:contain;margin-bottom:10px;" alt="Logo">
    <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#fff;">Definir Nova Senha</h1>
    <p style="font-size:11px;color:#b0b8e8;margin-top:3px;">Olá, {nome}</p>
  </div>
  <div style="padding:28px 32px 32px;">
    {aviso_html}
    {erro_html}
    <form method="POST" action="/professora/trocar-senha">
      <div style="margin-bottom:14px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Nova senha</label>
        <input name="nova_senha" type="password" required minlength="6" autocomplete="new-password"
          style="{_input}"
          onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#ddd'">
      </div>
      <div style="margin-bottom:20px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Confirmar nova senha</label>
        <input name="confirmar_senha" type="password" required minlength="6" autocomplete="new-password"
          style="{_input}"
          onfocus="this.style.borderColor='#2b3990'" onblur="this.style.borderColor='#ddd'">
      </div>
      <button type="submit"
        style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
               background:#2b3990;color:#fff;border:none;border-radius:10px;padding:13px;cursor:pointer;">
        Salvar nova senha →
      </button>
    </form>
    {cancelar_html}
  </div>
</div>
</div>"""
    return page_shell("Trocar Senha — Escola Espaço Alegre", body)


# ════════════════════════════════════════════════════════════════════════
#  DASHBOARD DA PROFESSORA
# ════════════════════════════════════════════════════════════════════════

def professora_dashboard(user: dict, turmas_data: list, msg: str = "", bemvindo: bool = False) -> str:
    """
    turmas_data: lista de dicts com:
      turma, periodo, total_alunos, is_infantil,
      pendentes, andamento, concluidos  (só para Infantil — para sem 1 e 2 somados)
    """
    nome = user.get("nome", "Professora")

    if not turmas_data:
        cards_html = '<div style="text-align:center;padding:40px;color:#aaa;font-size:14px;">Nenhum aluno vinculado ao seu nome ainda.<br>Entre em contato com a coordenação.</div>'
    else:
        cards_html = '<div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;">'
        for t in turmas_data:
            turma_enc = quote(t["turma"], safe="")
            infantil = t["is_infantil"]

            if infantil:
                total_relatorios = t["total_alunos"] * 2  # 2 semestres por aluno
                pend = t["pendentes"]
                and_ = t["andamento"]
                conc = t["concluidos"]

                barra_html = f"""
<div style="margin:14px 0 10px;">
  <div style="display:flex;justify-content:space-between;font-size:10px;font-weight:800;
              text-transform:uppercase;letter-spacing:.4px;color:#aaa;margin-bottom:6px;">
    <span>Relatórios semestrais</span>
    <span>{conc}/{total_relatorios}</span>
  </div>
  <div style="background:#f0f0ee;border-radius:6px;height:8px;overflow:hidden;">
    <div style="height:100%;width:{int(conc/total_relatorios*100) if total_relatorios else 0}%;
                background:#0a7c3e;border-radius:6px;transition:width .3s;"></div>
  </div>
  <div style="display:flex;gap:10px;margin-top:10px;flex-wrap:wrap;">
    <span style="font-size:11px;font-weight:700;color:#b52222;">🔴 {pend} pendente(s)</span>
    <span style="font-size:11px;font-weight:700;color:#c25b0d;">🟡 {and_} em andamento</span>
    <span style="font-size:11px;font-weight:700;color:#0a7c3e;">🟢 {conc} concluído(s)</span>
  </div>
</div>"""
            else:
                barra_html = '<p style="font-size:11px;color:#aaa;margin:12px 0 10px;">Boletim trimestral — gerenciado pela coordenação.</p>'

            cards_html += f"""
<div style="background:#fff;border-radius:14px;padding:20px 22px;box-shadow:0 2px 12px rgba(0,0,0,.08);display:flex;flex-direction:column;">
  <div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:4px;">
    <div style="flex:1;">
      <div style="font-family:'Fredoka One',cursive;font-size:17px;color:#2b3990;">{t["turma"]}</div>
      <div style="font-size:11px;color:#aaa;margin-top:2px;">{t["periodo"]} &nbsp;·&nbsp; {t["total_alunos"]} aluno(s)</div>
    </div>
    {"<span style=\"background:#e3f5ec;color:#0a7c3e;font-size:10px;font-weight:800;padding:2px 9px;border-radius:20px;\">Ed. Infantil</span>" if infantil else "<span style=\"background:#e8eaf8;color:#2b3990;font-size:10px;font-weight:800;padding:2px 9px;border-radius:20px;\">Fundamental</span>"}
  </div>
  {barra_html}
  <a href="/professora/turma/{turma_enc}"
     style="margin-top:auto;font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;
            background:#2b3990;color:#fff;border-radius:9px;padding:9px 0;
            text-align:center;display:block;">
    Ver alunos →
  </a>
</div>"""
        cards_html += '</div>'

    total_alunos = sum(t["total_alunos"] for t in turmas_data)
    msg_html = f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:16px;font-size:13px;color:#0a7c3e;font-weight:700;">✔ {msg}</div>' if msg else ""
    bemvindo_html = f"""
<div style="background:#fff8e1;border:1.5px solid #f7d800;border-radius:12px;padding:16px 20px;
            margin-bottom:16px;display:flex;align-items:center;gap:12px;">
  <span style="font-size:26px;">🎉</span>
  <div>
    <div style="font-family:'Fredoka One',cursive;font-size:15px;color:#2b3990;">Bem-vinda, {nome}!</div>
    <div style="font-size:12px;color:#6a6a4a;margin-top:2px;">
      Aqui você acompanha suas turmas e preenche os relatórios semestrais dos alunos.
      Em caso de dúvidas, fale com a coordenação.
    </div>
  </div>
</div>""" if bemvindo else ""
    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <!-- Header -->
  <div style="background:#2b3990;border-radius:16px;padding:24px 28px;margin-bottom:24px;
              display:flex;align-items:center;gap:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:48px;object-fit:contain;">
    <div style="flex:1;">
      <div style="font-family:'Fredoka One',cursive;font-size:22px;color:#fff;">Olá, {nome}! 👋</div>
      <div style="font-size:12px;color:#b0b8e8;margin-top:3px;">
        {len(turmas_data)} turma(s) &nbsp;·&nbsp; {total_alunos} aluno(s) vinculado(s)
      </div>
    </div>
    <a href="/professora/trocar-senha"
       style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:700;
              background:rgba(255,255,255,.15);color:#fff;padding:8px 16px;
              border-radius:9px;border:1px solid rgba(255,255,255,.3);">
      🔑 Trocar senha
    </a>
    <a href="/professora/logout"
       style="font-family:'Nunito',sans-serif;font-size:12px;font-weight:700;
              background:rgba(255,255,255,.15);color:#fff;padding:8px 16px;
              border-radius:9px;border:1px solid rgba(255,255,255,.3);">
      Sair
    </a>
  </div>

  {bemvindo_html}
  {msg_html}

  <!-- Título -->
  <div style="font-family:'Fredoka One',cursive;font-size:16px;color:#2b3990;margin-bottom:14px;">
    Minhas Turmas
  </div>

  {cards_html}
</div>"""
    return page_shell(f"Painel — {nome}", body)


# ════════════════════════════════════════════════════════════════════════
#  LISTA DE ALUNOS DA TURMA
# ════════════════════════════════════════════════════════════════════════

def professora_turma_page(user: dict, turma: str, alunos: list, msg: str = "") -> str:
    """
    alunos: lista de dicts com:
      matricula, nome, is_infantil, status_s1, status_s2, rel_id_s1, rel_id_s2
    """
    nome = user.get("nome", "Professora")
    infantil = is_infantil(turma)

    def _btn_acao(matricula: str, semestre: int, status: str) -> str:
        href = f"/professora/relatorio/{matricula}/{semestre}"
        if status == "concluido":
            return f'<a href="{href}" style="background:#e3f5ec;color:#0a7c3e;font-size:11px;font-weight:800;padding:5px 13px;border-radius:7px;white-space:nowrap;">👁 Ver</a>'
        elif status == "em_andamento":
            return f'<a href="{href}" style="background:#fef0e4;color:#c25b0d;font-size:11px;font-weight:800;padding:5px 13px;border-radius:7px;white-space:nowrap;">✏️ Continuar</a>'
        else:
            return f'<a href="{href}" style="background:#e8eaf8;color:#2b3990;font-size:11px;font-weight:800;padding:5px 13px;border-radius:7px;white-space:nowrap;">✏️ Preencher</a>'

    if not alunos:
        tabela = '<p style="text-align:center;color:#aaa;padding:30px;">Nenhum aluno encontrado nesta turma.</p>'
    elif infantil:
        rows = ""
        for i, al in enumerate(sorted(alunos, key=lambda x: x["nome"]), 1):
            s1 = al.get("status_s1", "pendente")
            s2 = al.get("status_s2", "pendente")
            rows += f"""
<tr style="border-bottom:.5px solid #f0f0ee;">
  <td style="padding:10px 12px;text-align:center;font-size:11px;color:#aaa;font-weight:700;">{i}</td>
  <td style="padding:10px 12px;font-weight:800;color:#2b3990;">{al['nome']}</td>
  <td style="padding:10px 12px;">
    <div style="display:flex;align-items:center;gap:8px;">
      {_dot(s1)} {_badge_status(s1)}
    </div>
  </td>
  <td style="padding:10px 12px;text-align:center;">{_btn_acao(al['matricula'], 1, s1)}</td>
  <td style="padding:10px 12px;">
    <div style="display:flex;align-items:center;gap:8px;">
      {_dot(s2)} {_badge_status(s2)}
    </div>
  </td>
  <td style="padding:10px 12px;text-align:center;">{_btn_acao(al['matricula'], 2, s2)}</td>
</tr>"""

        tabela = f"""
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;text-align:center;width:36px;">#</th>
      <th style="padding:9px 12px;text-align:left;">Aluno</th>
      <th style="padding:9px 12px;text-align:left;" colspan="2">1º Semestre</th>
      <th style="padding:9px 12px;text-align:left;" colspan="2">2º Semestre</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>"""
    else:
        # Turma fundamental — sem relatório semestral
        rows = ""
        for i, al in enumerate(sorted(alunos, key=lambda x: x["nome"]), 1):
            rows += f"""
<tr style="border-bottom:.5px solid #f0f0ee;">
  <td style="padding:10px 12px;text-align:center;font-size:11px;color:#aaa;font-weight:700;">{i}</td>
  <td style="padding:10px 12px;font-weight:800;color:#2b3990;">{al['nome']}</td>
  <td style="padding:10px 12px;">
    <a href="/boletim/{al['matricula']}" target="_blank"
       style="background:#e8eaf8;color:#2b3990;font-size:11px;font-weight:800;padding:5px 13px;border-radius:7px;">
      👁 Ver Boletim
    </a>
  </td>
</tr>"""
        tabela = f"""
<div style="background:#fef0e4;border:1px solid #f8d4a8;border-radius:10px;padding:11px 16px;margin-bottom:16px;font-size:12px;color:#c25b0d;font-weight:700;">
  ℹ️ Turma de Ed. Fundamental — notas e boletim gerenciados pela coordenação.
</div>
<div style="overflow-x:auto;">
<table style="width:100%;border-collapse:collapse;font-size:13px;">
  <thead>
    <tr style="background:#e8eaf8;font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#2b3990;">
      <th style="padding:9px 12px;width:36px;">#</th>
      <th style="padding:9px 12px;text-align:left;">Aluno</th>
      <th style="padding:9px 12px;text-align:left;">Boletim</th>
    </tr>
  </thead>
  <tbody>{rows}</tbody>
</table>
</div>"""

    periodo_hint = " (Manhã)" if turma.endswith("– A") else " (Tarde)" if turma.endswith("– B") else ""
    body = f"""
<div style="max-width:900px;margin:0 auto;padding:24px 16px;">
  <!-- Header -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="/professora"
       style="background:#e8eaf8;color:#2b3990;font-family:'Nunito',sans-serif;font-weight:800;
              font-size:12px;padding:8px 14px;border-radius:8px;">
      ← Minhas Turmas
    </a>
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#2b3990;">
        {turma}{periodo_hint}
      </h1>
      <p style="font-size:12px;color:#aaa;margin-top:2px;">
        {len(alunos)} aluno(s) &nbsp;·&nbsp; Profª {nome}
        {"&nbsp;·&nbsp; Relatórios Semestrais" if infantil else ""}
      </p>
    </div>
    <a href="/professora/logout"
       style="background:#f7f7f5;color:#888;font-family:'Nunito',sans-serif;font-weight:700;
              font-size:12px;padding:8px 14px;border-radius:9px;border:1px solid #dcdcd8;">
      Sair
    </a>
  </div>

  {f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:16px;font-size:13px;color:#0a7c3e;font-weight:700;">✔ {msg}</div>' if msg else ""}

  <!-- Legenda (só Infantil) -->
  {"" if not infantil else """
  <div style="display:flex;gap:16px;flex-wrap:wrap;margin-bottom:16px;font-size:12px;font-weight:700;">
    <span style="color:#b52222;">🔴 Pendente — não iniciado</span>
    <span style="color:#c25b0d;">🟡 Em andamento — rascunho salvo</span>
    <span style="color:#0a7c3e;">🟢 Concluído — relatório confirmado</span>
  </div>"""}

  <div style="background:#fff;border-radius:14px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.07);">
    {tabela}
  </div>
</div>"""
    return page_shell(f"{turma} — {nome}", body)
