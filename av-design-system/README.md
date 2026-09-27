# 🎨 AV Design System

Skill para **Claude Code** que faz duas coisas, em poucos minutos e por conversa:

- **(A) Criar um Design System** visual completo a partir dos logos e cores do seu projeto, paleta, tipografia e componentes, tudo gerado automaticamente.
- **(B) Clonar um site** de referência como template local autossuficiente (HTML + assets), pronto para estudar e adaptar.

Você não escreve uma linha de código. É só conversar com o Claude.

---

## 📦 O que vem no pacote

```
av-design-system/
├── SKILL.md         ← instruções que o Claude segue (não precisa abrir)
├── build.py         ← motor que gera o design system e clona sites
├── mirror.js        ← captura de sites (renderiza até SPA)
├── template.html    ← template base do design system
└── README.md        ← este guia
```

> Não edite os arquivos. A skill funciona sozinha, você só conversa.

---

## ✅ Requisitos

| Ferramenta | Para quê | Como verificar |
|------------|----------|----------------|
| **Claude Code** | rodar a skill | já instalado |
| **Python 3** | gerar o design system | `python3 --version` |
| **Pillow** | extrair cores dos logos (Fluxo A) | `pip3 install Pillow` |
| **Node.js** | clonar sites (Fluxo B) | `node --version` |

> O Chromium usado para clonar sites é baixado **automaticamente** na primeira vez (~1 min). Você não precisa instalar nada manualmente.

---

## 🚀 Instalação

1. Descompacte o ZIP.
2. Mova a pasta `av-design-system/` para a pasta de skills do Claude:
   - **Global** (vale para todos os projetos): `~/.claude/skills/`
   - **Só um projeto:** `<seu-projeto>/.claude/skills/`
3. Pronto. Abra o Claude Code e digite **`/av-design-system`**.

---

## 🟠 Fluxo A · Criar um Design System

1. Digite **`/av-design-system`** e escolha **Criar um novo Design System**.
2. Informe o **nome do projeto**.
3. Copie seus **logos em PNG** (fundo transparente) para a pasta que o Claude indicar.
4. O Claude renomeia os logos, **extrai a paleta de cores** e **sugere fontes** analisando sua logo.
5. Você confirma cores e fontes (pode ajustar à vontade, com preview ao vivo).
6. O Design System final abre no navegador. ✨

**Resultado:** `templates/av-design-system/av-design-system.html` + logos organizados em `images/`.

**Novidades da v2:**
- 🖥️ Layout premium com **menu no topo** (vira dropdown no celular).
- 🌗 **Tema claro e escuro** no mesmo arquivo, com **botão de switch**.
- 🪶 **Leve por padrão (~100 KB)**, usando as imagens reais da pasta `images/`. Pensado para viver em um **repositório Git**.
- 🧠 Gera também um **spec em Markdown (~4 KB)** com todos os tokens e regras: é o arquivo que **outras IAs leem** (Claude chat, cowork, Projetos). Conecte o repo ao Projeto e o modelo passa a conhecer sua marca.
- 📎 Precisa mandar o HTML sozinho por chat ou e-mail? Use `--embed`: vira um arquivo único (~1 MB) com imagens e fonte embutidas, que **renderiza sem nada ao lado**.

---

## 🔵 Fluxo B · Clonar um site

1. Digite **`/av-design-system`** e escolha **Baixar um template de referência**.
2. Informe a **URL** do site.
3. O Claude captura o site inteiro (inclusive SPAs) e salva tudo **localmente**.
4. Abre no navegador, funcionando offline. ✨

**Resultado:** `templates/{nome-do-site}/{nome-do-site}.html` + pasta `assets/` (CSS, imagens e fontes locais).

---

## 💡 Dicas

- Os arquivos são gerados na pasta `templates/` na raiz do seu projeto.
- Sites clonados devem ser abertos **via servidor local** (o Claude já sobe um pra você), não pelo `file://`.
- Quer trocar uma cor depois de pronto? É só pedir ao Claude.

---

Feito com 🧡 para acelerar a criação de interfaces.
