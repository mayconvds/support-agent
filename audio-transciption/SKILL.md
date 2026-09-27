---
name: audio-transciption
description: "Transcreve arquivos de áudio de conversas (WhatsApp, reuniões, calls) com diarização (separação de vozes) e extrai uma lista de tarefas acionáveis. Use esta skill sempre que o usuário enviar um áudio/vídeo de conversa (.mp4, .mp3, .ogg, .m4a, .wav) e pedir transcrição, 'quem falou o quê', separação de vozes, ata de reunião, resumo de conversa ou extração de tarefas/pendências/combinados a partir de um áudio — mesmo que não use a palavra 'transcrever'. Gera 3 arquivos: transcricao_bruta.md, transcricao_dialogo.md e tarefas.md."
metadata:
  version: "1.0.0"
---

# Transcrição com Diarização + Extração de Tarefas

Skill para processar um arquivo de áudio de uma conversa entre duas (ou mais) pessoas e gerar exatamente 3 arquivos de saída: transcrição bruta com tempos, diálogo limpo e lista de tarefas acionáveis.

## Fluxo de trabalho

### Etapa 0 — Preparação

1. Localize o arquivo de áudio em `/mnt/user-data/uploads/`. Se não houver arquivo, informe o usuário e pare — nunca invente uma transcrição.
2. Gere um breve **resumo do objetivo** do processamento antes de começar (1–3 frases: o que será feito e quais arquivos serão gerados).
3. Verifique as ferramentas disponíveis no ambiente:
   - `ffmpeg` / `ffprobe` para inspecionar e converter o áudio (ex: extrair áudio de .mp4 para .wav 16kHz mono).
   - Um modelo de transcrição local (ex: `openai-whisper` ou `faster-whisper` via pip). Instale com `pip install faster-whisper --break-system-packages` se necessário.
   - Se nenhuma ferramenta de transcrição puder ser instalada/executada no ambiente, informe o usuário claramente da limitação em vez de simular resultados.

### Etapa 1 — Transcrição

- Transcreva **todo** o áudio fielmente:
  - Sem resumir.
  - Sem corrigir gírias, erros gramaticais ou vícios de linguagem.
  - Sem inventar trechos.
- Trechos incompreensíveis: marque como `[inaudível]` em vez de adivinhar.
- Capture marcações de tempo por fala/segmento no formato `[MM:SS]` (ou `[HH:MM:SS]` para áudios longos).
- Idioma da saída: o mesmo do áudio.

### Etapa 2 — Diarização (identificação das vozes)

- Separe quem falou o quê.
- Rótulos consistentes do início ao fim: `Voz 1`, `Voz 2`, ... — a **primeira pessoa a falar é a Voz 1**.
- Se conseguir inferir nome ou papel pelo contexto, adicione entre parênteses: `Voz 1 (cliente)`, `Voz 2 (João)`.
- Em caso de dúvida sobre quem falou, use `Voz indefinida` — nunca atribua no chute.
- Dica técnica: se disponível, use diarização automática (ex: `pyannote.audio`); caso contrário, faça diarização por contexto (alternância de turnos, conteúdo, tratamento entre interlocutores), sinalizando incertezas com `Voz indefinida`.

## Arquivos de saída (gerar os 3, em `/mnt/user-data/outputs/`)

### 1) `transcricao_bruta.md`

Transcrição corrida, fiel, com marcação de tempo a cada fala quando possível:

```
[00:00] Voz 1: ...
[00:14] Voz 2: ...
```

### 2) `transcricao_dialogo.md`

A mesma conversa, limpa e legível (remover hesitações excessivas tipo "ééé", repetições truncadas), organizada como diálogo, sem tempos:

```
Voz 1: falou isso
Voz 2: falou aquilo
```

O conteúdo semântico deve ser idêntico ao da transcrição bruta — a limpeza é apenas de legibilidade, não de conteúdo.

### 3) `tarefas.md`

Lista de tarefas acionáveis em markdown. Regras:

- Cada item começa com `- [ ] ` (checkbox).
- Extraia **apenas** o que foi acordado, pedido ou prometido na conversa — não invente.
- Quando houver responsável: `(Resp: Voz 1)` ou `(Resp: nome)`.
- Quando houver prazo mencionado: `(Prazo: ...)`.
- Agrupe sob cabeçalhos `## ` se fizer sentido (por tema ou por pessoa).
- No final, seção `## Pendências / Dúvidas` com pontos que ficaram em aberto ou ambíguos.

## Regras gerais

- Não resuma além do necessário na transcrição.
- Não atribua falas a uma voz em caso de dúvida — use `Voz indefinida`.
- Idioma da saída: o mesmo do áudio.
- Ao final, apresente os 3 arquivos ao usuário e mostre o resumo do objetivo + um panorama curto do que foi encontrado (nº de vozes, duração, nº de tarefas extraídas).