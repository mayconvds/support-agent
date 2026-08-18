# Checklist — Plano de segurança, mitigação e resposta a incidente

Use para planos de hardening, correção de vulnerabilidade, rotação de credenciais e resposta a incidente. A diferença para o checklist técnico é o foco: aqui o risco principal não é "o plano introduz falha", é "o plano acha que fechou a falha e não fechou".

## Índice

1. Diagnóstico e escopo
2. Contenção e erradicação
3. Ordem de execução
4. Credenciais e acessos
5. Evidências e forense
6. Rollback e efeito colateral
7. Verificação e encerramento
8. Comunicação e obrigações legais

---

## 1. Diagnóstico e escopo

- A causa raiz está identificada, ou o plano trata sintoma? Fechar o sintoma sem a causa é o padrão mais comum de reincidência — trate como ALTO.
- O escopo do comprometimento foi determinado, ou assumido? "Só o servidor X foi afetado" sem evidência é hipótese, não escopo.
- O plano considera que o atacante pode ter movido lateralmente ou deixado persistência (webshell, chave SSH adicionada, cron, conta de serviço nova, regra de encaminhamento de e-mail)?
- Existe a mesma vulnerabilidade em outros sistemas/repositórios? Plano que corrige uma instância de um padrão presente em cinco lugares fecha 20% do risco.
- Data de início do incidente estimada com base em quê? Sem isso não dá para saber qual backup ainda é confiável.

## 2. Contenção e erradicação

- Distingue contenção (parar o sangramento) de erradicação (remover o acesso do atacante) e de recuperação? Plano que mistura as três tende a restaurar o sistema com o backdoor junto.
- A contenção destrói evidência necessária depois? Desligar a máquina apaga memória volátil; snapshot antes.
- Restauração de backup: o backup é anterior ao comprometimento e foi testado? Restaurar backup infectado reabre o incidente.
- O plano fecha o vetor original, ou só limpa o resultado? Se a entrada foi credencial vazada e a credencial não foi rotacionada, a limpeza é temporária.
- Mitigação temporária (WAF, bloqueio de IP, feature desligada) tem data e dono para a correção definitiva? Sem isso vira dívida permanente.

## 3. Ordem de execução

- A ordem está correta? Trocar senha antes de expulsar o atacante da sessão ativa não adianta — sessões existentes seguem válidas.
- Rotação de credenciais acontece depois de fechar o vetor, senão a credencial nova vaza pelo mesmo caminho.
- Passos que dependem de terceiro (provedor, fornecedor, cliente) estão no caminho crítico? Se sim, qual o prazo de resposta deles?
- Há passo que exige janela de manutenção e o plano não reservou?
- Cada passo tem um dono nomeado e um pré-requisito claro?

## 4. Credenciais e acessos

- Todas as credenciais potencialmente expostas estão na lista: senhas de usuário, tokens de API, chaves SSH, certificados, secrets de CI/CD, credenciais de banco, webhooks, contas de serviço, tokens OAuth de terceiros?
- Sessões ativas são invalidadas explicitamente (revogação de refresh token, bump de `SecurityStamp`, invalidação de sessão server-side)? Trocar senha sozinho raramente derruba sessão.
- MFA foi resetado onde faz sentido, e os dispositivos confiáveis foram limpos?
- Contas criadas ou elevadas durante o período do incidente foram revisadas?
- Chaves de recuperação/backup codes também rotacionadas?
- Acesso de terceiros e integrações revisados? Integração esquecida é o caminho de volta mais comum.

## 5. Evidências e forense

- Logs relevantes foram preservados antes de qualquer limpeza, e em local que o atacante não alcança?
- Retenção de log cobre o período do incidente? Se o log gira em 7 dias e o incidente começou há 30, o plano precisa admitir esse limite em vez de afirmar escopo que não pode provar.
- Há cadeia de custódia se houver chance de uso legal?
- O plano registra linha do tempo com horários e fuso? Ambiguidade de fuso arruína correlação de log.

## 6. Rollback e efeito colateral

- Cada medida de hardening pode quebrar uso legítimo? Bloquear IP, apertar CORS, forçar MFA, revogar token de integração — tudo isso derruba alguém. O plano diz quem?
- Existe rollback para cada medida, e ele é seguro (desfazer não reabre a brecha)?
- Mudança em produção durante incidente aumenta risco de indisponibilidade — o plano pesou isso?
- Comunicação prévia para quem será afetado?

## 7. Verificação e encerramento

- Como se **prova** que a falha foi fechada? Reteste, varredura, PoC que antes funcionava e agora falha. "Aplicamos o patch" não é verificação.
- Quem verifica é diferente de quem executou?
- Monitoramento novo para detectar reincidência, com alerta configurado para alguém que realmente recebe?
- Critério objetivo de encerramento do incidente?
- Post-mortem previsto, com ação corretiva de causa raiz e prazo?

## 8. Comunicação e obrigações legais

- Houve acesso a dado pessoal? Se sim, o plano prevê avaliação de notificação à ANPD e aos titulares (LGPD art. 48) em prazo razoável?
- Cliente/parceiro afetado por contrato com cláusula de notificação?
- Quem fala com imprensa/clientes, e o comunicado passa por jurídico?
- Comunicação interna definida — e por canal que não dependa do sistema comprometido? Coordenar incidente pelo e-mail invadido é falha real.
- Comunicação prematura com informação errada é risco também: o plano diz o que é fato confirmado e o que ainda é hipótese?
