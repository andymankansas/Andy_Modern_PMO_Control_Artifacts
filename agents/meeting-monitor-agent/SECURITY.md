# Security and Data

This agent reads your mailbox, calendar, and Teams through WorkIQ and writes notes to folders you choose. Keep your data private:

- Do not commit `meeting_monitor_config.json`, `meeting_monitor_state.json`, or any saved meeting, email, or Teams notes to source control.
- Do not share generated notes, digests, or the config outside your organization.
- The agent only reads what WorkIQ returns and never invents content.
- Report any issue with this package privately to the repository owner. Do not include personal or tenant data in a public issue.
