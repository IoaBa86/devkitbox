# DevKitBox

**Your Developer Toolbox for Windows**

DevKitBox is a local-first desktop toolbox for Windows containing the everyday
utilities developers reach for: JSON formatting, JWT decoding, Base64,
hashing, UUIDs, timestamp conversion, regex testing, and more — all running
natively, offline, with no account and no telemetry.

Website: https://devkitbox.net

> **Status:** in active development. This README reflects the current state
> of the project and is updated as milestones land — see the roadmap below.

## Why DevKitBox

- **Local-first.** Your data stays on your device. Nothing is uploaded unless
  you explicitly use a feature that requires the network (the API Client).
- **No account.** Launch it and use it.
- **No telemetry.** DevKitBox does not collect usage analytics.
- **Fast.** A native Qt desktop app, not a browser wrapped in a shell.

## Features (current)

- Application shell: collapsible sidebar, global search, command palette
  (Ctrl+K), routed pages, status bar
- Home dashboard: quick tools, recently used, categories
- Favorites and recently-used tracking (local SQLite)
- Light / Dark / System theming with an accent color picker
- Settings: Appearance, Network, Privacy, Updates, About
- One-time first-run welcome dialog
- Tool registry architecture — adding a new tool doesn't require touching
  the shell
- **JSON Formatter** — format, minify, validate, load/drop `.json` files
- **Base64** — text and URL-safe encode/decode, file ↔ Base64
- **UUID Generator** — v1/v4/v5, bulk generation, format options
- **Timestamp Converter** — Unix seconds/ms, UTC, local, ISO 8601
- **JWT Decoder** — header/payload/signature inspection
- **Hash Generator** — MD5/SHA family for text and files
- **Regex Tester** — live match highlighting and groups
- **URL Tools** — encode/decode, parse/build
- **Password Generator** — random passwords and passphrases, strength meter
- **Case Converter** — camelCase, snake_case, kebab-case, and more
- **Line Tools** — sort, dedupe, trim, reverse, shuffle, number
- **Text Statistics** — characters, words, lines, reading time
- **Whitespace Cleaner** — normalize line endings, trim, collapse, tabs/spaces
- **File Information** — size, MIME type, timestamps, MD5/SHA-256
- **Text Compare** — line-level diff with similarity score
- **Markdown Preview** — live render with table of contents
- **Random Test Data** — mock records as JSON or CSV
- **API Client** — send HTTP requests, inspect responses (network only on Send)
- **Color Picker/Converter** — HEX/RGB/HSL/HSV, WCAG contrast checker
- **Number Base Converter** — binary/octal/decimal/hex, 32-bit view
- **Data Converter** — JSON, YAML, and CSV, converted between each other
- **Cron Expression Explainer** — plain-English description, next 10 run times
- **XML Formatter** — format, validate, and minify
- **Unit Converter** — data size (decimal and binary) and time durations
- **Image Base64** — preview a Base64/data-URI image, or encode a local file
- **QR Code Generator** — encode text/URLs, save as PNG, entirely offline
- **IP/Subnet Calculator** — CIDR math for IPv4 and IPv6
- **HTML Entity Encoder/Decoder** — escape/unescape `&amp;`, `&lt;`, `&quot;`, etc.
- **Lorem Ipsum Generator** — placeholder text by words, sentences, or paragraphs
- **User-Agent Parser** — browser, OS, and device breakdown from a UA string
- **SQL Formatter** — pretty-print or minify SQL statements
- **Certificate Decoder** — inspect a PEM X.509 certificate: subject, issuer,
  validity, SANs, fingerprint
- **JWT Encoder** — build an HS256/384/512-signed test token from claims
- **Timezone Converter** — convert a date/time across common zones side-by-side
- **.env Parser/Validator** — flag duplicate keys, empty values, missing keys
- **Cookie Parser** — parse a Set-Cookie response header or a Cookie request header

See [Roadmap](#roadmap) for what's left.

## Installation

No published release yet — build the installer yourself (see
[Building the installer](#building-the-installer)), or run from source.

## Development setup

Requires Python 3.12+ (developed against 3.13) on Windows.

```powershell
py -3.13 -m venv .venv
.venv\Scripts\pip install -e ".[dev]"
```

Run the app:

```powershell
.venv\Scripts\python -m app.main
```

Run tests:

```powershell
.venv\Scripts\python -m pytest
```

Lint and format:

```powershell
.venv\Scripts\python -m ruff check .
.venv\Scripts\python -m ruff format .
```

## Architecture

DevKitBox separates concerns into four layers:

- `app/core` — startup, paths, logging, config, exceptions
- `app/models` — plain data models (settings, tool metadata)
- `app/services` — SQLite access, settings, favorites/history, clipboard
- `app/ui` — the Qt shell: main window, theme, widgets, pages
- `app/tools` — the tool registry and individual tool implementations

Tools are self-contained: each exposes `ToolMetadata` (id, name, category,
keywords) and a `ToolWidget` subclass. The shell discovers tools through the
registry — it never hard-codes a tool list. See
[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## Building the installer

Requires [Inno Setup 6](https://jrsoftware.org/isinfo.php) in addition to the
dev setup above.

```powershell
.venv\Scripts\pip install -e ".[dev]"
.venv\Scripts\pyinstaller installer\devkitbox.spec --noconfirm
& "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\devkitbox.iss
```

This produces a onedir PyInstaller build at `dist\DevKitBox\` and a signed-
ready installer at `installer\output\DevKitBox-Setup-<version>.exe`. The
installer is a per-user install (no admin required); DevKitBox's SQLite
database and logs always live under `%LOCALAPPDATA%\DevKitBox`, independent
of where the app itself is installed, so uninstalling never touches your
data unless you delete that folder yourself.

For the full version-bump-to-published-release checklist, and how
`.github/workflows/release.yml` fits in, see
[docs/RELEASING.md](docs/RELEASING.md).

`app/core/paths.py::get_resource_root()` is what makes bundled assets
(`assets/icons/app_icon.svg`, used at runtime) resolve correctly both from
source and from a frozen build — it switches on `sys.frozen`/`sys._MEIPASS`
rather than assuming a source-relative `__file__` layout.

## Privacy

- Local tools never transmit their input or output.
- The API Client makes a network request only when you press Send.
- Tool-content history and clipboard history are off by default and can be
  enabled per-feature in Settings > Privacy.
- No telemetry, no analytics, no background network calls.

## Testing

400+ tests: pure-logic unit tests for every tool, widget-level integration
tests exercising real button/signal wiring for every tool (the layer that
caught real bugs — clipped table text, a stranded form label, an unhandled
QR-encoder exception), plus the database layer, settings persistence, and
the tool registry. Run with `pytest`.

## Roadmap

- [x] Milestone 1 — Foundation (shell, theme, navigation, registry, settings)
- [x] Milestone 2 — Core tools: JSON Formatter, Base64, UUID, Timestamp
- [x] Milestone 3 — JWT Decoder, Hash Generator, Regex Tester, URL tools
- [x] Milestone 4 — Text tools: case conversion, statistics, line tools,
      whitespace cleaner, Markdown preview
- [x] Milestone 5 — Password Generator, Random Test Data, File Information,
      Text Compare
- [x] Milestone 6 — API Client
- [x] Milestone 7 — Command palette, keyboard shortcuts, full privacy
      controls, first-run experience
- [x] Milestone 7.5 — Color Picker/Converter, Number Base Converter,
      Data Converter (JSON/YAML/CSV), Cron Expression Explainer
- [x] Milestone 7.6 — XML Formatter, Unit Converter, Image Base64,
      QR Code Generator, IP/Subnet Calculator, HTML Entity Encoder/Decoder,
      Lorem Ipsum Generator, User-Agent Parser, SQL Formatter,
      Certificate Decoder
- [x] Milestone 7.7 — JWT Encoder, Timezone Converter, .env Parser/Validator,
      Cookie Parser
- [x] Milestone 8 — QA, security review, performance pass
- [x] Milestone 9 — PyInstaller packaging + Inno Setup installer
- [x] Milestone 10 — Documentation, GitHub Actions, release process

## Contributing

Not currently open for external contributions. See
[CONTRIBUTING.md](CONTRIBUTING.md) for dev setup, code style, and testing
expectations, and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for how the
codebase fits together.

## License

MIT — see [LICENSE](LICENSE).
