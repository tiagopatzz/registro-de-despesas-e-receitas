-- V003: Criar tabela CATEGORIA (DEMO DA APRESENTACAO)
-- =====================================================================
-- Este arquivo fica em migrations/exemplos/ e NAO e aplicado.
-- Durante a apresentacao, na branch 'homolog', execute:
--
--   cp migrations/exemplos/V003__criar_tabela_categoria.sql migrations/
--   git add migrations/V003__criar_tabela_categoria.sql
--   git commit -m "CHG-003: criar tabela categoria (issue #3)"
--   git push origin homolog
--
-- O pipeline roda e o deploy de HOMOLOG aplica esta migration.
-- Como o commit NAO foi mesclado na 'main', a PRODUCAO permanece
-- sem a tabela -> demonstrando o versionamento independente dos bancos.
--
-- Verificacao:
--   Homolog: docker compose -f docker-compose.homolog.yml exec db-homolog psql -U postgres -d financas -c '\dt'
--   Prod:    docker compose -f docker-compose.prod.yml exec db-prod psql -U postgres -d financas -c '\dt'
-- =====================================================================
CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) UNIQUE NOT NULL,
    descricao VARCHAR(255)
);

INSERT INTO categoria (nome, descricao) VALUES
('Moradia', 'Aluguel, condominio e contas da casa'),
('Alimentação', 'Supermercado e refeições'),
('Transporte', 'Combustível e manutenção'),
('Renda', 'Salário e rendimentos');
