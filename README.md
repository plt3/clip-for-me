## Notes:

- markdown-to-json is too old and needs a change:
  - find file `venv/lib/python3.10/site-packages/markdown_to_json/vendor/CommonMark/CommonMark.py`
    - (so basically just CommonMark.py within the markdown-to-json package, location might vary)
  - change line 19 from `HTMLunescape = html.parser.HTMLParser().unescape` to `HTMLunescape = html.unescape`
  - everything should work after that

### TODO:

- write Markdown format for highlights
- write automatic check to recommend saveStorage if not enough disk space
