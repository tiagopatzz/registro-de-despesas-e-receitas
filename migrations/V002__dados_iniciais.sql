-- V002: Carga inicial de dados (usuario admin + lancamentos de exemplo)
INSERT INTO usuario (nome, login, senha, situacao, email)
VALUES ('Administrador', 'admin', 'admin123', 'ATIVO', 'tiago.patzlaff@universo.univates.br');

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
