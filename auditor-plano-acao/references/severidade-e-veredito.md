# Régua de severidade e tabela de veredito

A consistência entre ciclos depende de usar a mesma régua. Se um achado era ALTO no ciclo 1, ele não vira MÉDIO no ciclo 3 porque o usuário argumentou — só muda se o plano mudou.

## Tipos de achado

| Prefixo | Tipo | Definição |
|---|---|---|
| `V-` | Vulnerabilidade | O plano abre ou mantém uma superfície de ataque, ou expõe dado. |
| `I-` | Inconsistência | O plano contradiz a si mesmo, a realidade técnica, ou a ordem de execução não funciona. |
| `R-` | Risco operacional | Sem atacante envolvido: perda de dado, indisponibilidade, operação destrutiva irreversível, ponto único de falha humano. |
| `L-` | Lacuna | Falta informação para julgar. Não é afirmação de que está errado — é impossibilidade de dizer que está certo. |

Numere sequencialmente por tipo (`V-01`, `V-02`, `I-01`, `R-01`) e **mantenha o número entre ciclos**. Achado novo no ciclo 3 continua a numeração; não renumere os antigos. MÉDIO e BAIXO usam os mesmos prefixos — a severidade decide onde o achado aparece no relatório (bloco completo em "Achados" para CRÍTICO/ALTO, uma linha em "Recomendações" para MÉDIO/BAIXO), mas todos entram no `estado.json`.

## Severidade

**CRÍTICO** — explorável ou destrutivo por si só, com dano relevante e sem barreira adicional. Exemplos:

- Credencial válida exposta em texto claro ou em arquivo versionado.
- Endpoint que expõe dado pessoal sem qualquer autenticação.
- SQL injection alcançável por input de usuário não autenticado.
- Operação destrutiva em produção (`DROP`, `DELETE` sem `WHERE`, sobrescrita) sem backup verificado — isso é `R-`, não `V-`.
- Cópia de base de produção com dado pessoal para outro ambiente sem anonimização declarada.
- Restauração de backup posterior ao início do incidente (reinfecção garantida).

**ALTO** — vulnerabilidade real que exige uma condição a mais (estar autenticado, acertar um id, ganhar uma corrida), ou inconsistência que quebra a execução em produção. Exemplos:

- IDOR: usuário autenticado acessa recurso de outro.
- Segredo sem plano de rotação, ou mesma chave em dev e produção.
- Migration sem rollback real, ou passo que depende de objeto criado depois.
- Dado pessoal indo para log ou para terceiro sem base legal declarada.
- Login compartilhado, ou ausência de segregação de funções em fluxo financeiro.
- Correção que trata sintoma sem fechar a causa raiz do incidente.
- Ausência total de critério de rollback em plano que toca produção.

**MÉDIO** — aumenta risco ou dificulta a operação, mas não é explorável direto e tem mitigação razoável no ambiente. Exemplos:

- Falta de rate limit em endpoint autenticado.
- Log sem informação suficiente para investigar depois.
- Dependência nova sem verificação de vulnerabilidade conhecida.
- Prazo apertado sem folga para a dependência externa.
- Critério de sucesso vago.

**BAIXO** — melhoria de robustez, clareza ou manutenção. Não bloqueia nada.

### Como decidir quando está entre dois níveis

Pergunte: **o que um atacante (ou um erro operacional) consegue fazer hoje, com o que o plano deixa aberto?** Se a resposta é "nada até conseguir outra coisa antes", é um nível abaixo. Se é "acessa/apaga/expõe direto", é CRÍTICO.

Uma lacuna (`L-`) recebe a severidade do **pior cenário plausível** que ela esconde — porque a função da lacuna é justamente impedir que você descarte esse cenário. "Vamos criptografar os dados" sem dizer onde fica a chave é ALTO, não BAIXO: a chave pode estar ao lado do dado.

## Tabela de veredito

| Achados | Veredito |
|---|---|
| Nenhum CRÍTICO e nenhum ALTO | **APROVADO** |
| Nenhum CRÍTICO, exatamente 1 ALTO **com mitigação já descrita no próprio plano** | **APROVADO COM RESSALVAS** |
| Qualquer CRÍTICO, ou 2+ ALTO, ou 1 ALTO sem mitigação | **REPROVADO** |
| Ciclo 5 e ainda há CRÍTICO ou ALTO | **REPROVADO FINAL** — pare de pedir revisão e proponha a solução |

Achados MÉDIO e BAIXO nunca reprovam sozinhos. Eles entram no relatório como recomendação. Isso é proposital: se tudo bloqueia, nada bloqueia, e o usuário perde a capacidade de priorizar.

## No REPROVADO FINAL (ciclo 5)

O usuário já tentou 5 vezes. Continuar pedindo revisão não é útil — a sua função agora é entregar a solução:

1. **O que falhou** — cada achado ainda aberto, quantos ciclos ele arrastou, e por que as tentativas de correção não fecharam. Se o padrão for "o usuário corrige o sintoma e não a raiz", diga isso com clareza; é a informação mais valiosa do relatório.
2. **Plano corrigido proposto** — escrito por você, passo a passo executável, resolvendo cada ponto aberto. Não é um resumo dos achados; é um plano que o usuário pode executar.
3. **O que você assumiu** — as decisões que você tomou no lugar dele, para ele revisar. Onde faltava informação, escolha o default mais seguro e diga qual foi.
4. **O que ainda depende de decisão dele** — trade-offs que não são seus para decidir (custo, prazo, apetite a risco).
