#!/usr/bin/env python3
"""
AV Design System · build.py
Subcomandos: rename | suggest | build
"""
import os, sys, shutil, argparse, colorsys, re

# ── Helpers ───────────────────────────────────────────────────────────────────

def hex_to_rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(r, g, b):
    return f'#{r:02X}{g:02X}{b:02X}'

def enc(f):
    return f.replace(' ', '%20')

def img_data_uri(path, max_px=512, quality=86):
    """Lê uma imagem e devolve um data: URI base64 (renderiza offline, sem arquivo externo).

    Converte para WebP redimensionado (reduz ~60% do peso sem perda visível nos
    tamanhos em que os logos aparecem). Se Pillow não estiver disponível ou a
    conversão falhar, cai para o arquivo original.
    """
    import base64, mimetypes, io
    if max_px:
        try:
            from PIL import Image
            im = Image.open(path).convert('RGBA')
            im.thumbnail((max_px, max_px), Image.LANCZOS)
            buf = io.BytesIO()
            im.save(buf, 'WEBP', quality=quality, method=6)
            b64 = base64.b64encode(buf.getvalue()).decode('ascii')
            return f'data:image/webp;base64,{b64}'
        except Exception:
            pass
    mime = mimetypes.guess_type(path)[0] or 'image/png'
    with open(path, 'rb') as fh:
        b64 = base64.b64encode(fh.read()).decode('ascii')
    return f'data:{mime};base64,{b64}'

FONT_URLS = {
    'inter':             'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap',
    'poppins':           'https://fonts.googleapis.com/css2?family=Poppins:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap',
    'manrope':           'https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700;800&display=swap',
    'montserrat':        'https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap',
    'raleway':           'https://fonts.googleapis.com/css2?family=Raleway:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap',
    'outfit':            'https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&display=swap',
    'dm sans':           'https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
    'plus jakarta sans': 'https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap',
    'nunito':            'https://fonts.googleapis.com/css2?family=Nunito:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap',
    'figtree':           'https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap',
}

def get_font_url(font_name):
    key = font_name.lower().strip()
    if key in FONT_URLS:
        return FONT_URLS[key]
    encoded = font_name.replace(' ', '+')
    return f'https://fonts.googleapis.com/css2?family={encoded}:wght@300;400;500;600;700;800;900&display=swap'

# User-Agent moderno para o Google Fonts devolver .woff2 (mais leve que ttf)
_FONT_UA = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
            '(KHTML, like Gecko) Chrome/120.0 Safari/537.36')

def embed_font_css(font_url):
    """Baixa o CSS do Google Fonts e embute os .woff2 como data: URI.

    Retorna o CSS com @font-face autossuficiente, ou None se a rede falhar
    (nesse caso o build mantém o <link> remoto, nunca quebra offline).
    Mantém só os subsets latin/latin-ext para não inflar o arquivo.
    """
    import urllib.request, base64 as _b64
    def _get(url, binary=False):
        req = urllib.request.Request(url, headers={'User-Agent': _FONT_UA})
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.read() if binary else r.read().decode('utf-8')
    try:
        css = _get(font_url)
    except Exception:
        return None

    # Mantém apenas blocos @font-face de subsets latinos
    blocks = re.split(r'(?=/\*)', css)
    kept = []
    for blk in blocks:
        m = re.match(r'/\*\s*([\w-]+)\s*\*/', blk)
        subset = m.group(1) if m else None
        if subset and subset not in ('latin', 'latin-ext'):
            continue
        kept.append(blk)
    css = ''.join(kept) if kept else css

    # Troca cada url(...woff2) por data: URI
    embedded = 0
    def _repl(m):
        nonlocal embedded
        url = m.group(1)
        try:
            data = _get(url, binary=True)
            b64 = _b64.b64encode(data).decode('ascii')
            embedded += 1
            return f'url(data:font/woff2;base64,{b64}) format("woff2")'
        except Exception:
            return m.group(0)
    css = re.sub(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)\s*format\(["\']woff2["\']\)', _repl, css)
    css = re.sub(r'url\((https://fonts\.gstatic\.com/[^)]+\.woff2)\)', _repl, css)

    return css if embedded else None

# ── SUBCOMANDO: rename ────────────────────────────────────────────────────────

PT_TO_EN = {
    'branco': 'white',  'branca': 'white',
    'preto':  'black',  'preta':  'black',
    'brnaca': 'white',  'brncoa': 'white',   # typos comuns
    'laranja': 'orange',
    'amarelo': 'yellow', 'amarela': 'yellow',
    'degrade': 'gradient', 'degradê': 'gradient',
    'icone': 'icon', 'ícone': 'icon',
    'icones': 'icons',
    'horizontal': 'horizontal',
    'vertical': 'vertical',
    'comunidade': 'community',
    'mentoria': 'mentorship',
    'imersao': 'immersion', 'imersão': 'immersion',
    'programa': 'program',
    'vida': 'life',
    'copia': 'copy', 'cópia': 'copy',
    'agencia': 'agency', 'agência': 'agency',
    'paisagem': 'landscape',
    'favion': 'favicon', 'fav': 'favicon',    # typos comuns
    'circulo': 'circle', 'círculo': 'circle',
    'marca': 'mark',
    'escuro': 'dark',  'claro': 'light',
    'colorido': 'color', 'colorida': 'color',
    'principal': 'main',
    'alternativo': 'alt', 'alternativa': 'alt',
    'simbolo': 'symbol', 'símbolo': 'symbol',
    'og': 'og',
}

# Palavras a remover completamente (abreviações de marca + artigos + preposições)
SKIP_WORDS = {'av', 'avs', 'de', 'da', 'do', 'das', 'dos', 'e', 'a', 'o', 'of', 'the',
              'valor', 'agencia', 'agency', 'copia', 'copy'}

def cmd_rename(args):
    """Renomeia logos para padrão {prefix}-*.png em inglês, slug web."""
    import unicodedata, re

    images_dir = args.images_dir
    prefix     = args.prefix.lower().strip('-') if args.prefix else 'av'
    files = sorted([f for f in os.listdir(images_dir) if f.lower().endswith('.png')])

    def normalize(text):
        return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()

    def to_slug(name):
        # Remove prefixo existente (evita duplicação)
        name = re.sub(r'^[a-z]{2,5}[-_]', '', name, flags=re.IGNORECASE)
        # Remove sufixo " - Brand Name" (ex: " - Agencia de Valor")
        name = re.sub(r'\s*-\s*[A-Za-zÀ-ÿ][A-Za-zÀ-ÿ\s]*$', '', name).strip()
        # Normalizar acentos
        name = normalize(name)
        # Separar em palavras
        words = re.sub(r'[^a-zA-Z0-9]+', ' ', name).strip().lower().split()
        # Traduzir PT → EN e remover palavras descartáveis
        result = []
        for w in words:
            translated = PT_TO_EN.get(w, w)
            if translated.lower() in SKIP_WORDS:
                continue
            result.append(translated)
        if not result:
            result = ['asset']
        return '-'.join(result)

    # Gerar mapeamento
    mapping = {}
    slug_count = {}
    for f in files:
        base = os.path.splitext(f)[0]
        slug = to_slug(base)
        new_name = f'{prefix}-{slug}.png'
        slug_count[new_name] = slug_count.get(new_name, 0) + 1
        mapping[f] = new_name

    # Resolver conflitos de nome
    slug_seen = {}
    final_mapping = {}
    for f in files:
        new_name = mapping[f]
        if slug_count[new_name] > 1:
            slug_seen[new_name] = slug_seen.get(new_name, 0) + 1
            base, ext = new_name.rsplit('.', 1)
            new_name = f'{base}-{slug_seen[new_name]}.{ext}'
        final_mapping[f] = new_name

    # Renomear
    renamed, skipped = [], []
    for original, new_name in final_mapping.items():
        if original == new_name:
            skipped.append(original)
            continue
        src = os.path.join(images_dir, original)
        dst = os.path.join(images_dir, new_name)
        if os.path.exists(dst):
            base, ext = new_name.rsplit('.', 1)
            new_name = f'{base}-x.{ext}'
            dst = os.path.join(images_dir, new_name)
        shutil.move(src, dst)
        renamed.append(f'  {original} → {new_name}')

    if renamed:
        print('RENAMED:')
        print('\n'.join(renamed))
    if skipped:
        print('SKIPPED:')
        print('\n'.join(f'  {f}' for f in skipped))

    final = sorted([f for f in os.listdir(images_dir) if f.lower().endswith('.png')])
    print('\nFINAL:')
    for f in final:
        print(f'  {f}')

# ── SUBCOMANDO: mirror ───────────────────────────────────────────────────────

def cmd_mirror(args):
    """Captura site com Playwright → assets/ + {slug}.html."""
    import subprocess

    skill_dir = os.path.dirname(os.path.abspath(__file__))
    mirror_js = os.path.join(skill_dir, 'mirror.js')
    node_mods = '/tmp/node_modules'

    os.makedirs(args.output_dir, exist_ok=True)

    # Garante playwright instalado
    if not os.path.isdir(os.path.join(node_mods, 'playwright')):
        print('Instalando playwright...', file=sys.stderr)
        subprocess.run(['npm', 'install', '--prefix', '/tmp', 'playwright'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run(['npx', '--prefix', '/tmp', 'playwright', 'install', 'chromium'],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    env = os.environ.copy()
    env['NODE_PATH'] = node_mods

    result = subprocess.run(
        ['node', mirror_js, args.url, args.output_dir, args.slug],
        capture_output=True, text=True, env=env
    )

    output = result.stdout.strip()
    if result.returncode != 0 or not output.startswith('OK:'):
        print(f'ERRO: {result.stderr.strip()}', file=sys.stderr)
        sys.exit(1)

    print(output)


# ── SUBCOMANDO: suggest ───────────────────────────────────────────────────────

def cmd_suggest(args):
    """Extrai cores dominantes dos logos e sugere paleta + fontes."""
    images_dir = args.images_dir
    files = [f for f in os.listdir(images_dir) if f.lower().endswith('.png')]
    if not files:
        print('ERRO: nenhum arquivo PNG encontrado.', file=sys.stderr)
        sys.exit(1)

    try:
        from PIL import Image
    except ImportError:
        print('ERRO: Pillow não instalado. Execute: pip3 install Pillow', file=sys.stderr)
        sys.exit(1)

    # Extrair cores de todos os logos (priorizar versão colorida)
    priority = sorted(files, key=lambda f: (
        0 if any(k in f.lower() for k in ['gradient', 'red', 'color', 'orange']) else 1
    ))

    all_colors = {}
    for fname in priority[:3]:
        path = os.path.join(images_dir, fname)
        try:
            img = Image.open(path).convert('RGBA').resize((150, 150))
            for r, g, b, a in img.getdata():
                if a < 180: continue
                if r > 240 and g > 240 and b > 240: continue  # branco
                if r < 15  and g < 15  and b < 15:  continue  # preto
                # quantizar
                rq, gq, bq = (r//12)*12, (g//12)*12, (b//12)*12
                key = (rq, gq, bq)
                all_colors[key] = all_colors.get(key, 0) + 1
        except Exception:
            continue

    if not all_colors:
        print('CORES: não foi possível extrair cores dos logos.')
        print('SUGGESTION: use #000000 como fundo e escolha uma cor primária manualmente.')
        return

    # Top cores por frequência, filtrar tons cinza
    def is_colorful(r, g, b, min_sat=0.15):
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        return s >= min_sat and v >= 0.2

    colored = [(cnt, rgb) for rgb, cnt in all_colors.items() if is_colorful(*rgb)]
    colored.sort(reverse=True)
    top = colored[:8]

    if not top:
        top = sorted(all_colors.items(), key=lambda x: -x[1])[:5]
        top = [(cnt, rgb) for rgb, cnt in top]

    # Cor primária = mais frequente e saturada
    primary_rgb = top[0][1]
    primary = rgb_to_hex(*primary_rgb)

    # Derivar acento (mais claro, +luminosidade)
    h, s, v = colorsys.rgb_to_hsv(primary_rgb[0]/255, primary_rgb[1]/255, primary_rgb[2]/255)
    accent_rgb = tuple(int(x*255) for x in colorsys.hsv_to_rgb(h, max(0, s-0.15), min(1, v+0.18)))
    accent = rgb_to_hex(*accent_rgb)

    # Derivar deep (mais escuro, -luminosidade)
    deep_rgb = tuple(int(x*255) for x in colorsys.hsv_to_rgb(h, min(1, s+0.08), max(0, v-0.35)))
    deep = rgb_to_hex(*deep_rgb)

    # deep hover
    dh, ds, dv = colorsys.rgb_to_hsv(deep_rgb[0]/255, deep_rgb[1]/255, deep_rgb[2]/255)
    hover_rgb = tuple(int(x*255) for x in colorsys.hsv_to_rgb(dh, ds, min(1, dv+0.12)))
    hover = rgb_to_hex(*hover_rgb)

    # Sugestão de fontes baseada no matiz da cor primária (heurística visual)
    hue_deg = h * 360
    if 15 <= hue_deg <= 55:      # laranja/amarelo → moderno, geométrico
        fonts = [('Figtree', 'Display geométrico, peso e personalidade'), ('Plus Jakarta Sans', 'Moderno, tecnológico'), ('Outfit', 'Clean e versátil')]
    elif 0 <= hue_deg < 15 or hue_deg > 340:   # vermelho → bold, premium
        fonts = [('Inter', 'Neutro, preciso, premium'), ('Manrope', 'Bold e sofisticado'), ('Montserrat', 'Forte, institucional')]
    elif 200 <= hue_deg <= 260:  # azul/roxo → confiança, tech
        fonts = [('Inter', 'Tech, preciso'), ('DM Sans', 'Clean e digital'), ('Plus Jakarta Sans', 'Moderno e leve')]
    elif 100 <= hue_deg <= 160:  # verde → orgânico, crescimento
        fonts = [('Nunito', 'Amigável e approachable'), ('Poppins', 'Redondo, acessível'), ('Outfit', 'Leve e moderno')]
    else:
        fonts = [('Inter', 'Universal, sempre funciona'), ('Figtree', 'Personalidade e peso'), ('Manrope', 'Sofisticado')]

    # As 5 cores que serão usadas no design system
    palette = [
        ('#000000', 'Black'),
        (primary,  'Primary'),
        (accent,   'Accent'),
        (deep,     'Deep'),
        ('#FFFFFF', 'White'),
    ]

    print('CORES SUGERIDAS:')
    print(f'  primary:    {primary}')
    print(f'  accent:     {accent}')
    print(f'  deep:       {deep}')
    print(f'  deep-hover: {hover}')
    print(f'  bg:         #000000')
    print()
    print('FONTES SUGERIDAS:')
    for i, (fname, reason) in enumerate(fonts, 1):
        print(f'  {i}. {fname}: {reason}')

    # Gera mini HTML com swatches (estilo design system)
    import subprocess, socket
    preview_path = os.path.join(os.path.dirname(args.images_dir), '.color-preview.html')

    swatches_html = ''.join(f'''
        <div class="swatch">
          <div class="block" style="background:{h};{' border:1px solid rgba(255,255,255,0.12);' if h == '#FFFFFF' else ''}"></div>
          <span class="label">{n}</span>
        </div>''' for h, n in palette)

    html = f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Paleta de Cores</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #111;
    color: #fff;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
  }}
  .card {{
    background: #1a1a1a;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 6px;
    padding: 2.5rem 3rem;
    width: 100%;
    max-width: 600px;
  }}
  .section-label {{
    font-size: 0.6rem;
    font-weight: 600;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.25);
    margin-bottom: 1.25rem;
  }}
  .swatches {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
    margin-bottom: 2rem;
  }}
  .swatch {{
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }}
  .block {{
    width: 100%;
    aspect-ratio: 1;
    border-radius: 3px;
  }}
  .label {{
    font-size: 0.58rem;
    color: rgba(255,255,255,0.35);
    text-align: center;
    letter-spacing: 0.04em;
  }}
  .gradient-bar {{
    height: 3.5rem;
    border-radius: 3px;
    background: linear-gradient(90deg, {primary} 0%, {deep} 100%);
    margin-top: 0.25rem;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="section-label">Paleta de Cores</div>
  <div class="swatches">{swatches_html}
  </div>
  <div class="section-label">CTA Gradient</div>
  <div class="gradient-bar"></div>
</div>
</body>
</html>'''

    with open(preview_path, 'w') as f:
        f.write(html)

    # Sobe servidor localhost efêmero
    with socket.socket() as s:
        s.bind(('', 0))
        port = s.getsockname()[1]

    preview_dir  = os.path.dirname(preview_path)
    preview_file = os.path.basename(preview_path)
    server_proc  = subprocess.Popen(
        ['python3', '-m', 'http.server', str(port), '--directory', preview_dir],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    print(f'\nPREVIEW:{preview_path}')
    print(f'SERVER_PID:{server_proc.pid}')
    print(f'PREVIEW_URL:http://localhost:{port}/{preview_file}')

# ── SUBCOMANDO: build ─────────────────────────────────────────────────────────

def replace_color(html, old_hex, new_hex):
    r1, g1, b1 = hex_to_rgb(old_hex)
    r2, g2, b2 = hex_to_rgb(new_hex)
    html = html.replace(old_hex.upper(), new_hex.upper())
    html = html.replace(old_hex.lower(), new_hex.upper())
    html = html.replace(f'rgba({r1},{g1},{b1},', f'rgba({r2},{g2},{b2},')
    return html

def generate_brand_tiles(images_dir, embed=True, max_px=512, quality=86):
    if not os.path.isdir(images_dir):
        return ''
    files = sorted([f for f in os.listdir(images_dir) if f.lower().endswith('.png')])
    if not files:
        return ''

    tiles = []
    for img in files:
        il = img.lower()
        is_light   = 'light' in il or 'black' in il
        bg         = '#F3F3F3' if is_light else '#000'
        tile_class = 'logo-tile logo-tile--light' if is_light else 'logo-tile'
        has_icon   = 'icon' in il
        has_text   = 'wordmark' in il or ('logo' in il and 'dark' in il) or ('logo' in il and 'light' in il) or ('logo' in il and 'gradient' in il and 'icon' not in il)
        has_grad   = 'gradient' in il
        img_style  = 'max-height:5rem;max-width:5rem;' if ('icon' in il and 'logo' not in il and 'wordmark' not in il) else ''

        if has_grad and 'icon' in il and 'wordmark' not in il:
            label, desc = 'Ícone · Gradiente', 'Favicon · app icon · cor primária'
        elif has_grad and 'wordmark' in il:
            label, desc = 'Wordmark · Gradiente', 'Wordmark cor primária · uso digital'
        elif has_grad:
            label, desc = 'Logo · Gradiente', 'Logo cor primária · uso digital principal'
        elif 'icon' in il and 'logo' not in il and 'wordmark' not in il and not is_light:
            label, desc = 'Ícone · Escuro', 'Fundos escuros · favicon · avatar'
        elif 'icon' in il and 'logo' not in il and 'wordmark' not in il and is_light:
            label, desc = 'Ícone · Claro', 'Fundos claros · impresso'
        elif 'wordmark' in il and not is_light:
            label, desc = 'Wordmark · Escuro', 'Horizontal · fundos escuros · nav / footer'
        elif 'wordmark' in il and is_light:
            label, desc = 'Wordmark · Claro', 'Horizontal · fundos claros · impresso'
        elif 'logo' in il and not is_light:
            label, desc = 'Logo · Escuro', 'Fundos escuros · uso principal digital'
        elif 'logo' in il and is_light:
            label, desc = 'Logo · Claro', 'Fundos claros · impresso'
        else:
            label, desc = os.path.splitext(img)[0], 'Asset de marca'

        data_uri = (img_data_uri(os.path.join(images_dir, img), max_px, quality)
                    if embed else f'./images/{enc(img)}')
        tiles.append(f'''      <div class="logo-tile">
        <div class="logo-tile-preview" style="background:{bg};">
          <img src="{data_uri}" alt="{label}" style="{img_style}">
        </div>
        <div class="logo-tile-meta">
          <div class="tt">{label}</div>
          <div class="dd">{desc}</div>
        </div>
      </div>''')

    return '\n'.join(tiles)

def generate_spec_md(name, url, version, font, primary, accent, deep, deep_hover, bg, assets):
    """Gera um spec compacto em Markdown do design system.

    Formato pensado para base de conhecimento de IA (ex.: Projetos do Claude):
    só tokens, escalas e regras, sem base64, sem CSS/JS. Pesa poucos KB.
    """
    files = '\n'.join(f'- `{a}`' for a in assets) if assets else '- (nenhum asset em images/)'
    return f"""# {name} · Design System

Fonte única da verdade do sistema visual da {name}. Versão {version}. Site: {url}

Use estes tokens ao gerar qualquer interface, peça ou componente da marca.

## 1. Cores

| Token | Hex | Uso |
|---|---|---|
| `--brand` (primary) | `{primary}` | Cor primária, CTAs, destaques, ícones |
| `--gold` (accent) | `{accent}` | Fim do gradiente CTA, realces |
| `--deep` | `{deep}` | Fim escuro do gradiente, estados profundos |
| `--deep-hover` | `{deep_hover}` | Hover de CTA |
| `--bg` (dark) | `{bg}` | Fundo do tema escuro |
| `--bg` (light) | `#F4F4F1` | Fundo do tema claro |

**Gradiente de marca (CTA):** `linear-gradient(90deg, {primary}, {deep})`. Versão 135° para ícones e bordas.

**Escala de texto (opacidades sobre o fundo):** t1 100% (títulos) · t2 72% (corpo forte) · t3 50–58% (corpo) · t4 35–46% (labels) · t5 22–42% (meta) · t6 (divisores).
Contraste mínimo: **4.5:1** para texto normal, 3:1 para texto grande. Nunca use cinza claro em texto de corpo.

**Superfícies:** fills de 1.5% a 5% sobre o fundo; linhas de 4% a 10%. O tema claro espelha os mesmos papéis com preto translúcido.

## 2. Tipografia

Família única: **{font}** (300–900). Títulos em 900, corpo em 400.

| Papel | Tamanho | Line-height | Peso | Tracking |
|---|---|---|---|---|
| Display | clamp(2.5rem, 6vw, 4.5rem) | 1.0 | 900 | −0.03em |
| H1 | clamp(2rem, 4.5vw, 3.5rem) | 1.05 | 900 | −0.025em |
| H2 | clamp(1.5rem, 3vw, 2.5rem) | 1.1 | 700 | −0.02em |
| H3 | 1.4rem | 1.2 | 700 | normal |
| H4 | 1.125rem | 1.3 | 700 | normal |
| Body L | 1rem | 1.8 | 400 | normal |
| Body M | 0.875rem | 1.75 | 400 | normal |
| Overline / label | 0.6rem | — | 600–700 | 0.18–0.25em, uppercase |

Corpo com no máximo 65–75 caracteres por linha.

## 3. Layout e espaçamento

- Container máximo: **74rem**; padding lateral `clamp(1.25rem, 4vw, 2.75rem)`.
- Seções: padding vertical `clamp(4.5rem, 9vw, 8rem)`, separadas por linha de 1px.
- Raio padrão: **4px** (cards e botões); 9999px para chips e toggles.
- Grids fluidos: `repeat(auto-fit, minmax(Xrem, 1fr))` (X de 10 a 18 conforme a densidade).
- Breakpoints: **960px** (hero passa a 2 colunas) · **900px** (menu vira dropdown) · **640px** (compacta labels).
- Alvos de toque no mobile: mínimo **44×44px**.

## 4. Componentes

- **Botões:** uppercase, 0.72rem, peso 800, tracking 0.1em, padding 0.9rem 1.8rem. Variantes: `primary` (gradiente de marca), `outline`, `ghost`, `solid`. Hover: leve `translateY(-1px)` + sweep de cor subindo.
- **Cards:** fundo translúcido + borda de 1px + blur. Nunca aninhe cards.
- **Chips/badges:** pílula com borda em gradiente sutil; ponto pulsante para status "live".
- **Inputs:** fundo de fill 3%, borda 1px, foco na cor da marca. Todo input tem label associado.
- **Icon box:** 2.75rem, borda em gradiente 135°, ícone com traço na cor da marca.
- **Ícones:** conjunto line, traço 1.6px, grade 24×24.

## 5. Movimento

| Token | Duração | Uso | Curva |
|---|---|---|---|
| micro | 100–150ms | hover, foco | linear |
| ui | 250–350ms | botão, tooltip | ease-back |
| enter | 500–700ms | card, reveal | ease-apple `cubic-bezier(0.16,1,0.3,1)` |
| cinematic | 900–1400ms | hero, texto escalonado | ease-expo `cubic-bezier(0.19,1,0.22,1)` |
| ambient | 3–8s | pulse, float, shimmer | ease-in-out (loop) |

Sempre respeitar `prefers-reduced-motion: reduce`.

## 6. Marca

Dois temas convivem no mesmo arquivo: a logo **clara** aparece no tema escuro e a **escura** no tema claro. Nunca recolorir, distorcer, girar ou aplicar efeitos fora do documentado.

Assets disponíveis:
{files}
"""

def cmd_build(args):
    skill_dir     = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(skill_dir, 'template.html')

    if not os.path.exists(template_path):
        print(f'ERRO: template.html não encontrado em {template_path}', file=sys.stderr)
        sys.exit(1)

    with open(template_path, 'r', encoding='utf-8') as f:
        html = f.read()

    html = replace_color(html, '#FFA01A', args.primary)
    html = replace_color(html, '#F7AC29', args.accent)
    html = replace_color(html, '#AA1818', args.deep)
    html = replace_color(html, '#D21B1B', args.deep_hover)

    p = hex_to_rgb(args.primary)
    a = hex_to_rgb(args.accent)
    d = hex_to_rgb(args.deep)
    for old in ['rgba(255,160,26,', 'rgba(255,100,0,', 'rgba(255,115,0,']:
        html = html.replace(old, f'rgba({p[0]},{p[1]},{p[2]},')
    html = html.replace('rgba(247,172,41,', f'rgba({a[0]},{a[1]},{a[2]},')
    html = html.replace('rgba(170,24,24,',  f'rgba({d[0]},{d[1]},{d[2]},')

    # Tema: dark/light convivem no mesmo HTML (toggle em runtime via [data-theme]).
    # --theme apenas define qual tema abre por padrão.
    theme = getattr(args, 'theme', 'dark')
    default_theme = 'light' if theme == 'light' else 'dark'
    html = html.replace('{{DEFAULT_THEME}}', default_theme)

    # Fundo dark customizado: troca só o token --bg do bloco [data-theme="dark"]
    # (não mexe nos swatches/#000 espalhados pela página).
    bg = args.bg.upper()
    if bg != '#000000':
        html = re.sub(r'(--bg:\s*)#000000;', rf'\g<1>{bg};', html, count=1)

    font     = args.font
    font_url = get_font_url(font)
    old_url  = 'https://fonts.googleapis.com/css2?family=Figtree:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;0,900;1,400&display=swap'
    html = html.replace(old_url, font_url)
    html = html.replace("'Figtree'", f"'{font}'")
    html = html.replace('>Figtree<', f'>{font}<')
    html = html.replace('· Figtree', f'· {font}')
    html = html.replace('Figtree Display', f'{font} Display')

    # Embute a fonte como @font-face base64 (100% offline). Best-effort:
    # se não houver rede, mantém o <link> remoto (funciona online).
    if getattr(args, 'embed', False) and not getattr(args, 'no_embed_font', False):
        font_css = embed_font_css(font_url)
        if font_css:
            link_tag  = f'<link href="{font_url}" rel="stylesheet">'
            style_tag = '<style>\n' + font_css + '</style>'
            if link_tag in html:
                html = html.replace(link_tag, style_tag)
                # preconnect não é mais necessário quando a fonte está embutida
                html = html.replace('<link rel="preconnect" href="https://fonts.googleapis.com">\n', '')
                html = html.replace('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n', '')

    name    = args.name
    url     = args.url or (name.lower().replace(' ', '').replace('-', '') + '.com')
    version = args.version

    html = html.replace('{{PROJECT_NAME}}', name)
    html = html.replace('{{PROJECT_URL}}',  url)
    html = html.replace('{{VERSION}}',      version)
    html = html.replace('{{FONT_NAME}}',    font)

    images_dir = os.path.join(args.output_dir, 'images')
    files = sorted([f for f in os.listdir(images_dir)
                    if f.lower().endswith('.png')]) if os.path.isdir(images_dir) else []

    def find(*inc, exc=[]):
        # inc: substring (lenient). exc: por token inteiro (evita 'og' casar em 'logo').
        for f in files:
            fl = f.lower()
            toks = re.split(r'[^a-z0-9]+', fl)
            if all(k in fl for k in inc) and not any(e in toks for e in exc):
                return f
        return None

    # Sub-marcas / lockups largos: evitar no hero e no ícone (usar a marca principal)
    SUB = ['immersion', 'mentorship', 'program', 'community', 'horizontal', 'og']

    def counterpart(fname, want):
        """Acha a versão equivalente 'branca' (want='white') ou 'preta' (want='black')
        do mesmo arquivo, trocando o tom no nome (white<->black, light<->dark)."""
        if not fname:
            return None
        fl = fname.lower()
        pairs = ([('white', 'black'), ('light', 'dark')] if want == 'black'
                 else [('black', 'white'), ('dark', 'light')])
        for a, b in pairs:
            if a in fl:
                cand = fl.replace(a, b)
                for f in files:
                    if f.lower() == cand:
                        return f
        return None

    # ── Cada logo tem 2 versões: uma para fundo ESCURO (clara) e uma para
    #    fundo CLARO (escura). O tema alterna via CSS. ──────────────────────

    # Wordmark principal (hero, footer)
    if args.main_logo and os.path.exists(os.path.join(images_dir, args.main_logo)):
        hero_dark  = args.main_logo
        hero_light = counterpart(args.main_logo, 'black') or args.main_logo
    else:
        hero_dark  = (find('logo', 'white', exc=['icon'] + SUB)
                      or find('logo', exc=['black', 'icon', 'light'] + SUB)
                      or find('logo', exc=['icon'] + SUB) or find('logo')
                      or (files[0] if files else 'logo.png'))
        hero_light = (find('logo', 'black', exc=['icon'] + SUB)
                      or counterpart(hero_dark, 'black') or hero_dark)

    # Ícone compacto (sidebar, topbar, header do card)
    if args.icon_logo and os.path.exists(os.path.join(images_dir, args.icon_logo)):
        icon_dark  = args.icon_logo
        icon_light = counterpart(args.icon_logo, 'black') or args.icon_logo
    else:
        icon_dark  = (find('circle', 'white') or find('icon', 'white', exc=SUB)
                      or find('circle', exc=['black'] + SUB) or find('icon', exc=['black'] + SUB)
                      or hero_dark)
        icon_light = (find('circle', 'black') or find('icon', 'black', exc=SUB)
                      or counterpart(icon_dark, 'black') or icon_dark)

    # Favicon (aba do browser)
    if args.favicon and os.path.exists(os.path.join(images_dir, args.favicon)):
        favicon = args.favicon
    else:
        favicon = find('favicon') or icon_dark

    # Padrão: HTML leve referenciando ./images/ (ideal para repo Git e leitura por IA).
    # --embed: embute imagens e fonte em base64 e gera um arquivo único autossuficiente.
    embed   = getattr(args, 'embed', False)
    img_max = getattr(args, 'img_max', 512)
    img_q   = getattr(args, 'img_quality', 86)

    def uri(fname):
        p = os.path.join(images_dir, fname)
        if not os.path.exists(p):
            return ''
        return img_data_uri(p, img_max, img_q) if embed else f'./images/{enc(fname)}'

    # Imagens embutidas como base64 (renderizam standalone, ex.: upload no chat)
    html = html.replace('{{FAVICON}}',       uri(favicon))
    html = html.replace('{{ICON_ONDARK}}',   uri(icon_dark))   # sidebar/topbar/card em tema escuro
    html = html.replace('{{ICON_ONLIGHT}}',  uri(icon_light))  # idem em tema claro
    html = html.replace('{{HERO_ONDARK}}',   uri(hero_dark))   # hero/footer em tema escuro
    html = html.replace('{{HERO_ONLIGHT}}',  uri(hero_light))  # idem em tema claro
    # Card "logo variants": fundos fixos (branco/preto), independem do tema
    html = html.replace('{{HERO_LOGO}}',       uri(hero_dark))   # sobre fundo preto do card
    html = html.replace('{{HERO_LOGO_LIGHT}}', uri(hero_light))  # sobre fundo branco do card
    html = html.replace('{{P1_GRAD}}', args.primary.upper())
    html = html.replace('{{P3_GRAD}}', args.deep.upper())
    html = html.replace('{{P1_HEX}}',  args.primary.upper())
    html = html.replace('{{P3_HEX}}',  args.deep.upper())

    # ── Escalas de cor derivadas ───────────────────────────────────────
    def derive_scale(base_hex, steps=5, lighten_max=0.25, darken_max=0.45):
        r, g, b = hex_to_rgb(base_hex)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        colors = []
        for i in range(steps):
            t = i / (steps - 1)
            new_v = v + (lighten_max if i < steps//2 else 0) - t * darken_max
            new_v = max(0.05, min(1.0, new_v))
            nr, ng, nb = colorsys.hsv_to_rgb(h, min(1, s + t*0.05), new_v)
            colors.append(rgb_to_hex(int(nr*255), int(ng*255), int(nb*255)))
        return f"linear-gradient(to bottom,{','.join(colors)})"

    def lighten(hex_color, amount=0.15):
        r, g, b = hex_to_rgb(hex_color)
        h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
        nr, ng, nb = colorsys.hsv_to_rgb(h, max(0, s-0.1), min(1, v+amount))
        return rgb_to_hex(int(nr*255), int(ng*255), int(nb*255))

    html = html.replace('{{FIRE_SCALE}}',        derive_scale(args.primary))
    html = html.replace('{{EMBER_SCALE}}',       derive_scale(args.deep))
    html = html.replace('{{CTA_HOVER_GRADIENT}}',
        f"linear-gradient(90deg,{lighten(args.primary, 0.12)},{args.deep_hover.upper()})")
    html = html.replace('{{CTA_HOVER_LABEL}}',
        f"{lighten(args.primary, 0.12)} → {args.deep_hover.upper()} · 90°")
    html = html.replace('{{BRAND_TILES}}', generate_brand_tiles(images_dir, embed, img_max, img_q))

    folder_name = os.path.basename(os.path.normpath(args.output_dir))
    suffix = getattr(args, 'out_suffix', '') or ''
    out = os.path.join(args.output_dir, f'{folder_name}{suffix}.html')
    with open(out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f'OK:{out}')

    # Spec em Markdown (base de conhecimento de IA): poucos KB, só tokens e regras
    if getattr(args, 'spec', False):
        spec = generate_spec_md(name, url, version, font, args.primary.upper(),
                                args.accent.upper(), args.deep.upper(),
                                args.deep_hover.upper(), bg, files)
        spec_out = os.path.join(args.output_dir, f'{folder_name}{suffix}-spec.md')
        with open(spec_out, 'w', encoding='utf-8') as f:
            f.write(spec)
        print(f'SPEC:{spec_out}')

# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == '__main__':
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest='cmd')

    # mirror
    mi = sub.add_parser('mirror', help='Baixa site como slug.html + assets/')
    mi.add_argument('--url',        required=True)
    mi.add_argument('--output-dir', required=True, dest='output_dir')
    mi.add_argument('--slug',       required=True)

    # serve
    sv = sub.add_parser('serve', help='Serve uma pasta via localhost e imprime a URL')
    sv.add_argument('--dir',  required=True, help='Pasta a servir')
    sv.add_argument('--file', required=True, help='Arquivo HTML a abrir (relativo à pasta)')

    # rename
    r = sub.add_parser('rename', help='Renomeia logos para padrão {prefix}-*.png')
    r.add_argument('--images-dir', required=True, dest='images_dir')
    r.add_argument('--prefix', default='av', help='Prefixo do projeto (ex: vas)')

    # suggest
    s = sub.add_parser('suggest', help='Sugere cores e fontes a partir dos logos')
    s.add_argument('--images-dir', required=True, dest='images_dir')

    # build (default, aceita sem subcomando para retrocompatibilidade)
    b = sub.add_parser('build', help='Gera design-system.html')
    b.add_argument('--name',       required=True)
    b.add_argument('--primary',    default='#FFA01A')
    b.add_argument('--accent',     default='#F7AC29')
    b.add_argument('--deep',       default='#AA1818')
    b.add_argument('--deep-hover', default='#D21B1B', dest='deep_hover')
    b.add_argument('--bg',         default='#000000')
    b.add_argument('--font',       default='Figtree')
    b.add_argument('--url',        default='')
    b.add_argument('--version',    default='v1.0 · 2026')
    b.add_argument('--main-logo',  default='', dest='main_logo',  help='Logo principal (hero)')
    b.add_argument('--icon-logo',  default='', dest='icon_logo',  help='Logo ícone (nav + color card)')
    b.add_argument('--favicon',    default='', dest='favicon',    help='Favicon')
    b.add_argument('--output-dir', required=True, dest='output_dir')
    b.add_argument('--theme',      default='dark', choices=['dark', 'light'],
                   help='Tema visual: dark (padrão) ou light')
    b.add_argument('--out-suffix', default='', dest='out_suffix',
                   help='Sufixo no nome do arquivo (ex: -02 gera {pasta}-02.html)')
    b.add_argument('--embed', action='store_true', dest='embed',
                   help='Arquivo único autossuficiente: embute imagens (WebP base64) e fonte. '
                        'Use para enviar o HTML sozinho (chat, e-mail). Sem esta flag o HTML '
                        'fica leve (~100KB) usando ./images/, ideal para repo Git.')
    b.add_argument('--no-embed-font', action='store_true', dest='no_embed_font',
                   help='Com --embed, não embutir a fonte (mantém o <link> do Google Fonts)')
    b.add_argument('--lite', action='store_true', dest='lite',
                   help='(obsoleto) O modo leve agora é o padrão; a flag é aceita e ignorada')
    b.add_argument('--img-max', type=int, default=512, dest='img_max',
                   help='Lado máximo (px) das imagens embutidas em WebP. 0 = manter PNG original')
    b.add_argument('--img-quality', type=int, default=86, dest='img_quality',
                   help='Qualidade WebP das imagens embutidas (padrão 86)')
    b.add_argument('--spec', action='store_true', dest='spec',
                   help='Também gera {pasta}-spec.md: o design system em Markdown (poucos KB), '
                        'formato ideal para base de conhecimento de IA')

    args = p.parse_args()

    if args.cmd == 'mirror':
        cmd_mirror(args)
    elif args.cmd == 'serve':
        import socket, subprocess
        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]
        proc = subprocess.Popen(
            ['python3', '-m', 'http.server', str(port), '--directory', args.dir],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        print(f'SERVER_PID:{proc.pid}')
        print(f'SERVE_URL:http://localhost:{port}/{args.file}')
    elif args.cmd == 'rename':
        cmd_rename(args)
    elif args.cmd == 'suggest':
        cmd_suggest(args)
    elif args.cmd == 'build':
        cmd_build(args)
    else:
        p.print_help()
        sys.exit(1)
