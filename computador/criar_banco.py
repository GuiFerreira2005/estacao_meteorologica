import sqlite3


def criar_banco_dados():
    # Conecta ao arquivo de banco de dados (cria o arquivo se nao existir)
    conn = sqlite3.connect('estacao.db')
    cursor = conn.cursor()

    # 1. Ativa o suporte obrigatório a Chaves Estrangeiras (Foreign Keys) no SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    # 2. Cria a Tabela Estática 'estacao'
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS estacao (
            id_estacao INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_estacao TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL
        );
    """)

    # 3. Cria a Tabela Transacional 'leitura' em 3FN
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leitura (
            id_leitura INTEGER PRIMARY KEY AUTOINCREMENT,
            id_estacao INTEGER NOT NULL,
            data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
            temperatura REAL,
            umidade REAL,
            pressao REAL,
            qualidade_ar INTEGER,
            luminosidade INTEGER,
            pluviometria REAL,
            FOREIGN KEY (id_estacao) REFERENCES estacao (id_estacao) ON DELETE CASCADE
        );
    """)

    # 4. Cadastra a Estação Inicial (Caso ainda não exista)
    cursor.execute("SELECT COUNT(*) FROM estacao;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
            INSERT INTO estacao (nome_estacao, latitude, longitude)
            VALUES (?, ?, ?)
        """, ('Estação Meteorológica Central ESP32', -23.550520, -46.633308))
        print("✅ Estação padrão cadastrada com sucesso!")

    conn.commit()
    conn.close()
    print("✅ Banco de dados 'estacao.db' recriado com sucesso em 3FN!")


if __name__ == '__main__':
    criar_banco_dados()