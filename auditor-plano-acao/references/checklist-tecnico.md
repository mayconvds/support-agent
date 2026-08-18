# Checklist — Plano técnico de implementação

Use para planos de desenvolvimento, refatoração, migração de banco, integração com terceiros e deploy. Passe seção por seção. Para cada item, a pergunta não é "o plano faz isso certo?" e sim "o plano diz como faz? se não diz, é lacuna".

## Índice

1. Autenticação e autorização
2. Entrada de dados e injeção
3. Segredos e configuração
4. Dados sensíveis e LGPD
5. Banco de dados e migrations
6. Dependências e cadeia de suprimentos
7. Deploy, rollback e observabilidade
8. Consistência interna do plano

---

## 1. Autenticação e autorização

- Cada endpoint/tela/job novo diz explicitamente quem pode acessar? Endpoint sem authz declarada é ALTO por padrão.
- Há verificação de **posse do recurso**, não só de papel? O caso clássico de IDOR: `GET /pedidos/{id}` valida que o usuário está logado mas não que o pedido é dele.
- Filtros de escopo (`empresaId`, `tenantId`, `clienteId`) vêm do token/sessão ou do cliente? Vindo do cliente é vulnerabilidade, não configuração.
- O plano cria algum bypass "temporário" para teste/homologação? Bypass temporário sem data e responsável vira permanente — CRÍTICO se tocar produção.
- Mudança em regra de permissão vem acompanhada de como as permissões existentes serão migradas? Usuário que perde acesso silenciosamente e usuário que ganha acesso indevido são o mesmo bug.
- Sessão/token: o plano mexe em expiração, refresh ou revogação? Se sim, diz o que acontece com as sessões já emitidas?

**C#**: `[Authorize]` sem policy só autentica. Confira se há `[Authorize(Policy = ...)]` ou checagem explícita no handler.
**PHP**: middleware de rota (Laravel `can:`, Symfony voters) cobre o controller inteiro? Rota nova fora do grupo protegido é o erro mais comum.
**TypeScript/Node**: middleware de auth aplicado antes do router da feature nova, e não só nas rotas antigas.

## 2. Entrada de dados e injeção

- SQL montado por concatenação/interpolação em qualquer passo? Procure por `$"...{var}..."`, `"..." . $var . "..."`, template literal em query.
- ORM com `raw`/`fromSql`/`whereRaw` recebendo valor de usuário?
- Nome de tabela/coluna/direção de `ORDER BY` vindo de input? Parâmetro não protege identificador — precisa de allowlist.
- Comando de sistema, path de arquivo ou URL montados com input? (command injection, path traversal, SSRF).
- Upload de arquivo: valida tipo pelo conteúdo (não pela extensão), limita tamanho, e grava fora do diretório servido publicamente?
- Saída em HTML/template escapa por padrão? O plano introduz algum `dangerouslySetInnerHTML`, `v-html`, `{!! !!}` ou `Html.Raw`?
- Desserialização de payload externo em tipo dinâmico/polimórfico?

**C#**: `SqlCommand` com `Parameters.AddWithValue`, `FromSqlInterpolated` (seguro) vs `FromSqlRaw` (perigoso com concatenação).
**PHP**: PDO com prepared statements e `PDO::ATTR_EMULATE_PREPARES => false`; cuidado com `DB::raw()`.
**TypeScript**: query builders parametrizados (Prisma, Knex `?`), evitar `$queryRawUnsafe`.

## 3. Segredos e configuração

- Alguma credencial, token, chave de API ou connection string aparece no plano em texto claro, ou vai para arquivo versionado (`appsettings.json`, `.env` commitado, `config.php`)? CRÍTICO.
- Segredo novo: onde nasce, quem tem acesso, como rotaciona? Plano que cria segredo sem plano de rotação é ALTO.
- Se um segredo foi exposto, o plano prevê **rotação** ou só remoção do repositório? Remover do repositório não invalida a chave — o histórico e quem já copiou continuam válidos.
- Configuração de produção separada de dev/homologação? Plano que usa a mesma chave nos dois ambientes é ALTO.
- Debug, stack trace detalhado, Swagger/Actuator/phpinfo expostos em produção?
- CORS: o plano libera `*` ou reflete o `Origin` recebido? Combinado com credenciais, é CRÍTICO.

## 4. Dados sensíveis e LGPD

- Que dado pessoal o plano toca? CPF, e-mail, telefone, endereço, dado de saúde, biometria, dado financeiro.
- Dado sensível vai para log, mensagem de erro, evento de analytics ou payload de webhook?
- Dado de produção é copiado para homologação/dev? É CRÍTICO se a base contém dado pessoal e o plano não declara anonimização; ALTO se anonimiza parcialmente ou se o ambiente destino tem controle de acesso equivalente ao de produção e isso está escrito. Se o plano não declara o controle de acesso do destino, trate o destino como não controlado — é a suposição que erra para o lado seguro.
- Criptografia: o plano diz **o quê**, **com qual algoritmo** e **onde fica a chave**? "Vamos criptografar" sem os três é lacuna, não controle.
- Senha: hash com algoritmo adequado (bcrypt/argon2), nunca MD5/SHA1 puro, nunca criptografia reversível.
- Exportação/relatório novo: quem pode baixar, e o arquivo gerado fica acessível por URL adivinhável?
- Retenção e exclusão: o plano cria dado novo sem dizer por quanto tempo fica?
- Terceiro recebe dado? Há base legal e contrato, e o volume enviado é o mínimo necessário?

## 5. Banco de dados e migrations

- Migration é reversível? Se o `Down`/rollback não existe ou não desfaz de fato, o plano não tem rollback — só acha que tem.
- Há `DROP`, `TRUNCATE`, `DELETE` sem `WHERE`, ou `ALTER COLUMN` que trunca dado? Exige backup verificado antes — não basta "temos backup", precisa de restore testado.
- Tabela grande: a operação trava a tabela? `ALTER TABLE` bloqueante em tabela de milhões de linhas em horário de pico é incidente de disponibilidade.
- Backfill de dados roda em lote com ponto de retomada, ou é uma transação gigante que estoura timeout no meio?
- Ordem dos passos: o passo N usa objeto criado no passo N+1? Deploy de código novo vai antes ou depois da migration? Se código novo exige coluna que ainda não existe, o deploy quebra na janela entre os dois.
- Índice novo em coluna usada em filtro de segurança, ou índice que muda plano de query crítica?
- Constraint de unicidade adicionada sobre dado que já tem duplicata falha em produção mesmo tendo passado em dev.

## 6. Dependências e cadeia de suprimentos

- Pacote novo: é mantido, quantos downloads, quando foi o último release? Pacote com nome parecido com um popular é typosquatting.
- Versão fixada (lockfile atualizado) ou range aberto?
- O plano roda `npm audit` / `dotnet list package --vulnerable` / `composer audit`?
- Script de build/postinstall de terceiro executando com acesso a segredos de CI?
- Imagem base de container com tag `latest` ou sem digest fixado?

## 7. Deploy, rollback e observabilidade

- Existe passo de rollback **explícito e testado**, não só "voltar a versão anterior"?
- Qual o critério objetivo para acionar rollback, e quem decide?
- Janela de execução e impacto no usuário estão declarados? Downtime não declarado é inconsistência.
- Feature flag: o plano permite desligar sem novo deploy?
- Como se detecta que deu errado? Métrica, alerta, log — se ninguém está olhando, o rollback só acontece quando o cliente reclamar.
- Passo manual crítico documentado com o comando exato, ou é "o fulano faz"? Passo que só uma pessoa sabe executar é risco operacional.
- Auditoria: ações sensíveis novas geram registro de quem fez o quê e quando?

## 8. Consistência interna do plano

Aqui nascem quase todos os achados `I-`:

- Ordem dos passos faz sentido? Dependência usada antes de existir.
- Passos se contradizem? Ex.: passo 2 diz "manter compatibilidade com a API v1", passo 6 remove o endpoint v1.
- Prazo/esforço bate com o escopo, e as dependências externas cabem no prazo?
- Papéis definidos? "Alguém precisa aprovar" sem dizer quem é lacuna.
- Critério de sucesso é verificável, ou é "funcionar bem"?
- O que fica fora do escopo está declarado? Escopo aberto vira mudança não auditada.
- Há teste cobrindo justamente a mudança de comportamento, incluindo o caso negativo (usuário sem permissão recebe 403)?
