import sys
from datetime import datetime

from markdown_to_json.scripts.md_to_json import jsonify_markdown

# Convert markdown highlight timestamps to JSON for easier parsing later

if __name__ == "__main__":
    date = datetime.now().strftime("%-m-%-d-%Y")
    jsonFile = f"highlights_{date}.json"

    if len(sys.argv) >= 2:
        jsonify_markdown(sys.argv[1], jsonFile, 2)
        print(f"{jsonFile} created in current directory.")
    else:
        print(f"USAGE: python3 {sys.argv[0]} /path/to/highlights.md")
        print(f"This will create a file called {jsonFile}.")
