# Security and Data

This agent has two stages. Stage 1 (optional) reads your mailbox, calendar, and Teams through
WorkIQ and writes notes to folders you choose. Stage 2 reads only local note files and writes a
local knowledge base. Keep your data private:

- Do not commit `context_layer/config.json`, the `context_layer/store/` folder, or any saved
  meeting, email, or Teams notes to source control. The included `.gitignore` already excludes them.
- Do not share generated notes, digests, rollups, or the store outside your organization.
- Stage 2 runs entirely offline over local files. It never sends data anywhere.
- Stage 1 only reads what WorkIQ returns and never invents content.
- The `samples/` notes are fictional and safe to publish. Replace them with your own private
  notes only in your local, gitignored folder.
- Report any issue with this package privately to the repository owner. Do not include personal
  or tenant data in a public issue.
