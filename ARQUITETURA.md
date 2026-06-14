# Tarefa Final — Gerência de Configuração de Software (2026/A)

**Projeto:** Sistema de Gerenciamento de Finanças Pessoais (registro de despesas e receitas)
**Aluno:** Tiago Patzlaff
**Repositório:** https://github.com/tiagopatzz/registro-de-despesas-e-receitas

---

## 1. Diagrama da arquitetura

```
                                    ┌────────────────────────────────────────────────────────┐
                                    │              VM UNIVATES (Ubuntu Linux)                 │
 ┌──────────┐                       │  ┌──────────────────────────────────────────────────┐  │
 │  GitHub  │  branch homolog       │  │                     DOCKER                       │  │
 │  Issues  │──┐                    │  │                  ┌─────────┐                     │  │
 │ (registro│  │   ┌────────────┐   │  │                  │  NGINX  │ :80                 │  │
 │de mudança│  ├──>│   GitHub   │   │  │                  └────┬────┘                     │  │
 └──────────┘  │   │   Actions  │   │  │         /homolog ────┴──── /prod                 │  │
 ┌──────────┐  │   │(Integração:│   │  │  ┌─────────────────┐  ┌─────────────────┐        │  │
 │   Git /  │──┘   │ 20 testes, │   │  │  │     HOMOLOG     │  │      PROD       │        │  │
 │  GitHub  │      │  coverage, │──────>│  │ Flask+Gunicorn │  │ Flask+Gunicorn  │        │  │
 │ (versio- │      │   flake8,  │runner │  │       │        │  │       │         │        │  │
 │ namento) │      │   build)   │ self- │  │  PostgreSQL 16 │  │  PostgreSQL 16  │        │  │
 └──────────┘      └────────────┘hosted │  │       │        │  │       │         │        │  │
   branch main                      │  │  │  [Volume HML]  │  │  [Volume PROD]  │        │  │
                                    │  │  └─────────────────┘  └─────────────────┘        │  │
                                    │  └──────────────────────────────────────────────────┘  │
                                    └────────────────────────────────────────────────────────┘
```

**Fluxo:** push na branch `homolog` → GitHub Actions roda a Integração (testes,
qualidade, build) → se passar, o runner self-hosted na VM atualiza o ambiente de
Homologação (containers + migrations do banco). Merge/push na branch `main` →
mesma Integração → atualiza Produção. Se a Integração falhar, **nenhum deploy ocorre**.

## 2. Tecnologias utilizadas (mapeamento das fases A–H)

| Fase da tarefa | Ferramenta escolhida |
|---|---|
| A) Registro da mudança | **GitHub Issues** (cada mudança = uma issue; commits referenciam `#N`) |
| B) Implementação | **Python 3.12 + Flask** (workspace local: VS Code) |
| C) Versionamento | **Git + GitHub** (branches `homolog` e `main`) |
| D) Testes automatizados (20) + estatísticas | **unittest** (20 testes) + **coverage** (relatório no log do pipeline + artefato `coverage.xml`) |
| E) Análise de qualidade de código | **flake8** (PEP 8; erro de sintaxe reprova o pipeline) |
| F) Atualização de Homologação | **GitHub Actions** (job `deploy-homolog`) via push na branch `homolog` |
| G) Atualização de Produção | **GitHub Actions** (job `deploy-prod`) via push/merge na branch `main` |
| H) Criação dos ambientes | **Docker + Docker Compose** (`scripts/criar_ambientes.sh`) |

**Ambiente:** VM da Univates (Ubuntu Linux) executando Docker. Containers: `nginx-gcs`
(proxy reverso, porta 80), `app-homolog`, `db-homolog`, `app-prod`, `db-prod`, todos na
rede Docker `gcs_net`. Cada ambiente tem volume de dados exclusivo (`vol_hml`, `vol_prod`).

**Linguagem e banco:** Python 3.12 (Flask, Gunicorn) e PostgreSQL 16.

**Versionamento do banco de dados:** migrations SQL numeradas em `migrations/`
(`V001__...`, `V002__...`), aplicadas pelo `migrate.py` na subida de cada container.
A tabela `schema_migrations` registra, em cada banco, quais versões já foram aplicadas —
por isso Homolog e Prod evoluem de forma independente.

**Integração contínua:** GitHub Actions com dois tipos de runner:
- `ubuntu-latest` (nuvem do GitHub) para a Integração: flake8 → 20 testes →
  estatísticas de cobertura → build da imagem Docker;
- **runner self-hosted instalado na VM da Univates** para os deploys (a VM não
  precisa expor SSH; o runner puxa os jobs do GitHub).

**Processo semi-automatizado:** os deploys disparam por `git push` (um comando) ou
pelo botão *Run workflow* no GitHub (`workflow_dispatch`). A criação da infraestrutura
do zero é feita por script: `./scripts/criar_ambientes.sh`.

## 3. Estrutura do repositório

```
├── app.py                        # aplicação Flask (CRUD, PDF, e-mail)
├── test_app.py                   # 20 testes unitários (unittest)
├── migrate.py                    # aplicador de migrations (versionamento do BD)
├── migrations/
│   ├── V001__criar_tabelas.sql
│   ├── V002__dados_iniciais.sql
│   └── exemplos/V003__criar_tabela_categoria.sql   # demo da apresentação
├── templates/                    # login, cadastro, index, perfil, edit
├── Dockerfile                    # imagem da aplicação (python:3.12-slim)
├── entrypoint.sh                 # migrate.py + gunicorn na subida do container
├── docker-compose.homolog.yml    # ambiente de Homologação
├── docker-compose.prod.yml       # ambiente de Produção
├── docker-compose.infra.yml      # NGINX (proxy reverso)
├── nginx/nginx.conf              # rotas /homolog e /prod
├── .github/workflows/pipeline.yml  # pipeline CI/CD
├── .flake8                       # configuração da análise de qualidade
└── scripts/
    ├── preparar_vm.sh            # instala Docker na VM (uma vez)
    ├── criar_homolog.sh          # cria/sobe SÓ Homologação
    ├── criar_prod.sh             # cria/sobe SÓ Produção
    ├── destruir_homolog.sh       # remove SÓ Homologação
    ├── destruir_prod.sh          # remove SÓ Produção
    ├── criar_ambientes.sh        # cria os dois de uma vez (atalho)
    └── destruir_ambientes.sh     # remove os dois de uma vez (atalho)
```

## 4. Configuração inicial (antes da apresentação)

1. **VM:** `./scripts/preparar_vm.sh` (instala Docker e cria a rede `gcs_net`).
2. **Runner self-hosted:** no GitHub, *Settings → Actions → Runners → New self-hosted
   runner (Linux x64)* e seguir os comandos exibidos na própria página dentro da VM.
   Ao final: `sudo ./svc.sh install && sudo ./svc.sh start` (roda como serviço).
3. **Branches:** criar a branch `homolog` a partir da `main`
   (`git checkout -b homolog && git push -u origin homolog`).
4. **Segredo de e-mail (opcional):** exportar `MAIL_PASSWORD` no ambiente do runner ou
   criar arquivo `.env` na pasta do projeto na VM (senha de app do Gmail).

## 5. Roteiro da validação (os 13 passos do enunciado)

1. **Ambientes não existentes:** `./scripts/destruir_ambientes.sh` e mostrar
   `docker ps` (somente o NGINX/runner no ar) e o erro 502 em `/homolog/` e `/prod/`.
2. **Criar Homologação:** `./scripts/criar_ambientes.sh homolog` — containers sobem,
   migrations V001/V002 são aplicadas automaticamente.
3. **Criar Produção:** `./scripts/criar_ambientes.sh prod`.
4. **App funcionando em Homolog:** abrir `http://<IP-da-VM>/homolog/` e logar (admin/admin123).
5. **App funcionando em Prod:** abrir `http://<IP-da-VM>/prod/`.
6. **Registrar mudança:** abrir uma **Issue no GitHub** (ex.: *#3 — Criar tabela
   categoria para classificar lançamentos*).
7. **Implementar (código + banco):** na branch `homolog`, fazer a alteração de código
   e copiar a migration: `cp migrations/exemplos/V003__criar_tabela_categoria.sql migrations/`.
8. **Versionar:** `git add . && git commit -m "CHG-003: criar tabela categoria (closes #3)" && git push origin homolog`.
9. **Integração:** mostrar no GitHub Actions o job *Integração* executando flake8,
   os **20 testes**, o relatório do **coverage** e o build da imagem.
10. **Atualizar Homologação:** o job *deploy-homolog* roda sozinho após a Integração
    (ou via *Run workflow*).
11. **Homolog atualizado + banco:** mostrar o app em `/homolog/` e a tabela nova:
    `docker compose -f docker-compose.homolog.yml exec db-homolog psql -U postgres -d financas -c '\dt'`
    → a tabela `categoria` existe em Homolog. Em Prod, **não** (rodar o mesmo comando no `db-prod`).
12. **Atualizar Produção:** quando desejado, `git checkout main && git merge homolog && git push origin main`
    → job *deploy-prod* executa.
13. **Prod atualizado + banco:** repetir a verificação no `db-prod`.

> **Observação para a banca:** no passo 11 fica demonstrado o versionamento
> independente dos bancos — a migration V003 (tabela `categoria`) existe apenas em
> Homologação, pois o commit ainda não foi promovido à branch `main`.

## 6. Demonstração de falha no pipeline (código errado preparado)

O `app.py` traz, no topo, um bloco **documentado** com a linha comentada
`# def funcao_quebrada(:` (erro de sintaxe proposital).

Roteiro da demo:
1. Descomentar a linha, commitar e dar push na branch `homolog`
   (`git commit -am "CHG-002: demo de falha no pipeline" && git push`).
2. No GitHub Actions, o job **Integração falha**: o flake8 acusa `E999 SyntaxError`
   e os 20 testes nem chegam a rodar (erro de import).
3. Os jobs de deploy aparecem como **Skipped** → Homolog e Prod continuam rodando
   a versão anterior, intactos (mostrar o app ainda no ar).
4. Comentar a linha de novo, commit/push → pipeline verde, deploy normal.

Isso evidencia o papel da Integração como **portão de qualidade**: código com defeito
não avança no pipeline.

## 7. Estatísticas de testes e qualidade

- **20 testes unitários** (`test_app.py`, via `app.test_client()`), executados com
  `coverage run -m unittest -v` em todo push.
- **Estatísticas:** `coverage report -m` exibido no log do pipeline e `coverage.xml`
  publicado como artefato de cada execução (histórico consultável no GitHub Actions).
- **Qualidade:** `flake8` com configuração em `.flake8`; violações graves
  (sintaxe, nomes indefinidos) reprovam a Integração.
