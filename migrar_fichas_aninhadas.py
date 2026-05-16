"""
Script de Migração - Fichas Técnicas Aninhadas
Adiciona suporte para usar fichas como ingredientes
"""
import sqlite3
from datetime import datetime

def migrar_banco(db_path='ficha_tecnica.db'):
    """Migra banco de dados para suportar fichas aninhadas"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔄 Iniciando migração do banco de dados...")
    
    try:
        # 1. Adicionar colunas em fichas_tecnicas
        print("\n1. Adicionando colunas em fichas_tecnicas...")
        
        try:
            cursor.execute("ALTER TABLE fichas_tecnicas ADD COLUMN rendimento_gramas REAL DEFAULT 0")
            print("   ✅ Coluna 'rendimento_gramas' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  Coluna 'rendimento_gramas' já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE fichas_tecnicas ADD COLUMN eh_intermediaria INTEGER DEFAULT 0")
            print("   ✅ Coluna 'eh_intermediaria' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  Coluna 'eh_intermediaria' já existe")
            else:
                raise
        
        # 2. Adicionar colunas em itens_ficha_tecnica
        print("\n2. Adicionando colunas em itens_ficha_tecnica...")
        
        try:
            cursor.execute("ALTER TABLE itens_ficha_tecnica ADD COLUMN tipo_item TEXT DEFAULT 'insumo'")
            print("   ✅ Coluna 'tipo_item' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  Coluna 'tipo_item' já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE itens_ficha_tecnica ADD COLUMN ficha_ingrediente_id INTEGER")
            print("   ✅ Coluna 'ficha_ingrediente_id' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  Coluna 'ficha_ingrediente_id' já existe")
            else:
                raise
        
        try:
            cursor.execute("ALTER TABLE itens_ficha_tecnica ADD COLUMN custo_unitario_historico REAL DEFAULT 0")
            print("   ✅ Coluna 'custo_unitario_historico' adicionada")
        except sqlite3.OperationalError as e:
            if "duplicate column" in str(e).lower():
                print("   ⚠️  Coluna 'custo_unitario_historico' já existe")
            else:
                raise
        
        # 3. Tornar insumo_id nullable (para itens do tipo 'ficha')
        print("\n3. Ajustando dados existentes...")
        
        # Garantir que todos os itens existentes são tipo='insumo'
        cursor.execute("UPDATE itens_ficha_tecnica SET tipo_item = 'insumo' WHERE tipo_item IS NULL OR tipo_item = ''")
        rows_updated = cursor.rowcount
        print(f"   ✅ {rows_updated} itens marcados como tipo='insumo'")
        
        # 4. Calcular custo_unitario_historico para itens existentes
        cursor.execute("""
            UPDATE itens_ficha_tecnica 
            SET custo_unitario_historico = (
                SELECT i.preco_unitario 
                FROM insumos i 
                WHERE i.id = itens_ficha_tecnica.insumo_id
            )
            WHERE tipo_item = 'insumo' AND insumo_id IS NOT NULL
        """)
        rows_updated = cursor.rowcount
        print(f"   ✅ Custo histórico calculado para {rows_updated} itens")
        
        conn.commit()
        print("\n✅ Migração concluída com sucesso!")
        print("\n📊 Resumo:")
        
        # Estatísticas
        cursor.execute("SELECT COUNT(*) FROM fichas_tecnicas WHERE ativo = 1")
        total_fichas = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM itens_ficha_tecnica WHERE tipo_item = 'insumo'")
        total_insumos = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM itens_ficha_tecnica WHERE tipo_item = 'ficha'")
        total_fichas_aninhadas = cursor.fetchone()[0]
        
        print(f"   - Fichas técnicas ativas: {total_fichas}")
        print(f"   - Itens tipo 'insumo': {total_insumos}")
        print(f"   - Itens tipo 'ficha': {total_fichas_aninhadas}")
        
        return True
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Erro na migração: {e}")
        return False
        
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'ficha_tecnica.db'
    
    print(f"🗄️  Banco de dados: {db_path}")
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    sucesso = migrar_banco(db_path)
    
    if sucesso:
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA!")
        print("\nO sistema agora suporta:")
        print("  ✅ Fichas técnicas aninhadas")
        print("  ✅ Histórico de custos")
        print("  ✅ Cálculo automático em cascata")
        sys.exit(0)
    else:
        print("\n❌ MIGRAÇÃO FALHOU!")
        sys.exit(1)
