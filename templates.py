"""HTML de todas as páginas."""
from urllib.parse import quote
from datetime import datetime

_ANO_ATUAL = datetime.now().year

# ── Paleta ──────────────────────────────────────────────────────────────────
CSS_VARS = """
:root{
  --azul:#2b3990;--azul-lt:#e8eaf8;--azul-md:#b0b8e8;
  --amarelo:#f7d800;--amarelo-dk:#c8ab00;
  --cinza-lt:#f7f7f5;--cinza-md:#dcdcd8;--cinza-dk:#4a4a4a;
  --verde:#0a7c3e;--verde-lt:#e3f5ec;
  --vermelho:#b52222;--vermelho-lt:#fef2f2;
  --laranja:#c25b0d;--laranja-lt:#fef0e4;
  --roxo:#6a1a8a;--roxo-lt:#f5eafc;--borda:#c8c8c4;
}
"""

# ── Shell comum ──────────────────────────────────────────────────────────────
def page_shell(title: str, body: str, extra_head: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800;900&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
{CSS_VARS}
body{{font-family:'Nunito',sans-serif;background:#d0d3e4;min-height:100vh;}}
a{{text-decoration:none;color:inherit;}}
{extra_head}
</style>
</head>
<body>
{body}
<footer style="text-align:center;padding:18px 12px 28px;font-family:'Nunito',sans-serif;
               font-size:11px;color:#9a9da8;">
  Sistema desenvolvido por <strong style="color:#6a6f87;">Pedro Falcão</strong> © {_ANO_ATUAL} — Todos os direitos reservados.
</footer>
</body>
</html>"""

# ── Página de login ──────────────────────────────────────────────────────────
def login_page(erro: bool = False) -> str:
    erro_html = '<div class="erro">Usuário ou senha incorretos.</div>' if erro else ''
    body = f"""
<div style="display:flex;align-items:center;justify-content:center;min-height:100vh;padding:24px;">
<div style="background:#fff;border-radius:20px;box-shadow:0 8px 48px rgba(0,0,0,.22);width:100%;max-width:400px;overflow:hidden;">
  <div style="background:var(--azul);padding:28px 32px 24px;text-align:center;border-bottom:4px solid var(--amarelo);">
    <img src="/static/logo.jpg" style="height:56px;object-fit:contain;margin-bottom:10px;" alt="Logo">
    <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:#fff;">Painel Administrativo</h1>
    <p style="font-size:11px;color:#b0b8e8;margin-top:3px;">Acesso exclusivo para professores e coordenação</p>
  </div>
  <div style="padding:28px 32px 32px;">
    {erro_html}
    <form method="POST" action="/admin/login">
      <div style="margin-bottom:14px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Usuário</label>
        <input name="usuario" type="text" autocomplete="username"
          style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;
                 padding:11px 14px;border:2px solid #ddd;border-radius:10px;outline:none;color:var(--azul);"
          onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='#ddd'">
      </div>
      <div style="margin-bottom:20px;">
        <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.7px;color:#aaa;display:block;margin-bottom:5px;">Senha</label>
        <input name="senha" type="password" autocomplete="current-password"
          style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;
                 padding:11px 14px;border:2px solid #ddd;border-radius:10px;outline:none;color:var(--azul);"
          onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='#ddd'">
      </div>
      <button type="submit"
        style="width:100%;font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
               background:var(--azul);color:#fff;border:none;border-radius:10px;
               padding:13px;cursor:pointer;">
        Entrar →
      </button>
    </form>
    <p style="text-align:center;font-size:10px;color:#bbb;margin-top:18px;">
      Desenvolvido por <strong style="color:#888;">Pedro Falcão</strong> © {_ANO_ATUAL}
    </p>
  </div>
</div>
</div>"""
    css = ".erro{background:var(--vermelho-lt);border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:var(--vermelho);font-weight:700;text-align:center;}"
    return page_shell("Login — Escola Espaço Alegre", body, css)

# ── Nav bar do admin ─────────────────────────────────────────────────────────
def admin_nav(current: str = "alunos") -> str:
    items = [
        ("alunos",      "/admin",               "📚 Alunos"),
        ("professoras", "/admin/professoras",    "👩‍🏫 Professoras"),
        ("temas",       "/admin/temas",          "🗂️ Estrutura Avaliativa"),
        ("relatorios",  "/admin/relatorios",     "📋 Relatórios Semestrais"),
    ]
    links = ""
    for key, href, label in items:
        if key == current:
            style = ("background:var(--azul);color:#fff;font-size:12px;font-weight:900;"
                     "padding:7px 16px;border-radius:8px;white-space:nowrap;")
        else:
            style = ("background:transparent;color:var(--azul);font-size:12px;font-weight:700;"
                     "padding:7px 16px;border-radius:8px;white-space:nowrap;"
                     "border:1.5px solid transparent;")
            style += "opacity:.7;"
        links += f'<a href="{href}" style="{style}">{label}</a>\n'
    return f'<div style="background:#fff;border-radius:10px;padding:6px 8px;margin-bottom:20px;box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;gap:4px;flex-wrap:wrap;">{links}</div>'


# ── Dashboard admin ──────────────────────────────────────────────────────────
def admin_dashboard(alunos: dict, resetado: bool = False, rel_status: dict = None) -> str:
    """
    rel_status: {matricula: {1: status_str, 2: status_str}} — status dos relatórios Infantil.
    """
    rel_status = rel_status or {}

    # Helpers de status para Ed. Infantil
    _ST_COR = {"pendente":"#b52222","em_andamento":"#c25b0d","concluido":"#0a7c3e"}
    _ST_BG  = {"pendente":"#fef2f2","em_andamento":"#fef0e4","concluido":"#e3f5ec"}
    _ST_ICO = {"pendente":"🔴","em_andamento":"🟡","concluido":"🟢"}
    _ST_LAB = {"pendente":"Pendente","em_andamento":"Andamento","concluido":"Concluído"}

    def _rel_pill(s):
        if s is None:
            return '<span style="color:#ccc;font-size:10px;font-weight:700;">–</span>'
        return (f'<span style="background:{_ST_BG[s]};color:{_ST_COR[s]};font-size:9px;'
                f'font-weight:800;padding:2px 8px;border-radius:10px;white-space:nowrap;">'
                f'{_ST_ICO[s]} {_ST_LAB[s]}</span>')

    # agrupar por turma
    turmas: dict = {}
    for mat, al in sorted(alunos.items(), key=lambda x: x[1]['nome']):
        t = al.get('turma','Sem turma')
        turmas.setdefault(t, []).append((mat, al))

    def _sort_turma(t: str):
        import re
        low = t.lower()
        if low.startswith("infantil"):
            m = re.search(r'(\d+)', t)
            num = int(m.group(1)) if m else 99
            letra = 0 if t.strip().endswith("A") else 1
            return (0, num, letra)
        m = re.search(r'(\d+)', t)
        num = int(m.group(1)) if m else 99
        letra = 0 if t.strip().endswith("A") else 1
        return (1, num, letra)

    turma_blocks = ""
    for turma, lista in sorted(turmas.items(), key=lambda x: _sort_turma(x[0])):
        e_infantil = turma.lower().startswith("infantil")
        rows = ""
        for i, (mat, al) in enumerate(lista, 1):
            nome = al['nome']
            prof = al.get('professora','–')

            if e_infantil:
                st = rel_status.get(mat, {})
                badge_html = f'{_rel_pill(st.get(1))} &nbsp; {_rel_pill(st.get(2))}'
                ver_href   = f"/admin/aluno/{mat}/relatorios"
                ver_label  = "📋 Relatórios"
            else:
                total_notas = sum(1 for disc_n in al.get('notas',{}).values() for k in ('p1','gl1') if disc_n.get(k))
                badge_color = "var(--verde)" if total_notas >= 18 else ("var(--laranja)" if total_notas > 0 else "#ccc")
                badge_html = f'<span style="background:{badge_color};color:#fff;font-size:10px;font-weight:800;padding:2px 9px;border-radius:20px;">{total_notas} notas</span>'
                ver_href  = f"/boletim/{mat}?ref=admin"
                ver_label = "👁 Ver"

            rows += f"""
<tr>
  <td style="text-align:center;font-size:11px;color:#aaa;font-weight:700;width:32px;">{i}</td>
  <td style="font-weight:700;color:var(--azul);">{mat}</td>
  <td>{nome}</td>
  <td style="font-size:12px;color:#888;">{prof}</td>
  <td style="text-align:center;">{badge_html}</td>
  <td style="text-align:center;white-space:nowrap;">
    <a href="/admin/aluno/{mat}{'/editar-infantil' if e_infantil else ''}"
       style="background:var(--azul-lt);color:var(--azul);
       font-size:11px;font-weight:800;padding:4px 12px;border-radius:7px;display:inline-block;">
      ✏️ Editar
    </a>
    &nbsp;
    <a href="{ver_href}" {"target='_blank'" if not e_infantil else ""} style="background:var(--verde-lt);color:var(--verde);
       font-size:11px;font-weight:800;padding:4px 12px;border-radius:7px;display:inline-block;">
      {ver_label}
    </a>
  </td>
</tr>"""
        turma_enc = quote(turma, safe='')
        turma_blocks += f"""
<div style="margin-bottom:24px;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
    <div style="font-family:'Fredoka One',cursive;font-size:16px;color:var(--azul);
                border-left:4px solid var(--amarelo);padding-left:10px;flex:1;">
      {turma} <span style="font-size:12px;font-family:'Nunito',sans-serif;font-weight:700;color:#aaa;">({len(lista)} alunos)</span>
    </div>
    <a href="/admin/imprimir?turma={turma_enc}" target="_blank"
       style="background:var(--azul);color:#fff;font-family:'Nunito',sans-serif;
              font-size:11px;font-weight:800;padding:5px 14px;border-radius:8px;white-space:nowrap;">
      🖨️ Imprimir Turma
    </a>
  </div>
  <div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.07);">
  <table style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead>
      <tr style="background:var(--azul-lt);font-size:10px;font-weight:800;
                 text-transform:uppercase;letter-spacing:.5px;color:var(--azul);">
        <th style="padding:8px 8px;text-align:center;width:32px;">#</th>
        <th style="padding:8px 12px;text-align:left;">Matrícula</th>
        <th style="padding:8px 12px;text-align:left;">Nome</th>
        <th style="padding:8px 12px;text-align:left;">Professor(a)</th>
        <th style="padding:8px 12px;text-align:center;">Status / Notas</th>
        <th style="padding:8px 12px;text-align:center;">Ações</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  </div>
</div>"""

    total = len(alunos)
    aviso_reset = '<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:12px;color:var(--verde);font-weight:700;">✔ Banco de dados resetado com sucesso!</div>' if resetado else ''
    nav = admin_nav("alunos")
    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <!-- Header -->
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:16px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:48px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:var(--azul);">Painel Administrativo</h1>
      <p style="font-size:12px;color:#888;">{total} alunos cadastrados</p>
    </div>
    <a href="/admin/imprimir?turma=todos" target="_blank"
       style="background:var(--azul);color:#fff;font-family:'Nunito',sans-serif;
              font-weight:800;font-size:13px;padding:10px 18px;border-radius:10px;">
      🖨️ Imprimir Todos
    </a>
    <a href="/admin/aluno/novo"
       style="background:var(--amarelo);color:var(--azul);font-family:'Nunito',sans-serif;
              font-weight:900;font-size:13px;padding:10px 20px;border-radius:10px;">
      ＋ Novo Aluno
    </a>
    <a href="/admin/logout"
       style="background:var(--cinza-lt);color:#888;font-family:'Nunito',sans-serif;
              font-weight:700;font-size:12px;padding:10px 16px;border-radius:10px;border:1px solid var(--borda);">
      Sair
    </a>
  </div>

  {nav}

  {aviso_reset}

  <!-- Aviso privacidade -->
  <div style="background:var(--azul-lt);border:1px solid var(--azul-md);border-radius:10px;
              padding:11px 16px;margin-bottom:20px;font-size:12px;color:var(--azul);">
    💡 <strong>Privacidade garantida:</strong> cada pai acessa apenas o boletim do próprio filho pelo número de matrícula.
    Nenhum pai consegue ver dados de outro aluno.
  </div>

  {turma_blocks}

  <!-- Importar Ed. Infantil -->
  <div style="background:#e8eaf8;border:1px solid #b0b8e8;border-radius:12px;
              padding:16px 20px;margin-top:24px;">
    <div style="font-family:'Fredoka One',cursive;font-size:14px;color:var(--azul);margin-bottom:6px;">
      📥 Importar alunos da Ed. Infantil
    </div>
    <p style="font-size:12px;color:#666;margin-bottom:12px;">
      Importa os 74 alunos e 6 professoras da Ed. Infantil 2026.
      <strong>Seguro para rodar várias vezes</strong> — não duplica registros existentes.
      Use quando o banco ainda não tiver os alunos do Infantil (ex: após novo deploy no Railway).
    </p>
    <form method="POST" action="/admin/seed-infantil"
          onsubmit="return confirm('Importar alunos da Ed. Infantil? Registros existentes não serão alterados.');">
      <button type="submit"
        style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;
               background:var(--azul);color:#fff;border:none;border-radius:8px;
               padding:10px 22px;cursor:pointer;">
        📥 Importar Ed. Infantil
      </button>
    </form>
  </div>

  <!-- Reset banco -->
  <div style="background:var(--vermelho-lt);border:1px solid #fecaca;border-radius:12px;
              padding:16px 20px;margin-top:16px;">
    <div style="font-family:'Fredoka One',cursive;font-size:14px;color:var(--vermelho);margin-bottom:6px;">
      ⚠️ Zona de perigo — Resetar banco de dados
    </div>
    <p style="font-size:12px;color:#888;margin-bottom:12px;">
      Apaga <strong>todos os dados</strong> e recarrega do arquivo de semente (<code>dados.json</code>).
      Use apenas quando necessário atualizar os dados iniciais após um novo deploy.
    </p>
    <form method="POST" action="/admin/resetar" onsubmit="return confirm('Tem certeza? Todos os dados atuais serão apagados e substituídos pelos dados do arquivo de semente.');">
      <button type="submit"
        style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:900;
               background:var(--vermelho);color:#fff;border:none;border-radius:8px;
               padding:10px 22px;cursor:pointer;">
        🗑 Resetar banco de dados
      </button>
    </form>
  </div>
</div>"""
    return page_shell("Painel — Escola Espaço Alegre", body)

# ── Formulário de edição de aluno ────────────────────────────────────────────
def aluno_form(matricula: str, aluno: dict, novo: bool, msg: str = "") -> str:
    DISCIPLINAS = [
        'Língua Portuguesa','Matemática','História','Geografia',
        'Ciências','Arte','Educação Física',
        'Língua Estrangeira – Inglês','Produção Textual',
    ]
    TURMAS = [
        # Ed. Infantil — A (Manhã) e B (Tarde)
        'Infantil 1 – A','Infantil 1 – B',
        'Infantil 2 – A','Infantil 2 – B',
        'Infantil 3 – A','Infantil 3 – B',
        'Infantil 4 – A','Infantil 4 – B',
        'Infantil 5 – A','Infantil 5 – B',
        # Ed. Fundamental Anos Iniciais
        '1º Ano A','1º Ano B','2º Ano A','2º Ano B',
        '3º Ano A','3º Ano B','4º Ano A','4º Ano B',
        '5º Ano A','5º Ano B',
    ]
    PERIODOS = ['Manhã','Tarde','Noite']

    def sel(opts, cur):
        return ''.join(f'<option {"selected" if o==cur else ""}>{o}</option>' for o in opts)

    def sid(d):
        return d.replace(' ','_').replace('–','_').replace('/','_')

    # ── estilos base ──
    lbl_s   = "font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;"
    lbl_sm  = "font-size:8px;font-weight:800;text-transform:uppercase;letter-spacing:.3px;color:#aaa;display:block;margin-bottom:2px;"
    inp_s   = ("width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;"
               "color:var(--azul);padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;")
    inp_ro  = ("width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;"
               "color:#999;padding:8px 12px;border:1.5px solid #e8e8e8;border-radius:8px;"
               "background:#f8f8f8;cursor:not-allowed;")
    nota_s  = ("width:60px;font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;"
               "text-align:center;padding:5px 3px;border:1.5px solid var(--borda);"
               "border-radius:7px;outline:none;color:var(--azul);")
    rec_s   = ("width:60px;font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;"
               "text-align:center;padding:5px 3px;border:1.5px solid #f0c060;"
               "border-radius:7px;outline:none;color:var(--laranja);"
               "opacity:0.3;cursor:not-allowed;background:#fffbf0;")

    # ── campos de identidade ──
    def field_ro(label, value):
        return f'''<div><label style="{lbl_s}">{label}</label>
          <div style="{inp_ro}border:1.5px solid #e8e8e8;">{value or '—'} 🔒</div></div>'''

    if novo:
        dados_html = f'''
        <div style="grid-column:span 2;">
          <label style="{lbl_s}">Nome Completo</label>
          <input name="nome" value="" required style="{inp_s}"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="{lbl_s}">Matrícula</label>
          <input name="matricula" value="" required style="{inp_s}"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="{lbl_s}">Turma</label>
          <select name="turma" style="{inp_s}background:#fff;">
            {sel(TURMAS, '')}
          </select>
        </div>
        <div>
          <label style="{lbl_s}">Período</label>
          <select name="periodo" style="{inp_s}background:#fff;">
            {sel(PERIODOS, '')}
          </select>
        </div>
        <div style="grid-column:span 2;">
          <label style="{lbl_s}">Professor(a)</label>
          <input name="professora" value="" style="{inp_s}"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="{lbl_s}">Ano Letivo</label>
          <input name="ano_letivo" value="2026" style="{inp_s}"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>'''
        lock_aviso = ''
    else:
        # campos bloqueados — hidden inputs garantem o envio
        nome_v  = aluno.get('nome','')
        turma_v = aluno.get('turma','')
        per_v   = aluno.get('periodo','')
        prof_v  = aluno.get('professora','')
        ano_v   = aluno.get('ano_letivo','2026')
        dados_html = f'''
        <input type="hidden" name="nome"       value="{nome_v}">
        <input type="hidden" name="matricula"  value="{matricula}">
        <input type="hidden" name="turma"      value="{turma_v}">
        <input type="hidden" name="periodo"    value="{per_v}">
        <input type="hidden" name="professora" value="{prof_v}">
        <input type="hidden" name="ano_letivo" value="{ano_v}">
        <div style="grid-column:span 2;">{field_ro("Nome Completo", nome_v)}</div>
        <div>{field_ro("Matrícula", matricula)}</div>
        <div>{field_ro("Turma", turma_v)}</div>
        <div>{field_ro("Período", per_v)}</div>
        <div style="grid-column:span 2;">{field_ro("Professor(a)", prof_v)}</div>
        <div>{field_ro("Ano Letivo", ano_v)}</div>'''
        lock_aviso = '<span style="font-size:11px;color:#aaa;font-weight:600;margin-left:8px;">🔒 Dados bloqueados — edite apenas as notas</span>'

    # ── tabela de notas ──
    T_COLORS = [("#2b3990","#f7d800"),("#1a6e30","#d8f5e4"),("#a34c00","#fef0e0")]
    T_LABELS = ["1º Trimestre","2º Trimestre","3º Trimestre"]

    header_cols = '<th style="text-align:left;padding:8px 10px;background:#f2f2f0;font-size:10px;color:#aaa;font-weight:800;text-transform:uppercase;min-width:140px;">Disciplina</th>'
    for i,(t_bg,t_fg) in enumerate(T_COLORS):
        header_cols += f'<th style="padding:8px 10px;background:{t_bg};color:{t_fg};font-size:10px;font-weight:900;text-transform:uppercase;">{T_LABELS[i]}<br><span style="font-size:8px;font-weight:600;opacity:.8;">Parcial · Global · Média · Rec.</span></th>'
    header_cols += '<th style="padding:8px 10px;background:#6a1a8a;color:#f0d8fa;font-size:10px;font-weight:900;text-transform:uppercase;">Resultado Anual<br><span style="font-size:8px;font-weight:600;opacity:.8;">Média · Rec. Final</span></th>'

    disc_rows = ""
    init_calls = []

    for disc in DISCIPLINAS:
        s   = sid(disc)
        n   = aluno.get('notas',{}).get(disc,{})
        cells = f'<td style="font-weight:700;font-size:12px;color:var(--cinza-dk);padding:7px 10px;min-width:140px;">{disc}</td>'

        for t in [1,2,3]:
            pv = n.get(f'p{t}',''); gv = n.get(f'gl{t}',''); rv = n.get(f'r{t}','')
            t_bg = T_COLORS[t-1][0]
            cells += f'''<td style="padding:6px 8px;border-left:2px solid {t_bg}20;">
              <div style="display:flex;gap:5px;align-items:flex-end;flex-wrap:wrap;">
                <div>
                  <label style="{lbl_sm}">Parcial</label>
                  <input type="number" name="nota_{s}_p{t}" value="{pv}" min="0" max="10" step="0.1"
                    placeholder="—" style="{nota_s}"
                    oninput="upd('{s}',{t})"
                    onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
                </div>
                <div>
                  <label style="{lbl_sm}">Global</label>
                  <input type="number" name="nota_{s}_gl{t}" value="{gv}" min="0" max="10" step="0.1"
                    placeholder="—" style="{nota_s}"
                    oninput="upd('{s}',{t})"
                    onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
                </div>
                <div style="text-align:center;min-width:40px;padding-bottom:2px;">
                  <label style="{lbl_sm}color:{t_bg};">Média</label>
                  <div id="med_{s}_{t}" style="font-size:15px;font-weight:800;color:#ccc;line-height:1.2;">–</div>
                </div>
                <div>
                  <label style="{lbl_sm}color:var(--laranja);">Rec.</label>
                  <input type="number" name="nota_{s}_r{t}" value="{rv}" min="0" max="10" step="0.1"
                    placeholder="—" style="{rec_s}" disabled
                    title="Habilitado automaticamente quando Média < 7,0"
                    onfocus="this.style.borderColor='var(--laranja)'" onblur="this.style.borderColor='#f0c060'">
                </div>
              </div>
            </td>'''
            init_calls.append(f"upd('{s}',{t},true);")

        rfv = n.get('rf','')
        cells += f'''<td style="padding:6px 8px;border-left:2px solid #6a1a8a30;">
          <div style="display:flex;gap:5px;align-items:flex-end;flex-wrap:wrap;">
            <div style="text-align:center;min-width:40px;padding-bottom:2px;">
              <label style="{lbl_sm}color:#6a1a8a;">Anual</label>
              <div id="anual_{s}" style="font-size:15px;font-weight:800;color:#ccc;line-height:1.2;">–</div>
            </div>
            <div>
              <label style="{lbl_sm}color:var(--laranja);">Rec. Final</label>
              <input type="number" name="nota_{s}_rf" value="{rfv}" min="0" max="10" step="0.1"
                placeholder="—" style="{rec_s}" disabled
                title="Habilitado quando Média Anual < 7,0"
                onfocus="this.style.borderColor='var(--laranja)'" onblur="this.style.borderColor='#f0c060'">
            </div>
          </div>
        </td>'''
        disc_rows += f"<tr style='border-bottom:.5px solid var(--cinza-md);'>{cells}</tr>"

    freq = aluno.get('frequencia', {})
    obs  = aluno.get('observacoes','')
    msg_html = f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:13px;color:var(--verde);font-weight:700;">✔ {msg}</div>' if msg else ''
    titulo = "Novo Aluno" if novo else aluno.get('nome','Aluno')
    init_js = '\n  '.join(init_calls)

    body = f"""
<div style="max-width:1100px;margin:0 auto;padding:24px 16px;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="/admin" style="background:var(--azul-lt);color:var(--azul);font-weight:800;font-size:12px;padding:7px 14px;border-radius:8px;">← Painel</a>
    <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:var(--azul);">{titulo}</h1>
    {lock_aviso}
    {"" if novo else f'<a href="/boletim/{matricula}?ref=admin" target="_blank" style="margin-left:auto;background:var(--verde-lt);color:var(--verde);font-weight:800;font-size:12px;padding:7px 14px;border-radius:8px;">👁 Ver Boletim</a>'}
  </div>

  {msg_html}

  <form method="POST" action="/admin/aluno/{matricula if not novo else 'novo'}/salvar">

    <!-- Dados cadastrais -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        👤 Dados do Aluno
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:12px 16px;">
        {dados_html}
      </div>
    </div>

    <!-- Notas -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        <span style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);">📊 Notas por Disciplina</span>
        <span style="font-size:11px;color:#aaa;margin-left:auto;">
          🟢 Média ≥ 7,0 · 🔴 Média &lt; 7,0 → Rec. desbloqueada automaticamente
        </span>
      </div>
      <div style="overflow-x:auto;">
        <table style="border-collapse:collapse;width:100%;">
          <thead><tr>{header_cols}</tr></thead>
          <tbody>{disc_rows}</tbody>
        </table>
      </div>
    </div>

    <!-- Frequência -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        📋 Frequência
      </div>
      <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-end;">
        <div>
          <label style="{lbl_s}">Total de Aulas no Ano</label>
          <input name="total_aulas" type="number" min="0" value="{freq.get('total_aulas','')}" placeholder="ex: 200"
            style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;color:var(--azul);
                   padding:8px 14px;border:1.5px solid var(--borda);border-radius:8px;outline:none;width:160px;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="{lbl_s}">Total de Faltas</label>
          <input name="total_faltas" type="number" min="0" value="{freq.get('total_faltas','')}" placeholder="0"
            style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;color:var(--azul);
                   padding:8px 14px;border:1.5px solid var(--borda);border-radius:8px;outline:none;width:140px;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div style="font-size:12px;color:#888;padding-bottom:8px;">Mín. legal: <strong>75%</strong> (LDB 9.394/96)</div>
      </div>
    </div>

    <!-- Observações -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        💬 Observações Pedagógicas
      </div>
      <textarea name="observacoes" rows="3" placeholder="Desempenho, comportamento, pontos de atenção..."
        style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;color:var(--cinza-dk);
               padding:10px 14px;border:1.5px solid var(--borda);border-radius:8px;outline:none;resize:vertical;"
        onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">{obs}</textarea>
    </div>

    <!-- Botões -->
    <div style="display:flex;gap:12px;flex-wrap:wrap;">
      <button type="submit"
        style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:900;
               background:var(--azul);color:#fff;border:none;border-radius:10px;padding:12px 32px;cursor:pointer;">
        💾 Salvar
      </button>
      <a href="/admin"
        style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:700;
               background:var(--cinza-lt);color:#888;border:1px solid var(--borda);border-radius:10px;
               padding:12px 24px;display:inline-block;">
        Cancelar
      </a>
      {"" if novo else f'''
      <button type="button" onclick="confirmarExclusao('{matricula}')"
        style="margin-left:auto;font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;
               background:var(--vermelho-lt);color:var(--vermelho);border:1px solid #fecaca;
               border-radius:10px;padding:12px 20px;cursor:pointer;">
        🗑 Excluir Aluno
      </button>'''}
    </div>
  </form>
</div>

<script>
function upd(s, t, init) {{
  var p = parseFloat(document.querySelector('[name="nota_'+s+'_p'+t+'"]').value);
  var g = parseFloat(document.querySelector('[name="nota_'+s+'_gl'+t+'"]').value);
  var medEl  = document.getElementById('med_'+s+'_'+t);
  var recInp = document.querySelector('[name="nota_'+s+'_r'+t+'"]');

  if (!isNaN(p) && !isNaN(g)) {{
    var med = Math.round((p+g)*10)/20;
    medEl.textContent = med.toFixed(1).replace('.',',');
    if (med >= 7) {{
      medEl.style.color = '#0a7c3e';
      recInp.disabled = true;
      recInp.style.opacity = '0.3';
      recInp.style.cursor = 'not-allowed';
      if (!init) recInp.value = '';
    }} else {{
      medEl.style.color = '#b52222';
      recInp.disabled = false;
      recInp.style.opacity = '1';
      recInp.style.cursor = '';
    }}
  }} else {{
    medEl.textContent = '–';
    medEl.style.color = '#ccc';
    recInp.disabled = true;
    recInp.style.opacity = '0.3';
    recInp.style.cursor = 'not-allowed';
  }}
  updAnual(s);
}}

function calcEf(s, t) {{
  var p  = parseFloat(document.querySelector('[name="nota_'+s+'_p'+t+'"]').value);
  var g  = parseFloat(document.querySelector('[name="nota_'+s+'_gl'+t+'"]').value);
  var r  = parseFloat(document.querySelector('[name="nota_'+s+'_r'+t+'"]').value);
  if (isNaN(p) || isNaN(g)) return null;
  var med = (p+g)/2;
  if (!isNaN(r)) med = Math.max(med, (med+r)/2);
  return Math.round(med*10)/10;
}}

function updAnual(s) {{
  var ef1=calcEf(s,1), ef2=calcEf(s,2), ef3=calcEf(s,3);
  var anualEl = document.getElementById('anual_'+s);
  var rfInp   = document.querySelector('[name="nota_'+s+'_rf"]');
  if (ef1!==null && ef2!==null && ef3!==null) {{
    var anual = Math.round((ef1+ef2+ef3)*100/3)/100;
    anualEl.textContent = anual.toFixed(1).replace('.',',');
    if (anual >= 7) {{
      anualEl.style.color = '#0a7c3e';
      rfInp.disabled = true;
      rfInp.style.opacity = '0.3';
      rfInp.style.cursor = 'not-allowed';
    }} else {{
      anualEl.style.color = '#b52222';
      rfInp.disabled = false;
      rfInp.style.opacity = '1';
      rfInp.style.cursor = '';
    }}
  }} else {{
    anualEl.textContent = '–';
    anualEl.style.color = '#ccc';
    rfInp.disabled = true;
    rfInp.style.opacity = '0.3';
  }}
}}

function confirmarExclusao(mat) {{
  if(confirm('Tem certeza que deseja excluir este aluno? Esta ação não pode ser desfeita.'))
    window.location.href='/admin/aluno/'+mat+'/excluir';
}}

// Inicializa todas as células ao carregar
window.addEventListener('DOMContentLoaded', function() {{
  {init_js}
}});
</script>"""
    return page_shell(f"Editar — {titulo}", body)
