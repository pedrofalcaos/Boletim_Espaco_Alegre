"""HTML otimizado para impressão/PDF do Relatório Semestral da Ed. Infantil."""
from design_system import FONTS_LINK, GLASS_BG_BLOBS, LIQUID_GLASS_CSS
from icons import ICON_PRINTER

# _HTML_HEAD usa .format(), então chaves literais do CSS importado precisam
# ser escapadas (dobradas) antes de entrar no template.
_FONTS_LINK_ESC = FONTS_LINK.replace("{", "{{").replace("}", "}}")
_GLASS_BG_BLOBS_ESC = GLASS_BG_BLOBS.replace("{", "{{").replace("}", "}}")
_LIQUID_GLASS_CSS_ESC = LIQUID_GLASS_CSS.replace("{", "{{").replace("}", "}}")

# Lembrete exibido antes de imprimir, para o navegador não inserir a URL na folha.
_MODAL_REL = """
<div id="print-modal-rel" class="no-print" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);z-index:999;align-items:center;justify-content:center;padding:16px;">
  <div style="background:#fff;border-radius:18px;padding:26px 26px 20px;max-width:360px;width:100%;text-align:center;box-shadow:0 8px 40px rgba(0,0,0,.3);">
    <div style="font-size:38px;margin-bottom:6px;">🖨️</div>
    <h3 style="font-family:'Fredoka One',cursive;color:#2b3990;font-size:18px;margin-bottom:10px;">Antes de imprimir</h3>
    <p style="font-size:13px;color:#555;line-height:1.6;margin-bottom:10px;">No diálogo de impressão, ajuste:</p>
    <div style="background:#e8eaf8;border-radius:10px;padding:11px 14px;margin-bottom:16px;text-align:left;">
      <div style="font-size:13px;color:#2b3990;font-weight:800;margin-bottom:5px;">📐 Margens &rarr; <strong>Nenhuma</strong></div>
      <div style="font-size:13px;color:#2b3990;font-weight:800;">🚫 Desmarque <strong>Cabe&ccedil;alhos e rodap&eacute;s</strong></div>
      <div style="font-size:11px;color:#888;margin-top:6px;">Assim o endere&ccedil;o do site n&atilde;o aparece na folha.</div>
    </div>
    <button onclick="fecharEImprimirRel()" style="width:100%;background:#2b3990;color:#fff;border:none;border-radius:10px;padding:12px;font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-weight:800;font-size:14px;cursor:pointer;margin-bottom:8px;">Imprimir agora</button>
    <button onclick="document.getElementById('print-modal-rel').style.display='none'" style="width:100%;background:#f3f3f3;color:#666;border:none;border-radius:10px;padding:10px;font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-weight:700;font-size:13px;cursor:pointer;">Cancelar</button>
  </div>
</div>
<script>
function abrirImpressaoRel(){document.getElementById('print-modal-rel').style.display='flex';}
function fecharEImprimirRel(){document.getElementById('print-modal-rel').style.display='none';setTimeout(function(){window.print();},150);}
</script>
"""
_MODAL_REL_ESC = _MODAL_REL.replace("{", "{{").replace("}", "}}")

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

    # ── Assinaturas ── (espaço extra acima para caber a assinatura à mão)
    assinaturas = """
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:52px;break-inside:avoid;page-break-inside:avoid;">
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

  <!-- Descrição final + assinaturas: mantidas no mesmo bloco para não se
       separarem na impressão; se não couberem, vão juntas para a próxima página -->
  <div style="break-inside:avoid;page-break-inside:avoid;">
    {desc_html}
    {assinaturas}
  </div>
"""


_HTML_HEAD = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>{titulo}</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
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
  /* Margem vai para o padding do conteúdo; a @page fica com margin:0 para o
     navegador NÃO imprimir cabeçalho/rodapé (URL, data, número de página). */
  .pagina{{max-width:100%;padding:11mm 12mm;margin:0;background:#fff!important;backdrop-filter:none!important;
    -webkit-backdrop-filter:none!important;border:none!important;box-shadow:none!important;border-radius:0!important;}}
  .no-print{{display:none!important;}}
  @page{{size:A4 portrait;margin:0;}}
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
  <button onclick="abrirImpressaoRel()"
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
{extra_top}
{paginas}
""" + _MODAL_REL_ESC + """
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
        extra_top="",
    )


def gerar_relatorios_aluno_print_html(aluno: dict, matricula: str, itens: list, extra_html: str = "") -> str:
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
        extra_top=extra_html,
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
        extra_top="",
    )


# ════════════════════════════════════════════════════════════════════════
#  ÁREA DO RESPONSÁVEL — escolha de semestre e mensagem de indisponível
# ════════════════════════════════════════════════════════════════════════
# CSS importado tem chaves literais; por isso montamos por concatenação (sem
# f-string) ao redor das constantes de design.
def _shell_responsavel(titulo: str, corpo: str, extra_html: str = "") -> str:
    cabeca = (
        '<!DOCTYPE html><html lang="pt-BR"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        '<link rel="icon" type="image/png" href="/static/favicon.png">'
        f'<title>{titulo}</title>'
    )
    estilo = (
        "<style>*{box-sizing:border-box;margin:0;padding:0}"
        "body{font-family:'Plus Jakarta Sans','Nunito',sans-serif;-webkit-font-smoothing:antialiased;"
        "background:linear-gradient(160deg,#e9ecfb 0%,#d8dcf2 45%,#cfe7f0 100%);color:#333;"
        "min-height:100vh;padding:26px 16px;position:relative;overflow-x:hidden;}"
        "</style>"
    )
    return (cabeca + FONTS_LINK + estilo + "</head><body>"
            + GLASS_BG_BLOBS + extra_html + corpo + "</body></html>")


def gerar_escolha_semestre_html(aluno: dict, matricula: str, disponivel: dict, extra_html: str = "") -> str:
    """Tela onde o responsável escolhe o semestre do relatório.
    disponivel: {1: bool, 2: bool} — se o relatório do semestre já está concluído."""
    nome  = aluno.get("nome", "")
    turma = aluno.get("turma", "")

    def _cartao(sem: int) -> str:
        ok = bool(disponivel.get(sem))
        if ok:
            badge = ('<span style="background:#e3f5ec;border:1px solid #a8ddc0;color:#0a7c3e;'
                     'font-size:11px;font-weight:800;padding:3px 12px;border-radius:20px;">✓ Disponível</span>')
            sub = "Toque para ver o relatório"
            seta = "Ver relatório →"
        else:
            badge = ('<span style="background:#fef0e4;border:1px solid #f8d4a8;color:#c25b0d;'
                     'font-size:11px;font-weight:800;padding:3px 12px;border-radius:20px;">⏳ Em breve</span>')
            sub = "Ainda não disponível"
            seta = "Saiba mais →"
        return (
            f'<a href="/relatorio/{matricula}/{sem}" '
            'style="flex:1;min-width:200px;text-decoration:none;display:block;'
            'background:rgba(255,255,255,.72);backdrop-filter:blur(20px) saturate(180%);'
            '-webkit-backdrop-filter:blur(20px) saturate(180%);border:1px solid rgba(255,255,255,.6);'
            'border-radius:20px;padding:24px 22px;box-shadow:0 12px 34px rgba(43,57,144,.16);'
            'transition:transform .15s,box-shadow .2s;">'
            '<div style="display:flex;align-items:center;justify-content:space-between;gap:8px;margin-bottom:12px;">'
            f'<span style="font-family:\'Fredoka One\',cursive;font-size:19px;color:#2b3990;">{sem}º Semestre</span>'
            f'{badge}</div>'
            f'<div style="font-size:13px;color:#5a6079;font-weight:600;margin-bottom:18px;">{sub}</div>'
            '<div style="display:inline-flex;align-items:center;gap:6px;background:linear-gradient(135deg,#3b49b8,#1a2570);'
            'color:#fff;font-weight:800;font-size:13px;padding:10px 20px;border-radius:999px;'
            f'box-shadow:0 6px 16px rgba(26,37,112,.3);">{seta}</div>'
            '</a>'
        )

    corpo = (
        '<div style="max-width:680px;margin:0 auto;position:relative;z-index:1;">'
        '<div style="text-align:center;margin-bottom:24px;">'
        '<img src="/static/logo.png" alt="Escola Espaço Alegre" '
        'style="height:58px;object-fit:contain;background:#fff;padding:10px 18px;border-radius:18px;'
        'box-shadow:0 8px 22px rgba(26,37,112,.18);margin-bottom:16px;">'
        '<h1 style="font-family:\'Fredoka One\',cursive;font-size:23px;color:#2b3990;line-height:1.3;">'
        'Relatório Semestral</h1>'
        f'<p style="font-size:14px;color:#5a6079;font-weight:600;margin-top:6px;">{nome} &nbsp;·&nbsp; {turma}</p>'
        '<p style="font-size:13px;color:#7d83a3;margin-top:4px;">Escolha o semestre que deseja visualizar:</p>'
        '</div>'
        '<div style="display:flex;gap:16px;flex-wrap:wrap;">'
        f'{_cartao(1)}{_cartao(2)}'
        '</div>'
        '<div style="text-align:center;margin-top:26px;">'
        '<a href="/" style="text-decoration:none;color:#2b3990;font-weight:700;font-size:13px;">← Voltar ao início</a>'
        '</div>'
        '</div>'
    )
    return _shell_responsavel(f"Relatório — {nome}", corpo, extra_html)


def gerar_relatorio_indisponivel_html(aluno: dict, matricula: str, semestre: int) -> str:
    """Mensagem amigável quando o relatório do semestre escolhido ainda não está
    disponível (não concluído pela coordenação)."""
    nome = aluno.get("nome", "")
    sem_label = f"{semestre}º semestre"
    corpo = (
        '<div style="max-width:460px;margin:0 auto;position:relative;z-index:1;text-align:center;">'
        '<div style="background:rgba(255,255,255,.72);backdrop-filter:blur(22px) saturate(180%);'
        '-webkit-backdrop-filter:blur(22px) saturate(180%);border:1px solid rgba(255,255,255,.6);'
        'border-radius:24px;padding:36px 30px;box-shadow:0 16px 44px rgba(43,57,144,.18);">'
        '<div style="font-size:46px;margin-bottom:10px;">⏳</div>'
        '<h1 style="font-family:\'Fredoka One\',cursive;font-size:21px;color:#2b3990;line-height:1.3;margin-bottom:12px;">'
        f'Relatório do {sem_label} ainda não disponível</h1>'
        '<p style="font-size:14px;color:#41476b;font-weight:600;line-height:1.7;">'
        f'O relatório do <strong>{sem_label}</strong> de {nome} ainda não foi finalizado pela coordenação. '
        'Assim que estiver pronto, ele aparecerá aqui para você. Volte um pouco mais tarde. 💛</p>'
        f'<a href="/relatorio/{matricula}" '
        'style="display:inline-block;margin-top:22px;text-decoration:none;background:#2b3990;color:#fff;'
        'font-weight:800;padding:12px 26px;border-radius:999px;font-size:14px;">← Escolher outro semestre</a>'
        '</div></div>'
    )
    return _shell_responsavel(f"Relatório indisponível — {nome}", corpo)
