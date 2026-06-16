# Roteiro da Apresentação — Tarefa Final GCS 2026/A

Simulação completa, passo a passo. Reflete a arquitetura final:
compose único, limpeza total de imagens, sessão isolada por ambiente,
pipeline com PR automático e Branch Protection.

**Aplicação:** Sistema de Finanças Pessoais (Flask + PostgreSQL)
**IP da VM:** http://177.44.248.72
**Branches:** `homolog` (→ Homologação) e `main` (→ Produção)

---

## PARTE A — SETUP (feito UMA vez, ANTES da apresentação)

Estes itens já devem estar prontos. Confira antes do dia:

1. **Docker instalado na VM** e usuário `univates` no grupo `docker`
   (`docker ps` funciona sem sudo).
2. **Runner self-hosted** instalado como serviço e ativo
   (GitHub → Settings → Actions → Runners → "Idle"/verde).
3. **Branches `homolog` e `main`** existem no GitHub.
4. **Permissão do Actions criar PR:** Settings → Actions → General → Workflow
   permissions → "Read and write permissions" + "Allow GitHub Actions to create
   and approve pull requests".
5. **Branch Protection (ruleset) na `main`:** Enforcement Active, target `main`,
   "Require a pull request before merging" (approvals = 0) e "Require status checks
   to pass" → check `Integracao (testes + qualidade + build)`.

> Observação: o check só aparece na lista do ruleset depois que a Integração rodou
> uma vez dentro de um PR. Se não aparecer, crie um PR de teste, deixe rodar, e volte
> para adicioná-lo.

---

## PARTE B — ESTADO INICIAL: nada existe

### Passo 1 — Mostrar a VM zerada

```bash
cd ~/registro-de-despesas-e-receitas
./scripts/destruir_ambientes.sh
```

Confirme:
```bash
docker ps        # VAZIO - nenhum container
docker images    # sem imagens do projeto
```

**Falar:** "Começo com a VM totalmente limpa: nenhum container e nenhuma imagem do
projeto. Toda a infraestrutura será criada de forma automatizada pelos scripts."

---

## PARTE C — CRIAR OS AMBIENTES

### Passo 2 — Criar Homologação

```bash
./scripts/criar_homolog.sh
```

**Falar:** "Um script criou do zero: baixou as imagens base, construiu a imagem da
aplicação, subiu o banco e o app, e aplicou as migrations automaticamente."

Mostre as migrations aplicadas:
```bash
docker compose logs app-homolog | grep migrate
docker compose exec db-homolog psql -U postgres -d financas -c '\dt'
# tabelas: usuario, lancamento, schema_migrations
```

### Passo 3 — Mostrar que Produção ainda NÃO existe

```bash
docker ps   # só nginx, app-homolog, db-homolog (nada de prod)
```

**Falar:** "Produção ainda não existe — vou criá-la separadamente, mostrando que os
ambientes são independentes."

### Passo 4 — Criar Produção

```bash
./scripts/criar_prod.sh
docker ps   # agora os 5: nginx, app-homolog, db-homolog, app-prod, db-prod
```

---

## PARTE D — APLICAÇÃO FUNCIONANDO

### Passo 5 — Homologação no ar
Navegador (aba anônima): **http://177.44.248.72/homolog/**
Login: `admin` / `admin123`. Mostre o dashboard, crie um lançamento, exporte o PDF.

### Passo 6 — Produção no ar
Outra aba anônima: **http://177.44.248.72/prod/** — mesmo login.

**Falar:** "Dois ambientes isolados: bancos, volumes e sessões independentes. Posso
estar logado nos dois ao mesmo tempo sem um derrubar o outro."

---

## PARTE E — CICLO DE MUDANÇA (os 3 momentos-chave)

### Passo 7 — Registrar a mudança
No GitHub, abra uma **Issue** (ex.: "Criar tabela categoria para classificar
lançamentos", #3).

**Falar:** "Toda mudança começa com um registro rastreável."

---

### ★ MOMENTO 1 — Código com erro NÃO chega aos ambientes

1. Na branch `homolog`, no `app.py`, **descomente** a linha 12:
   ```python
   # de:    # def funcao_quebrada(:
   # para:  def funcao_quebrada(:
   ```
2. Commit e push:
   ```bash
   git add app.py
   git commit -m "CHG-002: demonstracao de falha no pipeline"
   git push origin homolog
   ```
3. No GitHub Actions: o job **Integração fica VERMELHO**
   - flake8 acusa `E999 SyntaxError`
   - os 20 testes falham no `from app import app`
4. Os jobs **Atualizar HOMOLOGAÇÃO**, **abrir-pr** e **Atualizar PRODUÇÃO** ficam
   **Skipped** — não rodam.
5. Prove que homolog seguiu intacto:
   ```bash
   curl -I http://177.44.248.72/homolog/   # ainda responde (versão anterior)
   ```

**Falar:** "O pipeline é um portão. Como a Integração reprovou, nenhum deploy rodou e
nenhum PR foi criado. Código quebrado não chega a Homologação nem a Produção."

6. **Reverter:** comente a linha de novo e faça push:
   ```bash
   git add app.py
   git commit -m "Revert: remove erro de demonstracao"
   git push origin homolog
   ```
   Agora a Integração fica **VERDE**, o deploy de homolog roda e o **PR é criado
   automaticamente**.

---

### ★ MOMENTO 2 — Alterar um label (diferença entre ambientes)

1. Na branch `homolog`, altere uma letra/texto em `templates/index.html`
   (ex.: o título da página).
2. Commit e push:
   ```bash
   git add templates/index.html
   git commit -m "feat: ajusta label do dashboard (closes #3)"
   git push origin homolog
   ```
3. Actions **VERDE** → **Atualizar HOMOLOGAÇÃO** roda → homolog atualiza.
4. Recarregue **/homolog/** (a letra mudou) e **/prod/** (continua a antiga).

**Falar:** "A mudança está só em Homologação. Produção segue intacta porque ainda não
promovi. Os ambientes são independentes."

---

### ★ MOMENTO 3 — Tabela nova no banco via migrate

1. Na branch `homolog`, traga a migration:
   ```bash
   cp migrations/exemplos/V003__criar_tabela_categoria.sql migrations/
   git add migrations/V003__criar_tabela_categoria.sql
   git commit -m "CHG-003: cria tabela categoria"
   git push origin homolog
   ```
2. Actions verde → deploy de homolog roda o `migrate.py` e aplica a V003.
3. Prove a diferença nos bancos:
   ```bash
   docker compose exec db-homolog psql -U postgres -d financas -c '\dt'   # TEM categoria
   docker compose exec db-prod    psql -U postgres -d financas -c '\dt'   # NÃO tem
   ```

**Falar:** "A migration foi versionada e aplicada só em Homologação. O versionamento
do banco acompanha o do código: cada ambiente evolui conforme o que chega nele."

---

## PARTE F — PROMOÇÃO PARA PRODUÇÃO (via PR automático)

### Passo 8 — Revisar e aprovar o PR

Após cada push verde na `homolog`, o pipeline **cria/atualiza automaticamente** um PR
de `homolog → main` (job `abrir-pr`).

1. GitHub → **Pull requests** → abra o PR "Promover Homologacao para Producao".
2. Veja o diff (suas mudanças: label + migration V003).
3. Confirme que a Integração está **verde** no PR (se vermelha, o Branch Protection
   bloqueia o merge).
4. **Merge pull request** → **Confirm merge**.

**Falar:** "A promoção é controlada: eu reviso o PR e decido aprovar. O merge só é
liberado porque a Integração passou."

### Passo 9 — Produção atualizada

O merge gera um push na `main` → a Integração roda de novo → o job **Atualizar
PRODUÇÃO** aplica tudo em produção (código + migrations).

Prove que agora produção tem a tabela e o label novo:
```bash
docker compose exec db-prod psql -U postgres -d financas -c '\dt'   # AGORA tem categoria
```
Recarregue **http://177.44.248.72/prod/** → label atualizado.

**Falar:** "Promovida para a main, a mesma mudança foi aplicada em Produção pelo
pipeline. Os dois ambientes agora estão na mesma versão, cada um com seus dados."

---

## PARTE G — ENCERRAMENTO (opcional)

Se o professor quiser ver a VM limpa de novo:
```bash
./scripts/destruir_ambientes.sh
docker ps        # vazio
docker images    # sem imagens do projeto
```

---

## COLA RÁPIDA (sequência de comandos)

| # | Comando |
|---|---|
| 1 | `./scripts/destruir_ambientes.sh` → `docker ps` / `docker images` (vazios) |
| 2 | `./scripts/criar_homolog.sh` |
| 3 | `docker ps` (sem prod) |
| 4 | `./scripts/criar_prod.sh` |
| 5-6 | navegador `/homolog/` e `/prod/` (admin/admin123) |
| 7 | abrir Issue no GitHub |
| M1 | descomenta erro → push homolog → Actions vermelho → tudo Skipped → reverte |
| M2 | altera label → push homolog → homolog muda, prod não |
| M3 | `cp migrations/exemplos/V003*.sql migrations/` → push → `\dt` (homolog tem, prod não) |
| 8 | GitHub → PR automático → revisar → Merge |
| 9 | `docker compose exec db-prod ... '\dt'` (agora tem categoria) |

---

## MAPEAMENTO DAS FASES DO ENUNCIADO (A–H)

| Fase | Onde aparece |
|---|---|
| A) Registro da mudança | Issue no GitHub (Passo 7) |
| B) Implementação | Python/Flask (Momentos 2 e 3) |
| C) Versionamento | Git + branches homolog/main |
| D) Testes automatizados (20) + estatísticas | Job Integração: unittest + coverage |
| E) Análise de qualidade | flake8 no job Integração |
| F) Atualizar Homologação | Job "Atualizar HOMOLOGAÇÃO" |
| G) Atualizar Produção | Job "Atualizar PRODUÇÃO" (após merge do PR) |
| H) Criar ambientes Homolog e Prod | scripts criar_homolog.sh / criar_prod.sh |

Versionamento do banco: migrations em `migrations/` aplicadas pelo `migrate.py` em cada
deploy; tabela `schema_migrations` controla o que já rodou em cada banco.

---

## PLANO B (se algo der errado no dia)

- **Runner offline / sem internet:** atualize os ambientes na mão após o push verde:
  `git pull origin homolog && ./scripts/criar_homolog.sh`
- **PR automático não criou:** crie o PR manualmente (Pull requests → New → base main,
  compare homolog).
- **Build demorando:** a primeira criação após destruir baixa as imagens base; é
  esperado. Ensaie antes para saber o tempo na rede da Univates.
