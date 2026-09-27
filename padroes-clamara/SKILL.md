---
name: padroes-clamara
description: "Instala os padrões de projeto (CLAUDE.md + CONVENTIONS.md) no estilo LavaJatoClarama/Clamara — .NET + Angular Material + PostgreSQL + Docker — em um projeto. SEMPRE pergunta ao usuário o que é necessário (nome do projeto, versões, portas, banco, produção, design system) antes de gerar. Gera APENAS CLAUDE.md e CONVENTIONS.md, nada mais. Trigger: /padroes-clamara"
---

# /padroes-clamara

Instala em um projeto os dois arquivos de padrões no estilo **LavaJatoClarama / Clamara Design System**:

- `CLAUDE.md` — fluxo de trabalho do agente (stack, Docker, produção, Git, migrations, E2E).
- `CONVENTIONS.md` — convenções de código (Clean Code, nomenclatura, documentação, front-end Angular Material, `if/else`, exceptions, migrations).

**Gera APENAS esses dois arquivos.** Nunca cria `DESIGN-SYSTEM.md`, HTML de design, código, `docker-compose` ou estrutura de projeto — só os dois `.md`.

## Regra inegociável: SEMPRE perguntar antes de gerar

Nunca gere os arquivos com valores assumidos em silêncio. **Antes de escrever qualquer arquivo**, colete as respostas abaixo do usuário. Use a ferramenta `AskUserQuestion` para as escolhas fechadas (com as opções sugeridas como recomendadas) e pergunte em texto o que for aberto (nome, host de produção). Se o usuário passar o nome do projeto como argumento (`/padroes-clamara MeuProjeto`), use-o e não repita essa pergunta.

### O que perguntar (o "necessário para instalar")

1. **Nome do projeto** (aberto) — ex.: `LavaJatoClarama`. Base para os nomes de projeto .NET (`<Nome>.Api`, `<Nome>.Domain`, `<Nome>.Infrastructure`), o `DbContext` (`<Nome>Context`) e o namespace de exceptions (`<Nome>.Api.Exceptions`).
2. **Versão do .NET** — opções: `10` (recomendada), `9`, `8`.
3. **Frontend** — opções: `Angular + Angular Material` (recomendada) | `sem frontend`. Se Angular, perguntar **versão do Angular** (ex.: `22`) e **versão do Material** (ex.: `22`). Atenção: o major do `@angular/material` acompanha o do `@angular/core` — Angular 22 usa Material 22 (não existe Material 23 com Angular 22). Confirmar no registro se houver dúvida.
4. **Usa o Clamara Design System?** — `Sim` (recomendada, mantém as referências a `DESIGN-SYSTEM.md`/`clamara-design-system.html` — que o usuário traz à parte) | `Não` (remove as referências, mantém só a orientação minimalista do Material). Só perguntar se houver frontend.
5. **Banco de dados** — opções: `PostgreSQL` (recomendada) | `outro` (nesse caso, ajustar dialeto/provider conforme informado). Assumir EF Core na versão do .NET.
6. **Portas do Docker** — frontend, backend e o PostgreSQL de **dev** (porta alternativa para não conflitar). Sugerir defaults: frontend `8080`, backend `8081`, Postgres dev `5433`. Confirmar ou ajustar.
7. **Produção** — opções: `A definir` (recomendada — deixa o bloco de infra como pendente) | `Informar agora` (então pedir host de acesso, forma de deploy e nomes dos containers/serviços, e preencher o bloco). Reforçar que **senha/credencial nunca entra no arquivo**.

Agrupe perguntas relacionadas numa mesma chamada de `AskUserQuestion` (até 4 por vez). Confirme o resumo das respostas antes de gerar.

## Como gerar

1. Ler os templates em `templates/CLAUDE.md` e `templates/CONVENTIONS.md` (ao lado deste `SKILL.md`).
2. Substituir os placeholders `{{...}}` pelas respostas:

   | Placeholder | Origem |
   |---|---|
   | `{{PROJECT_NAME}}` | nome do projeto |
   | `{{DOTNET_VERSION}}` | versão do .NET |
   | `{{EFCORE_VERSION}}` | mesma versão do .NET |
   | `{{ANGULAR_VERSION}}` | versão do Angular |
   | `{{MATERIAL_VERSION}}` | versão do Material |
   | `{{API_PROJECT}}` | `{{PROJECT_NAME}}.Api` |
   | `{{DOMAIN_PROJECT}}` | `{{PROJECT_NAME}}.Domain` |
   | `{{INFRA_PROJECT}}` | `{{PROJECT_NAME}}.Infrastructure` |
   | `{{DB_CONTEXT}}` | `{{PROJECT_NAME}}Context` |
   | `{{EXCEPTIONS_NAMESPACE}}` | `{{PROJECT_NAME}}.Api.Exceptions` |
   | `{{DB_ENGINE}}` | ex.: `PostgreSQL` |
   | `{{DB_PROVIDER}}` | ex.: `Npgsql` |
   | `{{DEV_DB_PORT}}` | porta do Postgres de dev |
   | `{{FRONTEND_PORT}}` | porta do frontend |
   | `{{BACKEND_PORT}}` | porta do backend |

3. **Blocos condicionais** marcados por comentários HTML:
   - `<!-- CLAMARA:IF_FRONTEND -->…<!-- /CLAMARA:IF_FRONTEND -->` — manter só se houver frontend; senão, remover o bloco inteiro.
   - `<!-- CLAMARA:IF_DESIGN_SYSTEM -->…<!-- /CLAMARA:IF_DESIGN_SYSTEM -->` — manter só se usar o Clamara Design System.
   - `<!-- CLAMARA:PROD_TBD -->…<!-- /CLAMARA:PROD_TBD -->` — manter se produção for "a definir".
   - `<!-- CLAMARA:PROD_KNOWN -->…<!-- /CLAMARA:PROD_KNOWN -->` — manter e preencher se a infra foi informada.
   Sempre **remover os próprios comentários de marcação** do resultado final.
4. Escrever `CLAUDE.md` e `CONVENTIONS.md` na **raiz do projeto** de destino (diretório de trabalho atual, salvo se o usuário indicar outro).
5. Se algum dos arquivos já existir, **avisar e pedir confirmação** antes de sobrescrever (mostrar o que muda). Nunca sobrescrever calado.
6. Se o design system foi mantido, lembrar o usuário de trazer `DESIGN-SYSTEM.md` e `clamara-design-system.html` (a skill não os gera).

## Depois de gerar

Reportar quais arquivos foram escritos e os valores usados (nome, versões, portas, estado da produção). Não fazer commit — deixar para o usuário.
