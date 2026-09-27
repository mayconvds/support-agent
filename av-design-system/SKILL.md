---
name: av-design-system
version: 3.0.0
description: "Cria um Design System visual completo para um projeto ou espelha um site como template. Usar quando o usuário digitar 'criar design system', 'design system' ou invocar /av-design-system."
---

# AV Design System

> **Versionamento (obrigatório):** sempre que esta skill for editada (SKILL.md, `build.py`, `mirror.js`, `template.html` ou README), **incremente o campo `version`** na frontmatter acima seguindo SemVer (`MAJOR.MINOR.PATCH`): PATCH para correções, MINOR para novos recursos compatíveis, MAJOR para mudanças que quebram compatibilidade. Regenere o ZIP de distribuição após o bump.

Skill profissional para **(A) criar** um Design System visual completo a partir dos logos/cores de um projeto, ou **(B) baixar** um site de referência como template local autossuficiente.

Todo HTML é gerado pelo motor `build.py`, **nunca leia nem escreva HTML manualmente.** `build.py`, `mirror.js` e `template.html` ficam na Base directory desta skill (no cabeçalho). Use esse caminho como `$SKILL_DIR`.

### Novidades v2.0 (Fluxo A)

O design system gerado agora é **premium, responsivo e 100% standalone**:

- **Menu no topo** (nav fixo) com scrollspy, underline de seção ativa e dropdown no mobile (< 900px).
- **Totalmente responsivo:** o card de identidade do hero aparece em **todas** as larguras (lado a lado a partir de **960px**, empilhado e centralizado abaixo disso). Sem overflow horizontal de 360px a wide.
- **Acessibilidade (WCAG AA):** contraste de texto/labels ≥ 4.5:1 nos dois temas, **foco de teclado visível**, respeito a `prefers-reduced-motion`, alvos de toque ≥ 44px no mobile, `<h1>` semântico e labels de formulário associados. (Auditado via `/impeccable audit`.)
- **Tema claro + escuro no mesmo arquivo**, com **botão de switch** no nav (persiste em `localStorage`). O `--theme` só define qual tema abre por padrão; o usuário alterna ao vivo.
- **Leve por padrão (~100 KB):** o HTML usa as imagens reais em `./images/` e ícones em **SVG inline**. Feito para viver em um **repositório Git**, que é a melhor forma de servir o design system para outras IAs (Claude chat, cowork, Projetos).
- **Arquivo único quando precisar (`--embed`):** embute imagens em **base64 WebP** (redimensionadas, ~60% mais leves que PNG) e a **fonte** como `@font-face` base64. Gera ~1 MB e renderiza sozinho, sem a pasta `images/` e sem rede. Use para enviar o `.html` avulso por chat ou e-mail.
  - O embed da fonte é **best-effort**: precisa de rede no `build` para baixar os `.woff2`. Sem rede, o build **não quebra**, mantém o `<link>` do Google Fonts. Use `--no-embed-font` para forçar o `<link>` remoto.
- **Logo por tema (automático):** o `build.py` embute a versão **clara** (para o dark) e a **escura** (para o light) de cada logo e alterna via CSS conforme o tema. Por isso é importante fornecer **as duas versões** de cada logo (ex.: `*-white.png` e `*-black.png`). A escolha por tema é automática, sem argumento extra.

### Servindo o design system para outras IAs (Git)

O objetivo principal deste projeto é **alimentar outras IAs** (Claude chat, cowork, Projetos) com a identidade e os padrões da marca. A melhor forma é **versionar a pasta em um repositório Git** e conectar esse repo ao Projeto. Assim tudo fica leve, versionado e atualiza sozinho.

Estrutura que o repo deve ter:

```
templates/av-design-system/
  av-design-system-spec.md   ← o que a IA lê (tokens e regras, ~4 KB)
  av-design-system.html      ← o que humanos veem (~100 KB)
  images/                    ← logos reais (PNG)
```

**O `-spec.md` continua sendo a peça central**, e num repo Git fica ainda mais importante: a IA lê texto, então um Markdown denso de 4 KB é infinitamente mais útil (e mais barato em contexto) do que 100 KB de HTML cheio de estilo inline. O HTML fica como referência visual humana; o `images/` fornece os arquivos reais para uso.

| Finalidade | Comando | Saída |
|---|---|---|
| **Repo Git / base para IA** | (padrão) `--spec` | `~100 KB` HTML + **`~4 KB` spec.md** + `images/` |
| Enviar o HTML avulso (chat, e-mail) | `--embed` | `~1 MB` · arquivo único autossuficiente |

Ajuste fino das imagens no modo `--embed`: `--img-max` (lado máximo em px, padrão 512; `0` mantém o PNG original) e `--img-quality` (padrão 86).

## Mapa de comandos (`build.py`)

Toda a lógica vive em 5 subcomandos. Saída sempre começa com `OK:` (ou `RENAMED:`/`CORES SUGERIDAS:`) em sucesso; erros vão para stderr.

| Comando | Função | Argumentos | Retorna |
|---------|--------|------------|---------|
| `rename`  | Padroniza logos para `{prefix}-*.png` | `--images-dir --prefix` | mapa `RENAMED:` + lista `FINAL:` |
| `suggest` | Extrai paleta dos logos + sugere fontes; sobe preview de cores | `--images-dir` | `CORES SUGERIDAS:` + `PREVIEW_URL:`/`SERVER_PID:` |
| `build`   | Gera o `av-design-system.html` final (tema claro/escuro) | `--name --primary --accent --deep --deep-hover --bg --font --url --version --main-logo --icon-logo --favicon --theme --out-suffix --embed --no-embed-font --spec --img-max --img-quality --output-dir` | `OK:<arquivo>` (+ `SPEC:` com `--spec`) |
| `mirror`  | Captura um site (até SPA) como `{slug}.html` + `assets/` locais | `--url --slug --output-dir` | `OK:<arquivo>` + `ASSETS:` + `SIZE:` |
| `serve`   | Sobe um servidor HTTP local e imprime a URL | `--dir --file` | `SERVER_PID:` + `SERVE_URL:` |

**Requisitos:** Python 3 (sempre). O `mirror` usa Playwright/Chromium, instalado automaticamente em `/tmp` na primeira execução (pode levar ~1 min só na 1ª vez).

**Performance esperada:** `build` ~3 a 5s (baixa e embute os `.woff2` da fonte; ~1s com `--no-embed-font`) · `mirror` ~5 a 20s conforme o nº de assets do site.

---

## ESTRUTURA DE PASTAS

```
$ROOT/                        ← pwd do projeto do usuário
  templates/
    av-design-system/         ← Fluxo A: design system
      images/
      av-design-system.html
    {slug}/                   ← Fluxo B: site espelhado
      {slug}.html
```

- `$ROOT` = resultado de `pwd`
- Pasta sempre **`templates`** (plural), sempre na raiz
- O arquivo HTML sempre tem o **mesmo nome da pasta** (ex: pasta `{slug}` → `{slug}.html`)
- **Nunca** crie dentro de `exemplo/`, `src/` ou qualquer subpasta

---

## PASSO 0 · Escolha do modo

Pergunte com `AskUserQuestion`:
- **Criar um novo Design System**
- **Baixar um template de referência**

---

## FLUXO A · Criar novo Design System

### A1. Criar pastas

```bash
ROOT=$(pwd)
mkdir -p "$ROOT/templates/av-design-system/images"
```

### A2. Nome do projeto

Pergunte o nome do projeto.

### A3. Logos

Exiba o link clicável com o caminho absoluto real:

> "Copie os logos para:
> **[📁 Abrir pasta images]($ROOT/templates/av-design-system/images)**
>
> Arquivos esperados (PNG, fundo transparente):
> - Logo fundo escuro (versão branca/clara)
> - Logo fundo claro (versão preta/escura)
> - Logo cor primária ou degradê
> - Ícone quadrado (favicon, avatar)
> - Wordmark horizontal (opcional)
> - Outros que quiser
>
> Me avise quando terminar."

**Aguarde o aviso antes de continuar.**

### A4. Renomear logos

Derive o prefixo pegando a **primeira letra de cada palavra** do nome do projeto (lowercase):
- "Velocce Auto Sales" → `vas`
- "Agência de Valor" → `adv`
- "Sistema de Demanda" → `sdd`
- "Beyow" → `b`
- "Inter" → `i`

Use o Bash para derivar automaticamente:
```bash
PREFIX=$(echo "NOME DO PROJETO" | awk '{for(i=1;i<=NF;i++) printf tolower(substr($i,1,1))}')
```

Execute o rename com o prefixo correto:

```bash
python3 "$SKILL_DIR/build.py" rename \
  --images-dir "$ROOT/templates/av-design-system/images" \
  --prefix "{acronimo}"
```

Mostre o mapeamento `original → novo` e a lista FINAL ao usuário.

Em seguida, pergunte os 3 slots de logo. Liste os arquivos do FINAL e pergunte em texto:

> "Preciso definir 3 usos de logo:
>
> ```
> [arquivos disponíveis listados aqui]
> ```
>
> 1. **Logo principal**: aparece no hero, acima do badge DESIGN SYSTEM (ex: logo completo com nome)
> 2. **Logo ícone**: nav header + color palette card (ex: ícone ou badge quadrado)
> 3. **Favicon**: aba do browser (ex: ícone mínimo ou favicon dedicado)
>
> Qual arquivo para cada um?"

Guarde como `$MAIN_LOGO`, `$ICON_LOGO` e `$FAVICON`.

### A5. Sugerir fontes e cores

**Passo 1 · Extrair cores com o script:**

```bash
python3 "$SKILL_DIR/build.py" suggest \
  --images-dir "$ROOT/templates/av-design-system/images"
```

Guarde os valores de CORES SUGERIDAS para usar no A6.

**Passo 2 · Analisar visualmente a logo para sugerir fontes:**

Liste os arquivos em `images/` e escolha o melhor para análise visual, prefira `av-logo-*.png` com fundo escuro ou a versão com cor primária. Leia a imagem com o `Read` tool.

Ao analisar, observe:
- **Traço**: geométrico e preciso / orgânico e humanista / condensado / expandido
- **Peso**: bold e impactante / light e elegante / equilibrado
- **Estilo**: moderno e tech / clássico e institucional / amigável e arredondado / editorial
- **Serifa**: sem serifa (sans) / com serifa / mista

Com base nesses atributos, escolha **2 combinações de fontes do Google Fonts** que reflitam o mesmo DNA visual da logo. Exemplos de pares:
- Geométrico + bold → `Figtree + Inter`, `Outfit + DM Sans`
- Humanista + elegante → `Plus Jakarta Sans + Manrope`, `DM Sans + Nunito`
- Institucional + forte → `Montserrat + Inter`, `Raleway + Manrope`
- Tech + preciso → `Inter + Inter`, `Manrope + Manrope`

**Passo 3 · Apresentar com `AskUserQuestion`:**

Monte as 2 opções com as fontes que você escolheu na análise visual:
- Opção 1: `"[Fonte1] + [Fonte2]"`, descrição: "[Fonte1] para títulos, [Fonte2] para corpo"
- Opção 2: `"[Fonte1] para tudo"`, descrição: "Mesma fonte para tudo, consistente e clean"

Pergunta: **"Escolha uma combinação de fontes, ou informe as suas:"**
(o "Other" aparece automaticamente para quem quiser digitar outra fonte)

Se o usuário escolher "Other", pergunte em texto:
> "Informe a fonte primária (títulos) e a secundária (corpo), ou só uma se quiser usar a mesma para tudo."

**Passo 4 · Confirmar cores:**

O script imprime três linhas, capture cada valor:
- `PREVIEW:/caminho` → `$PREVIEW_PATH`
- `SERVER_PID:12345` → `$SERVER_PID`
- `PREVIEW_URL:http://localhost:PORT/.color-preview.html` → `$PREVIEW_URL`

Apresente as cores com hex values e o link localhost clicável:

> "Com base nos logos, sugiro esta paleta:
> - Primary: `#XXXXXX`
> - Accent: `#XXXXXX`
> - Deep: `#XXXXXX`
> - Deep Hover: `#XXXXXX`
> - Background: `#000000`
>
> [🎨 Visualizar cores]($PREVIEW_URL)
>
> Confirma esta paleta ou quer ajustar alguma cor?"

Aguarde a resposta:

- **Se pedir ajuste de cor**: atualize apenas os valores no HTML já gerado (reescreva só o arquivo `$PREVIEW_PATH`) e diga: > "Atualizei, recarregue a página (Cmd+R)." O servidor continua rodando. Repita até confirmar.
- **Ao confirmar**: encerre o servidor e delete o arquivo:
```bash
kill $SERVER_PID 2>/dev/null; rm -f "$PREVIEW_PATH"
```

**Só avance para A6 após encerrar o servidor e deletar o preview.**

### A6. Gerar

Com nome, fontes e cores confirmados, execute:

```bash
python3 "$SKILL_DIR/build.py" build \
  --name        "NOME DO PROJETO" \
  --primary     "#HEXCOLOR" \
  --accent      "#HEXCOLOR" \
  --deep        "#HEXCOLOR" \
  --deep-hover  "#HEXCOLOR" \
  --bg          "#000000" \
  --font        "FontePrimaria" \
  --url         "site.com" \
  --version     "v1.0 · 2026" \
  --main-logo   "$MAIN_LOGO" \
  --icon-logo   "$ICON_LOGO" \
  --favicon     "$FAVICON" \
  --spec \
  --output-dir  "$ROOT/templates/av-design-system"
```

O `--spec` gera junto o `av-design-system-spec.md` (~4 KB): o mesmo sistema em Markdown, que é o arquivo que outras IAs devem ler. Informe os dois arquivos ao usuário no final e sugira versionar a pasta em Git para conectar ao Projeto do Claude.

Se o usuário pedir um arquivo único para enviar avulso, refaça com `--embed`.

Opcional: `--theme light` faz o arquivo **abrir** no tema claro (o toggle na sidebar troca ao vivo de qualquer forma; o padrão é escuro). As imagens vão embutidas em base64 e os ícones em SVG inline, então o `.html` gerado **funciona sozinho** mesmo copiado para fora da pasta.

Se a saída começar com `OK:`, suba o servidor e mostre o link, **não abra automaticamente**:

```bash
OUTPUT=$(python3 "$SKILL_DIR/build.py" serve \
  --dir  "$ROOT/templates/av-design-system" \
  --file "av-design-system.html")
SERVE_PID=$(echo "$OUTPUT" | grep '^SERVER_PID:' | cut -d: -f2)
SERVE_URL=$(echo "$OUTPUT" | grep '^SERVE_URL:' | sed 's/^SERVE_URL://')
```

Informe:
> "✓ Design System gerado: [$SERVE_URL]($SERVE_URL)
> *(Servidor ativo, feche a aba quando terminar de revisar)*"

O servidor fica rodando para o usuário navegar. **Não mate o servidor automaticamente**, deixe o usuário fechar quando quiser.

Se houver erro no build, leia a mensagem e corrija os argumentos.

---

## FLUXO B · Baixar template de referência

### B1. URL e slug

Pergunte exatamente: **"Qual url do site você quer clonar?"**

Derive o slug a partir do domínio da URL informada (remova `www.`, protocolo e TLD).

### B2. Criar pasta

```bash
ROOT=$(pwd)
mkdir -p "$ROOT/templates/{slug}"
```

### B3. Espelhar

Execute o mirror, renderiza o site (inclusive SPAs) e salva `{slug}.html` + uma pasta `assets/` com CSS, imagens e fontes **locais** (autossuficiente):

```bash
python3 "$SKILL_DIR/build.py" mirror \
  --url        "{URL}" \
  --slug       "{slug}" \
  --output-dir "$ROOT/templates/{slug}"
```

O mirror já trata reveals por blur/fade/scroll (neutraliza animações travadas) e remove scripts da SPA para o snapshot não "des-renderizar".

### B4. Servir e mostrar

Sites espelhados devem ser abertos **via HTTP** (não `file://`), pois carregam assets da pasta `assets/`. Suba o servidor e entregue a URL, **não abra automaticamente**:

```bash
OUTPUT=$(python3 "$SKILL_DIR/build.py" serve \
  --dir  "$ROOT/templates/{slug}" \
  --file "{slug}.html")
SERVE_URL=$(echo "$OUTPUT" | grep '^SERVE_URL:' | sed 's/^SERVE_URL://')
```

> "✓ Site capturado: [$SERVE_URL]($SERVE_URL)
> *(Servidor ativo, feche a aba quando terminar de revisar)*"

---

## REGRAS

- **Nunca leia nem gere HTML**, o `build.py`/`mirror.js` fazem isso
- **Nunca use caminhos relativos**, sempre `$ROOT` e `$SKILL_DIR` absolutos
- Pasta sempre **`templates`** (plural), na raiz do projeto (`$ROOT`)
- O arquivo HTML tem sempre o **mesmo nome da pasta**: Fluxo A → `av-design-system.html`; Fluxo B → `{slug}.html`
- **Nunca** crie dentro de `exemplo/`, `src/` ou subpastas
- Nunca pule etapas, cada passo depende do anterior
- Se um comando falhar, leia o stderr e corrija os argumentos antes de seguir
