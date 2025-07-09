import os
import psycopg2
from psycopg2 import sql

def get_db_connection():
    """Obtém a conexão com o banco de dados a partir da DATABASE_URL."""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        raise ValueError("A variável de ambiente DATABASE_URL não foi definida.")
    
    print("Conectando ao banco de dados...")
    conn = psycopg2.connect(database_url)
    print("Conexão bem-sucedida.")
    return conn

def reset_all_sequences():
    """
    Encontra todas as sequências associadas às chaves primárias das tabelas
    e as re-sincroniza com o valor máximo de ID da tabela correspondente.
    """
    conn = None
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        # Query para encontrar todas as tabelas do usuário no schema 'public'
        cur.execute("""
            SELECT tablename
            FROM pg_tables
            WHERE schemaname = 'public'
        """)
        tables = [row[0] for row in cur.fetchall()]
        
        print(f"\nEncontradas {len(tables)} tabelas. Verificando sequências...")

        for table_name in tables:
            # Encontra a sequência associada à chave primária da tabela
            # A convenção de nome é 'nomeTabela_nomeColuna_seq'
            # Esta query busca a sequência diretamente dos metadados da coluna
            cur.execute(sql.SQL("""
                SELECT pg_get_serial_sequence(quote_ident({table}), c.attname)
                FROM pg_class AS t
                JOIN pg_attribute AS c ON c.attrelid = t.oid
                JOIN pg_constraint AS con ON con.conrelid = t.oid AND c.attnum = con.conkey[1]
                WHERE t.relname = {table}
                  AND con.contype = 'p';
            """).format(table=sql.Literal(table_name)))
            
            sequence_result = cur.fetchone()
            
            if not sequence_result or not sequence_result[0]:
                # print(f"  - Nenhuma sequência de chave primária encontrada para a tabela '{table_name}'. Pulando.")
                continue
                
            sequence_name = sequence_result[0]
            
            # Pega o nome da coluna da chave primária
            cur.execute(sql.SQL("""
                SELECT c.attname
                FROM pg_class AS t
                JOIN pg_attribute AS c ON c.attrelid = t.oid
                JOIN pg_constraint AS con ON con.conrelid = t.oid AND c.attnum = con.conkey[1]
                WHERE t.relname = {table}
                  AND con.contype = 'p';
            """).format(table=sql.Literal(table_name)))
            
            pk_column = cur.fetchone()[0]

            # Query para obter o valor máximo do ID
            max_id_query = sql.SQL("SELECT MAX({}) FROM {}").format(
                sql.Identifier(pk_column),
                sql.Identifier(table_name)
            )
            cur.execute(max_id_query)
            max_id = cur.fetchone()[0]

            if max_id is None:
                max_id = 0 # Tabela vazia, a sequência deve começar em 1

            # Atualiza a sequência para o próximo valor
            next_val = max_id + 1
            reset_query = sql.SQL("ALTER SEQUENCE {} RESTART WITH {}").format(
                sql.Identifier(sequence_name.split('.')[-1]),  # Usa apenas o nome da sequência
                sql.Literal(next_val)
            )
            
            print(f"  - Tabela: '{table_name}', PK: '{pk_column}', Sequência: '{sequence_name}'")
            print(f"    -> Valor Máximo do ID: {max_id}. Resetando sequência para: {next_val}")
            
            cur.execute(reset_query)

        conn.commit()
        print("\n✅ Todas as sequências foram sincronizadas com sucesso!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"\n❌ Erro ao conectar ou sincronizar o banco de dados:\n{error}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            cur.close()
            conn.close()
            print("\nConexão com o banco de dados fechada.")

if __name__ == '__main__':
    reset_all_sequences() 