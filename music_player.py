"""Tocador de música ambiente da escola — widget fixo com play/pause e volume,
reutilizado nas áreas dos pais, professoras e coordenação/admin."""

PLAYER_MUSICA_HTML = """
<style>@media print{ #player-musica{ display:none!important; } }</style>
<div id="player-musica" class="no-print" style="position:fixed;bottom:16px;right:16px;z-index:9999;
     background:#fff;border:1.5px solid #dcdcd8;border-radius:14px;
     box-shadow:0 4px 18px rgba(0,0,0,.18);padding:9px 14px;
     display:flex;align-items:center;gap:9px;font-family:'Nunito',sans-serif;">
  <audio id="audio-escola" src="/static/musica_escola.mp3" loop></audio>
  <button id="btn-musica" type="button" onclick="toggleMusica()" title="Pausar/tocar música"
    style="background:#2b3990;color:#fff;border:none;border-radius:50%;
           width:32px;height:32px;cursor:pointer;font-size:13px;flex:none;">⏸️</button>
  <input type="range" id="vol-musica" min="0" max="100" value="40" title="Volume da música"
    oninput="ajustarVolumeMusica(this.value)" style="width:74px;cursor:pointer;">
</div>
<script>
(function(){
  function $(id){ return document.getElementById(id); }
  window.ajustarVolumeMusica = function(v){
    var a = $('audio-escola');
    if (a) a.volume = v / 100;
    try { localStorage.setItem('ea_musica_vol', v); } catch(e){}
  };
  window.toggleMusica = function(){
    var a = $('audio-escola'), b = $('btn-musica');
    if (!a) return;
    if (a.paused) {
      a.play().catch(function(){});
      b.textContent = '⏸️';
      try { localStorage.setItem('ea_musica_tocando', '1'); } catch(e){}
    } else {
      a.pause();
      b.textContent = '▶️';
      try { localStorage.setItem('ea_musica_tocando', '0'); } catch(e){}
    }
  };
  document.addEventListener('DOMContentLoaded', function(){
    var a = $('audio-escola'), b = $('btn-musica'), vol = $('vol-musica');
    if (!a) return;
    var volSalvo = null, tocandoSalvo = null;
    try {
      volSalvo = localStorage.getItem('ea_musica_vol');
      tocandoSalvo = localStorage.getItem('ea_musica_tocando');
    } catch(e){}
    var v = volSalvo !== null ? parseInt(volSalvo, 10) : 40;
    a.volume = v / 100;
    if (vol) vol.value = v;
    if (tocandoSalvo !== '0') {
      a.play().catch(function(){ b.textContent = '▶️'; });
    } else {
      b.textContent = '▶️';
    }
  });
})();
</script>"""


def inject_player(html: str) -> str:
    """Injeta o tocador de música fixo (play/pause + volume) antes do </body>."""
    if "</body>" in html:
        return html.replace("</body>", PLAYER_MUSICA_HTML + "</body>", 1)
    return html + PLAYER_MUSICA_HTML
