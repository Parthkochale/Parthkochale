import requests, re, sys

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
themes    = ", ".join(puzzle.get("themes", [])[:4]).replace("_", " ").title()

# Use lichess board editor image — more reliable with GitHub camo proxy
fen_position = fen.split(" ")[0] if " " in fen else fen
fen_encoded  = fen_position.replace("/", "%2F")

board_url  = f"https://lichess.org/export/fen.gif?fen={fen.replace(' ', '%20')}&color={'white' if side == 'White' else 'black'}&theme=brown&piece=cburnett"
puzzle_url = f"https://lichess.org/training/{puzzle_id}" if puzzle_id else "https://lichess.org/training"

# Use markdown image with puzzle link
block = f"""<div align="center">

### ♟️ Today's Puzzle — {side} to Move

| | |
|:---:|:---|
| **Rating** | {rating} |
| **Played** | {plays:,}× |
| **Themes** | {themes if themes else "tactics"} |
| **Side** | {side} to move |

[![Open Puzzle on Lichess]({board_url})]({puzzle_url})

**[🔗 Click the board or here to solve on Lichess →]({puzzle_url})**

</div>"""

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

pattern     = r"<!-- CHESS-PUZZLE:START -->.*?<!-- CHESS-PUZZLE:END -->"
replacement = f"<!-- CHESS-PUZZLE:START -->\n{block}\n<!-- CHESS-PUZZLE:END -->"

if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"✅ Updated: {puzzle_id} | {side} to move | Rating {rating}")
else:
    print("❌ Markers not found")
    sys.exit(1)
