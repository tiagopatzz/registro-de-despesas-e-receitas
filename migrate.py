"""
Versionamento do Banco de Dados (Migrations)
============================================
Aplica, em ordem, todos os arquivos .sql da pasta migrations/ que ainda
nao foram executados neste banco. O controle e feito pela tabela
schema_migrations, que registra a versao e a data de aplicacao.

- Cada ambiente (Homolog e Prod) tem seu proprio banco, entao cada um
  evolui de forma independente conforme o codigo que chega nele.
- Para criar uma nova versao do banco: adicionar um novo arquivo
  migrations/V00X__descricao.sql e fazer commit/push. O deploy aplica.

Uso: python migrate.py  (executado automaticamente no entrypoint do container)
"""
import os
import sys
import time

import psycopg2

MIGRATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'migrations')


def conectar(tentativas=30):
    """Aguarda o PostgreSQL ficar disponivel (util na subida do container)."""
    erro = None
    for _ in range(tentativas):
        try:
            return psycopg2.connect(
                host=os.environ.get('DB_HOST', 'localhost'),
                database=os.environ.get('DB_NAME', 'financas'),
                user=os.environ.get('DB_USER', 'postgres'),
                password=os.environ.get('DB_PASSWORD', 'postgres'),
                port=os.environ.get('DB_PORT', '5432'),
            )
        except psycopg2.OperationalError as e:
            erro = e
            print("[migrate] Aguardando banco de dados...")
            time.sleep(2)
    raise SystemExit(f"[migrate] Banco indisponivel: {erro}")


def main():
    conn = conectar()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS schema_migrations (
            versao VARCHAR(255) PRIMARY KEY,
            aplicada_em TIMESTAMP NOT NULL DEFAULT NOW()
        )
    """)
    conn.commit()

    cur.execute("SELECT versao FROM schema_migrations")
    aplicadas = {linha[0] for linha in cur.fetchall()}

    arquivos = sorted(
        f for f in os.listdir(MIGRATIONS_DIR)
        if f.endswith('.sql') and os.path.isfile(os.path.join(MIGRATIONS_DIR, f))
    )

    novas = 0
    for arquivo in arquivos:
        if arquivo in aplicadas:
            print(f"[migrate] {arquivo} ja aplicada, pulando.")
            continue
        caminho = os.path.join(MIGRATIONS_DIR, arquivo)
        with open(caminho, 'r', encoding='utf-8') as f:
            sql = f.read()
        try:
            cur.execute(sql)
            cur.execute("INSERT INTO schema_migrations (versao) VALUES (%s)", (arquivo,))
            conn.commit()
            novas += 1
            print(f"[migrate] OK -> {arquivo} aplicada com sucesso.")
        except Exception as e:
            conn.rollback()
            print(f"[migrate] ERRO ao aplicar {arquivo}: {e}")
            sys.exit(1)

    print(f"[migrate] Concluido. {novas} migration(s) nova(s) aplicada(s).")
    cur.close()
    conn.close()


if __name__ == '__main__':
    main()
