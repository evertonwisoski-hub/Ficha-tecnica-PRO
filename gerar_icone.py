"""
Gerador de Ícone .ICO
Converte SVG em arquivo .ico com múltiplas resoluções
"""
try:
    from PIL import Image, ImageDraw, ImageFont
    import io
except ImportError:
    print("Instalando Pillow...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'pillow'])
    from PIL import Image, ImageDraw, ImageFont
    import io

def criar_icone():
    """Cria ícone .ico com múltiplas resoluções"""
    
    # Tamanhos padrão de ícone do Windows
    tamanhos = [16, 32, 48, 64, 128, 256]
    imagens = []
    
    for tamanho in tamanhos:
        # Cria imagem com fundo transparente
        img = Image.new('RGBA', (tamanho, tamanho), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Círculo de fundo (verde)
        margem = int(tamanho * 0.05)
        draw.ellipse([margem, margem, tamanho-margem, tamanho-margem], 
                     fill=(76, 175, 80, 255))
        
        # Retângulo branco (prancheta)
        rect_margem = int(tamanho * 0.27)
        rect_width = int(tamanho * 0.45)
        rect_height = int(tamanho * 0.58)
        draw.rectangle([rect_margem, rect_margem, rect_margem+rect_width, rect_margem+rect_height],
                      fill=(255, 255, 255, 255), outline=(150, 150, 150, 255), width=max(1, int(tamanho/64)))
        
        # Clipe superior (laranja)
        clip_y = int(tamanho * 0.20)
        clip_width = int(tamanho * 0.20)
        clip_height = int(tamanho * 0.08)
        clip_x = (tamanho - clip_width) // 2
        draw.rounded_rectangle([clip_x, clip_y, clip_x+clip_width, clip_y+clip_height],
                              radius=max(2, int(tamanho/32)), fill=(255, 183, 77, 255))
        
        # Linhas da receita
        if tamanho >= 32:
            line_y = int(tamanho * 0.38)
            line_x = int(tamanho * 0.33)
            line_width = int(tamanho * 0.33)
            line_spacing = max(3, int(tamanho * 0.06))
            line_thickness = max(1, int(tamanho/64))
            
            # Linha título (verde)
            draw.rectangle([line_x, line_y, line_x+line_width, line_y+line_thickness*2],
                          fill=(76, 175, 80, 255))
            
            # Linhas de texto (cinza)
            for i in range(1, 4):
                y = line_y + (i * line_spacing)
                w = int(line_width * (0.7 + (i * 0.05)))
                draw.rectangle([line_x, y, line_x+w, y+line_thickness],
                              fill=(158, 158, 158, 255))
        
        # Símbolo R$ na parte inferior
        if tamanho >= 48:
            try:
                # Tenta usar fonte do sistema
                font_size = int(tamanho * 0.25)
                font = ImageFont.truetype("arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = "R$"
            # Calcula posição centralizada
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = (tamanho - text_width) // 2
            text_y = int(tamanho * 0.68)
            
            draw.text((text_x, text_y), text, fill=(76, 175, 80, 255), font=font)
        
        imagens.append(img)
    
    # Salva como .ico com múltiplas resoluções
    imagens[0].save(
        'icone.ico',
        format='ICO',
        sizes=[(img.width, img.height) for img in imagens],
        append_images=imagens[1:]
    )
    
    print("✅ Ícone criado com sucesso: icone.ico")
    print(f"   Resoluções: {', '.join([f'{t}x{t}' for t in tamanhos])}")

if __name__ == "__main__":
    criar_icone()
