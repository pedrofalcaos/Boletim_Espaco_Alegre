"""HTML otimizado para impressão/PDF do Relatório Semestral da Ed. Infantil."""

_COR_RESP = {
    "Sim":               ("#0a7c3e", "#e3f5ec"),
    "Não":               ("#b52222", "#fef2f2"),
    "Em desenvolvimento":("#c25b0d", "#fef0e4"),
}


def gerar_relatorio_print_html(
    aluno: dict,
    matricula: str,
    semestre: int,
    relatorio: dict,
    temas: list,
    respostas: dict,   # {subtema_id: resposta}
) -> str:
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

    # ── Temas e subtemas ──
    temas_html = ""
    for tema in temas:
        subtemas = tema.get("subtemas", [])
        if not subtemas:
            continue
        linhas = ""
        for i, st in enumerate(subtemas, 1):
            resp = respostas.get(st["id"], "")
            cor, bg = _COR_RESP.get(resp, ("#888", "#f5f5f5"))
            resp_label = resp if resp else "Não respondido"
            linhas += f"""
<tr style="border-bottom:1px solid #eee;">
  <td style="padding:6px 10px;font-size:11px;color:#555;width:28px;text-align:center;">{i}</td>
  <td style="padding:6px 10px;font-size:12px;color:#333;">{st['descricao']}</td>
  <td style="padding:6px 10px;text-align:center;white-space:nowrap;">
    <span style="background:{bg};color:{cor};font-size:10px;font-weight:800;
                 padding:2px 10px;border-radius:12px;border:1px solid {cor}30;">
      {resp_label}
    </span>
  </td>
</tr>"""

        temas_html += f"""
<div style="margin-bottom:18px;break-inside:avoid;">
  <div style="background:#2b3990;color:#fff;font-family:'Fredoka One',cursive;
              font-size:13px;padding:7px 14px;border-radius:6px 6px 0 0;">
    {tema['nome']}
  </div>
  <table style="width:100%;border-collapse:collapse;border:1px solid #ddd;border-top:none;
                border-radius:0 0 6px 6px;overflow:hidden;">
    <thead>
      <tr style="background:#f7f7f5;font-size:9px;font-weight:800;text-transform:uppercase;
                 letter-spacing:.4px;color:#aaa;">
        <th style="padding:5px 10px;width:28px;">#</th>
        <th style="padding:5px 10px;text-align:left;">Critério</th>
        <th style="padding:5px 10px;width:140px;">Avaliação</th>
      </tr>
    </thead>
    <tbody>{linhas}</tbody>
  </table>
</div>"""

    # ── Descrição final ──
    desc_html = f"""
<div style="margin-bottom:20px;break-inside:avoid;">
  <div style="background:#2b3990;color:#fff;font-family:'Fredoka One',cursive;
              font-size:13px;padding:7px 14px;border-radius:6px 6px 0 0;">
    Descrição Final do Semestre
  </div>
  <div style="border:1px solid #ddd;border-top:none;border-radius:0 0 6px 6px;
              padding:14px;font-size:12px;color:#333;line-height:1.7;min-height:80px;">
    {descricao or '<span style="color:#aaa;">Não preenchida.</span>'}
  </div>
</div>"""

    # ── Assinaturas ──
    assinaturas = """
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:20px;margin-top:32px;break-inside:avoid;">
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

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Semestral — {nome}</title>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700;800&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Nunito',sans-serif;background:#fff;color:#333;}}
.pagina{{max-width:750px;margin:0 auto;padding:28px 32px;}}
@media print{{
  body{{margin:0;}}
  .pagina{{max-width:100%;padding:16px 20px;}}
  .no-print{{display:none!important;}}
  @page{{size:A4 portrait;margin:15mm 12mm;}}
}}
</style>
</head>
<body>
<div class="pagina">

  <!-- Botão imprimir -->
  <div class="no-print" style="text-align:right;margin-bottom:16px;">
    <button onclick="window.print()"
      style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:800;
             background:#2b3990;color:#fff;border:none;border-radius:8px;
             padding:9px 22px;cursor:pointer;">
      🖨️ Imprimir / Salvar PDF
    </button>
    <button onclick="window.history.back()"
      style="font-family:'Nunito',sans-serif;font-size:13px;font-weight:700;
             background:#f7f7f5;color:#555;border:1px solid #ddd;border-radius:8px;
             padding:9px 18px;cursor:pointer;margin-left:8px;">
      ← Voltar
    </button>
  </div>

  <!-- Cabeçalho -->
  <div style="display:flex;align-items:center;gap:16px;margin-bottom:20px;
              border-bottom:3px solid #2b3990;padding-bottom:14px;">
    <img src="/static/logo.jpg" style="height:60px;object-fit:contain;" alt="Logo">
    <div style="flex:1;">
      <div style="font-family:'Fredoka One',cursive;font-size:18px;color:#2b3990;">
        Escola Espaço Alegre
      </div>
      <div style="font-size:11px;color:#888;margin-top:2px;">
        Ed. Infantil e Fundamental Anos Iniciais &nbsp;|&nbsp; Bilíngue
      </div>
      <div style="font-family:'Fredoka One',cursive;font-size:14px;color:#f7d800;
                  background:#2b3990;display:inline-block;padding:2px 12px;
                  border-radius:4px;margin-top:6px;">
        Relatório Semestral — {sem_label} / {ano}
      </div>
    </div>
  </div>

  <!-- Dados do aluno -->
  <div style="background:#f7f7f5;border-radius:8px;padding:12px 16px;margin-bottom:20px;
              display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;">
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
                border-top:1px solid #e0e0e0;padding-top:8px;margin-top:4px;">
      <span style="font-size:11px;color:#888;">Matrícula: <strong>{matricula}</strong></span>
      {confirmado_info}
    </div>
  </div>

  <!-- Temas e subtemas -->
  {temas_html}

  <!-- Descrição final -->
  {desc_html}

  <!-- Assinaturas -->
  {assinaturas}

</div>
</body>
</html>"""
