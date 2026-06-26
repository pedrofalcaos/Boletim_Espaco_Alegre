"""
Recortador de foto no navegador (zoom + arrastar) antes de enviar.

Quando o usuário escolhe uma imagem, abre um modal com um círculo do tamanho
exato em que a foto vai aparecer; ele arrasta para posicionar e usa o controle
para dar zoom. Ao confirmar, a área recortada é exportada em 400×400 e enviada
para a mesma rota de upload (campo 'foto') via fetch — sem dependências externas.

Como usar nos formulários: troque o <input type=file> por
  <input type="file" accept="image/*" data-action="/rota/de/upload"
         onchange="abrirCropper(this)">
"""

FOTO_CROPPER_HTML = """
<div id="crop-modal" class="no-print" style="display:none;position:fixed;inset:0;z-index:10000;
     background:rgba(15,20,45,.62);-webkit-backdrop-filter:blur(5px);backdrop-filter:blur(5px);
     align-items:center;justify-content:center;padding:18px;">
  <div style="background:#fff;border-radius:22px;padding:22px 22px 18px;max-width:340px;width:100%;
       text-align:center;box-shadow:0 26px 72px rgba(10,15,50,.5);">
    <div style="font-family:'Fredoka One',cursive;color:#2b3990;font-size:18px;">Ajustar foto</div>
    <div style="font-size:11.5px;color:#888;margin:4px 0 14px;">Arraste para posicionar e use a barra para dar zoom.</div>
    <div style="position:relative;width:280px;height:280px;margin:0 auto;border-radius:50%;overflow:hidden;
         box-shadow:0 0 0 3px #2b3990,0 10px 26px rgba(0,0,0,.22);background:#eef1fb;">
      <canvas id="crop-canvas" width="280" height="280" style="touch-action:none;cursor:grab;display:block;"></canvas>
    </div>
    <input id="crop-zoom" type="range" oninput="zoomCropper(this.value)"
      style="width:100%;margin:16px 0 4px;cursor:pointer;accent-color:#2b3990;">
    <div style="font-size:10px;color:#aaa;margin-bottom:12px;">🔍 zoom</div>
    <div style="display:flex;gap:8px;">
      <button type="button" onclick="fecharCropper()"
        style="flex:1;background:#f3f3f3;color:#666;border:none;border-radius:11px;padding:12px;
               font-family:'Nunito',sans-serif;font-weight:800;font-size:13px;cursor:pointer;">Cancelar</button>
      <button type="button" id="crop-enviar" onclick="enviarCropper(this)"
        style="flex:1.5;background:linear-gradient(135deg,#3b49b8,#1a2570);color:#fff;border:none;border-radius:11px;
               padding:12px;font-family:'Nunito',sans-serif;font-weight:800;font-size:13px;cursor:pointer;">Enviar foto</button>
    </div>
  </div>
</div>
<script>
(function(){
  var img=new Image(), scale=1, minScale=1, tx=0, ty=0, action='', drag=false, lx=0, ly=0;
  var VP=280, OUT=400;
  function el(id){return document.getElementById(id);}
  function ctx(){return el('crop-canvas').getContext('2d');}
  function clamp(){
    var w=img.naturalWidth*scale, h=img.naturalHeight*scale;
    if(tx>0)tx=0; if(ty>0)ty=0;
    if(tx<VP-w)tx=VP-w; if(ty<VP-h)ty=VP-h;
  }
  function draw(){
    var g=ctx(); g.clearRect(0,0,VP,VP);
    g.drawImage(img, tx, ty, img.naturalWidth*scale, img.naturalHeight*scale);
  }
  window.abrirCropper=function(input){
    if(!input.files||!input.files[0])return;
    var f=input.files[0];
    if(!/^image\\//.test(f.type)){alert('Selecione uma imagem (JPG, PNG ou WEBP).');return;}
    if(f.size>8*1024*1024){alert('Imagem muito grande (máximo 8 MB).');return;}
    action=input.getAttribute('data-action');
    var rd=new FileReader();
    rd.onload=function(e){
      img=new Image();
      img.onload=function(){
        minScale=Math.max(VP/img.naturalWidth, VP/img.naturalHeight);
        scale=minScale;
        tx=(VP-img.naturalWidth*scale)/2; ty=(VP-img.naturalHeight*scale)/2;
        var z=el('crop-zoom'); z.min=minScale; z.max=minScale*4; z.step=minScale/40; z.value=scale;
        el('crop-modal').style.display='flex';
        draw();
      };
      img.src=e.target.result;
    };
    rd.readAsDataURL(f);
    input.value='';
  };
  window.fecharCropper=function(){el('crop-modal').style.display='none';};
  window.zoomCropper=function(v){
    var nv=parseFloat(v), cx=VP/2, cy=VP/2, k=nv/scale;
    tx=cx-(cx-tx)*k; ty=cy-(cy-ty)*k; scale=nv; clamp(); draw();
  };
  window.enviarCropper=function(btn){
    btn.disabled=true; btn.textContent='Enviando…';
    var out=document.createElement('canvas'); out.width=OUT; out.height=OUT;
    var g=out.getContext('2d'), r=OUT/VP;
    g.fillStyle='#ffffff'; g.fillRect(0,0,OUT,OUT);
    g.drawImage(img, tx*r, ty*r, img.naturalWidth*scale*r, img.naturalHeight*scale*r);
    out.toBlob(function(blob){
      var fd=new FormData(); fd.append('foto', blob, 'foto.jpg');
      fetch(action,{method:'POST',body:fd}).then(function(resp){
        window.location.href = resp.url || window.location.href;
      }).catch(function(){ btn.disabled=false; btn.textContent='Enviar foto'; alert('Falha no envio. Tente novamente.'); });
    },'image/jpeg',0.9);
  };
  document.addEventListener('DOMContentLoaded',function(){
    var c=el('crop-canvas'); if(!c)return;
    function pos(e){var r=c.getBoundingClientRect();var p=e.touches?e.touches[0]:e;return [p.clientX-r.left,p.clientY-r.top];}
    function down(e){drag=true;var p=pos(e);lx=p[0];ly=p[1];}
    function move(e){if(!drag)return;var p=pos(e);tx+=p[0]-lx;ty+=p[1]-ly;lx=p[0];ly=p[1];clamp();draw();if(e.touches)e.preventDefault();}
    function up(){drag=false;}
    c.addEventListener('mousedown',down); window.addEventListener('mousemove',move); window.addEventListener('mouseup',up);
    c.addEventListener('touchstart',down,{passive:true}); c.addEventListener('touchmove',move,{passive:false}); c.addEventListener('touchend',up);
  });
})();
</script>"""
