import requests, re, sys, os

# ── Chess piece Unicode symbols ────────────────────────────────
PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
}

PIECE_COLORS = {
    'K': '#FFFFFF', 'Q': '#FFFFFF', 'R': '#FFFFFF',
    'B': '#FFFFFF', 'N': '#FFFFFF', 'P': '#FFFFFF',
    'k': '#1a1a1a', 'q': '#1a1a1a', 'r': '#1a1a1a',
    'b': '#1a1a1a', 'n': '#1a1a1a', 'p': '#1a1a1a',
}

STROKE_COLORS = {
    'K': '#333333', 'Q': '#333333', 'R': '#333333',
    'B': '#333333', 'N': '#333333', 'P': '#333333',
    'k': '#888888', 'q': '#888888', 'r': '#888888',
    'b': '#888888', 'n': '#888888', 'p': '#888888',
}

def fen_to_board(fen_position):
    """Convert FEN position string to 8x8 board array."""
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
    """Generate a clean SVG chess board with pieces."""
    size      = 400
    sq        = size // 8
    padding   = 30   # for rank/file labels
    total     = size + padding * 2

    light_sq  = "#F0D9B5"
    dark_sq   = "#B58863"
    bg_color  = "#1a1a2e"
    label_col = "#8b949e"
    accent    = "#36BCF7"

    svg_parts = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{total}" height="{total + 60}" '
        f'viewBox="0 0 {total} {total + 60}">'
    )

    # Background
    svg_parts.append(
        f'<rect width="{total}" height="{total + 60}" fill="{bg_color}" rx="12"/>'
    )

    # Title bar
    svg_parts.append(
        f'<text x="{total//2}" y="18" '
        f'font-family="monospace" font-size="11" '
        f'fill="{accent}" text-anchor="middle" font-weight="bold">'
        f'♟ Daily Chess Puzzle — {side} to Move</text>'
    )
    svg_parts.append(
        f'<text x="{total//2}" y="30" '
        f'font-family="monospace" font-size="9" '
        f'fill="{label_col}" text-anchor="middle">'
        f'Rating: {rating}  ·  {themes}</text>'
    )

    # Board squares
    files = ['a','b','c','d','e','f','g','h']
    ranks = ['8','7','6','5','4','3','2','1']

    for row in range(8):
        for col in range(8):
            x   = padding + col * sq
            y   = padding + row * sq + 35
            col_sq = light_sq if (row + col) % 2 == 0 else dark_sq
            svg_parts.append(
                f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{col_sq}"/>'
            )

            # Piece
            piece = board[row][col] if row < len(board) and col < len(board[row]) else ''
            if piece and piece in PIECES:
                symbol = PIECES[piece]
                fill   = PIECE_COLORS[piece]
                stroke = STROKE_COLORS[piece]
                cx     = x + sq // 2
                cy     = y + sq // 2 + 9
                svg_parts.append(
                    f'<text x="{cx}" y="{cy}" '
                    f'font-size="{int(sq * 0.72)}" '
                    f'text-anchor="middle" '
                    f'fill="{fill}" '
                    f'stroke="{stroke}" '
                    f'stroke-width="0.8" '
                    f'paint-order="stroke">'
                    f'{symbol}</text>'
                )

    # File labels (a-h) bottom
    for col in range(8):
        x = padding + col * sq + sq // 2
        y = padding + 8 * sq + 48
        svg_parts.append(
            f'<text x="{x}" y="{y}" '
            f'font-family="monospace" font-size="11" '
            f'fill="{label_col}" text-anchor="middle">{files[col]}</text>'
        )

    # Rank labels (1-8) left
    for row in range(8):
        x = padding - 8
        y = padding + row * sq + sq // 2 + 4 + 35
        svg_parts.append(
            f'<text x="{x}" y="{y}" '
            f'font-family="monospace" font-size="11" '
            f'fill="{label_col}" text-anchor="middle">{ranks[row]}</text>'
        )

    # Bottom info bar
    bar_y = total + 35
    svg_parts.append(
        f'<text x="{total//2}" y="{bar_y}" '
        f'font-family="monospace" font-size="10" '
        f'fill="{label_col}" text-anchor="middle">'
        f'Click to solve on Lichess → lichess.org/training/{puzzle_id}</text>'
    )

    svg_parts.append('</svg>')
    return '\n'.join(svg_parts)

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
themes_list = puzzle.get("themes", [])

side_char = fen.split(" ")[1] if " " in fen else "w"
side      = "White" if side_char == "w" else "Black"
themes    = ", ".join(themes_list[:3]).replace("_", " ").title()

fen_position = fen.split(" ")[0] if " " in fen else fen

# ── Generate SVG board ─────────────────────────────────────────
board = fen_to_board(fen_position)
svg   = generate_svg(board, side, puzzle_id, rating, themes)

# Save SVG to assets folder
os.makedirs("assets", exist_ok=True)
with open("assets/chess-puzzle.svg", "w", encoding="utf-8") as f:
    f.write(svg)
print(f"SVG board saved.")

puzzle_url = f"https://lichess.org/training/{puzzle_id}" if puzzle_id else "https://lichess.org/training"

# ── Build README block ─────────────────────────────────────────
block = (
    '<div align="center">\n\n'
    f'[![Daily Chess Puzzle](https://raw.githubusercontent.com/Parthkochale/Parthkochale/main/assets/chess-puzzle.svg)]({puzzle_url})\n\n'
    f'**{side} to move · Rating: {rating} · Played {plays:,}× times**\n\n'
    f'Themes: `{themes if themes else "tactics"}`\n\n'
    f'[🔗 Solve Today\'s Puzzle on Lichess →]({puzzle_url})&nbsp;&nbsp;|&nbsp;&nbsp;[♟️ Play Chess](https://lichess.org)\n\n'
    '</div>'
)

# ── Update README ──────────────────────────────────────────────
with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

pattern     = r"<!-- CHESS-PUZZLE:START -->.*?<!-- CHESS-PUZZLE:END -->"
replacement = f"<!-- CHESS-PUZZLE:START -->\n{block}\n<!-- CHESS-PUZZLE:END -->"

if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ README updated: {puzzle_id} | {side} to move | Rating {rating}")
else:
    print("❌ Markers not found in README.md")
    sys.exit(1)
