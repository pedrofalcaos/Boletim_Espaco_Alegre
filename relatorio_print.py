"""HTML otimizado para impressão/PDF do Relatório Semestral da Ed. Infantil."""
from design_system import FONTS_LINK, GLASS_BG_BLOBS, LIQUID_GLASS_CSS
from icons import ICON_PRINTER

# _HTML_HEAD usa .format(), então chaves literais do CSS importado precisam
# ser escapadas (dobradas) antes de entrar no template.
_FONTS_LINK_ESC = FONTS_LINK.replace("{", "{{").replace("}", "}}")
_GLASS_BG_BLOBS_ESC = GLASS_BG_BLOBS.replace("{", "{{").replace("}", "}}")
_LIQUID_GLASS_CSS_ESC = LIQUID_GLASS_CSS.replace("{", "{{").replace("}", "}}")

_COR_RESP = {
    "CA": ("#0a7c3e", "#e3f5ec"),
    "CC": ("#2b3990", "#e8eaf8"),
    "ED": ("#c25b0d", "#fef0e4"),
}

_LEGENDA_RESP = {
    "CA": "Com Autonomia",
    "CC": "Com Colaboração",
    "ED": "Em Desenvolvimento",
}


def _pagina_relatorio_html(
    aluno: dict,
    matricula: str,
    semestre: int,
    relatorio: dict,
    temas: list,
    respostas: dict,   # {subtema_id: resposta}
) -> str:
    """Conteúdo de uma página de relatório (cabeçalho, dados, temas, descrição,
    assinaturas) — sem o shell HTML, para poder ser reutilizado tanto na
    impressão individual quanto na impressão de vários alunos em sequência."""
    nome       = aluno.get("nome", "")
    turma      = aluno.get("turma", "")
    periodo    = aluno.get("periodo", "")
    professora = aluno.get("professora", "")
    ano        = aluno.get("ano_letivo", "2026")
    sem_label  = "1º Semestre" if semestre == 1 else "2º Semestre"
    descricao  = relatorio.get("descricao_final", "")
    confirmado = relatorio.get("confirmado_em", "")
    if confirmado and isinstance(confirmado, str):
        confirmado = confirmado[:10]  # só a data

    # ── Tópicos → Temas → Subtemas ──
    # temas é lista de tópicos: [{id, nome, temas:[{id, nome, subtemas:[...]}]}]
    temas_html = ""
    for topico in temas:
        temas_do_topico = topico.get("temas", [])
        if not temas_do_topico:
            continue
        subtemas_bloco = ""
        for tema in temas_do_topico:
            subtemas = tema.get("subtemas", [])
            if not subtemas:
                continue
            linhas = ""
            for i, st in enumerate(subtemas, 1):
                resp = respostas.get(st["id"], "")
                cor, bg = _COR_RESP.get(resp, ("#888", "#f5f5f5"))
                resp_label = f"{resp} — {_LEGENDA_RESP[resp]}" if resp in _LEGENDA_RESP else "Não respondido"
                linhas += f"""
<tr style="border-bottom:1px solid #eee;break-inside:avoid;page-break-inside:avoid;">
  <td style="padding:3px 8px;font-size:11px;color:#555;width:24px;text-align:center;">{i}</td>
  <td style="padding:3px 8px;font-size:11px;color:#333;">{st['descricao']}</td>
  <td style="padding:3px 8px;text-align:center;white-space:nowrap;">
    <span style="background:{bg};color:{cor};font-size:10px;font-weight:800;
                 padding:2px 9px;border-radius:12px;border:1px solid {cor}30;">
      {resp_label}
    </span>
  </td>
</tr>"""
            subtemas_bloco += f"""
<div style="margin-bottom:8px;border-left:3px solid #f7d800;padding-left:10px;break-inside:avoid;page-break-inside:avoid;">
  <div style="font-family:'Fredoka One',cursive;font-size:11px;color:#2b3990;
              padding:3px 0 5px;text-transform:uppercase;letter-spacing:.3px;">
    🏷️ {tema['nome']}
  </div>
  <table style="width:100%;border-collapse:collapse;font-size:11px;">
    <thead>
      <tr style="background:#f7f7f5;font-size:9px;font-weight:800;text-transform:uppercase;
                 letter-spacing:.3px;color:#aaa;">
        <th style="padding:3px 8px;width:24px;">#</th>
        <th style="padding:3px 8px;text-align:left;">Critério</th>
        <th style="padding:3px 8px;width:130px;">Avaliação</th>
      </tr>
    </thead>
    <tbody>{linhas}</tbody>
  </table>
</div>"""

        temas_html += f"""
<div style="margin-bottom:12px;">
  <div style="background:#2b3990;color:#fff;font-family:'Fredoka One',cursive;
              font-size:13px;padding:6px 14px;border-radius:6px 6px 0 0;break-after:avoid;page-break-after:avoid;">
    📂 {topico['nome']}
  </div>
  <div style="border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px;
              padding:8px 12px;">
    {subtemas_bloco}
  </div>
</div>"""

    # ── Descrição final ──
    desc_html = f"""
<div style="margin-bottom:14px;">
  <div style="background:#2b3990;color:#fff;font-family:'Fredoka One',cursive;
              font-size:13px;padding:6px 14px;border-radius:6px 6px 0 0;break-after:avoid;page-break-after:avoid;">
    Descrição Final do Semestre
  </div>
  <div class="desc-rendered" style="border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px;
              padding:14px;font-size:12px;color:#333;line-height:1.6;min-height:60px;">
    {descricao or '<span style="color:#aaa;">Não preenchida.</span>'}
  </div>
</div>"""

    # ── Assinaturas ──
    assinaturas = """
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:20px;break-inside:avoid;page-break-inside:avoid;">
  <div style="text-align:center;">
    <div style="border-top:1.5px solid #333;padding-top:6px;font-size:11px;color:#555;">
      Professora
    </div>
  </div>
  <div style="text-align:center;">
    <div style="border-top:1.5px solid #333;padding-top:6px;font-size:11px;color:#555;">
      Coordenação Pedagógica
    </div>
  </div>
  <div style="text-align:center;">
    <div style="border-top:1.5px solid #333;padding-top:6px;font-size:11px;color:#555;">
      Responsável pelo Aluno
    </div>
  </div>
</div>"""

    confirmado_info = f'<span style="font-size:10px;color:#0a7c3e;font-weight:700;">✔ Confirmado em {confirmado}</span>' if confirmado else ""

    return f"""
  <!-- Cabeçalho -->
  <div style="display:flex;align-items:center;gap:14px;margin-bottom:12px;
              border-bottom:3px solid #2b3990;padding-bottom:10px;break-inside:avoid;page-break-inside:avoid;">
    <img src="/static/logo.png" style="height:48px;object-fit:contain;" alt="Logo">
    <div style="flex:1;">
      <div style="font-family:'Fredoka One',cursive;font-size:16px;color:#2b3990;">
        Escola Espaço Alegre
      </div>
      <div style="font-size:10px;color:#888;margin-top:1px;">
        Ed. Infantil e Fundamental Anos Iniciais &nbsp;|&nbsp; Bilíngue
      </div>
      <div style="font-family:'Fredoka One',cursive;font-size:13px;color:#f7d800;
                  background:#2b3990;display:inline-block;padding:2px 12px;
                  border-radius:4px;margin-top:5px;">
        Relatório Semestral — {sem_label} / {ano}
      </div>
    </div>
  </div>

  <!-- Dados do aluno -->
  <div style="background:#f7f7f5;border-radius:8px;padding:10px 16px;margin-bottom:12px;
              display:grid;grid-template-columns:1fr 1fr 1fr;gap:6px;break-inside:avoid;page-break-inside:avoid;">
    <div>
      <div style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;">Aluno(a)</div>
      <div style="font-size:13px;font-weight:800;color:#2b3990;margin-top:2px;">{nome}</div>
    </div>
    <div>
      <div style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;">Turma / Período</div>
      <div style="font-size:13px;font-weight:700;color:#333;margin-top:2px;">{turma} — {periodo}</div>
    </div>
    <div>
      <div style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;color:#aaa;">Professora</div>
      <div style="font-size:13px;font-weight:700;color:#333;margin-top:2px;">{professora}</div>
    </div>
    <div style="grid-column:span 3;display:flex;justify-content:space-between;align-items:center;
                border-top:1px solid #e0e0e0;padding-top:6px;margin-top:2px;">
      <span style="font-size:11px;color:#888;">Matrícula: <strong>{matricula}</strong></span>
      {confirmado_info}
    </div>
  </div>

  <!-- Legenda de avaliação -->
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:10px;
              padding:8px 14px;background:#f7f7f5;border-radius:8px;border:1px solid #e0e0e0;
              break-inside:avoid;page-break-inside:avoid;">
    <span style="font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:.5px;
                 color:#aaa;white-space:nowrap;margin-right:4px;">Legenda:</span>
    <span style="background:#e3f5ec;color:#0a7c3e;font-size:10px;font-weight:800;
                 padding:2px 10px;border-radius:12px;border:1px solid #a8ddc0;white-space:nowrap;">
      CA — Com Autonomia
    </span>
    <span style="background:#e8eaf8;color:#2b3990;font-size:10px;font-weight:800;
                 padding:2px 10px;border-radius:12px;border:1px solid #b0b8e8;white-space:nowrap;">
      CC — Com Colaboração
    </span>
    <span style="background:#fef0e4;color:#c25b0d;font-size:10px;font-weight:800;
                 padding:2px 10px;border-radius:12px;border:1px solid #f8d4a8;white-space:nowrap;">
      ED — Em Desenvolvimento
    </span>
  </div>

  <!-- Temas e subtemas -->
  {temas_html}

  <!-- Descrição final -->
  {desc_html}

  <!-- Assinaturas -->
  {assinaturas}
"""


_HTML_HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
""" + _FONTS_LINK_ESC + """
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Plus Jakarta Sans','Nunito',sans-serif;-webkit-font-smoothing:antialiased;
  background:linear-gradient(160deg,#e9ecfb 0%,#d8dcf2 45%,#cfe7f0 100%);color:#333;
  min-height:100vh;padding:18px 0 36px;position:relative;overflow-x:hidden;}}
.pagina{{max-width:750px;margin:0 auto 22px;padding:26px 30px;position:relative;z-index:1;
  background:rgba(255,255,255,.66);backdrop-filter:blur(24px) saturate(180%);
  -webkit-backdrop-filter:blur(24px) saturate(180%);
  border:1px solid rgba(255,255,255,.55);border-radius:22px;
  box-shadow:0 12px 40px rgba(43,57,144,.18),inset 0 1px 0 rgba(255,255,255,.6);}}
@media print{{
  body{{margin:0;padding:0;background:#fff;}}
  .lg-bg{{display:none!important;}}
  .pagina{{max-width:100%;padding:0;margin:0;background:#fff!important;backdrop-filter:none!important;
    -webkit-backdrop-filter:none!important;border:none!important;box-shadow:none!important;border-radius:0!important;}}
  .no-print{{display:none!important;}}
  @page{{size:A4 portrait;margin:10mm 10mm;}}
}}
.pagina + .pagina{{page-break-before:always;}}
.desc-rendered{{text-align:justify;text-justify:inter-word;}}
.desc-rendered p{{margin:0 0 8px 0;}}
.desc-rendered ul,.desc-rendered ol{{margin:0 0 8px 22px;padding:0;}}
.desc-rendered li{{margin-bottom:3px;}}
.desc-rendered img{{max-width:100%;}}
@media (max-width:640px){{
  .pagina{{margin:0 12px 18px;padding:18px 16px;border-radius:18px;}}
}}
""" + _LIQUID_GLASS_CSS_ESC + """
</style>
</head>
<body>
""" + _GLASS_BG_BLOBS_ESC + """
<div class="no-print" style="text-align:right;margin-bottom:16px;padding:0 16px;position:relative;z-index:1;">
  <button onclick="window.print()"
    style="font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:13px;font-weight:800;
           background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;border:none;border-radius:999px;
           padding:10px 24px;cursor:pointer;box-shadow:0 6px 18px rgba(26,37,112,.35);">
    """ + ICON_PRINTER + """Imprimir / Salvar PDF
  </button>
  <button onclick="window.history.back()"
    style="font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:13px;font-weight:700;
           background:rgba(255,255,255,.55);color:#555;border:1px solid #ddd;border-radius:999px;
           padding:10px 20px;cursor:pointer;margin-left:8px;">
    ← Voltar
  </button>
</div>
{paginas}
</body>
</html>"""


def gerar_relatorio_print_html(
    aluno: dict,
    matricula: str,
    semestre: int,
    relatorio: dict,
    temas: list,
    respostas: dict,   # {subtema_id: resposta}
) -> str:
    """Impressão de um único relatório (aluno + semestre)."""
    corpo = _pagina_relatorio_html(aluno, matricula, semestre, relatorio, temas, respostas)
    nome = aluno.get("nome", "")
    return _HTML_HEAD.format(
        titulo=f"Relatório Semestral — {nome}",
        paginas=f'<div class="pagina">{corpo}</div>',
    )


def gerar_relatorios_aluno_print_html(aluno: dict, matricula: str, itens: list) -> str:
    """Impressão combinada dos relatórios de um único aluno (ex.: 1º e 2º semestre
    confirmados), usada na área pública do responsável — todas as páginas saem
    no mesmo documento/PDF, uma por semestre, mantendo a continuidade entre elas.

    itens: lista de tuplas (semestre, relatorio, temas, respostas).
    """
    nome = aluno.get("nome", "")
    paginas = "".join(
        f'<div class="pagina">{_pagina_relatorio_html(aluno, matricula, semestre, relatorio, temas, respostas)}</div>'
        for semestre, relatorio, temas, respostas in itens
    )
    if not paginas:
        paginas = '<div class="pagina"><p style="text-align:center;color:#888;padding:40px;">Nenhum relatório confirmado pela coordenação ainda. Assim que o relatório semestral for concluído, ele ficará disponível aqui.</p></div>'
    return _HTML_HEAD.format(
        titulo=f"Relatório Semestral — {nome}",
        paginas=paginas,
    )


def gerar_relatorios_print_html_multiplos(itens: list, semestre: int) -> str:
    """Impressão em lote de vários relatórios em sequência (uma página por aluno).

    itens: lista de tuplas (aluno, matricula, relatorio, temas, respostas).
    """
    sem_label = "1º Semestre" if semestre == 1 else "2º Semestre"
    paginas = "".join(
        f'<div class="pagina">{_pagina_relatorio_html(aluno, matricula, semestre, relatorio, temas, respostas)}</div>'
        for aluno, matricula, relatorio, temas, respostas in itens
    )
    if not paginas:
        paginas = '<div class="pagina"><p style="text-align:center;color:#888;padding:40px;">Nenhum relatório encontrado para os filtros selecionados.</p></div>'
    return _HTML_HEAD.format(
        titulo=f"Relatórios Semestrais — {sem_label}",
        paginas=paginas,
    )
