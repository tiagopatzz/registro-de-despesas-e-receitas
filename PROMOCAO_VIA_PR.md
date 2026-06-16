# Promoção para Produção via Pull Request

Em vez de um script, a promoção de Homologação → Produção é feita por **Pull Request**
no GitHub. É o padrão da indústria e o mais alinhado com Gerência de Configuração:
fica registrado quem promoveu, quando, e com o status da Integração visível.

## Configuração única — Branch Protection na `main`

Isto faz o PR ser um portão de verdade: **não deixa fazer merge se o Actions estiver vermelho.**

1. No GitHub: **Settings → Branches → Add branch ruleset** (ou "Add rule" no modo clássico).
2. Branch name pattern: `main`
3. Marque:
   - **Require a pull request before merging** (obriga PR; ninguém empurra direto na main)
   - **Require status checks to pass before merging** → e selecione o check
     **"Integracao (testes + qualidade + build)"**
4. Salve.

Pronto. A partir de agora, a `main` só recebe código via PR aprovado e com Integração verde.

## Fluxo de promoção (na apresentação)

1. Você desenvolve na branch `homolog` e dá push. O Actions roda e atualiza Homologação.
2. Quando a mudança estiver validada em Homolog, abra o PR:
   - No GitHub: **Pull requests → New pull request**
   - **base: `main`**  ←  **compare: `homolog`**
   - **Create pull request**
3. Dentro do PR, o GitHub mostra o resultado da Integração:
   - **Verde:** botão **Merge pull request** habilitado.
   - **Vermelho:** merge **bloqueado** (graças ao Branch Protection).
4. Clique **Merge pull request** → **Confirm merge**.
5. O merge gera um push na `main` → o Actions roda de novo e o job **deploy-prod**
   atualiza a Produção.

## Como isso reforça sua demonstração

- **Momento "erro bloqueia"**: com o erro de sintaxe na `homolog`, se você abrir o PR para a
  `main`, o merge fica **travado** porque a Integração está vermelha. Prova visual e inegável
  de que código quebrado não chega à produção.
- **Rastreabilidade**: cada promoção é um PR registrado, ligado às issues e commits.
  Exatamente o que a disciplina valoriza.

## Observação

O Actions agora roda também em `pull_request` para a `main` — por isso o status aparece
dentro do PR. O deploy de produção continua acontecendo só no **merge** (push na main),
nunca na simples abertura do PR.

---

## PR automático (configurado no pipeline)

O pipeline cria o Pull Request `homolog → main` **automaticamente** quando o deploy de
Homologação termina com sucesso. Você não precisa abrir o PR na mão — só revisar e
clicar **Merge** (ou **Close** se não quiser promover).

### Pré-requisito (configuração única no GitHub)

Para o Actions ter permissão de criar PRs:

1. **Settings → Actions → General → Workflow permissions**
2. Marque **"Read and write permissions"**
3. Marque **"Allow GitHub Actions to create and approve pull requests"**
4. Salve.

Sem isso, o job `abrir-pr` falha com erro de permissão (`GraphQL: ... permission`).

### Fluxo resultante

```
push na homolog
  → Integração (testes + qualidade + build)
  → deploy-homolog (atualiza Homologação na VM)
  → abrir-pr (cria/atualiza o PR homolog → main automaticamente)
       você revisa e clica Merge
       → push na main
          → Integração + deploy-prod (atualiza Produção)
```

O job `abrir-pr` é inteligente: se já houver um PR aberto de `homolog → main`, ele não
cria outro — o PR existente é atualizado com o novo commit automaticamente pelo GitHub.
