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

board_url = (
    "https://lichess1.org/export/fen.gif"
    "?fen=" + fen.replace(" ", "%20") +
    "&color=" + ("white" if side == "White" else "black") +
    "&theme=brown&piece=cburnett"
) if fen else "https://lichess.org/images/puzzle_placeholder.png"

puzzle_url = (
    "https://lichess.org/training/" + puzzle_id
    if puzzle_id else "https://lichess.org/training"
)

block = (
    '<div align="center">\n\n'
    "[![Daily Chess Puzzle](" + board_url + ")](" + puzzle_url + ")\n\n"
    "**" + side + " to move · Rating: " + str(rating) + " · Played " + f"{plays:,}" + "× times**\n\n"
    "Themes: `" + (themes if themes else "tactics") + "`\n\n"
    "[🔗 Solve Today's Puzzle on Lichess →](" + puzzle_url + ")&nbsp;&nbsp;|&nbsp;&nbsp;[♟️ Play Chess](https://lichess.org)\n\n"
    "</div>"
)

with open("README.md", "r", encoding="utf-8") as f:
    content = f.read()

pattern     = r"<!-- CHESS-PUZZLE:START -->.*?<!-- CHESS-PUZZLE:END -->"
replacement = "<!-- CHESS-PUZZLE:START -->\n" + block + "\n<!-- CHESS-PUZZLE:END -->"

if re.search(pattern, content, re.DOTALL):
    new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Puzzle updated: " + puzzle_id + " | Rating: " + str(rating) + " | " + side + " to move")
else:
    print("Markers not found in README.md")
    sys.exit(1)
