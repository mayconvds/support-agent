# Template do relatório

Use esta estrutura em `auditoria-plano/relatorio-ciclo-N.md`. Seções sem conteúdo são omitidas — não deixe cabeçalho vazio.

---

# Auditoria de Plano de Ação — [Nome do plano]

**Ciclo:** N de 5
**Tipo:** técnico + processo *(combine com "+" quando o plano cruzar famílias)*
**Data:** AAAA-MM-DD
**Veredito:** APROVADO | APROVADO COM RESSALVAS | REPROVADO | REPROVADO FINAL

## Resumo

Duas ou três frases: o que o plano faz, qual o risco dominante, e o que precisa acontecer agora.

| Severidade | Qtd |
|---|---|
| CRÍTICO | 0 |
| ALTO | 0 |
| MÉDIO | 0 |
| BAIXO | 0 |

*(V = vulnerabilidade, I = inconsistência, R = risco operacional, L = lacuna)*

## Evolução entre ciclos

*(a partir do ciclo 2)*

| ID | Achado | Ciclo 1 | Ciclo 2 | Ciclo N | Situação |
|---|---|---|---|---|---|
| V-01 | Token no appsettings | CRÍTICO | CRÍTICO | ALTO | Aberto há 3 ciclos |
| I-02 | Migration sem rollback | ALTO | — | — | Resolvido no ciclo 2 |

Comente em uma linha o que melhorou e o que continua parado.

## Achados

Um bloco por achado **CRÍTICO ou ALTO**, ordenados por severidade decrescente. MÉDIO e BAIXO vão para "Recomendações", em uma linha cada — o relatório perde utilidade se o leitor tiver que atravessar 15 blocos para achar o que bloqueia.

Quando houver mais de 5 blocos, abra a seção com uma linha de ordem de correção: `Corrija nesta ordem: V-03 (bloqueia o deploy) → V-01 → R-05 → ...`.

### [SEVERIDADE] V-01 — Título curto e específico

**Onde:** passo/seção do plano, citando o trecho.
**Risco:** o que acontece de concreto se o plano for executado assim — quem consegue fazer o quê.
**Por quê:** o mecanismo da falha, em uma ou duas frases.
**Correção esperada:** a mudança concreta no plano. Se for técnico, mostre o código ou o comando em C#, PHP ou TypeScript conforme o stack do plano.
**Esforço:** baixo / médio / alto — ajuda o usuário a sequenciar a correção.
**Como verificar:** o teste que prova que fechou.

Para achado `L-` de severidade CRÍTICO/ALTO, acrescente ao bloco:
**Falta:** o dado ausente. **Assumo:** a hipótese default que você usou para atribuir a severidade.

## Informações faltando

*(apenas quando o plano é uma alteração incompleta e a falta de contexto impede a auditoria — lacunas pontuais dentro de um plano completo viram achados `L-` na seção acima)*

### L-0N — [O que falta]

**Falta:** descrição concreta do dado ausente.
**Por que é necessário:** o risco que não dá para avaliar sem isso.
**Assumo:** a hipótese default, para o usuário só confirmar.

## Recomendações (MÉDIO e BAIXO)

Lista enxuta, uma linha por item. Não bloqueiam a aprovação.

## Pontos críticos virados em tarefa

Lista dos IDs CRÍTICO/ALTO que foram criados como tarefa, para o usuário conferir o rastro.

## Próximo passo

- **Reprovado (ciclos 1–4):** "Corrija os itens acima e me envie o plano atualizado — vou reauditar como ciclo N+1."
- **Reprovado final (ciclo 5):** seção **Plano corrigido proposto**, escrita por você, com passos executáveis, o que foi assumido e o que ainda depende de decisão do usuário.
- **Aprovado:** o que monitorar durante a execução e qual o sinal para abortar.
