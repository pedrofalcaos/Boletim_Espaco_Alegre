"""Liquid Glass — sistema de design compartilhado (fontes modernas + efeito de
vidro líquido no estilo das interfaces mais recentes) usado em todas as
páginas do site: login, área dos pais, professoras, coordenação e admin."""

FONTS_LINK = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">"""

GLASS_BG_BLOBS = """<div class="lg-bg" aria-hidden="true">
  <span class="lg-blob lg-blob-1"></span>
  <span class="lg-blob lg-blob-2"></span>
  <span class="lg-blob lg-blob-3"></span>
</div>"""

# ── Avatar por iniciais ──────────────────────────────────────────────────────
# Em vez de foto enviada (dado sensível + armazenamento), gera um círculo
# colorido com as iniciais do nome. Cor estável por nome.
_AVATAR_CORES = ["#2b3990", "#0a7c3e", "#c25b0d", "#6a1a8a", "#b52222",
                 "#1a5fa8", "#0f766e", "#9333ea", "#be185d", "#0369a1"]


def _iniciais(nome: str) -> str:
    partes = [p for p in (nome or "").strip().split() if p]
    if not partes:
        return "?"
    if len(partes) == 1:
        return partes[0][:2].upper()
    return (partes[0][0] + partes[-1][0]).upper()


def avatar_iniciais(nome: str, size: int = 36, fonte: int = None) -> str:
    """Retorna um <span> circular com as iniciais do nome (cor estável)."""
    ini = _iniciais(nome)
    cor = _AVATAR_CORES[sum(ord(c) for c in (nome or "?")) % len(_AVATAR_CORES)]
    fs = fonte or max(10, int(size * 0.4))
    return (f'<span title="{nome}" style="display:inline-flex;align-items:center;justify-content:center;'
            f'width:{size}px;height:{size}px;min-width:{size}px;border-radius:50%;background:{cor};color:#fff;'
            f"font-family:'Nunito',sans-serif;font-weight:800;font-size:{fs}px;line-height:1;flex:none;"
            f'box-shadow:0 2px 6px rgba(0,0,0,.18);">{ini}</span>')


def avatar(nome: str, foto_url: str = None, size: int = 36, fonte: int = None) -> str:
    """Mostra a foto (se houver) num círculo; senão, cai no avatar de iniciais."""
    if foto_url:
        return (f'<img src="{foto_url}" alt="{nome}" title="{nome}" loading="lazy" '
                f'style="width:{size}px;height:{size}px;min-width:{size}px;border-radius:50%;'
                f'object-fit:cover;flex:none;box-shadow:0 2px 6px rgba(0,0,0,.18);background:#e8eaf8;">')
    return avatar_iniciais(nome, size=size, fonte=fonte)

# ── Tema claro/escuro ────────────────────────────────────────────────────────
# Botão flutuante + tema salvo por dispositivo (localStorage). TODAS as regras
# escuras ficam sob html[data-tema="dark"] e dentro de @media screen, de modo que
# o tema claro (padrão) e a impressão permanecem 100% inalterados.
TEMA_TOGGLE = """
<button class="tema-btn no-print" onclick="toggleTema()" title="Alternar tema claro/escuro" aria-label="Alternar tema claro/escuro"><span class="tema-ico">\U0001F319</span><span class="tema-txt">Modo escuro</span></button>
<style>
.tema-btn{position:fixed;bottom:18px;left:18px;z-index:9999;display:inline-flex;align-items:center;gap:8px;border:2px solid rgba(255,255,255,.3);border-radius:999px;background:#2b3990;color:#fff;font-family:'Nunito',sans-serif;font-weight:800;font-size:13px;line-height:1;padding:11px 18px;cursor:pointer;box-shadow:0 8px 22px rgba(0,0,0,.38);}
.tema-btn .tema-ico{font-size:16px;}
.tema-btn:hover{transform:translateY(-2px);}
@media print{.tema-btn{display:none!important;}}
@media screen{
  /* Paleta escura azul-marinho (coesa com o azul da escola). Sobrescreve as
     variáveis de cor para corrigir elementos que usam var(--azul) etc. */
  html[data-tema="dark"]{--azul:#7488f0;--azul-lt:#243056;--azul-md:#4a5890;
    --cinza-lt:#1d2540;--cinza-md:#3a4568;--cinza-dk:#cdd2e8;--borda:#3a4568;}
  html[data-tema="dark"] body{background:linear-gradient(160deg,#111733 0%,#141d3d 55%,#0f1c38 100%)!important;color:#dfe3f3!important;}
  html[data-tema="dark"] .lg-bg,html[data-tema="dark"] .lg-blob{opacity:.28!important;}
  html[data-tema="dark"] .tema-btn{background:#f7d800;color:#1a2570;border-color:rgba(0,0,0,.18);}
  /* cartões e caixas brancas */
  html[data-tema="dark"] [style*="background:#fff"],
  html[data-tema="dark"] [style*="background:#ffffff"],
  html[data-tema="dark"] [style*="background: #fff"],
  html[data-tema="dark"] .pagina,html[data-tema="dark"] .page{background:#1c2342!important;color:#e7eaf6!important;}
  /* áreas cinza-claras */
  html[data-tema="dark"] [style*="background:#f7f7f5"],
  html[data-tema="dark"] [style*="background:#f5f7ff"],
  html[data-tema="dark"] [style*="background:#fafafa"],
  html[data-tema="dark"] [style*="background:#f2f2f0"],
  html[data-tema="dark"] [style*="background:#f3f3f3"],
  html[data-tema="dark"] [style*="background:#f7f8ff"]{background:#232c4f!important;}
  /* cabeçalho de tabela / chips azul-claro */
  html[data-tema="dark"] [style*="background:#e8eaf8"]{background:#2a3565!important;color:#d3dbff!important;}
  /* textos escuros -> claros */
  html[data-tema="dark"] [style*="color:#333"],
  html[data-tema="dark"] [style*="color:#444"],
  html[data-tema="dark"] [style*="color:#555"],
  html[data-tema="dark"] [style*="color:#4a4a4a"],
  html[data-tema="dark"] [style*="color:#666"]{color:#d3d8ee!important;}
  html[data-tema="dark"] [style*="color:#777"],
  html[data-tema="dark"] [style*="color:#888"],
  html[data-tema="dark"] [style*="color:#999"],
  html[data-tema="dark"] [style*="color:#aaa"],
  html[data-tema="dark"] [style*="color:#bbb"],
  html[data-tema="dark"] [style*="color:#ccc"]{color:#a3abce!important;}
  /* azul de marca (hardcoded) -> azul claro legível */
  html[data-tema="dark"] [style*="color:#2b3990"]{color:#aab8ff!important;}
  html[data-tema="dark"] input,html[data-tema="dark"] select,html[data-tema="dark"] textarea{background:#232c4f!important;color:#eef0fa!important;border-color:#3a4568!important;}
  html[data-tema="dark"] table tr{border-color:#2e3760!important;}
}
</style>
<script>
(function(){var t=localStorage.getItem('tema')==='dark'?'dark':'light';document.documentElement.setAttribute('data-tema',t);})();
function _temaLabel(t){
  document.querySelectorAll('.tema-ico').forEach(function(e){e.textContent=t==='dark'?'☀️':'\U0001F319';});
  document.querySelectorAll('.tema-txt').forEach(function(e){e.textContent=t==='dark'?'Modo claro':'Modo escuro';});
}
function toggleTema(){var h=document.documentElement;var n=h.getAttribute('data-tema')==='dark'?'light':'dark';h.setAttribute('data-tema',n);try{localStorage.setItem('tema',n);}catch(e){}_temaLabel(n);}
document.addEventListener('DOMContentLoaded',function(){_temaLabel(document.documentElement.getAttribute('data-tema'));});
</script>"""

LIQUID_GLASS_CSS = """
:root{
  --lg-blur:22px;
  --lg-radius:22px;
  --lg-radius-sm:14px;
  --lg-border:rgba(255,255,255,.55);
  --lg-glass:rgba(255,255,255,.6);
  --lg-shadow:0 8px 32px rgba(26,37,112,.16), inset 0 1px 0 rgba(255,255,255,.65);
  --lg-shadow-sm:0 4px 18px rgba(26,37,112,.12);
  --lg-shadow-lift:0 16px 48px rgba(26,37,112,.22), inset 0 1px 0 rgba(255,255,255,.7);

  /* Escala tipográfica */
  --fs-display: clamp(28px, 5vw, 44px);
  --fs-h1: 24px;
  --fs-h2: 18px;
  --fs-h3: 15px;
  --fs-body: 14px;
  --fs-small: 12px;
  --fs-label: 10px;

  /* Espaçamento (escala 4px) */
  --space-1:4px; --space-2:8px; --space-3:12px;
  --space-4:16px; --space-5:24px; --space-6:32px; --space-7:48px;

  /* Cores de texto secundário com contraste adequado (substituem #aaa/#bbb/#ccc) */
  --text-secondary:#6b7094;
  --text-tertiary:#9a9db8;

  /* Raios padronizados */
  --radius-sm:12px; --radius-md:18px; --radius-lg:26px; --radius-pill:999px;
}
*{ -webkit-tap-highlight-color:transparent; }
body{
  font-family:'Plus Jakarta Sans','Nunito',sans-serif !important;
  -webkit-font-smoothing:antialiased;
  text-rendering:optimizeLegibility;
}
h1,h2,h3,.brand,.fredoka{ font-family:'Fredoka One','Plus Jakarta Sans',cursive,sans-serif; }

/* ── Fundo líquido com blobs animados ── */
.lg-bg{ position:fixed; inset:0; z-index:0; overflow:hidden; pointer-events:none; }
.lg-blob{ position:absolute; border-radius:50%; filter:blur(60px); opacity:.5; animation:lg-float 18s ease-in-out infinite; }
.lg-blob-1{ width:440px; height:440px; top:-130px; left:-110px; background:#6a7ff7; }
.lg-blob-2{ width:380px; height:380px; bottom:-150px; right:-90px; background:#f7d800; opacity:.32; animation-delay:-6s; }
.lg-blob-3{ width:320px; height:320px; top:42%; left:62%; background:#19c7b4; opacity:.28; animation-delay:-11s; }
@keyframes lg-float{
  0%,100%{ transform:translate(0,0) scale(1); }
  50%{ transform:translate(28px,-36px) scale(1.08); }
}
body>*:not(.lg-bg){ position:relative; z-index:1; }
@media (max-width:640px){
  .lg-blob{ filter:blur(38px); }
  .lg-blob-1,.lg-blob-2,.lg-blob-3{ width:230px; height:230px; }
}
@media (prefers-reduced-motion:reduce){ .lg-blob{ animation:none; } }

/* ── Retrofit: aplica vidro líquido sobre cartões/botões/inputs já existentes ── */
div[style*="background:#fff"],div[style*="background: #fff"],
div[style*="background:#ffffff"],div[style*="background: #ffffff"]{
  background:var(--lg-glass) !important;
  backdrop-filter:blur(var(--lg-blur)) saturate(180%) !important;
  -webkit-backdrop-filter:blur(var(--lg-blur)) saturate(180%) !important;
  border:1px solid var(--lg-border) !important;
  box-shadow:var(--lg-shadow) !important;
}
div[style*="border-radius:14px"],div[style*="border-radius:12px"],div[style*="border-radius:20px"],
div[style*="border-radius:16px"],div[style*="border-radius:10px"],div[style*="border-radius:9px"],
div[style*="border-radius:6px"],div[style*="border-radius:8px"]{
  border-radius:var(--lg-radius) !important;
}

button,input[type="submit"],a.btn,.btn{
  border-radius:999px !important;
  transition:transform .15s ease,box-shadow .15s ease,filter .15s ease !important;
}
button:hover,a.btn:hover,.btn:hover{ transform:translateY(-1px); filter:brightness(1.07); }
button:active,a.btn:active,.btn:active{ transform:translateY(0) scale(.98); }

button[style*="background:#2b3990"],button[style*="background: #2b3990"],
button[style*="background:var(--azul)"]{
  background:linear-gradient(135deg,#3b49b8,#1a2570) !important;
  box-shadow:0 6px 18px rgba(26,37,112,.35),inset 0 1px 0 rgba(255,255,255,.25) !important;
  border:none !important;
}

input[type="text"],input[type="password"],input[type="email"],input[type="number"],
input[type="date"],select,textarea{
  background:rgba(255,255,255,.55) !important;
  backdrop-filter:blur(10px) !important;
  -webkit-backdrop-filter:blur(10px) !important;
  border:1.5px solid rgba(43,57,144,.18) !important;
  border-radius:var(--lg-radius-sm) !important;
}
input:focus,select:focus,textarea:focus{
  border-color:#2b3990 !important;
  box-shadow:0 0 0 4px rgba(43,57,144,.14) !important;
  outline:none !important;
}

/* ── Contraste: substitui cinzas claros de baixo contraste por tokens legíveis ── */
[style*="color:#aaa"],[style*="color: #aaa"],
[style*="color:#bbb"],[style*="color: #bbb"],
[style*="color:#ccc"],[style*="color: #ccc"]{
  color:var(--text-secondary) !important;
}

/* ── Acessibilidade: foco sempre visível, mesmo sobre vidro ── */
button:focus-visible,a:focus-visible,.btn:focus-visible{
  outline:2px solid #2b3990 !important;
  outline-offset:2px !important;
}
input:focus-visible,select:focus-visible,textarea:focus-visible{
  outline:2px solid #2b3990 !important;
  outline-offset:1px !important;
}

@media print{
  .lg-bg{ display:none !important; }
  div[style*="background:#fff"],div[style*="background: #fff"],
  div[style*="background:#ffffff"]{
    background:#fff !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
    box-shadow:none !important; border:1px solid #ddd !important;
  }
}
"""
