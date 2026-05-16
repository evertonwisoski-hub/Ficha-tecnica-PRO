"""
Gerenciador de Logos dos Clientes
"""
import os
from pathlib import Path
from PIL import Image
import io


def criar_pasta_logos():
    """Cria pasta para armazenar logos se não existir"""
    pasta = Path("logos_clientes")
    if not pasta.exists():
        pasta.mkdir()
    return pasta


def salvar_logo_cliente(cliente_id, arquivo_upload):
    """
    Salva logo do cliente
    
    Args:
        cliente_id: ID do cliente
        arquivo_upload: Arquivo de upload do Streamlit
    
    Returns:
        Caminho relativo do arquivo salvo
    """
    pasta = criar_pasta_logos()
    
    # Nome do arquivo
    extensao = arquivo_upload.name.split('.')[-1].lower()
    nome_arquivo = f"cliente_{cliente_id}.{extensao}"
    caminho_completo = pasta / nome_arquivo
    
    # Abre e redimensiona imagem
    try:
        img = Image.open(arquivo_upload)
        
        # Converte para RGB se necessário (remove transparência)
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Redimensiona mantendo proporção (máx 800x600)
        img.thumbnail((800, 600), Image.Resampling.LANCZOS)
        
        # Salva
        img.save(str(caminho_completo), quality=95, optimize=True)
        
        return str(caminho_completo)
    
    except Exception as e:
        print(f"Erro ao salvar logo: {e}")
        return None


def carregar_logo_cliente(caminho_logo):
    """
    Carrega logo do cliente
    
    Args:
        caminho_logo: Caminho do arquivo
    
    Returns:
        Imagem PIL ou None
    """
    if not caminho_logo or not os.path.exists(caminho_logo):
        return None
    
    try:
        return Image.open(caminho_logo)
    except:
        return None


def deletar_logo_cliente(caminho_logo):
    """Deleta logo do cliente"""
    if caminho_logo and os.path.exists(caminho_logo):
        try:
            os.remove(caminho_logo)
            return True
        except:
            pass
    return False


def obter_logo_como_bytes(caminho_logo, formato='PNG'):
    """
    Retorna logo como bytes para inserir em PDF/Excel
    
    Args:
        caminho_logo: Caminho do arquivo
        formato: Formato de saída (PNG, JPEG)
    
    Returns:
        bytes da imagem ou None
    """
    img = carregar_logo_cliente(caminho_logo)
    if not img:
        return None
    
    output = io.BytesIO()
    
    # Redimensiona para tamanho adequado para impressão
    img.thumbnail((300, 200), Image.Resampling.LANCZOS)
    
    # Salva como bytes
    img.save(output, format=formato, quality=95)
    output.seek(0)
    
    return output.read()
