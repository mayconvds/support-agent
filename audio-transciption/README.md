# Transcrição com Diarização + Extração de Tarefas

**Name:** `audio-transciption`
**Version:** `1.0.0`
**Description:** Transcreve arquivos de áudio de conversas (WhatsApp, reuniões, calls) com diarização (separação de vozes) e extrai uma lista de tarefas acionáveis, gerando 3 arquivos markdown prontos para uso.

---

## O que esta skill faz

Recebe um arquivo de áudio/vídeo de uma conversa entre duas ou mais pessoas e produz:

| Arquivo | Conteúdo |
|---|---|
| `transcricao_bruta.md` | Transcrição fiel e completa, com marcação de tempo por fala (`[00:14] Voz 2: ...`) |
| `transcricao_dialogo.md` | A mesma conversa, limpa e legível, organizada como diálogo (`Voz 1: ... / Voz 2: ...`) |
| `tarefas.md` | Lista de tarefas acionáveis com checkboxes, responsáveis, prazos e seção de pendências |

## Como usar

1. Envie o arquivo de áudio na conversa (formatos aceitos: `.mp4`, `.mp3`, `.ogg`, `.m4a`, `.wav`).
2. Peça algo como:
   - "Transcreva este áudio e separe as vozes"
   - "Extraia as tarefas dessa conversa de WhatsApp"
   - "Gere a ata dessa call com quem falou o quê"
3. A skill executa as etapas na ordem e entrega os 3 arquivos.

## Etapas do processamento

1. **Resumo do objetivo** — antes de começar, é gerado um resumo curto do que será feito.
2. **Transcrição** — fiel, sem resumir, sem corrigir gírias, sem inventar trechos. Trechos incompreensíveis são marcados como `[inaudível]`.
3. **Diarização** — separação de vozes com rótulos consistentes (`Voz 1`, `Voz 2`, ...). A primeira pessoa a falar é sempre a `Voz 1`. Nome ou papel inferido pelo contexto aparece entre parênteses: `Voz 1 (cliente)`. Falas incertas são marcadas como `Voz indefinida`.
4. **Extração de tarefas** — apenas o que foi acordado, pedido ou prometido, no formato:

```markdown
## Site do cliente
- [ ] Enviar o orçamento revisado (Resp: Voz 2) (Prazo: sexta-feira)
- [ ] Aprovar o layout da home (Resp: Voz 1 (cliente))

## Pendências / Dúvidas
- Não ficou definido quem paga a hospedagem no primeiro ano.
```

## Regras e garantias

- **Fidelidade:** nada é resumido nem inventado na transcrição.
- **Idioma:** a saída é sempre no mesmo idioma do áudio.
- **Honestidade sobre limitações:** se o ambiente não tiver ferramentas de transcrição disponíveis, a skill informa em vez de simular resultados.

## Dependências (ambiente de execução)

- `ffmpeg` / `ffprobe` — inspeção e conversão do áudio.
- `faster-whisper` (ou `openai-whisper`) — transcrição local, instalável via `pip`.
- Opcional: `pyannote.audio` para diarização automática; na ausência, a diarização é feita por contexto.

## Changelog

- **1.0.0** — Versão inicial: transcrição + diarização de 2 vozes + extração de tarefas, com 3 arquivos de saída.