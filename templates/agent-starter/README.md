# <Agent Name>

One-line description of what this agent does.

> This folder was copied from `templates/agent-starter`. Replace every `<Agent Name>`, `<agent-slug>`, and `<agent_module>` placeholder, then delete `HOW-TO-USE.md`.

## Capabilities

- Describe the main capability.
- Describe safety or approval behavior if any.

## Install

Extract the release ZIP, open the extracted folder in VS Code, and run:

```powershell
Set-ExecutionPolicy -Scope Process RemoteSigned
.\setup.ps1
```

Then select **<Agent Name>** in VS Code Chat.

See [INSTALL.md](INSTALL.md) for prerequisites.

## Release

Publish from this folder with:

```powershell
.\scripts\build_release.ps1 -Version 1.0.0
gh release create "<agent-slug>/v1.0.0" .\..\<Agent Name>_Setup_1.0.0.zip .\..\<Agent Name>_Setup_1.0.0.zip.sha256 `
  --repo andymankansas/Andy_Modern_PMO_Control_Artifacts --target main `
  --title "<Agent Name> v1.0.0" --notes "First release."
```

Tags are product-scoped: `<agent-slug>/vMAJOR.MINOR.PATCH[-prerelease]`.
