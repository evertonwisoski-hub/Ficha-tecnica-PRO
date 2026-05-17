"""
Migracao: Adicionar campo percentual_quebra na tabela fichas_tecnicas
"""
import sqlite3
from pathlib import Path

def migrar_adicionar_quebra():
    """Adiciona campo percentual_quebra se nao existir"""
    
    db_path = Path(__file__).parent / 'ficha_tecnica.db'
    
    if not db_path.exists():
        print("Banco nao encontrado, sera criado na primeira execucao")
        return True
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    try:
        # Verificar se coluna ja existe
        cursor.execute("PRAGMA table_info(fichas_tecnicas)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'percentual_quebra' not in colunas:
            print("Adicionando coluna percentual_quebra...")
            cursor.execute("""
                ALTER TABLE fichas_tecnicas 
                ADD COLUMN percentual_quebra NUMERIC(5, 2) DEFAULT 0
            """)
            conn.commit()
            print("Coluna adicionada com sucesso!")
        else:
            print("Coluna percentual_quebra ja existe")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"Erro na migracao: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    migrar_adicionar_quebra()
