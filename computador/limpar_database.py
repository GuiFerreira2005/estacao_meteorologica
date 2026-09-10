import sqlite3
import os

# Nome do banco de dados unificado
db_name = "db_estacao.db"

def limpar_banco():
    # [MANUTENÇÃO PREVENTIVA] Verifica se o arquivo físico do banco existe
    if not os.path.exists(db_name):
        print(f"⚠️ ALERTA: O arquivo '{db_name}' não foi encontrado nesta pasta!")
        print(f"Diretório atual de execução do terminal: {os.getcwd()}")
        return

    try:
        # Abre a conexão física de forma temporária
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # 1. Remove de forma limpa todas as linhas da tabela
        cursor.execute("DELETE FROM leituras_sensores")
        
        # 2. Reseta o contador interno do AUTOINCREMENT para o ID inicializar em 1
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='leituras_sensores'")
        
        # Confirma as alterações e fecha a conexão imediatamente para liberar recursos
        conn.commit()
        conn.close()
        
        print(f"✨ SUCESSO: O banco de dados '{db_name}' foi limpo e os IDs foram redefinidos para 1!")
        
    except sqlite3.OperationalError as lock_err:
        print("\n❌ ERRO DE CONCORRÊNCIA: O banco de dados está bloqueado (Locked).")
        print("Certifique-se de que o script 'conexao_mqtt.py' ou outro visualizador de banco de dados não esteja gravando dados no exato momento da limpeza!\n")
    except sqlite3.Error as e:
        print(f"❌ Erro interno do SQLite: {e}")

if __name__ == '__main__':
    limpar_banco()