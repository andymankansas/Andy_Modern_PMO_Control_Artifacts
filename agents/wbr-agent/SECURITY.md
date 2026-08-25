# Security and Data

This agent edits PowerPoint files on your machine. It runs entirely offline over local files
and never sends data anywhere.

- The agent always writes a NEW dated copy of your deck. It never modifies your source template
  or prior week's deck in place.
- Do not commit `wbr_config.json`, `weekly_input.json`, `deck-structure.json`, generated `.pptx`
  files, or the `drafts/` folder. The included `.gitignore` already excludes them.
- Your deck, its content, and any metrics stay local. Nothing is uploaded.
- The optional knowledge base integration is off by default. When absent, the agent simply skips
  the change digest and uses your weekly input file.
- Report any issue with this package privately to the repository owner. Do not include company or
  customer data in a public issue.
