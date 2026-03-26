CREATE DATABASE financas;
\c financas;

CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    situacao VARCHAR(20) NOT NULL
);

CREATE TABLE lancamento (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL REFERENCES usuario(id),
    descricao VARCHAR(255) NOT NULL,
    data_lancamento DATE NOT NULL,
    valor NUMERIC(10, 2) NOT NULL,
    tipo_lancamento VARCHAR(20) NOT NULL,
    situacao VARCHAR(20) NOT NULL
);

INSERT INTO usuario (nome, login, senha, situacao) VALUES ('Administrador', 'admin', 'admin123', 'ATIVO');

INSERT INTO lancamento (usuario_id, descricao, data_lancamento, valor, tipo_lancamento, situacao) VALUES
(1, 'Salário Mensal', '2026-03-05', 5000.00, 'RECEITA', 'PAGO'),
(1, 'Aluguel', '2026-03-06', 1500.00, 'DESPESA', 'PAGO'),
(1, 'Supermercado', '2026-03-10', 800.00, 'DESPESA', 'PAGO'),
(1, 'Conta de Luz', '2026-03-12', 150.00, 'DESPESA', 'PENDENTE'),
(1, 'Conta de Água', '2026-03-15', 80.00, 'DESPESA', 'PAGO'),
(1, 'Internet', '2026-03-15', 120.00, 'DESPESA', 'PAGO'),
(1, 'Venda de Bicicleta', '2026-03-18', 600.00, 'RECEITA', 'PAGO'),
(1, 'Combustível', '2026-03-20', 250.00, 'DESPESA', 'PAGO'),
(1, 'Manutenção Carro', '2026-03-22', 400.00, 'DESPESA', 'PENDENTE'),
(1, 'Rendimento Poupança', '2026-03-25', 45.00, 'RECEITA', 'PAGO');