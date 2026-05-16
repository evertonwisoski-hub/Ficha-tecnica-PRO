"""
Migração: Adiciona coluna logo_path na tabela clientes
"""
import sqlite3
import os

def migrar_banco():
    """Adiciona coluna logo_path se não existir"""
    
    # Verifica se banco existe
    if not os.path.exists('ficha_tecnica.db'):
        print("✅ Banco ainda não existe, será criado na primeira execução")
        return
    
    conn = sqlite3.connect('ficha_tecnica.db')
    cursor = conn.cursor()
    
    try:
        # Verifica se coluna já existe
        cursor.execute("PRAGMA table_info(clientes)")
        colunas = [col[1] for col in cursor.fetchall()]
        
        if 'logo_path' not in colunas:
            print("Adicionando coluna logo_path...")
            cursor.execute("ALTER TABLE clientes ADD COLUMN logo_path VARCHAR(500)")
            conn.commit()
            print("✅ Coluna logo_path adicionada com sucesso!")
        else:
            print("✅ Coluna logo_path já existe")
    
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        conn.rollback()
    
    finally:
        conn.close()

if __name__ == "__main__":
    migrar_banco()
