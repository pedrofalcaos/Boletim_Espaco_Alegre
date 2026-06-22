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

LIQUID_GLASS_CSS = """
:root{
  --lg-blur:22px;
  --lg-radius:22px;
  --lg-radius-sm:14px;
  --lg-border:rgba(255,255,255,.55);
  --lg-glass:rgba(255,255,255,.6);
  --lg-shadow:0 8px 32px rgba(26,37,112,.16), inset 0 1px 0 rgba(255,255,255,.65);
  --lg-shadow-sm:0 4px 18px rgba(26,37,112,.12);
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

@media print{
  .lg-bg{ display:none !important; }
  div[style*="background:#fff"],div[style*="background: #fff"],
  div[style*="background:#ffffff"]{
    background:#fff !important; backdrop-filter:none !important; -webkit-backdrop-filter:none !important;
    box-shadow:none !important; border:1px solid #ddd !important;
  }
}
"""
