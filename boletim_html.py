import re, os
from design_system import FONTS_LINK, GLASS_BG_BLOBS, LIQUID_GLASS_CSS
from icons import ICON_PRINTER, icon_printer

DISCIPLINAS = [
    'Língua Portuguesa','Matemática','História','Geografia',
    'Ciências','Arte','Educação Física',
    'Língua Estrangeira – Inglês','Produção Textual',
]
MEDIA_MIN = 7.0

def arred(v): return round(v*100)/100
def fmt(v):   return '–' if v is None else f"{v:.1f}"

def calc_media(p, g):
    if not p or not g: return None
    try: return arred((float(p)+float(g))/2)
    except: return None

def calc_rec(base, rec):
    if base is None: return None
    if not rec: return base
    try: return max(base, arred((base+float(rec))/2))
    except: return base

def color_cls(v):
    if v is None: return 'na'
    return 'ap' if v >= MEDIA_MIN else 'rep'

def sit_txt(v):
    if v is None: return '–'
    return 'Aprovado' if v >= MEDIA_MIN else 'Reprovado'

def gerar_tbody(notas_aluno):
    rows = []
    for disc in DISCIPLINAS:
        n  = notas_aluno.get(disc, {})
        p1=n.get('p1',''); gl1=n.get('gl1','')
        p2=n.get('p2',''); gl2=n.get('gl2','')
        p3=n.get('p3',''); gl3=n.get('gl3','')

        b1=calc_media(p1,gl1); ef1=calc_rec(b1,n.get('r1',''))
        b2=calc_media(p2,gl2); ef2=calc_rec(b2,n.get('r2',''))
        b3=calc_media(p3,gl3); ef3=calc_rec(b3,n.get('r3',''))
        mfano = arred((ef1+ef2+ef3)/3) if ef1 and ef2 and ef3 else None
        mfef  = calc_rec(mfano, n.get('rf',''))

        def tdv(v): return f'<td class="calc {color_cls(v)}">{fmt(v)}</td>'
        def tdp(v): return f'<td class="nota-val">{v if v else "–"}</td>'

        rows.append(f'''<tr>
<td class="disc-name">{disc}</td>
{tdp(p1)}{tdp(gl1)}{tdv(b1)}<td class="nota-val {'rec-val' if n.get('r1') else ''}">{n.get('r1','–') or '–'}</td>{tdv(ef1)}
{tdp(p2)}{tdp(gl2)}{tdv(b2)}<td class="nota-val {'rec-val' if n.get('r2') else ''}">{n.get('r2','–') or '–'}</td>{tdv(ef2)}
{tdp(p3)}{tdp(gl3)}{tdv(b3)}<td class="nota-val {'rec-val' if n.get('r3') else ''}">{n.get('r3','–') or '–'}</td>{tdv(ef3)}
{tdv(mfano)}<td class="nota-val {'rec-val' if n.get('rf') else ''}">{n.get('rf','–') or '–'}</td>
{tdv(mfef)}<td class="{color_cls(mfef)} sit-txt">{sit_txt(mfef)}</td>
</tr>''')
    return '\n'.join(rows)

def _calc_freq(aluno: dict):
    freq = aluno.get('frequencia', {})
    ta = str(freq.get('total_aulas','')).strip()
    tf = str(freq.get('total_faltas','')).strip()
    if ta and tf:
        try:
            aulas_n = float(ta); faltas_n = float(tf)
            if aulas_n > 0:
                pct = (aulas_n - faltas_n) / aulas_n * 100
                max_f = int(aulas_n * 0.25)
                pct_str   = f"{pct:.1f}%"
                max_str   = str(max_f)
                pct_color = 'var(--verde)' if pct >= 75 else 'var(--vermelho)'
                badge     = ('<span class="sit-badge sit-ok">Freq. OK ✓</span>'
                             if pct >= 75 else
                             '<span class="sit-badge sit-rep-freq">Freq. Insuf. ✗</span>')
                return ta, tf, pct_str, max_str, pct_color, badge
        except: pass
    return (ta or '–'), (tf or '–'), '–', '–', '#aaa', '<span class="sit-badge sit-vazio">A preencher</span>'

# ── CSS compartilhado ────────────────────────────────────────────────────────
_CSS = """
*{box-sizing:border-box;margin:0;padding:0}
:root{
  --azul:#2b3990;--azul-lt:#e8eaf8;--azul-md:#b0b8e8;
  --amarelo:#f7d800;--amarelo-dk:#c8ab00;
  --cinza-lt:#f7f7f5;--cinza-md:#dcdcd8;--cinza-dk:#4a4a4a;
  --verde:#0a7c3e;--verde-lt:#e3f5ec;
  --vermelho:#b52222;--laranja:#c25b0d;--laranja-lt:#fef0e4;
  --roxo:#6a1a8a;--roxo-lt:#f5eafc;--borda:#c8c8c4;
}

/* ── Base ── */
body{font-family:'Plus Jakarta Sans','Nunito',sans-serif;-webkit-font-smoothing:antialiased;
  background:linear-gradient(160deg,#e9ecfb 0%,#d8dcf2 45%,#cfe7f0 100%);min-height:100vh;
  display:flex;flex-direction:column;align-items:center;padding:24px 12px;gap:16px;
  position:relative;overflow-x:hidden;}

/* ── Topbar ── */
.topbar{
  width:100%;max-width:960px;
  display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;
  background:rgba(255,255,255,.62);backdrop-filter:blur(22px) saturate(180%);
  -webkit-backdrop-filter:blur(22px) saturate(180%);
  border:1px solid rgba(255,255,255,.55);border-radius:18px;padding:10px 20px;
  box-shadow:0 8px 28px rgba(43,57,144,.16),inset 0 1px 0 rgba(255,255,255,.6);
  position:relative;z-index:1;
}
.topbar-left{display:flex;align-items:center;gap:10px;flex-wrap:wrap;}
.back-btn{
  font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:13px;font-weight:800;
  background:var(--azul-lt);color:var(--azul);
  border:none;border-radius:999px;padding:7px 16px;cursor:pointer;
  text-decoration:none;display:inline-block;white-space:nowrap;
  transition:transform .15s ease,filter .15s ease;
}
.back-btn:hover{background:var(--azul-md);transform:translateY(-1px);}
.print-btn{
  font-family:'Plus Jakarta Sans','Nunito',sans-serif;font-size:13px;font-weight:800;
  background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;
  border:none;border-radius:999px;padding:7px 20px;cursor:pointer;
  white-space:nowrap;box-shadow:0 4px 14px rgba(26,37,112,.35);
  transition:transform .15s ease,filter .15s ease;
}
.print-btn:hover{filter:brightness(1.08);transform:translateY(-1px);}
.topbar span{font-size:12px;color:#888;}

/* ── Página ── */
.page{
  width:min(277mm, 100%);
  background:rgba(255,255,255,.66);
  backdrop-filter:blur(24px) saturate(180%);
  -webkit-backdrop-filter:blur(24px) saturate(180%);
  border:1px solid rgba(255,255,255,.55);
  border-radius:18px;
  box-shadow:0 12px 40px rgba(43,57,144,.22),inset 0 1px 0 rgba(255,255,255,.6);
  padding:6mm 8.5mm 5.5mm;
  position:relative;overflow:hidden;z-index:1;
}
.page::before{
  content:'';position:absolute;top:0;left:0;right:0;height:5px;
  background:linear-gradient(90deg,var(--azul) 0%,var(--amarelo) 50%,var(--azul) 100%);
}

/* ── Header ── */
.header{
  display:grid;grid-template-columns:128px 1fr auto;
  align-items:center;gap:8px;
  padding-bottom:3.5px;margin-bottom:3.5px;
  border-bottom:2.5px solid var(--amarelo);
}
.header-logo img{height:40px;max-width:126px;object-fit:contain;}
.header-center h1{font-family:'Fredoka One',cursive;font-size:15px;color:var(--azul);line-height:1.1;}
.header-center p{font-size:9px;color:#888;margin-top:2px;}
.header-right{text-align:right;}
.pill-azul{background:var(--azul);color:var(--amarelo);font-family:'Fredoka One',cursive;font-size:11px;padding:2px 11px;border-radius:20px;display:inline-block;margin-bottom:2px;}
.pill-amarelo{background:var(--amarelo);color:var(--azul);font-family:'Fredoka One',cursive;font-size:9.5px;padding:2px 9px;border-radius:20px;display:inline-block;}

/* ── Info do aluno ── */
.aluno-grid{
  display:grid;grid-template-columns:2fr 1fr 1.2fr 0.9fr;
  gap:2px 10px;padding:2.5px 0;margin-bottom:3px;
  border-bottom:1px solid var(--borda);
}
.field{display:flex;flex-direction:column;gap:1px;}
.field label{font-size:7.5px;text-transform:uppercase;letter-spacing:.6px;color:#aaa;font-weight:800;}
.field span{font-size:11px;font-weight:700;color:var(--azul);padding:2px 0;border-bottom:1.5px solid var(--borda);}

/* ── Tabela ── */
.table-scroll{
  overflow-x:auto;
  -webkit-overflow-scrolling:touch;
  margin:0 -2px;
  padding:0 2px;
}
table.notas{width:100%;border-collapse:collapse;font-size:8.5px;min-width:680px;}
table.notas th,table.notas td{padding:2px 1.5px;text-align:center;border:.5px solid var(--cinza-md);}
.disc-name{
  text-align:left!important;padding-left:4px!important;
  font-weight:700;font-size:8px;min-width:90px;
  position:sticky;left:0;z-index:2;
  background:#fff;
  box-shadow:2px 0 4px rgba(0,0,0,.06);
}
.nota-val{font-size:9px;font-weight:600;}
.rec-val{color:var(--laranja);font-weight:800;}

.th-trim{font-size:8px;font-weight:900;letter-spacing:.3px;text-transform:uppercase;padding:3.5px 2px!important;}
.th-t1{background:var(--azul);color:var(--amarelo);}
.th-t2{background:#1a6e30;color:#d8f5e4;}
.th-t3{background:#a34c00;color:#fef0e0;}
.th-rf{background:var(--roxo);color:#f0d8fa;}
.th-fin{background:#2a2a2a;color:#fff;}
.th-sub{font-size:7px;font-weight:800;text-transform:uppercase;letter-spacing:.1px;padding:1.5px!important;}
.th-sub-t1{background:var(--azul-lt);color:var(--azul);}
.th-sub-t2{background:var(--verde-lt);color:var(--verde);}
.th-sub-t3{background:var(--laranja-lt);color:var(--laranja);}
.th-sub-rf{background:var(--roxo-lt);color:var(--roxo);}
.th-sub-fin{background:#ebebeb;color:#333;}

/* cabeçalho fixo (sticky) da coluna disciplina */
table.notas thead tr:first-child th:first-child{
  position:sticky;left:0;z-index:4;background:#f2f2f0;
  box-shadow:2px 0 4px rgba(0,0,0,.06);
}
table.notas thead tr:last-child th:first-child{
  position:sticky;left:0;z-index:4;background:var(--azul-lt);
  box-shadow:2px 0 4px rgba(0,0,0,.06);
}

table.notas tbody tr:nth-child(even) td{background:var(--cinza-lt);}
table.notas tbody tr:nth-child(even) .disc-name{background:#efefed;}

td.calc{font-weight:800;font-size:9.5px;}
td.ap{color:var(--verde);} td.rep{color:var(--vermelho);} td.na{color:#ccc;font-size:8px;}
td.sit-txt{font-weight:800;font-size:9px;}

/* ── Legenda ── */
.legenda{display:flex;gap:8px;align-items:center;font-size:7px;color:#888;flex-wrap:wrap;margin-top:2.5px;}
.leg-dot{width:6px;height:6px;border-radius:50%;display:inline-block;margin-right:2px;}

/* ── Frequência ── */
.freq-bloco{
  background:var(--azul-lt);border:1px solid var(--azul-md);border-radius:7px;
  padding:4px 9px;display:grid;grid-template-columns:repeat(4,1fr) auto;
  gap:3px 9px;align-items:end;margin-top:3px;
}
.freq-field{display:flex;flex-direction:column;gap:1.5px;}
.freq-field label{font-size:7px;text-transform:uppercase;letter-spacing:.5px;color:var(--azul);font-weight:800;}
.freq-val{font-size:11.5px;font-weight:800;padding:1px 0;color:var(--cinza-dk);}
.sit-badge{font-family:'Fredoka One',cursive;font-size:11px;padding:3px 10px;border-radius:20px;white-space:nowrap;display:inline-block;}
.sit-ok{background:var(--verde);color:#fff;}
.sit-rep-freq{background:var(--vermelho);color:#fff;}
.sit-vazio{background:var(--cinza-md);color:#888;font-family:'Nunito',sans-serif;font-size:9.5px;font-weight:700;}
.freq-nota{font-size:7px;color:#888;margin-top:2px;font-style:italic;}

/* ── Rodapé / assinaturas ── */
.footer-area{margin-top:3px;padding-top:3px;border-top:2px solid var(--amarelo);}
.obs-box label{font-size:7.5px;text-transform:uppercase;letter-spacing:.5px;color:#aaa;font-weight:800;display:block;margin-bottom:2px;}
.obs-line{border-bottom:1px solid var(--borda);height:16px;margin-bottom:3px;}
.sign-row{display:grid;grid-template-columns:1.6fr 1.6fr 1fr;gap:0 16px;margin-top:5px;}
.sign-box{display:flex;flex-direction:column;}
.sign-label{font-size:7.5px;text-transform:uppercase;letter-spacing:.5px;color:#aaa;font-weight:800;}
.sign-space{height:28px;}
.sign-line{border-bottom:1px solid var(--borda);}
.sign-caption{font-size:7px;color:#bbb;margin-top:2px;font-style:italic;}

/* ══════════════════════════════════════
   RESPONSIVO — TELA (não afeta impressão)
   ══════════════════════════════════════ */
@media screen and (max-width:800px){
  body{padding:0;gap:0;background:#f0f1f7;}

  .topbar{
    border-radius:0;max-width:100%;
    padding:8px 12px;gap:8px;
    position:sticky;top:0;z-index:10;
  }
  .topbar span{font-size:11px;}

  .page{
    width:100%;border-radius:0;
    padding:10px 10px 14px;
    box-shadow:none;
  }

  /* Header: esconde pills, reduz logo */
  .header{grid-template-columns:44px 1fr;gap:6px;}
  .header-right{display:none;}
  .header-logo img{height:30px;max-width:42px;}
  .header-center h1{font-size:12px;}
  .header-center p{font-size:7.5px;}

  /* Info aluno: 2 colunas */
  .aluno-grid{grid-template-columns:1fr 1fr;gap:3px 8px;}
  .field label{font-size:7px;}
  .field span{font-size:10px;}

  /* Scroll hint */
  .table-scroll::before{
    content:'← deslize para ver mais →';
    display:block;font-size:10px;color:var(--azul);
    text-align:center;padding:3px 0 4px;font-weight:700;
    opacity:.7;
  }

  /* Frequência: 2+2+1 */
  .freq-bloco{
    grid-template-columns:1fr 1fr;
    grid-template-rows:auto auto auto;
  }
  .freq-bloco > div:last-child{grid-column:1/-1;justify-self:center;}

  /* Assinaturas: empilhadas */
  .sign-row{grid-template-columns:1fr;gap:10px 0;}
  .sign-space{height:20px;}
}

/* Landscape mobile: aproveita largura sem dica de scroll */
@media screen and (max-width:900px) and (orientation:landscape){
  body{padding:0 0 8px;}
  .topbar{border-radius:0;max-width:100%;padding:6px 14px;}
  .page{width:100%;border-radius:0;padding:8px 10px 10px;box-shadow:none;}
  .table-scroll::before{content:'';}
}

/* ══════════════════════════════════════
   IMPRESSÃO — A4 paisagem
   ══════════════════════════════════════ */
@media print{
  @page{size:A4 landscape;margin:0;}

  /* reset total do body — sem flex, sem padding, sem gap */
  html,body{
    display:block!important;
    width:297mm!important;
    padding:0!important;margin:0!important;gap:0!important;
    background:#fff!important;min-height:unset!important;
    align-items:unset!important;
  }

  .topbar{display:none!important;}
  .page{background:#fff!important;backdrop-filter:none!important;-webkit-backdrop-filter:none!important;border:none!important;}

  /* scroll hint e overflow */
  .table-scroll::before{display:none!important;}
  .table-scroll{overflow:visible!important;width:100%!important;}

  /* sticky desativado */
  .disc-name{position:static!important;box-shadow:none!important;}
  table.notas thead tr:first-child th:first-child,
  table.notas thead tr:last-child th:first-child{
    position:static!important;box-shadow:none!important;
  }
  table.notas{min-width:unset!important;width:100%!important;}

  /* página exata A4 landscape */
  .page{
    display:block!important;
    width:297mm!important;height:210mm!important;
    overflow:hidden!important;
    box-shadow:none!important;border-radius:0!important;
    padding:5mm 8mm 4mm!important;
    page-break-after:always!important;break-after:page!important;
  }
  /* último boletim NÃO cria página em branco extra */
  .page:last-child{
    page-break-after:avoid!important;break-after:avoid!important;
  }
  #print-modal{display:none!important;}

  /* restaura grids do layout de impressão */
  .header{grid-template-columns:128px 1fr auto!important;}
  .header-right{display:block!important;}
  .header-logo img{height:40px!important;max-width:126px!important;}
  .header-center h1{font-size:15px!important;}
  .header-center p{font-size:9px!important;}
  .aluno-grid{grid-template-columns:2fr 1fr 1.2fr 0.9fr!important;}
  .freq-bloco{grid-template-columns:repeat(4,1fr) auto!important;}
  .sign-row{grid-template-columns:1.6fr 1.6fr 1fr!important;}
  .sign-space{height:22px!important;}
  .lg-bg{display:none!important;}
}
""" + LIQUID_GLASS_CSS

# ── Gera apenas o div .page de um aluno ─────────────────────────────────────
def _gerar_pagina(aluno: dict) -> str:
    tbody   = gerar_tbody(aluno.get('notas', {}))
    nome    = aluno['nome']
    turma   = aluno['turma']
    periodo = aluno.get('periodo', '')
    prof    = aluno.get('professora', '')
    mat     = aluno.get('matricula', '')
    ano     = aluno.get('ano_letivo', '2026')
    obs     = aluno.get('observacoes', '').strip()

    ta, tf, pct_str, max_str, pct_color, freq_badge = _calc_freq(aluno)
    obs_conteudo = (f'<p style="font-size:9px;color:#444;padding:2px 0;">{obs}</p>'
                    if obs else '<div class="obs-line"></div>')

    return f'''<div class="page">
  <div class="header">
    <div class="header-logo"><img src="/static/logo.png" alt="Escola Espaço Alegre"></div>
    <div class="header-center">
      <h1>Escola Espaço Alegre</h1>
      <p>R. Manoel de Arruda Câmara, 54 – Prado, Recife &nbsp;|&nbsp; Tel: (81) 3227-3158</p>
      <p style="margin-top:1.5px;">Ed. Infantil e Fundamental Anos Iniciais &nbsp;·&nbsp; <span style="color:#2b3990;font-weight:800;">Escola Bilíngue</span></p>
    </div>
    <div class="header-right">
      <div class="pill-azul">Ano Letivo {ano}</div><br>
      <div class="pill-amarelo">BOLETIM ESCOLAR</div>
    </div>
  </div>

  <div class="aluno-grid">
    <div class="field"><label>Nome do(a) Aluno(a)</label><span>{nome}</span></div>
    <div class="field"><label>Turma / Série</label><span>{turma} – {periodo}</span></div>
    <div class="field"><label>Professor(a)</label><span>{prof}</span></div>
    <div class="field"><label>Matrícula</label><span>{mat}</span></div>
  </div>

  <div class="table-scroll">
  <table class="notas">
    <thead>
      <tr>
        <th rowspan="2" style="text-align:left;padding-left:4px;background:#f2f2f0;font-size:7px;color:#aaa;text-transform:uppercase;letter-spacing:.4px;vertical-align:middle;">Disciplina</th>
        <th class="th-trim th-t1" colspan="5">1º Trimestre</th>
        <th class="th-trim th-t2" colspan="5">2º Trimestre</th>
        <th class="th-trim th-t3" colspan="5">3º Trimestre</th>
        <th class="th-trim th-rf" colspan="2">Rec. Final</th>
        <th class="th-trim th-fin" colspan="2">Resultado</th>
      </tr>
      <tr>
        <th class="th-sub th-sub-t1">Parc.</th><th class="th-sub th-sub-t1">Global</th><th class="th-sub th-sub-t1">Méd.T1</th><th class="th-sub th-sub-t1">Rec.T1</th><th class="th-sub th-sub-t1">Ef.T1</th>
        <th class="th-sub th-sub-t2">Parc.</th><th class="th-sub th-sub-t2">Global</th><th class="th-sub th-sub-t2">Méd.T2</th><th class="th-sub th-sub-t2">Rec.T2</th><th class="th-sub th-sub-t2">Ef.T2</th>
        <th class="th-sub th-sub-t3">Parc.</th><th class="th-sub th-sub-t3">Global</th><th class="th-sub th-sub-t3">Méd.T3</th><th class="th-sub th-sub-t3">Rec.T3</th><th class="th-sub th-sub-t3">Ef.T3</th>
        <th class="th-sub th-sub-rf">M.Anual</th><th class="th-sub th-sub-rf">Rec.Fin</th>
        <th class="th-sub th-sub-fin">M.Final</th><th class="th-sub th-sub-fin">Situação</th>
      </tr>
    </thead>
    <tbody>{tbody}</tbody>
  </table>
  </div>

  <div class="legenda">
    <span><span class="leg-dot" style="background:var(--verde)"></span><strong>Aprovado</strong> ≥ 7,0</span>
    <span><span class="leg-dot" style="background:var(--vermelho)"></span><strong>Reprovado</strong> &lt; 7,0</span>
    <span style="font-style:italic;">Méd.Trim=(Parc+Global)÷2 | Rec=(Méd+Rec)÷2 | M.Anual=(Ef1+Ef2+Ef3)÷3 | Rec.Fin=(M.Anual+Rec)÷2</span>
  </div>

  <div class="freq-bloco">
    <div class="freq-field"><label>Total de Aulas</label><div class="freq-val">{ta}</div></div>
    <div class="freq-field"><label>Total de Faltas</label><div class="freq-val">{tf}</div></div>
    <div class="freq-field"><label>% Frequência</label><div class="freq-val" style="color:{pct_color};">{pct_str}</div></div>
    <div class="freq-field"><label>Máx. Faltas (25%)</label><div class="freq-val" style="color:var(--azul);font-size:9.5px;">{max_str}</div></div>
    <div class="freq-field" style="align-items:center;"><label>&nbsp;</label>{freq_badge}</div>
  </div>
  <div class="freq-nota">📋 Freq. mínima: <strong>75%</strong> (LDB 9.394/96, Art. 24 VI)</div>

  <div class="footer-area">
    <div class="obs-box">
      <label>Observações / Anotações Pedagógicas</label>
      {obs_conteudo}
    </div>
    <div class="sign-row">
      <div class="sign-box">
        <span class="sign-label">Professor(a) / Coordenador(a)</span>
        <div class="sign-space"></div><div class="sign-line"></div>
        <span class="sign-caption">Assinatura</span>
      </div>
      <div class="sign-box">
        <span class="sign-label">Responsável / Encarregado(a)</span>
        <div class="sign-space"></div><div class="sign-line"></div>
        <span class="sign-caption">Assinatura &nbsp;&nbsp;&nbsp; Data: ____/____/________</span>
      </div>
      <div class="sign-box">
        <span class="sign-label">Data de Entrega</span>
        <div class="sign-space"></div><div class="sign-line"></div>
        <span class="sign-caption">Carimbo / Rubrica da Escola</span>
      </div>
    </div>
  </div>
</div>'''

_MODAL_HTML = '''
<div id="print-modal" style="display:none;position:fixed;inset:0;background:rgba(0,0,0,.55);
     z-index:999;align-items:center;justify-content:center;padding:16px;">
  <div style="background:#fff;border-radius:18px;padding:28px 28px 20px;max-width:340px;
              width:100%;text-align:center;box-shadow:0 8px 40px rgba(0,0,0,.3);">
    <div style="color:#2b3990;margin-bottom:10px;">''' + icon_printer(40) + '''</div>
    <h3 style="font-family:\'Fredoka One\',cursive;color:#2b3990;font-size:19px;margin-bottom:10px;">
      Antes de imprimir
    </h3>
    <p style="font-size:13px;color:#555;line-height:1.6;margin-bottom:6px;">
      No diálogo de impressão, selecione:
    </p>
    <div style="background:#e8eaf8;border-radius:10px;padding:10px 14px;margin-bottom:16px;text-align:left;">
      <div style="font-size:13px;color:#2b3990;font-weight:800;margin-bottom:4px;">
        📄 Orientação → <strong>Paisagem</strong>
      </div>
      <div style="font-size:11px;color:#888;">Margens: Nenhuma &nbsp;·&nbsp; Tamanho: A4</div>
    </div>
    <button onclick="fecharEImprimir()"
      style="width:100%;background:#2b3990;color:#fff;border:none;border-radius:10px;
             padding:13px;font-family:\'Nunito\',sans-serif;font-size:14px;font-weight:900;
             cursor:pointer;margin-bottom:8px;">
      OK, continuar
    </button>
    <button onclick="document.getElementById(\'print-modal\').style.display=\'none\'"
      style="background:none;border:none;color:#aaa;font-size:12px;cursor:pointer;
             font-family:\'Nunito\',sans-serif;padding:4px;">
      Cancelar
    </button>
  </div>
</div>
<script>
function abrirImpressao(){
  var mobile=/Android|iPhone|iPad|iPod/i.test(navigator.userAgent);
  if(mobile){
    document.getElementById('print-modal').style.display='flex';
  } else {
    window.print();
  }
}
function fecharEImprimir(){
  document.getElementById('print-modal').style.display='none';
  setTimeout(function(){ window.print(); }, 120);
}
</script>'''

def _html_shell(title: str, topbar: str, pages: str, extra_html: str = '') -> str:
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{title}</title>
<link rel="icon" type="image/png" href="/static/favicon.png">
{FONTS_LINK}
<style>{_CSS}</style>
</head>
<body>
{GLASS_BG_BLOBS}
{topbar}
{extra_html}
{pages}
{_MODAL_HTML}
</body>
</html>'''

# ── Boletim individual ───────────────────────────────────────────────────────
def gerar_boletim_html(aluno: dict, back_url: str = '/', extra_html: str = '') -> str:
    nome    = aluno['nome']
    turma   = aluno['turma']
    periodo = aluno.get('periodo', '')
    topbar = f'''<div class="topbar">
  <div class="topbar-left">
    <a href="{back_url}" class="back-btn">← Voltar</a>
    <span>Boletim de <strong>{nome}</strong> — {turma} ({periodo})</span>
  </div>
  <button class="print-btn" onclick="abrirImpressao()">{ICON_PRINTER}Imprimir / Salvar PDF</button>
</div>'''
    return _html_shell(f'Boletim – {nome}', topbar, _gerar_pagina(aluno), extra_html=extra_html)

# ── Impressão em série (turma ou todos) ─────────────────────────────────────
def gerar_boletins_multiplos_html(alunos: list, titulo: str) -> str:
    n = len(alunos)
    topbar = f'''<div class="topbar">
  <div class="topbar-left">
    <a href="/admin" class="back-btn">← Painel Admin</a>
    <span><strong>{titulo}</strong> — {n} boletim(s)</span>
  </div>
  <button class="print-btn" onclick="abrirImpressao()">{ICON_PRINTER}Imprimir Todos ({n})</button>
</div>'''
    pages = '\n'.join(_gerar_pagina(a) for a in alunos)
    return _html_shell(f'Boletins – {titulo}', topbar, pages)
