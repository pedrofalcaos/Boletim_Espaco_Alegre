"""HTML de todas as páginas."""

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
<body>{body}</body>
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
  </div>
</div>
</div>"""
    css = ".erro{background:var(--vermelho-lt);border:1px solid #fecaca;border-radius:8px;padding:10px 14px;margin-bottom:14px;font-size:12px;color:var(--vermelho);font-weight:700;text-align:center;}"
    return page_shell("Login — Escola Espaço Alegre", body, css)

# ── Dashboard admin ──────────────────────────────────────────────────────────
def admin_dashboard(alunos: dict, resetado: bool = False) -> str:
    # agrupar por turma
    turmas: dict = {}
    for mat, al in sorted(alunos.items(), key=lambda x: x[1]['nome']):
        t = al.get('turma','Sem turma')
        turmas.setdefault(t, []).append((mat, al))

    turma_blocks = ""
    for turma, lista in sorted(turmas.items()):
        rows = ""
        for mat, al in lista:
            nome = al['nome']
            prof = al.get('professora','–')
            # conta notas preenchidas
            total_notas = sum(1 for disc_n in al.get('notas',{}).values() for k in ('p1','gl1') if disc_n.get(k))
            badge_color = "var(--verde)" if total_notas >= 18 else ("var(--laranja)" if total_notas > 0 else "#ccc")
            rows += f"""
<tr>
  <td style="font-weight:700;color:var(--azul);">{mat}</td>
  <td>{nome}</td>
  <td style="font-size:12px;color:#888;">{prof}</td>
  <td style="text-align:center;">
    <span style="background:{badge_color};color:#fff;font-size:10px;font-weight:800;
                 padding:2px 9px;border-radius:20px;">{total_notas} notas</span>
  </td>
  <td style="text-align:center;">
    <a href="/admin/aluno/{mat}" style="background:var(--azul-lt);color:var(--azul);
       font-size:11px;font-weight:800;padding:4px 12px;border-radius:7px;display:inline-block;">
      ✏️ Editar
    </a>
    &nbsp;
    <a href="/boletim/{mat}" target="_blank" style="background:var(--verde-lt);color:var(--verde);
       font-size:11px;font-weight:800;padding:4px 12px;border-radius:7px;display:inline-block;">
      👁 Ver
    </a>
  </td>
</tr>"""
        turma_blocks += f"""
<div style="margin-bottom:24px;">
  <div style="font-family:'Fredoka One',cursive;font-size:16px;color:var(--azul);
              margin-bottom:8px;padding-left:4px;border-left:4px solid var(--amarelo);padding-left:10px;">
    {turma}
  </div>
  <div style="background:#fff;border-radius:12px;overflow:hidden;box-shadow:0 2px 10px rgba(0,0,0,.07);">
  <table style="width:100%;border-collapse:collapse;font-size:13px;">
    <thead>
      <tr style="background:var(--azul-lt);font-size:10px;font-weight:800;
                 text-transform:uppercase;letter-spacing:.5px;color:var(--azul);">
        <th style="padding:8px 12px;text-align:left;">Matrícula</th>
        <th style="padding:8px 12px;text-align:left;">Nome</th>
        <th style="padding:8px 12px;text-align:left;">Professor(a)</th>
        <th style="padding:8px 12px;text-align:center;">Notas T1</th>
        <th style="padding:8px 12px;text-align:center;">Ações</th>
      </tr>
    </thead>
    <tbody>{rows}</tbody>
  </table>
  </div>
</div>"""

    total = len(alunos)
    aviso_reset = '<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:10px;padding:11px 16px;margin-bottom:20px;font-size:12px;color:var(--verde);font-weight:700;">✔ Banco de dados resetado com sucesso!</div>' if resetado else ''
    body = f"""
<div style="max-width:960px;margin:0 auto;padding:24px 16px;">
  <!-- Header -->
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:24px;flex-wrap:wrap;">
    <img src="/static/logo.jpg" style="height:48px;object-fit:contain;">
    <div style="flex:1;">
      <h1 style="font-family:'Fredoka One',cursive;font-size:22px;color:var(--azul);">Painel Administrativo</h1>
      <p style="font-size:12px;color:#888;">{total} alunos cadastrados</p>
    </div>
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

  {aviso_reset}

  <!-- Aviso privacidade -->
  <div style="background:var(--azul-lt);border:1px solid var(--azul-md);border-radius:10px;
              padding:11px 16px;margin-bottom:20px;font-size:12px;color:var(--azul);">
    💡 <strong>Privacidade garantida:</strong> cada pai acessa apenas o boletim do próprio filho pelo número de matrícula.
    Nenhum pai consegue ver dados de outro aluno.
  </div>

  {turma_blocks}

  <!-- Reset banco -->
  <div style="background:var(--vermelho-lt);border:1px solid #fecaca;border-radius:12px;
              padding:16px 20px;margin-top:24px;">
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
        '1º Ano – A','1º Ano – B','2º Ano – A','2º Ano – B',
        '3º Ano – A','3º Ano – B','4º Ano – A','4º Ano – B',
        '5º Ano – A','5º Ano – B',
    ]
    PERIODOS = ['Manhã','Tarde','Noite']

    def sel(opts, cur):
        return ''.join(f'<option {"selected" if o==cur else ""}>{o}</option>' for o in opts)

    def nota_inp(disc, campo, label_short):
        val = aluno.get('notas',{}).get(disc,{}).get(campo,'')
        sid = disc.replace(' ','_').replace('–','_').replace('/','_')
        return f"""
        <div>
          <label style="font-size:8.5px;color:#aaa;font-weight:800;text-transform:uppercase;letter-spacing:.4px;display:block;margin-bottom:2px;">{label_short}</label>
          <input type="number" name="nota_{sid}_{campo}" value="{val}" min="0" max="10" step="0.1"
            placeholder="—"
            style="width:68px;font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;
                   text-align:center;padding:6px 4px;border:1.5px solid var(--borda);
                   border-radius:7px;outline:none;color:var(--azul);"
            onfocus="this.style.borderColor='var(--azul)'"
            onblur="this.style.borderColor='var(--borda)'">
        </div>"""

    # Linhas da tabela de notas
    disc_rows = ""
    T_COLORS = [
        ("T1","#2b3990","#f7d800"),
        ("T2","#1a6e30","#d8f5e4"),
        ("T3","#a34c00","#fef0e0"),
    ]
    for disc in DISCIPLINAS:
        cells = f'<td style="font-weight:700;font-size:13px;color:var(--cinza-dk);padding:8px 12px;min-width:160px;">{disc}</td>'
        for t_label, t_bg, t_fg in T_COLORS:
            n = t_label[-1]  # "1","2","3"
            cells += f"""
            <td style="padding:6px 10px;">
              <div style="display:flex;gap:8px;align-items:flex-end;">
                {nota_inp(disc, f'p{n}', 'Parcial')}
                {nota_inp(disc, f'gl{n}', 'Global')}
                {nota_inp(disc, f'r{n}', 'Rec.')}
              </div>
            </td>"""
        cells += f'<td style="padding:6px 10px;">{nota_inp(disc,"rf","Rec. Final")}</td>'
        disc_rows += f"<tr style='border-bottom:.5px solid var(--cinza-md);'>{cells}</tr>"

    freq = aluno.get('frequencia', {})
    obs  = aluno.get('observacoes','')
    msg_html = f'<div style="background:#e3f5ec;border:1px solid #a8ddc0;border-radius:8px;padding:10px 14px;margin-bottom:16px;font-size:13px;color:var(--verde);font-weight:700;">✔ {msg}</div>' if msg else ''

    titulo = "Novo Aluno" if novo else aluno.get('nome','Aluno')
    mat_readonly = 'readonly style="background:#f5f5f5;color:#aaa;"' if not novo else ''

    header_cols = '<th style="text-align:left;padding:8px 12px;background:#f2f2f0;font-size:10px;color:#aaa;font-weight:800;text-transform:uppercase;min-width:160px;">Disciplina</th>'
    for t_label, t_bg, t_fg in T_COLORS:
        header_cols += f'<th style="padding:8px 12px;background:{t_bg};color:{t_fg};font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.3px;">{t_label} (Parcial · Global · Rec.)</th>'
    header_cols += '<th style="padding:8px 12px;background:#6a1a8a;color:#f0d8fa;font-size:11px;font-weight:900;text-transform:uppercase;letter-spacing:.3px;">Rec. Final</th>'

    body = f"""
<div style="max-width:1080px;margin:0 auto;padding:24px 16px;">
  <!-- Nav -->
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:20px;flex-wrap:wrap;">
    <a href="/admin" style="background:var(--azul-lt);color:var(--azul);font-weight:800;font-size:12px;padding:7px 14px;border-radius:8px;">← Painel</a>
    <h1 style="font-family:'Fredoka One',cursive;font-size:20px;color:var(--azul);">{titulo}</h1>
    {"" if novo else f'<a href="/boletim/{matricula}" target="_blank" style="margin-left:auto;background:var(--verde-lt);color:var(--verde);font-weight:800;font-size:12px;padding:7px 14px;border-radius:8px;">👁 Ver Boletim</a>'}
  </div>

  {msg_html}

  <form method="POST" action="/admin/aluno/{matricula if not novo else 'novo'}/salvar">

    <!-- Dados cadastrais -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        👤 Dados do Aluno
      </div>
      <div style="display:grid;grid-template-columns:1fr 1fr 1fr 1fr 1fr;gap:12px 16px;">
        <div style="grid-column:span 2;">
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Nome Completo</label>
          <input name="nome" value="{aluno.get('nome','')}" required
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Matrícula</label>
          <input name="matricula" value="{matricula if not novo else ''}" {mat_readonly} required
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Turma</label>
          <select name="turma"
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;background:#fff;">
            {sel(TURMAS, aluno.get('turma',''))}
          </select>
        </div>
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Período</label>
          <select name="periodo"
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;background:#fff;">
            {sel(PERIODOS, aluno.get('periodo',''))}
          </select>
        </div>
        <div style="grid-column:span 2;">
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Professor(a)</label>
          <input name="professora" value="{aluno.get('professora','')}"
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Ano Letivo</label>
          <input name="ano_letivo" value="{aluno.get('ano_letivo','2026')}"
            style="width:100%;font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;color:var(--azul);
                   padding:8px 12px;border:1.5px solid var(--borda);border-radius:8px;outline:none;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
      </div>
    </div>

    <!-- Notas -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        📊 Notas por Disciplina
      </div>
      <div style="overflow-x:auto;">
      <table style="border-collapse:collapse;width:100%;">
        <thead><tr>{header_cols}</tr></thead>
        <tbody>{disc_rows}</tbody>
      </table>
      </div>
      <p style="font-size:11px;color:#aaa;margin-top:10px;font-style:italic;">
        * Rec. = Nota de recuperação. Preencher apenas se o aluno foi à recuperação naquele trimestre.
      </p>
    </div>

    <!-- Frequência -->
    <div style="background:#fff;border-radius:14px;padding:20px 24px;margin-bottom:18px;box-shadow:0 2px 10px rgba(0,0,0,.07);">
      <div style="font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);margin-bottom:14px;border-bottom:2px solid var(--amarelo);padding-bottom:6px;">
        📋 Frequência
      </div>
      <div style="display:flex;gap:20px;flex-wrap:wrap;align-items:flex-end;">
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Total de Aulas no Ano</label>
          <input name="total_aulas" type="number" min="0" value="{freq.get('total_aulas','')}" placeholder="ex: 200"
            style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;color:var(--azul);
                   padding:8px 14px;border:1.5px solid var(--borda);border-radius:8px;outline:none;width:160px;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div>
          <label style="font-size:10px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#aaa;display:block;margin-bottom:4px;">Total de Faltas</label>
          <input name="total_faltas" type="number" min="0" value="{freq.get('total_faltas','')}" placeholder="0"
            style="font-family:'Nunito',sans-serif;font-size:14px;font-weight:800;color:var(--azul);
                   padding:8px 14px;border:1.5px solid var(--borda);border-radius:8px;outline:none;width:140px;"
            onfocus="this.style.borderColor='var(--azul)'" onblur="this.style.borderColor='var(--borda)'">
        </div>
        <div style="font-size:12px;color:#888;padding-bottom:8px;">
          Mín. legal: <strong>75%</strong> de frequência (LDB 9.394/96)
        </div>
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
               background:var(--azul);color:#fff;border:none;border-radius:10px;
               padding:12px 32px;cursor:pointer;">
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
function confirmarExclusao(mat){{
  if(confirm('Tem certeza que deseja excluir este aluno? Esta ação não pode ser desfeita.')){{
    window.location.href='/admin/aluno/'+mat+'/excluir';
  }}
}}
</script>"""
    return page_shell(f"Editar — {titulo}", body)
