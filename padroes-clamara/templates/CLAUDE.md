# Padrões do projeto — {{PROJECT_NAME}}

Instruções para a `{{API_PROJECT}}` (.NET {{DOTNET_VERSION}})<!-- CLAMARA:IF_FRONTEND --> e o frontend Angular {{ANGULAR_VERSION}} + Angular Material {{MATERIAL_VERSION}}<!-- /CLAMARA:IF_FRONTEND -->. **Seguir exatamente.**

> **Convenções de código** (Clean Code, nomenclatura, documentação, design do front, `if/else`, exceptions, migrations) estão em [`CONVENTIONS.md`](CONVENTIONS.md) — leia e siga antes de escrever ou alterar código.
<!-- CLAMARA:IF_DESIGN_SYSTEM -->>
> **Design visual / regras de template** estão em [`DESIGN-SYSTEM.md`](DESIGN-SYSTEM.md) (Clamara Design System), com a referência de HTML em [`clamara-design-system.html`](clamara-design-system.html). Todo template/tela **DEVE** seguir esse design system.
<!-- /CLAMARA:IF_DESIGN_SYSTEM -->

## Stack

- **Backend:** .NET {{DOTNET_VERSION}}, `{{API_PROJECT}}` + camadas (`{{DOMAIN_PROJECT}}`, `{{INFRA_PROJECT}}`). Banco **{{DB_ENGINE}}**, acesso via EF Core {{EFCORE_VERSION}} + {{DB_PROVIDER}}.
<!-- CLAMARA:IF_FRONTEND -->- **Frontend:** Angular {{ANGULAR_VERSION}} (standalone components + signals) + Angular Material {{MATERIAL_VERSION}} + SCSS. **Ionic não é usado** — não usar `ion-*`, `@ionic/*`, Capacitor nem tokens `--ion-*`.
<!-- /CLAMARA:IF_FRONTEND -->- **Empacotamento:** Docker, com **containers separados por portas diferentes** para frontend e backend.

## Context7 — documentação sempre atualizada

**Sempre usar o Context7 antes de gerar código, configuração ou exemplos que envolvam bibliotecas externas** — mesmo as conhecidas — para não cair em API defasada. A base de treino pode não refletir mudanças recentes. Vale para o backend (ASP.NET Core, EF Core, {{DB_PROVIDER}}, xUnit)<!-- CLAMARA:IF_FRONTEND --> e para o frontend (Angular, Angular Material, RxJS)<!-- /CLAMARA:IF_FRONTEND -->.

1. **`resolve-library-id`** para achar a biblioteca correspondente — a menos que o usuário informe o ID exato no formato `/org/project`.
2. **`query-docs`** com o ID encontrado, buscando por conceito (não por palavra solta) e um conceito por chamada.
3. **Priorizar documentação compatível com a stack deste projeto:** **.NET {{DOTNET_VERSION}} / C# / EF Core {{EFCORE_VERSION}} / {{DB_PROVIDER}}** no backend<!-- CLAMARA:IF_FRONTEND --> e **Angular {{ANGULAR_VERSION}} / Angular Material {{MATERIAL_VERSION}} / RxJS** no frontend<!-- /CLAMARA:IF_FRONTEND -->, conforme os pacotes do `.csproj`<!-- CLAMARA:IF_FRONTEND --> e do `package.json`<!-- /CLAMARA:IF_FRONTEND -->.
4. **Não usar** APIs de .NET Framework nem de versões antigas do ASP.NET<!-- CLAMARA:IF_FRONTEND -->; nem padrões de Angular legado (`NgModule`, `*ngIf`/`*ngFor`) — seguir standalone components + signals, como manda o [`CONVENTIONS.md`](CONVENTIONS.md)<!-- /CLAMARA:IF_FRONTEND -->.
5. **Não usar Context7** para refatoração, scripts do zero, regra de negócio, code review ou conceitos gerais de programação.

## Docker e ambientes — INEGOCIÁVEL

- **Frontend e backend em containers separados, em portas distintas** (frontend `{{FRONTEND_PORT}}`, backend `{{BACKEND_PORT}}`). Nunca subir os dois no mesmo container/porta.
- **Produção usa um {{DB_ENGINE}} externo** (fora do compose). A app se conecta a ele por connection string vinda de variável de ambiente — nunca hardcodar credenciais no código ou no compose versionado.
- **Desenvolvimento sobe um {{DB_ENGINE}} próprio em porta alternativa** (`{{DEV_DB_PORT}}` no host) para **não conflitar** com outros projetos/banco já rodando no mesmo desktop.
- **Segredos por variável de ambiente / arquivo não versionado** (`.env` local, secrets do runner). Não commitar `.env` com credencial real.

## Git

- **Nunca fazer commit.** Não rodar `git commit`, `git push`, `git merge` nem qualquer comando que altere o histórico. Fazer apenas as alterações nos arquivos e deixar o commit para o usuário.

## Produção — acesso e autorização — INEGOCIÁVEL
<!-- CLAMARA:PROD_TBD -->
> A infraestrutura de produção (host, deploy, container do backend, {{DB_ENGINE}} externo) **ainda não foi provisionada**. Quando for, registrar aqui host de acesso, forma de deploy e nome dos containers/serviços — e manter as regras abaixo, que valem desde já.
<!-- /CLAMARA:PROD_TBD -->
<!-- CLAMARA:PROD_KNOWN -->
> Host de acesso: `PREENCHER`. Deploy: `PREENCHER`. Containers/serviços: `PREENCHER`. (A senha/credencial NUNCA fica registrada aqui.)
<!-- /CLAMARA:PROD_KNOWN -->

- **Só leitura por padrão.** Diagnóstico é livre: status dos containers (`docker ps`, `docker logs`), `journalctl` do host, `SELECT` no banco, ler arquivo de configuração. Nada disso precisa perguntar.

- **Qualquer coisa que ALTERE produção exige autorização explícita do usuário,
  pedida na hora e para aquela ação.** Isso inclui — e não se limita a —
  reiniciar/parar/recriar container (`docker restart/stop/compose up`), editar arquivo
  no servidor, `UPDATE`/`INSERT`/`DELETE`/DDL no banco, mexer no runner de deploy, e
  rodar deploy. Ter acesso é acesso, não é autorização: uma coisa não implica a outra,
  e autorização dada uma vez não vale para a próxima.

- **Senha/credencial de produção não entra em lugar nenhum.** Não pedir, não guardar,
  não aceitar credencial colada no chat — se aparecer, ela está comprometida e o certo
  é trocá-la. Preferir acesso por chave; connection string do {{DB_ENGINE}} externo só
  via variável de ambiente no servidor.

- O repositório é privado; por isso dados de infra podem ser registrados aqui. Se um
  dia ele virar público, esta seção é a primeira coisa a sair.

## Migrations — INEGOCIÁVEL

> Detalhes de EF Core {{EFCORE_VERSION}} + {{DB_PROVIDER}} (como criar, revisar e o auto-baseline) estão em [`CONVENTIONS.md`](CONVENTIONS.md). As regras abaixo são invioláveis.

- **Migration que já está no `master` NUNCA é removida nem recriada.** Nada de
  `dotnet ef migrations remove` seguido de `add` numa migration que já foi empurrada.
  A mudança vira uma migration NOVA por cima.

  O motivo é concreto: o `MigrationId` carrega o timestamp. Recriar gera outro id, o
  servidor não reconhece a migration como aplicada e tenta criar tabelas que já
  existem. No {{DB_ENGINE}} o DDL é transacional, então a migration que falhar no meio
  faz **rollback** — mas a app sobe com *fail-fast*: em toda subida seguinte ela tenta
  aplicar de novo, bate no mesmo `already exists`, aborta e **não sobe**. Fica no laço
  até intervenção manual no banco (`__EFMigrationsHistory`).

- **Antes de mexer numa migration, confira se ela já foi publicada:**

  ```bash
  git log --oneline origin/master -- 'backend/{{INFRA_PROJECT}}/Migrations/*NomeDaMigration*'
  ```

  Voltou commit? Ela está lá fora. Não mexa.

- **Sempre revisar o que o `ef migrations add` gerou antes de commitar.** O gerador
  costuma incluir `AlterColumn` da coluna de identidade de TODAS as tabelas — deriva
  de snapshot, semanticamente no-op, mas são ALTERs em tabela de produção. Apagar da
  migration e deixar só as operações da mudança. O snapshot absorve a deriva e a
  próxima migration nasce limpa.

- **Migration que SÓ cria tabela** pode entrar no auto-baseline do `DatabaseMigrator`.
  Migration que ALTERA tabela existente (`AddColumn`, backfill) **nunca** — ela
  precisa rodar de verdade.

## Testes E2E — INEGOCIÁVEL
<!-- CLAMARA:IF_FRONTEND -->
Toda feature ou mudança de comportamento **DEVE** ser validada **end-to-end (E2E)** pelo **Claude Chrome** (o navegador real, com a sessão logada) contra o dev server em Docker. Sem E2E cobrindo o fluxo, a tarefa **não está concluída** — não reporte como pronta.

- **Ferramenta: Claude Chrome** — dirigir o app real (frontend em Docker, na porta de dev) pela sessão do Claude Chrome (`mcp__claude-in-chrome__*`), exercitando a UI como o usuário. **Não** configurar suíte automatizada (Playwright/Cypress); a validação E2E é feita pelo Claude Chrome.
- **Reutilizar sempre a aba existente** — checar `tabs_context_mcp` e navegar na aba já aberta do app; **não** abrir aba nova a cada validação. Só criar aba nova se não houver nenhuma ou se a existente estiver travada (renderer congelado); nesse caso, fechar a abandonada.
- **Cobrir o caminho feliz + os estados principais** — sucesso, vazio, erro/validação e, quando houver, não autenticado. Cada fluxo novo precisa ser exercitado.
- **Rodar de verdade antes de dar como pronto** — executar o fluxo no Claude Chrome e reportar o **resultado real** (o que aconteceu na tela / na resposta da API), com evidência (screenshot ou leitura da página/rede). Nunca afirmar que passou sem ter rodado.
- **Sem mock do caminho crítico** — o E2E exercita a UI real ponta a ponta contra o backend em Docker. Detalhes finos ficam nos testes unitários (`ng test`).
- **Não mutar dados reais** — usar registros de teste claramente rotulados (ex.: prefixo `TESTE`) e **limpá-los ao final** (deletar o que foi criado). Nunca alterar ou remover dados que não foram criados na própria validação.
- **Seletores estáveis** — ao inspecionar a página, preferir `data-testid` (ou roles/acessibilidade), nunca depender de texto volátil ou de classes de estilo.
- **Manter verde** — mudou o comportamento, revalide o fluxo no mesmo passo. Fluxo quebrado bloqueia a conclusão.
<!-- /CLAMARA:IF_FRONTEND -->
