import requests, re, sys, os

# ── SVG piece paths (scaled to 1x1, will be transformed per square) ──
# Each piece is drawn using pure SVG paths — no fonts, no Unicode
PIECE_PATHS = {
    # WHITE PIECES
    'P': '''<g transform="translate({x},{y}) scale({s})">
      <ellipse cx="0.5" cy="0.85" rx="0.28" ry="0.08" fill="#555" opacity="0.3"/>
      <rect x="0.3" y="0.75" width="0.4" height="0.08" rx="0.04" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.38" y="0.45" width="0.24" height="0.32" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.38" r="0.16" fill="#fff" stroke="#333" stroke-width="0.04"/>
    </g>''',
    'R': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.32" y="0.42" width="0.36" height="0.38" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.28" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.44" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.6" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
    </g>''',
    'N': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.35" y="0.68" width="0.3" height="0.12" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <path d="M0.5 0.65 C0.3 0.55 0.25 0.35 0.35 0.22 C0.42 0.15 0.55 0.18 0.6 0.28 C0.65 0.22 0.72 0.2 0.72 0.32 C0.72 0.5 0.65 0.62 0.5 0.65Z" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.41" cy="0.27" r="0.04" fill="#333"/>
    </g>''',
    'B': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <ellipse cx="0.5" cy="0.68" rx="0.18" ry="0.07" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <path d="M0.5 0.62 C0.35 0.5 0.32 0.32 0.5 0.22 C0.68 0.32 0.65 0.5 0.5 0.62Z" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.19" r="0.06" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.14" r="0.03" fill="#333"/>
    </g>''',
    'Q': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.22" y="0.78" width="0.56" height="0.07" rx="0.03" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <path d="M0.28 0.72 L0.32 0.42 L0.5 0.52 L0.68 0.42 L0.72 0.72Z" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.28" cy="0.38" r="0.07" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.32" r="0.07" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.72" cy="0.38" r="0.07" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.38" cy="0.34" r="0.05" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <circle cx="0.62" cy="0.34" r="0.05" fill="#fff" stroke="#333" stroke-width="0.04"/>
    </g>''',
    'K': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.22" y="0.78" width="0.56" height="0.07" rx="0.03" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <path d="M0.28 0.72 L0.35 0.45 L0.5 0.55 L0.65 0.45 L0.72 0.72Z" fill="#fff" stroke="#333" stroke-width="0.04"/>
      <rect x="0.46" y="0.18" width="0.08" height="0.28" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.03"/>
      <rect x="0.36" y="0.24" width="0.28" height="0.08" rx="0.02" fill="#fff" stroke="#333" stroke-width="0.03"/>
    </g>''',
    # BLACK PIECES
    'p': '''<g transform="translate({x},{y}) scale({s})">
      <ellipse cx="0.5" cy="0.85" rx="0.28" ry="0.08" fill="#222" opacity="0.3"/>
      <rect x="0.3" y="0.75" width="0.4" height="0.08" rx="0.04" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.38" y="0.45" width="0.24" height="0.32" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.38" r="0.16" fill="#222" stroke="#999" stroke-width="0.04"/>
    </g>''',
    'r': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.32" y="0.42" width="0.36" height="0.38" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.28" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.44" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.6" y="0.28" width="0.12" height="0.18" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
    </g>''',
    'n': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.35" y="0.68" width="0.3" height="0.12" rx="0.02" fill="#222" stroke="#999" stroke-width="0.04"/>
      <path d="M0.5 0.65 C0.3 0.55 0.25 0.35 0.35 0.22 C0.42 0.15 0.55 0.18 0.6 0.28 C0.65 0.22 0.72 0.2 0.72 0.32 C0.72 0.5 0.65 0.62 0.5 0.65Z" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.41" cy="0.27" r="0.04" fill="#aaa"/>
    </g>''',
    'b': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.25" y="0.78" width="0.5" height="0.07" rx="0.03" fill="#222" stroke="#999" stroke-width="0.04"/>
      <ellipse cx="0.5" cy="0.68" rx="0.18" ry="0.07" fill="#222" stroke="#999" stroke-width="0.04"/>
      <path d="M0.5 0.62 C0.35 0.5 0.32 0.32 0.5 0.22 C0.68 0.32 0.65 0.5 0.5 0.62Z" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.19" r="0.06" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.14" r="0.03" fill="#aaa"/>
    </g>''',
    'q': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.22" y="0.78" width="0.56" height="0.07" rx="0.03" fill="#222" stroke="#999" stroke-width="0.04"/>
      <path d="M0.28 0.72 L0.32 0.42 L0.5 0.52 L0.68 0.42 L0.72 0.72Z" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.28" cy="0.38" r="0.07" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.5" cy="0.32" r="0.07" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.72" cy="0.38" r="0.07" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.38" cy="0.34" r="0.05" fill="#222" stroke="#999" stroke-width="0.04"/>
      <circle cx="0.62" cy="0.34" r="0.05" fill="#222" stroke="#999" stroke-width="0.04"/>
    </g>''',
    'k': '''<g transform="translate({x},{y}) scale({s})">
      <rect x="0.22" y="0.78" width="0.56" height="0.07" rx="0.03" fill="#222" stroke="#999" stroke-width="0.04"/>
      <path d="M0.28 0.72 L0.35 0.45 L0.5 0.55 L0.65 0.45 L0.72 0.72Z" fill="#222" stroke="#999" stroke-width="0.04"/>
      <rect x="0.46" y="0.18" width="0.08" height="0.28" rx="0.02" fill="#222" stroke="#999" stroke-width="0.03"/>
      <rect x="0.36" y="0.24" width="0.28" height="0.08" rx="0.02" fill="#222" stroke="#999" stroke-width="0.03"/>
    </g>''',
}

def fen_to_board(fen_position):
    board = []
    for row in fen_position.split('/'):
        board_row = []
        for ch in row:
            if ch.isdigit():
                board_row.extend([''] * int(ch))
            else:
                board_row.append(ch)
        board.append(board_row)
    return board

def generate_svg(board, side, puzzle_id, rating, themes):
    SQ       = 52
    PADDING  = 22
    BOARD    = SQ * 8
    TOTAL_W  = BOARD + PADDING * 2
    HEADER   = 48
    FOOTER   = 28
    TOTAL_H  = BOARD + PADDING * 2 + HEADER + FOOTER

    light  = "#F0D9B5"
    dark   = "#B58863"
    bg     = "#1a1a2e"
    lbl    = "#8b949e"
    accent = "#36BCF7"
    hi     = "#36BCF744"   # highlight last move squares

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{TOTAL_W}" height="{TOTAL_H}" '
        f'viewBox="0 0 {TOTAL_W} {TOTAL_H}">'
    )

    # Background card
    parts.append(f'<rect width="{TOTAL_W}" height="{TOTAL_H}" fill="{bg}" rx="10"/>')

    # Header
    parts.append(
        f'<text x="{TOTAL_W//2}" y="20" font-family="monospace" font-size="12" '
        f'fill="{accent}" text-anchor="middle" font-weight="bold">'
        f'Daily Chess Puzzle</text>'
    )
    parts.append(
        f'<text x="{TOTAL_W//2}" y="36" font-family="monospace" font-size="10" '
        f'fill="{lbl}" text-anchor="middle">'
        f'{side} to move  ·  Rating {rating}  ·  {themes}</text>'
    )

    # Board
    files = list("abcdefgh")
    ranks = list("87654321")
    BX = PADDING
    BY = HEADER + PADDING

    for row in range(8):
        for col in range(8):
            x  = BX + col * SQ
            y  = BY + row * SQ
            sq_color = light if (row + col) % 2 == 0 else dark
            parts.append(f'<rect x="{x}" y="{y}" width="{SQ}" height="{SQ}" fill="{sq_color}"/>')

            # Piece
            piece = board[row][col] if row < len(board) and col < len(board[row]) else ''
            if piece in PIECE_PATHS:
                parts.append(
                    PIECE_PATHS[piece].format(x=x, y=y, s=SQ)
                )

    # File labels
    for col in range(8):
        x = BX + col * SQ + SQ // 2
        y = BY + BOARD + 14
        parts.append(
            f'<text x="{x}" y="{y}" font-family="monospace" font-size="10" '
            f'fill="{lbl}" text-anchor="middle">{files[col]}</text>'
        )

    # Rank labels
    for row in range(8):
        x = BX - 8
        y = BY + row * SQ + SQ // 2 + 4
        parts.append(
            f'<text x="{x}" y="{y}" font-family="monospace" font-size="10" '
            f'fill="{lbl}" text-anchor="middle">{ranks[row]}</text>'
        )

    # Footer
    fy = BY + BOARD + PADDING + 14
    parts.append(
        f'<text x="{TOTAL_W//2}" y="{fy}" font-family="monospace" font-size="9" '
        f'fill="{accent}" text-anchor="middle">'
        f'&#x1F517; lichess.org/training/{puzzle_id}</text>'
    )

    parts.append('</svg>')
    return '\n'.join(parts)

# ── Fetch puzzle ───────────────────────────────────────────────
try:
    resp = requests.get(
        "https://lichess.org/api/puzzle/daily",
        headers={"Accept": "application/json"},
        timeout=15
    )
    resp.raise_for_status()
    data = resp.json()
except Exception as e:
    print(f"API error: {e}")
    sys.exit(0)

puzzle    = data.get("puzzle", {})
game      = data.get("game", {})
puzzle_id = puzzle.get("id", "")
fen       = game.get("fen", "")
rating    = puzzle.get("rating", "?")
plays     = puzzle.get("plays", 0)

side_char = fen.split(" ")[1] if " " in fen else "w"
side      = "White" if side_char == "w" else "Black"
themes    = ", ".join(puzzle.get("themes", [])[:3]).replace("_", " ").title()
fen_pos   = fen.split(" ")[0] if " " in fen else fen

board = fen_to_board(fen_pos)
svg   = generate_svg(board, side, puzzle_id, rating, themes)

os.makedirs("assets", exist_ok=True)
with open("assets/chess-puzzle.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print("SVG saved.")

puzzle_url = f"https://lichess.org/training/{puzzle_id}" if puzzle_id else "https://lichess.org/training"

block = (
    '<div align="center">\n\n'
    f'[![Daily Chess Puzzle](https://raw.githubusercontent.com/Parthkochale/Parthkochale/main/assets/chess-puzzle.svg)]({puzzle_url})\n\n'
    f'**{side} to move · Rating: {rating} · Played {plays:,}× times**\n\n'
    f'Themes: `{themes if themes else "tactics"}`\n\n'
    f'[🔗 Solve on Lichess →]({puzzle_url})\n\n'
    '</div>'
)

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

pattern     = r"<!-- CHESS-PUZZLE:START -->.*?<!-- CHESS-PUZZLE:END -->"
replacement = f"<!-- CHESS-PUZZLE:START -->\n{block}\n<!-- CHESS-PUZZLE:END -->"

if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ Done: {puzzle_id} | {side} to move | Rating {rating}")
else:
    print("❌ Markers not found")
    sys.exit(1)
