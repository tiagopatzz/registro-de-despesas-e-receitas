# Roteiro da Apresentação — Tarefa Final GCS 2026/A

Simulação completa, passo a passo, do que fazer e falar na banca.
Os 13 passos do enunciado estão mapeados abaixo, mais a demo de falha (passo 6 do seu pedido).

> **Antes de começar:** garanta que já fez UMA vez na vida da VM:
> `./scripts/preparar_vm.sh` (instala Docker + cria rede) e que o **runner self-hosted**
> do GitHub está rodando como serviço. Isso NÃO faz parte da apresentação — é setup prévio.
> Tenha dois terminais abertos na VM e o navegador no GitHub Actions do repositório.

---

## FASE 0 — Preparar a "mesa limpa" (antes da banca entrar, ou no início)

Objetivo: começar com os ambientes **inexistentes**, para poder criá-los ao vivo.

```bash
# Limpa Homolog e Prod (containers + volumes). O NGINX pode ficar de pé.
./scripts/destruir_homolog.sh
./scripts/destruir_prod.sh

# Garante que o NGINX (proxy) está no ar
docker compose -f docker-compose.infra.yml up -d

docker ps   # deve mostrar SÓ o nginx-gcs
```

**O que falar:** "Vou começar com a estrutura zerada para mostrar a criação automatizada dos ambientes."

---

## PASSO 1 — Apresentar ambientes com a estrutura NÃO existente

```bash
docker ps                       # só o nginx aparece
curl -I http://localhost/homolog/   # retorna 502 Bad Gateway
curl -I http://localhost/prod/      # retorna 502 Bad Gateway
```

**O que falar:** "Repare que não existe nenhum container de aplicação nem de banco. As URLs
retornam 502 porque o NGINX não tem para onde encaminhar ainda."

---

## PASSO 2 — Criar ambiente de Homologação

```bash
./scripts/criar_homolog.sh
```

**O que acontece:** o Docker constrói a imagem, sobe `db-homolog` e `app-homolog`. No log
do `app-homolog` você vê o `migrate.py` aplicando **V001** (tabelas) e **V002** (dados).

```bash
docker compose -f docker-compose.homolog.yml logs app-homolog | grep migrate
```

**O que falar:** "Um único comando criou o container, instalou as ferramentas dentro dele,
aplicou as migrations do banco e subiu a aplicação."

---

## PASSO 3 — Criar ambiente de Produção

```bash
./scripts/criar_prod.sh
docker ps   # agora: nginx, app-homolog, db-homolog, app-prod, db-prod
```

---

## PASSO 4 — Aplicação funcionando em Homologação

No navegador: **http://<IP-da-VM>/homolog/**
- Login: `admin` / senha: `admin123`
- Mostrar a lista de lançamentos, criar um lançamento, exportar o PDF.

---

## PASSO 5 — Aplicação funcionando em Produção

No navegador: **http://<IP-da-VM>/prod/** — mesmo login. Mostre que é um ambiente separado
(dados independentes do de Homolog).

**O que falar:** "São dois ambientes isolados: bancos diferentes, volumes diferentes, mesmo
código. O NGINX separa por caminho: /homolog e /prod."

---

## PASSO 6 — Registrar a mudança

No GitHub, abrir uma **Issue**. Ex.: título *"Criar tabela categoria para classificar
lançamentos"*, número **#3**.

**O que falar:** "A mudança começa com um registro rastreável. Toda alteração vai referenciar
essa issue no commit."

---

## ★ DEMONSTRAÇÃO DE BLOQUEIO DO PIPELINE (o ponto que você pediu) ★

Faça isto ANTES de implementar a mudança real, para mostrar o portão de qualidade.

**1. Descomentar o erro** no `app.py` (linha ~12), na branch `homolog`:

```python
# de:
# def funcao_quebrada(:
# para:
def funcao_quebrada(:
```

**2. Commit e push:**
```bash
git checkout homolog
git add app.py
git commit -m "CHG-002: demo de falha no pipeline (issue #2)"
git push origin homolog
```

**3. No GitHub Actions**, mostrar ao vivo:
- O job **Integração** fica VERMELHO.
- No passo do flake8: erro `E999 SyntaxError`.
- No passo dos testes: os 20 falham no `from app import app` (erro de import).
- Os jobs **deploy-homolog** aparecem como **Skipped** (cinza) — nunca executam.

**4. Provar que o ambiente seguiu intacto:**
```bash
curl -I http://localhost/homolog/   # continua 200 OK, versão anterior no ar
```

**O que falar (importante para a banca):** "O pipeline é um portão. Como o código não passou
na Integração — nem o lint nem os testes — a etapa de deploy nem chega a rodar. O ambiente
de Homologação continua funcionando com a versão anterior. Nenhum código quebrado chega aos
ambientes."

**5. Reverter o erro** (comentar de novo) para liberar o fluxo:
```bash
# voltar a linha para: # def funcao_quebrada(:
git add app.py
git commit -m "Revert CHG-002: remove erro de demonstracao"
git push origin homolog
```
Agora o pipeline fica VERDE e o deploy-homolog roda. (Pode deixar esse push já encadeado
com o passo 7/8 abaixo, num commit só, para economizar tempo.)

---

## PASSO 7 — Implementar (código-fonte + banco de dados)

Na branch `homolog`, trazer a migration da tabela nova:

```bash
cp migrations/exemplos/V003__criar_tabela_categoria.sql migrations/
```

(Se for alterar código junto, faça aqui. Para a demo da tabela, a migration já basta.)

---

## PASSO 8 — Versionar

```bash
git add migrations/V003__criar_tabela_categoria.sql
git commit -m "CHG-003: criar tabela categoria (closes #3)"
git push origin homolog
```

---

## PASSO 9 — Integração (testes + qualidade + build)

No GitHub Actions, mostrar o job **Integração** agora VERDE:
- **flake8** passou (qualidade de código).
- **20 testes** executados com `coverage run -m unittest -v`.
- **Estatísticas** do coverage no log + artefato `coverage.xml` para download.
- **Build** da imagem Docker concluído.

**O que falar:** "Agora com o código correto, a Integração passa nas três frentes: qualidade,
os 20 testes automatizados com estatística de cobertura, e o build."

---

## PASSO 10 — Atualizar ambiente de Homologação

O job **deploy-homolog** roda automaticamente após a Integração (é o runner self-hosted da VM).
Se preferir disparar manualmente: GitHub → Actions → *Run workflow* na branch `homolog`.

```bash
# acompanhar na VM:
docker compose -f docker-compose.homolog.yml logs app-homolog | grep migrate
```
Você verá: `V003 aplicada com sucesso`.

---

## PASSO 11 — Homolog atualizado + atualização do Banco de Dados

Mostrar a tabela nova SÓ em Homolog:

```bash
docker compose -f docker-compose.homolog.yml exec db-homolog \
  psql -U postgres -d financas -c '\dt'
# aparece: usuario, lancamento, schema_migrations, CATEGORIA  ✅
```

E provar que em Produção **NÃO** existe ainda:

```bash
docker compose -f docker-compose.prod.yml exec db-prod \
  psql -U postgres -d financas -c '\dt'
# NÃO aparece categoria  ❌  (Prod está na versão anterior do banco)
```

**O que falar:** "Aqui está o versionamento independente do banco: a migration V003 foi aplicada
só em Homologação, porque o commit ainda não foi promovido para a branch main. Produção
permanece na versão anterior do schema."

---

## PASSO 12 — Atualizar ambiente de Produção

Promover a mudança para produção (merge na `main`):

```bash
git checkout main
git merge homolog
git push origin main
```

O push na `main` dispara a Integração de novo e, passando, o job **deploy-prod**.

---

## PASSO 13 — Prod atualizado + atualização do Banco de Dados

```bash
docker compose -f docker-compose.prod.yml exec db-prod \
  psql -U postgres -d financas -c '\dt'
# agora a tabela CATEGORIA aparece também em Produção  ✅
```

Abrir **http://<IP-da-VM>/prod/** e mostrar a aplicação no ar com o banco atualizado.

**O que falar:** "Promovida para a main, a mesma migration foi aplicada em Produção pelo pipeline.
Os dois ambientes agora estão na mesma versão de schema, cada um com seus próprios dados."

---

## Resumo do mapeamento (cola rápida)

| Passo | Comando-chave |
|---|---|
| 1 | `docker ps` / `curl -I .../homolog/` (502) |
| 2 | `./scripts/criar_homolog.sh` |
| 3 | `./scripts/criar_prod.sh` |
| 4-5 | navegador `/homolog/` e `/prod/` (admin/admin123) |
| 6 | abrir Issue no GitHub |
| ★ | descomentar erro → push homolog → Actions vermelho → deploy Skipped → reverter |
| 7 | `cp migrations/exemplos/V003__*.sql migrations/` |
| 8 | `git commit` + `git push origin homolog` |
| 9 | GitHub Actions: flake8 + 20 testes + coverage + build |
| 10 | deploy-homolog (auto) |
| 11 | `\dt` no db-homolog (tem categoria) vs db-prod (não tem) |
| 12 | `git checkout main && git merge homolog && git push` |
| 13 | `\dt` no db-prod (agora tem categoria) |

---

## Plano B (se a VM não tiver internet para o runner)

Se o runner self-hosted não conseguir falar com o GitHub, os deploys automáticos não rodam.
Nesse caso, o processo continua **semi-automatizado e válido**: após a Integração verde no
GitHub, você atualiza o ambiente na VM com um comando:

```bash
git pull origin homolog && ./scripts/criar_homolog.sh   # atualiza Homolog
git pull origin main    && ./scripts/criar_prod.sh      # atualiza Prod
```

Vale confirmar o acesso à internet da VM antes da apresentação, para saber qual caminho seguir.
