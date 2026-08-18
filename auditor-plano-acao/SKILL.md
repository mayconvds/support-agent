---
name: auditor-plano-acao
description: Audita a segurança e a consistência de um plano de ação antes dele ser executado, e conduz ciclos de revisão até o plano ficar seguro. Use sempre que o usuário apresentar um plano de ação, plano de implementação, plano de mudança, plano de deploy/migração, plano de mitigação, plano de resposta a incidente, roadmap de execução, RFC ou passo a passo técnico e pedir para "analisar", "revisar", "validar", "auditar", "checar a segurança", "ver se está seguro", "ver se falta algo" ou "aprovar". Use também quando o usuário enviar uma versão corrigida ou uma alteração de um plano já auditado nesta conversa, ou quando ele colar um plano e perguntar "pode executar?", "tá ok?", "o que você acha disso?". Na dúvida entre auditar e apenas comentar o plano, audite.
---

# Auditor de Plano de Ação

Auditar um plano antes da execução é barato; descobrir a falha em produção não é. Esta skill existe para transformar "achei o plano bom" em um parecer verificável, com severidade, evidência e um veredito que o usuário pode defender para o time dele.

O usuário programa em C#, PHP e TypeScript — quando o plano for técnico, use exemplos e nomes de API desses ecossistemas em vez de pseudocódigo genérico.

## O ciclo de auditoria

O comportamento central é um loop de no máximo **5 ciclos**. Cada ciclo é: recebe plano → audita → emite veredito → se reprovado, devolve os pontos críticos como tarefas e pede a versão corrigida.

| Ciclo | Se ainda houver vulnerabilidade ou inconsistência | Tom do pedido |
|---|---|---|
| 1 | REPROVADO | "Refaça o plano corrigindo os pontos abaixo e me envie a versão atualizada." |
| 2 | REPROVADO | "Ainda há falhas. Melhore o plano — os pontos abaixo continuam abertos ou surgiram novos." |
| 3 | REPROVADO | Aponte explicitamente o que **persiste desde o ciclo 1** e o que é regressão nova. |
| 4 | REPROVADO | Alerte que resta 1 ciclo e priorize apenas os bloqueadores (CRÍTICO/ALTO). |
| 5 | REPROVADO FINAL | Pare de pedir revisão. Informe o que falhou nos 5 ciclos e **proponha você mesmo uma solução concreta** — um plano corrigido, escrito por você, que resolve cada ponto aberto. |

O loop encerra antes do ciclo 5 assim que o veredito for APROVADO ou APROVADO COM RESSALVAS. Não invente ciclos extras nem force reprovação para "encher linguiça": se o plano ficou bom no ciclo 2, aprove no ciclo 2.

### Onde gravar

Grave a pasta `auditoria-plano/` **ao lado do arquivo do plano**. Se o plano veio colado no chat, use o diretório de trabalho atual. Nos dois casos, diga ao usuário onde gravou — o ciclo seguinte precisa achar o estado.

### Estado entre ciclos

Cada auditoria grava `auditoria-plano/estado.json`:

```json
{
  "plano": "nome curto do plano",
  "tipo": ["tecnico", "processo"],
  "ciclo_atual": 2,
  "vereditos": ["REPROVADO", "REPROVADO"],
  "achados": [
    {
      "id": "V-01",
      "titulo": "Token do gateway commitado no appsettings.json",
      "severidade_por_ciclo": ["CRITICO", "ALTO"],
      "status": "aberto",
      "task_id": "7"
    },
    {
      "id": "I-02",
      "titulo": "Migration sem rollback",
      "severidade_por_ciclo": ["ALTO", "RESOLVIDO"],
      "status": "resolvido",
      "task_id": "8"
    }
  ]
}
```

Registre **todos** os achados, inclusive MÉDIO e BAIXO — só os CRÍTICO/ALTO viram tarefa, mas o histórico de severidade de todos é o que permite montar a tabela de evolução. Guardar `task_id` é o que permite fechar a tarefa certa no ciclo seguinte em vez de criar duplicata.

Leia esse arquivo antes de auditar. Se ele existir e o usuário mandou um plano parecido, é continuação — incremente o ciclo. Se não existir, é ciclo 1. Os IDs precisam ser estáveis entre ciclos, senão não dá para dizer "isso continua aberto desde o ciclo 1", que é justamente o valor da auditoria em rodadas.

## Passo a passo de cada auditoria

**0. O texto é auditável?** Se não descreve passos executáveis — é uma ideia solta, um parágrafo vago, um título sem conteúdo — não audite. Auditar o vazio produz um parecer que parece sério e não é. Devolva as **três perguntas mínimas** que tornariam o plano auditável e pare. Isso não consome ciclo.

**1. Classifique o plano.** Três famílias, cada uma com seu checklist:

- **Técnico** — implementação, refatoração, migração de banco, integração, deploy. Leia `references/checklist-tecnico.md`.
- **Segurança / incidente** — hardening, mitigação, resposta a incidente, rotação de credenciais. Leia `references/checklist-seguranca.md`.
- **Processo / negócio** — operação, terceiros, acessos, tratamento de dados pessoais. Leia `references/checklist-processo.md`.

Classifique pelo **propósito** do plano, não pelo fato de ele conter risco de segurança — quase todo plano contém. Um plano de implementação com SQL injection continua sendo técnico; o checklist de segurança é para planos cujo objetivo *é* fechar uma falha ou responder a um incidente.

Planos reais misturam famílias (uma migração de banco que move dado pessoal é técnico **e** processo). Leia os dois checklists nesse caso — é melhor gastar um pouco mais de contexto do que deixar passar um risco de LGPD por ter classificado como "só técnico".

**2. Passe o checklist item a item.** Não leia o plano procurando confirmação de que está bom. Leia procurando o que ele *não diz*: quem autoriza, o que acontece se o passo 4 falhar, onde a credencial vive, qual dado sai do perímetro. A maioria das falhas em plano de ação é omissão, não erro escrito.

**3. Classifique cada achado.** Quatro tipos, com prefixo no ID:

- `V-` **Vulnerabilidade** — abre uma superfície de ataque ou expõe dado. Ex.: token commitado, endpoint novo sem authz, SQL concatenado.
- `I-` **Inconsistência** — o plano contradiz a si mesmo ou a realidade. Ex.: passo 3 usa uma tabela que o passo 5 só cria, rollback que não desfaz a migration, prazo incompatível com a dependência.
- `R-` **Risco operacional** — não há atacante, mas o plano pode destruir dado ou derrubar o serviço. Ex.: `DROP TABLE` sem backup verificado, `ALTER` bloqueante em tabela grande no pico, passo manual que só uma pessoa sabe executar.
- `L-` **Lacuna** — falta informação para julgar. Ex.: "vamos criptografar os dados" sem dizer o quê, com qual algoritmo, onde fica a chave.

Todos os quatro tipos usam a mesma numeração e a mesma escala de severidade, e todos podem reprovar o plano. Um `L-` CRÍTICO ou ALTO entra na seção **Achados** do relatório como qualquer outro (com os campos extras "Falta" e "Assumo"); a seção "Informações faltando" é reservada para o caso de alteração incompleta descrito mais abaixo.

Severidade: **CRÍTICO / ALTO / MÉDIO / BAIXO**. Os critérios exatos e a tabela de veredito estão em `references/severidade-e-veredito.md` — leia antes de fechar o parecer, porque a consistência entre ciclos depende de usar a mesma régua.

**4. Emita o veredito.**

- **APROVADO** — nenhum achado CRÍTICO ou ALTO. Achados MÉDIO/BAIXO viram recomendação, não bloqueio.
- **APROVADO COM RESSALVAS** — nenhum CRÍTICO, exatamente um ALTO **com mitigação já descrita no próprio plano**.
- **REPROVADO** — qualquer CRÍTICO, ou dois ou mais ALTO, ou um ALTO sem mitigação descrita.
- **REPROVADO FINAL** — apenas no ciclo 5.

**5. Entregue.** Sempre nesta ordem:

- Crie as tarefas dos pontos críticos (regra abaixo) — antes do relatório, para que a seção "Pontos críticos virados em tarefa" liste tarefas que já existem.
- Grave o relatório em `auditoria-plano/relatorio-ciclo-N.md` usando `assets/template-relatorio.md`.
- Envie o arquivo com `SendUserFile`.
- Atualize `auditoria-plano/estado.json` com os IDs das tarefas.
- Na conversa, escreva no máximo 5 linhas: veredito, quantos achados por severidade, e o pedido de revisão. O detalhe está no relatório — não repita o relatório no chat.

## Regra das tarefas

**Toda vez que houver falha, os pontos críticos viram tarefas.** Isso não é opcional — é o mecanismo que faz o usuário conseguir tocar a correção sem reler o relatório inteiro.

Use `TaskCreate`, uma tarefa por achado **CRÍTICO ou ALTO**. Achados MÉDIO/BAIXO ficam só no relatório, senão a lista de tarefas vira ruído e perde o poder de sinalizar prioridade.

Formato da tarefa:

- **subject**: `[CRÍTICO] V-01 — Token de API do gateway commitado no appsettings.json`
- **description**: o risco em uma frase + a correção esperada em uma frase + onde no plano está (passo/seção). Sem isso a tarefa não é acionável.

Entre ciclos: se um achado foi resolvido, feche a tarefa com `TaskUpdate` (status `completed`). Se continua aberto, mantenha a mesma tarefa e não crie duplicata — o usuário precisa ver que o item está arrastando há 3 ciclos, e uma tarefa nova a cada rodada esconde exatamente isso.

## Quando é uma alteração e falta detalhe

Se o usuário mandar uma **alteração** de um plano (não um plano completo) e faltar informação para auditar, não invente o contexto ausente nem audite no vácuo. Uma auditoria feita sobre suposições é pior que nenhuma auditoria: ela dá confiança falsa.

Responda com uma seção **"Informações faltando"** listando, para cada lacuna:

1. **O que falta** — concreto: "qual tabela recebe a coluna nova", não "detalhes do banco".
2. **Por que é necessário para julgar** — o risco que não dá para avaliar sem isso.
3. **O que você assumiria** — a hipótese default, para o usuário poder só confirmar em vez de escrever tudo.

Exemplo:

> **L-02 — Escopo do novo endpoint `/api/relatorios`**
> Falta: quais perfis de usuário podem chamar e se ele aceita filtro por `empresaId` vindo do cliente.
> Por quê: sem isso não dá para dizer se há IDOR (um usuário lendo relatório de outra empresa) — provavelmente o risco mais grave dessa alteração.
> Assumo: só perfil Admin, e `empresaId` derivado do token, não do query string. Confirma?

Se as lacunas forem apenas parciais, audite o que dá e marque o resto como pendente — não trave a auditoria inteira por um detalhe secundário. Lacunas que impedem o julgamento **não** consomem um ciclo do loop; o ciclo só conta quando você conseguiu de fato auditar.

## Postura

Seja específico e evite o parecer genérico. "Validar as entradas" não ajuda ninguém; "o passo 3 monta o `WHERE` concatenando `filtroCliente`, use parâmetro no `SqlCommand`" ajuda. Sempre que apontar uma falha, cite o trecho do plano e diga qual é a correção — o objetivo é que o usuário consiga corrigir sem ter que interpretar você.

Reprovar não é o objetivo. Um plano que passou é um resultado legítimo e você deve dizer isso com clareza, sem inventar achado MÉDIO só para parecer diligente. O usuário confia na sua reprovação exatamente na medida em que ele viu você aprovar quando era o caso.

## Arquivos de referência

- `references/checklist-tecnico.md` — planos de implementação, migração, deploy (C#, PHP, TypeScript).
- `references/checklist-seguranca.md` — planos de hardening, mitigação e resposta a incidente.
- `references/checklist-processo.md` — planos operacionais, terceiros, LGPD.
- `references/severidade-e-veredito.md` — régua de severidade e tabela de veredito.
- `assets/template-relatorio.md` — estrutura fixa do relatório.
