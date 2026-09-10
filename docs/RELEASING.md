# Release process

## 1. Bump the version

Update the version in two places (they must match):

- `pyproject.toml` → `[project].version`
- `installer/devkitbox.iss` → `#define MyAppVersion`

`app/core/constants.py::APP_VERSION` is read from the installed package
metadata at import time in a future milestone; for now keep it in sync by
hand as a third spot if it's ever hardcoded there instead.

## 2. Verify locally

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format --check .
.venv\Scripts\python -m pytest -q
```

All must pass. Don't skip this because CI will also run it — CI catches
mistakes, it shouldn't be the first time you find them.

## 3. Build and smoke-test the installer locally

```powershell
.venv\Scripts\pyinstaller installer\devkitbox.spec --noconfirm
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\devkitbox.iss
```

Run `installer\output\DevKitBox-Setup-<version>.exe`, confirm the app
launches, and uninstall it again (Settings > Apps, or the Start Menu
uninstaller shortcut) before moving on — don't ship a build you haven't
actually run.

## 4. Tag and push

```powershell
git tag v<version>
git push origin v<version>
```

Pushing a `v*.*.*` tag triggers `.github/workflows/release.yml`, which
rebuilds the installer on a clean runner and attaches it to a **draft**
GitHub Release (`softprops/action-gh-release`, `draft: true`) — it does not
publish automatically. Review the draft, edit the release notes if needed,
and publish it manually from the GitHub UI when it's ready.

## 5. After publishing

Nothing else is automated yet — there's no update-check backend for the
app to call (see Settings > Updates), so there's no server-side step here
beyond the GitHub Release itself.
