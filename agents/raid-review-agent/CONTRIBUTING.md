# Contributing

This repository is currently maintained as a pre-release project.

## Before Contributing

1. Do not include customer, tenant, employee, or project data.
2. Use synthetic workbook fixtures only.
3. Keep review, approval, and apply as separate workflow phases.
4. Preserve the rule that no workbook write occurs without a validated approval manifest.
5. Add tests for workbook structure and data preservation changes.
6. Avoid machine-specific paths and personal account details.

## Validation

Before opening a pull request:

```powershell
python -m pytest
```

When the package builder is available, also run its release validation command and inspect the generated ZIP contents.
