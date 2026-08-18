# Checklist — Plano operacional, de processo e de negócio

Use para planos que mudam como as pessoas trabalham: novo fluxo de atendimento, contratação de fornecedor, mudança de política de acesso, campanha que coleta dados, terceirização, onboarding/offboarding.

O risco aqui raramente é código. É pessoa com acesso demais, dado saindo pela porta lateral, e processo sem dono.

## Índice

1. Dados pessoais e LGPD
2. Acessos e segregação de funções
3. Terceiros e fornecedores
4. Continuidade e dependências
5. Governança, dono e evidência
6. Consistência interna

---

## 1. Dados pessoais e LGPD

- Que dados pessoais o processo coleta, e todos são realmente necessários? Coletar "porque pode ser útil depois" viola minimização e aumenta o dano de qualquer vazamento.
- Qual a base legal (consentimento, execução de contrato, legítimo interesse, obrigação legal)? Plano que coleta sem base legal declarada é ALTO.
- Se é consentimento: como é coletado, registrado e revogado? Consentimento sem registro é o mesmo que não ter.
- Há dado sensível (saúde, biometria, origem racial, opinião política, dado de criança/adolescente)? O regime é mais estrito — trate qualquer lacuna aqui como no mínimo ALTO.
- Onde o dado é armazenado, por quanto tempo, e quem apaga quando o prazo vence?
- O titular consegue exercer os direitos dele (acesso, correção, exclusão, portabilidade) nesse novo fluxo, e alguém está designado para responder?
- Há transferência internacional (ferramenta SaaS fora do Brasil)? Precisa estar declarada.
- Planilha, WhatsApp, e-mail e Drive pessoal aparecem como meio de tratar dado? É o vazamento mais comum de processo — e quase sempre está implícito, não escrito.

## 2. Acessos e segregação de funções

- Quem ganha acesso a quê, e é o mínimo necessário? Acesso concedido "para agilizar" é permanente na prática.
- Acesso é nominal ou compartilhado? Login compartilhado destrói rastreabilidade — sem ele não existe responsabilização.
- Quem aprova o acesso é diferente de quem recebe?
- Há segregação entre quem cadastra e quem aprova (pagamento, cadastro de fornecedor, alteração de dado bancário, concessão de desconto)? Sem segregação, uma pessoa sozinha completa uma fraude.
- Offboarding: o plano diz como o acesso é removido quando a pessoa sai ou muda de função, e em quanto tempo?
- Revisão periódica de acessos prevista?
- Acesso temporário tem prazo de expiração automático, ou depende de alguém lembrar?

## 3. Terceiros e fornecedores

- O terceiro trata dado pessoal ou acessa sistema interno? Se sim, há contrato com cláusula de proteção de dados e de notificação de incidente?
- Que nível de acesso o terceiro recebe, e é revogável rapidamente?
- Houve alguma avaliação mínima de segurança do fornecedor?
- Subcontratação: o fornecedor pode repassar o dado para outro?
- O que acontece com os dados no fim do contrato — devolução, exclusão, comprovante?
- Dependência de fornecedor único para um passo crítico é risco de continuidade.

## 4. Continuidade e dependências

- O que acontece se o passo crítico falhar ou atrasar? Há plano B?
- O processo depende de uma pessoa específica? Ponto único de falha humano precisa de backup e documentação.
- Dependência externa (órgão público, banco, integração) com prazo fora do seu controle está no caminho crítico?
- Volume/capacidade: o processo aguenta o pico esperado, ou foi dimensionado pela média?
- Há processo manual de contingência se o sistema cair?

## 5. Governança, dono e evidência

- Cada passo tem responsável nomeado (papel, não "a equipe")?
- Quem aprova o plano e quem decide em caso de exceção?
- Como se comprova depois que o processo foi seguido? Registro, log, ata, checklist assinado.
- Há treinamento/comunicação para quem vai executar? Processo novo sem comunicação é executado do jeito antigo.
- Indicador de acompanhamento definido, com alguém olhando e uma frequência?
- Data de revisão do processo?

## 6. Consistência interna

- Os passos estão em ordem executável, sem depender de algo que só existe depois?
- Prazos são compatíveis entre si e com as dependências externas?
- Papéis mencionados existem na organização e têm a autoridade que o plano supõe?
- O plano contradiz política interna, contrato ou norma vigente?
- Critério de sucesso é mensurável?
- Custo/esforço declarado bate com o escopo?
- O que está fora do escopo está dito?
