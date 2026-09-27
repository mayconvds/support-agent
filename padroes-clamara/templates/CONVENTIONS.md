# Convenções de código — {{PROJECT_NAME}}

Padrões de código do projeto (`{{API_PROJECT}}` em .NET {{DOTNET_VERSION}}<!-- CLAMARA:IF_FRONTEND --> e frontend Angular {{ANGULAR_VERSION}} + Angular Material {{MATERIAL_VERSION}}<!-- /CLAMARA:IF_FRONTEND -->). Valem para **qualquer** contribuidor ou ferramenta. **Seguir exatamente.**

> Regras de fluxo de trabalho do agente (Git, Docker, produção, Context7, validação E2E) ficam no [`CLAUDE.md`](CLAUDE.md).
<!-- CLAMARA:IF_DESIGN_SYSTEM -->> Design visual e regras de template ficam em [`DESIGN-SYSTEM.md`](DESIGN-SYSTEM.md) (Clamara), com referência de HTML em [`clamara-design-system.html`](clamara-design-system.html).
<!-- /CLAMARA:IF_DESIGN_SYSTEM -->

## Clean Code

Escrever sempre **clean code**:

- **Nomes claros e intencionais** — variáveis, métodos e classes revelam o propósito; sem abreviações obscuras.
- **Métodos pequenos e com responsabilidade única** — cada função faz uma coisa; extrair quando crescer.
- **Sem duplicação (DRY)** — reutilizar/extrair em vez de copiar.
- **Sem números/strings mágicos** — usar constantes/enums nomeados.
- **Baixo aninhamento** — guard clauses (ver regra abaixo), early return, sem pirâmides de indentação.
- **Sem código morto** — remover comentários obsoletos, `using` e variáveis não usados.
- **Comentários explicam o "porquê"**, não o "o quê" (o código já diz o quê).
- Seguir os idiomas e o estilo já existentes no arquivo/pasta em que se está mexendo.

## Nomenclatura — INEGOCIÁVEL

- **Nomes de funções, variáveis e propriedades sempre em inglês** — em qualquer linguagem, sem exceção.
  Vale para variáveis locais, parâmetros, campos, métodos, propriedades, classes, interfaces, enums e
  **nomes de método de teste**. A descrição de um teste não é identificador: o texto de `it('...')` e de
  `describe('...')` segue em pt-BR, como a documentação. Identificador em português é motivo de rejeição
  na revisão mesmo que o código funcione, mesmo em variável de uma linha e mesmo em código "temporário".
  Só texto voltado ao usuário final (mensagens de validação, labels da UI) fica em pt-BR — e
  comentários/documentação, que por regra própria são em português.
  - ❌ `var totalGasto = ...;` / `void CalcularTotal()`
  - ✅ `var totalSpent = ...;` / `void CalculateTotal()`
- **C# — propriedades e métodos em `PascalCase`**; variáveis locais e parâmetros em `camelCase`.
<!-- CLAMARA:IF_FRONTEND -->- **TypeScript — propriedades, variáveis e métodos em `camelCase`**.
<!-- /CLAMARA:IF_FRONTEND -->- **Banco de dados — nomes de tabela e coluna sempre em inglês** e em `snake_case` (ex.: `created_at`, não `criado_em`). Valores/enum armazenados também em inglês. Só o rótulo exibido ao usuário é traduzido no front.

## Documentação de código — em português

Membros públicos **DEVEM** ter documentação em **pt-BR**. O identificador continua em inglês (regra acima); o **texto da documentação** é em português. A doc descreve o contrato e o "porquê" — não repete o óbvio do nome.

### C# — comentário XML (`///`)

Documentar classes, métodos e propriedades **públicas** com `<summary>`; usar `<param>`, `<returns>` e `<exception>` quando houver.

```csharp
/// <summary>
/// Descreve o que o método faz e o "porquê" — nunca parafraseia o nome.
/// </summary>
/// <param name="items">O que recebe.</param>
/// <returns>O que devolve.</returns>
/// <exception cref="ValidationsErrorException">Quando falha a validação de negócio.</exception>
public decimal CalculateTotal(IReadOnlyList<Item> items)
```
<!-- CLAMARA:IF_FRONTEND -->
### TypeScript — comentário JSDoc/TSDoc (`/** */`)

Documentar funções, métodos e classes **públicas** de `services/` e `models/` com `/** */`; usar `@param` e `@returns` quando ajudarem.

```ts
/**
 * Descreve o contrato e o porquê da função.
 * @param input O que recebe.
 * @returns O que devolve.
 */
export function transform(input: InputModel): OutputModel
```
<!-- /CLAMARA:IF_FRONTEND -->
**Diretrizes:**
- Documentar o **contrato** (o que recebe, o que devolve, o que lança) e o **porquê** — nunca parafrasear o nome do método.
- Comentários inline dentro do corpo continuam explicando só o "porquê", como no Clean Code.
- Não documentar o trivial (getters/setters óbvios, DTOs autoexplicativos); o esforço vai para regra de negócio, resolvedores, services e contratos públicos.
<!-- CLAMARA:IF_FRONTEND -->
## Front-end (Angular {{ANGULAR_VERSION}} + Angular Material {{MATERIAL_VERSION}})

Stack: Angular {{ANGULAR_VERSION}} (**standalone components** + signals) + Angular Material {{MATERIAL_VERSION}} + SCSS. **Sem Ionic/Capacitor.** Segue os padrões da pasta em que se está mexendo<!-- CLAMARA:IF_DESIGN_SYSTEM --> e, para o visual, o [`DESIGN-SYSTEM.md`](DESIGN-SYSTEM.md)<!-- /CLAMARA:IF_DESIGN_SYSTEM -->.
<!-- CLAMARA:IF_DESIGN_SYSTEM -->
### Design — seguir o Clamara Design System

O visual é definido pelo Clamara (ver [`DESIGN-SYSTEM.md`](DESIGN-SYSTEM.md) e [`clamara-design-system.html`](clamara-design-system.html)). Pontos que o código não pode violar:

- **"Preto age, ciano indica."** Ação neutra = preto (claro) / branco (escuro); ação com consequência usa a cor da função (verde conclui, vermelho destrói, âmbar pede atenção). **Nunca existe botão ciano.** Ciano ≤ ~8% da tela.
- **Tokens são a fonte de verdade** — cor, forma, espaçamento, tipografia vêm dos tokens CSS do design system. **Nunca** hardcodar cor, raio ou espaçamento no componente; usar `var(--...)`. Cor nova/ajuste = editar o token global, não o componente.
- **Tema claro E escuro** — validar nos dois (`[data-theme="dark"]`); contraste AA. **Nunca** texto `--cyan` sobre branco; usar `--cyan-text` no claro.
- **Angular Material por token** — configurar via `mat.theme` + `mat.theme-overrides` com a paleta do design system, corners 4/6/10, ripple global desativado, `mat-card appearance="outlined"`.
- **Componentes próprios (não Material)** — status, placa/identificador, sidebar e linha do tempo são componentes do projeto.
- **Status = forma + cor + palavra** — todo estado tem rótulo escrito, nunca só cor.
- **Uma ação primária por tela.** Confirmação só para o que não tem volta; **nunca** `alert()`/`confirm()`/`prompt()` — usar `ConfirmService` (MatDialog) que retorna `Promise<boolean>`.
<!-- /CLAMARA:IF_DESIGN_SYSTEM -->
### Padrão técnico

- **Standalone components** — sem `NgModule` novo; declarar `imports` no próprio componente. Usar `ChangeDetectionStrategy.OnPush`.
- **Signals e a nova API de I/O** — estado com `signal`/`computed`; entradas com `input()`/`input.required()`, saídas com `output()`. Fluxo no template com `@if`/`@for`/`@switch` (nada de `*ngIf`/`*ngFor` novos).
- **Tipar tudo** — sem `any`; interfaces/models em `models/`.
- **Lógica em services** — componentes cuidam de apresentação; regra/HTTP ficam em `services/`. HTTP via `HttpClient` tipado; preferir injeção com `inject()`.
- **SCSS enxuto** — estilos escopados ao componente; sem `!important`; sem seletores profundos frágeis.
- **Sem estado morto** — remover imports, variáveis e estilos não usados.
<!-- /CLAMARA:IF_FRONTEND -->
## Nunca usar `if/else`

Proibido `else` e `else if`. Use **guard clauses** (early return / early throw) e mantenha o "caminho feliz" no nível de indentação principal.

- Valide as pré-condições no topo do método; cada falha faz `throw` (ou `return`) imediato.
- Para escolher entre valores, use `switch`/expressão `switch`, operador ternário ou dicionário de mapeamento — nunca `if/else`.
- Um `if` isolado (guard) é permitido; o que é proibido é o par `if/else`.

```csharp
// ✅ Guard clause — sem else
if (entity is null)
    throw new ValidationsErrorException("Registro não encontrado.");

Process(entity);
```

## Regra de throw de exception

Falhas de validação/regra de negócio **lançam exceção** — não retornam código de erro nem usam `if/else` para desviar o fluxo. O tratamento é **centralizado**, nunca por `try/catch` local para montar resposta.

- **`ValidationsErrorException`** (em `{{EXCEPTIONS_NAMESPACE}}`) — para erro de validação/negócio. Aceita `string` (mensagem única) ou `List<string>` (várias). Resulta em **HTTP 400** com `ErrorResponse`.
- **`ApplicationExceptions`** — base de exceções da aplicação (herda de `SystemException`).
- **`ExceptionFilters`** (`IExceptionFilter`, registrado global no `Program.cs`) é quem captura: `ValidationsErrorException` → 400; qualquer outra é logada e vira erro genérico. **Não** replicar esse tratamento nos controllers/repositórios.

Diretrizes:
- **Não** engolir exceção (`catch` vazio) nem transformar erro de negócio em `bool`/`null` de retorno.
- **Não** usar exceção para controle de fluxo normal — apenas para pré-condições e erros.
- Mensagens de validação em **pt-BR**, voltadas ao usuário final.

## Migrations (EF Core {{EFCORE_VERSION}} + {{DB_PROVIDER}}/{{DB_ENGINE}})

Migrations ficam em `backend/{{INFRA_PROJECT}}/Migrations`, sobre o `{{DB_CONTEXT}}`. Cada uma gera **três** arquivos que andam juntos e vão no mesmo commit: `<timestamp>_<Nome>.cs`, `<timestamp>_<Nome>.Designer.cs` e a atualização do `{{DB_CONTEXT}}ModelSnapshot.cs`. Commit sem o snapshot faz a próxima migration nascer errada.

### Quem aplica

A API aplica no **startup** — `DatabaseMigrator.ApplyMigrationsAsync`, chamado no `Program.cs` dentro de um `try/catch` que derruba a aplicação se falhar (fail-fast: melhor não subir do que servir com schema inconsistente). **O pipeline de deploy não roda migration**; subir a versão nova (o container novo) já migra.

No {{DB_ENGINE}} o DDL é **transacional**: o EF Core/{{DB_PROVIDER}} envolve cada migration numa transação, então uma migration que falhar no meio faz rollback (não deixa objeto meio-criado). Isso **não** dispensa as regras do `CLAUDE.md`: recriar migration já publicada continua derrubando produção, porque o `MigrationId` muda e a app entra em laço de `already exists` a cada boot.

O migrador faz **auto-baseline**: se as tabelas de uma migration já existem no banco, ela é gravada no `__EFMigrationsHistory` sem rodar. A lista fica em `DatabaseMigrator.Baselines`, como pares `(sufixo do MigrationId, tabela representativa)`.

- **Entra na lista:** migration que só **cria tabela**.
- **Nunca entra:** migration que altera tabela existente — `AddColumn`, `DropColumn`, backfill. Ela **precisa rodar de verdade**; baselinar uma dessas deixa o banco sem a coluna e sem erro nenhum.

### Como criar

```bash
cd backend
dotnet ef migrations add NomeDaMigration --project {{INFRA_PROJECT}} --startup-project {{API_PROJECT}}
```

- **`--startup-project {{API_PROJECT}}` é obrigatório.** O pacote `Microsoft.EntityFrameworkCore.Design` está só na API.
- **Nunca usar `--no-build`.** O comando lê o **assembly compilado**: com `--no-build` sobre um build velho a migration nasce **vazia** e o erro só aparece em produção.
- **Fechar a API antes.** Com ela rodando, o build falha ao copiar as DLLs.
- **Banco lido em tempo de design:** vem do `{{DB_CONTEXT}}Factory` (`IDesignTimeDbContextFactory`), pela env `MIGRATIONS_CONNECTION`, com default local (o banco de dev do Docker, na porta alternativa).

### Revisar sempre o que o EF gerou

1. **Ordem das operações.** Quando a mudança **move dados**, a ordem correta é **criar → copiar → derrubar**, com um `migrationBuilder.Sql` no meio. Trocar isso apaga dado do usuário.
2. **Backfill idempotente.** Todo `Sql` de correção leva um `WHERE` que o torna inócuo na segunda execução.
3. **`Down` que desfaz de verdade.** Se o `Down` não recria coluna/tabela/dado, assuma por escrito no PR que não há rollback.
4. **Comentar o "porquê"** das partes editadas à mão.
5. **SQL no dialeto do banco.** Usar as funções do {{DB_ENGINE}} (ex.: `date_trunc`, `to_char`, `COALESCE`), nunca funções de outro SGBD.

### Schema

O mapeamento é por **atributo na entidade** (`{{DOMAIN_PROJECT}}/Entities/…`), não fluent — o fluent no `OnModelCreating` fica só para relacionamento e índice composto.

- **Tabela e coluna em `snake_case` e em inglês**, prefixo `app_` nas tabelas da aplicação. Nome de coluna e `JsonPropertyName` são o mesmo texto.
- **Toda tabela tem `id` identity, `created_at` (`NOT NULL`) e `updated_at` (nulável).**
- **Datas/horas em `timestamptz`** (usar `DateTimeOffset`, gravar em UTC). {{DB_ENGINE}} é UTF-8 nativo — não anotar charset por coluna.
- **Restrição de negócio vira índice**, não checagem só no C#.
- **Arquivo nunca vai para o banco** — grava-se o caminho, o binário fica no storage.

### Nunca

- **Editar migration já aplicada em produção.** Corrija com uma migration nova.
- **Renomear ou apagar migration antiga** pelo mesmo motivo.
- **`EnsureCreated()`** — ele ignora o histórico e não convive com migration.
