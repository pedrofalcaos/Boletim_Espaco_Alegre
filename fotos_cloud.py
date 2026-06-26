"""
Upload de fotos para o Cloudinary (equipe e alunos).

Configurado por variáveis de ambiente no Railway:
  CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

Se não estiver configurado (ex.: desenvolvimento local), o upload fica
desativado e o sistema continua usando o avatar de iniciais como fallback.
"""
import os

_CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME", "")
_API_KEY    = os.environ.get("CLOUDINARY_API_KEY", "")
_API_SECRET = os.environ.get("CLOUDINARY_API_SECRET", "")

MAX_FOTO_BYTES = 8 * 1024 * 1024  # 8 MB
TIPOS_ACEITOS = ("image/jpeg", "image/png", "image/webp")

_pronto = False


def cloud_ativo() -> bool:
    """True quando as credenciais do Cloudinary estão configuradas."""
    return bool(_CLOUD_NAME and _API_KEY and _API_SECRET)


def _config():
    global _pronto
    if _pronto:
        return
    import cloudinary
    cloudinary.config(
        cloud_name=_CLOUD_NAME, api_key=_API_KEY, api_secret=_API_SECRET,
        secure=True,
    )
    _pronto = True


def _validar(conteudo: bytes) -> str | None:
    """Retorna mensagem de erro ou None se a imagem for válida."""
    if not conteudo:
        return "O arquivo está vazio."
    if len(conteudo) > MAX_FOTO_BYTES:
        return "Imagem muito grande (máximo 8 MB)."
    # Assinaturas de imagem comuns
    if conteudo[:3] == b"\xff\xd8\xff":            # JPEG
        return None
    if conteudo[:8] == b"\x89PNG\r\n\x1a\n":       # PNG
        return None
    if conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":  # WEBP
        return None
    return "Envie uma imagem JPG, PNG ou WEBP."


def upload_foto(conteudo: bytes, public_id: str) -> tuple[str | None, str | None]:
    """Envia a imagem ao Cloudinary recortada em quadrado (com foco no rosto).
    Retorna (url, erro). Sobrescreve a foto anterior do mesmo public_id."""
    if not cloud_ativo():
        return None, "Upload de fotos ainda não configurado (Cloudinary)."
    erro = _validar(conteudo)
    if erro:
        return None, erro
    try:
        _config()
        import cloudinary.uploader
        res = cloudinary.uploader.upload(
            conteudo,
            public_id=public_id,
            folder="escola_espaco_alegre",
            overwrite=True,
            invalidate=True,
            resource_type="image",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
            ],
        )
        return res.get("secure_url"), None
    except Exception:
        return None, "Falha ao enviar a imagem. Tente novamente."
