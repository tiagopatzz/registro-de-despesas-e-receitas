CREATE TABLE categoria (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(80) UNIQUE NOT NULL,
    descricao VARCHAR(255)
);