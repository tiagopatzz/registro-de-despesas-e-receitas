-- V001: Estrutura inicial do banco (versao 1 do schema)
CREATE TABLE usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    login VARCHAR(50) UNIQUE NOT NULL,
    senha VARCHAR(100) NOT NULL,
    situacao VARCHAR(20) NOT NULL,
    email VARCHAR(120)
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
