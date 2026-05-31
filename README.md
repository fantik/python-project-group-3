# 📒 Address Book CLI Assistant

![Python](https://img.shields.io/badge/python-3.10%2B-blue) ![License](https://img.shields.io/badge/license-MIT-green)

A command-line **Personal Assistant application** built with Python.

It provides contact management, birthday tracking, and persistent local storage with a clean terminal interface powered by `rich`.

---

## 🔗 Repository

Clone using HTTPS or SSH:

**HTTPS**

```bash
git clone https://github.com/fantik/python-project-group-3.git
cd python-project-group-3
```

**SSH (recommended)**

```bash
git clone git@github.com:fantik/python-project-group-3.git
cd python-project-group-3
```

---

## 📌 Project Requirements

### 🧠 Core Functional Requirements

The personal assistant must be able to:

1. Store contacts with:
   - Name
   - Address
   - Phone numbers
   - Email
   - Birthday
     in a contact book
2. Display a list of contacts whose birthdays occur within a specified number of days from the current date
3. Validate phone numbers and email addresses during creation or editing and notify the user in case of invalid input
4. Search contacts within the address book
5. Edit and delete contact records
6. Store textual notes
7. Search notes
8. Edit and delete notes

---

## 📊 Project Evaluation Checklist (Core Requirements)

### 📇 Contacts Management

| Requirement                                          | Status |
| ---------------------------------------------------- | ------ |
| Add contacts (name, address, phone, email, birthday) | ✅     |
| Search contacts by criteria (exact match, AND)       | ✅     |
| Edit contacts                                        | ✅     |
| Delete contacts                                      | ✅     |
| Show upcoming birthdays (N days range)               | ✅     |
| Validate phone number and email                      | ✅     |

### 📝 Notes Management

| Requirement                | Status |
| -------------------------- | ------ |
| Add textual notes          | ✅     |
| Search, edit, delete notes | ✅     |

### 💾 Data Persistence

| Requirement                    | Status |
| ------------------------------ | ------ |
| Store all data locally on disk | ✅     |
| Persist data across restarts   | ✅     |

---

## 🚀 Optional Features (Bonus Tasks)

The project can be extended with additional functionality:

1. Add **tags (keywords)** to notes
2. Search and sort notes by tags
3. Suggest the **closest command** when the user mistypes an unknown command

---

## 🏆 Bonus Evaluation Checklist

| Requirement                                      | Status |
| ------------------------------------------------ | ------ |
| Add tags to notes                                | ✅     |
| Search and sort notes by tags                    | ✅     |
| Suggest closest command for unknown input        | ✅     |

---

## 🧱 Tech Stack

- Python 3.10+
- uv
- Rich (CLI UI)
- Sphinx
- Pickle (data serialization)
- OOP architecture (UserDict-based storage)

---

## 📁 Project Structure

```
python-project-group-3/
├── pyproject.toml       # Project metadata and uv dependencies
├── uv.lock              # Locked dependency versions for uv
├── main.py              # CLI entry point
├── contacts.py          # Compatibility re-export for contact models
├── models.py            # Field, Record, AddressBook
├── validators.py        # Shared validation helpers
├── storage.py           # save/load persistence
├── handlers.py          # Command handlers and input parsing
├── tests/               # Automated tests
├── docs/                # Sphinx documentation
├── addressbook.pkl      # Local storage (auto-generated)
├── .gitignore
└── README.md
```

---

## ⚡ Getting Started

### 1. Clone repository

```bash
git clone git@github.com:fantik/python-project-group-3.git
cd python-project-group-3
```

### 2. Install uv

[uv](https://docs.astral.sh/uv/) is a fast Python package and project manager. It supports **macOS**, **Linux**, and **Windows**.

**macOS / Linux (Homebrew)**

Install Homebrew first if needed:
[Homebrew installation guide](https://brew.sh/)

```bash
brew install uv
```

**Windows (Chocolatey)**

Install Chocolatey first if needed:
[Chocolatey installation guide](https://chocolatey.org/install)

```powershell
choco install uv
```

**Windows (WinGet)**

WinGet is the Microsoft package manager for Windows.
If you do not have WinGet yet, see the
[Microsoft WinGet installation guide](https://learn.microsoft.com/en-us/windows/package-manager/winget/).

```powershell
winget install --id=astral-sh.uv -e
```

Then verify:

```bash
uv --version
```

For other installation methods, see the [official installation guide](https://docs.astral.sh/uv/getting-started/installation/).

### 3. Sync dependencies with uv

```bash
uv sync
```

### (Optional) Install developer dependencies

Some commands below (coverage, docs) require extra dependency groups defined in `pyproject.toml`.

```bash
# Coverage tools
uv sync --group dev

# Sphinx docs
uv sync --group docs

# Everything (app + dev + docs)
uv sync --group dev --group docs
```

### 4. Run application

```bash
uv run python main.py
```

### 5. Run tests

```bash
uv run python -m unittest discover -s tests
```

### ⚡ Fast CLI checks (copy/paste)

Quick feedback loops for local development:

```bash
# Run a single test module (fast)
uv run python -m unittest tests.test_validators

# Run one feature test file
uv run python -m unittest tests.test_birthdays_feature

# Run command-guessing tests
uv run python -m unittest tests.test_command_guessing_feature

# Run a subset by filename pattern
uv run python -m unittest discover -s tests -p "test_*feature.py"

# Quiet output (less noise)
uv run python -m unittest -q discover -s tests
```

### 6. Check test coverage

```bash
uv run python -m coverage run -m unittest discover -s tests
uv run python -m coverage report -m
```

To generate an HTML report:

```bash
uv run python -m coverage html
```

Then open:

```text
htmlcov/index.html
```

### 7. Build Sphinx documentation

```bash
uv sync --group docs
LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8 uv run --group docs sphinx-build -b html docs/source docs/build/html
```

Or (faster to type) from repo root:

```bash
make -C docs html
```

To clean the docs build:

```bash
make -C docs clean
```

After the build finishes, open:

```text
docs/build/html/index.html
```

---

## 🌿 Git Workflow

### Branch strategy

- `main` → stable production code
- `feature-{taskname}` → development branches

### Create feature branch

```bash
git checkout main
git pull origin main
git checkout -b feature-{taskname}
```

### Push changes

```bash
git push origin feature-{taskname}
```

Then create a Pull Request into `main`.

---

## 🧠 Available Commands

### General

| Command        | Description |
| -------------- | ----------- |
| `hello`        | Greeting    |
| `help`         | Show help   |
| `exit`/`close` | Exit app    |

When you mistype a command, the assistant suggests the closest match:

| Input   | Suggestion |
| ------- | ---------- |
| `serch` | `search`   |
| `hepl`  | `help`     |
| `add-not Olga buy milk` | `add-note` |
| `xyz`   | no match — shows `Type 'help' to see usage.` |

The suggestion is shown only; enter the correct command manually to run it.

### Contacts

| Command        | Example                                 |
| -------------- | --------------------------------------- |
| `add`          | `add "Vasilij Olexandrovich Melnik" 0500000000`                   |
| `add-address`  | `add-address "Vasilij Olexandrovich Melnik" Petržílkova 2583/15, 158 00 Praha 13-Stodůlky`    |
| `add-email`    | `add-email "Vasilij Olexandrovich Melnik" vasilij.melnik@example.com`       |
| `search`       | `search "mar" - - "street"`                    |
| `edit-contact` | `edit-contact "Vasilij Olexandrovich Melnik" email vasilij.olexandrovich.melnik@gmail.com` |
| `remove-contact` | `remove-contact "Vasilij Olexandrovich Melnik"` |
| `phone`        | `phone "Vasilij Olexandrovich Melnik"`                            |
| `show-contact` | `show-contact "Vasilij Olexandrovich Melnik"`                     |
| `all`          | Show all contacts                       |

### Search contacts (`search`)

Find contacts by **partial match (contains)** in two ways:

- **Partial match**: searches by “contains” (case-insensitive) for name/email/address, and by substring for phone.
- **Global query (recommended)**: `search <query>` matches when **any field** contains the query (OR logic).
- **Advanced filter**: positional arguments use **AND logic** (a contact must match **all** provided criteria).

#### Quick usage

```text
search <query>
search <name|-> <phone|-> <email|-> <address|->
```

#### Arguments (positional)

| Position | Meaning   | How to skip | Notes |
| -------- | --------- | ----------- | ----- |
| 1        | name      | `-`         | Use quotes for multi-word names |
| 2        | phone     | `-`         | Substring match (e.g. `1234`) |
| 3        | email     | `-`         | Substring match (e.g. `@gmail`) |
| 4        | address   | `-`         | Use quotes for multi-word addresses |

#### Examples

```text
# Global query (search in name/phones/email/address/notes/tags)
search @gmail.com
search shopping

# Search by name only
search "Mary Jane" - - -

# Search by phone only (skip name/email/address)
search - 0671234567 - -

# Phone in international format (still works)
search - +380731234567 - -

# Search by email only
search - - mary.jane@example.com -

# Search by address only (quote multi-word address)
search - - - "Petržílkova 2583/15, 158 00 Praha 13-Stodůlky"

# AND search (name AND email)
search "Mary Jane" - mary.jane@example.com -

# AND search across all fields
search "Mary Jane" 0671234567 mary.jane@example.com "Main Street 10, Kyiv"

# More flexible partial search (case-insensitive)
search "mar" - - "street"

# Phone substring search
search - 1234 - -

```

### Birthdays

| Command         | Example                        |
| --------------- | ------------------------------ |
| `add-birthday`  | `add-birthday "Vasilij Olexandrovich Melnik" 06.09.1996` |
| `show-birthday` | `show-birthday "Vasilij Olexandrovich Melnik"`           |
| `birthdays`     | `birthdays` or `birthdays 14`  |

### Notes and tags

Notes belong to a contact. Each note gets a numeric **id** (1, 2, 3…) within that contact.
Create a note first, then attach tags with `#` syntax.

**Limits**

| Limit | Value |
| ----- | ----- |
| Notes per contact | 5 |
| Tags per note | 5 |
| Note text length | 3–100 characters |
| Tag length | 3–20 characters (`a-z`, `0-9`, `_`, `-`) |

**Workflow**

```text
add-note Olga buy coffee
add-tag Olga 1 #shopping #urgent
all-notes Olga
edit-note Olga 1 buy oat milk
remove-tag Olga 1 #urgent
find-notes-by-tag Olga #shop
sort-notes-by-tag Olga
remove-note Olga 1
```

| Command               | Example |
| --------------------- | ------- |
| `add-note`            | `add-note "Mary Jane" buy milk` |
| `edit-note`           | `edit-note Olga 1 buy oat milk` |
| `remove-note`         | `remove-note Olga 1` |
| `find-note`           | `find-note Olga milk` |
| `all-notes`           | `all-notes Olga` |
| `add-tag`             | `add-tag Olga 1 #shopping #urgent` |
| `remove-tag`          | `remove-tag Olga 1 #shopping` |
| `find-notes-by-tag`   | `find-notes-by-tag Olga #shop` |
| `sort-notes-by-tag`   | `sort-notes-by-tag Olga` |

- `edit-note` and `remove-note` work **by note id only** (not by note text).
- Tags in CLI must start with `#` (`add-tag`, `remove-tag`).
- `find-notes-by-tag` supports partial match (`#shop` matches `#shopping`).
- `sort-notes-by-tag` shows tagged notes first (A→Z by first tag), then untagged notes.
- `search <query>` also matches note text and tags.
- `all-notes` / `find-note` tables show columns: **ID**, **Note**, **Tags**.

### Edit contact (`edit-contact`)

Update any contact field in one command. All values are validated through `validators.py`.

| Field      | Example                                              |
| ---------- | ---------------------------------------------------- |
| `name`     | `edit-contact "Vasilij Olexandrovich Melnik" name "Vasilij Melnik"`                    |
| `email`    | `edit-contact "Vasilij Olexandrovich Melnik" email vasilij.olexandrovich.melnik@gmail.com`      |
| `address`  | `edit-contact "Vasilij Olexandrovich Melnik" address Anny Letenské 1197/3, 120 00, Praha 2 - Vinohrady` |
| `phone`    | `edit-contact "Vasilij Olexandrovich Melnik" phone 0500000000 +380733664142`      |
| `birthday` | `edit-contact "Vasilij Olexandrovich Melnik" birthday 09.06.1996`              |

- **Name** must contain at least 2 letters. Multi-word names are supported.
- **Phone** requires the old and new numbers (same rules as `change`).
- If the contact does not exist, the bot shows `[red]Contact not found[/red]`.

---

## 🎂 Birthday Logic

- Stored format: `DD.MM.YYYY`
- Upcoming range: 7 days
- Weekend adjustment:
  - Saturday → Monday (+2 days)
  - Sunday → Monday (+1 day)

---

## 💾 Data Storage

All data is automatically saved to:

```
addressbook.pkl
```

- Loaded on startup
- Saved on exit

---

## 🧪 Example Usage

```
Enter a command: add "Vasilij Olexandrovich Melnik" 0500000000
Contact added.

Enter a command: add-birthday "Vasilij Olexandrovich Melnik" 06.09.1996
Birthday added.

Enter a command: show-contact "Vasilij Olexandrovich Melnik"

Enter a command: search "Vasilij Olexandrovich Melnik" - - -

Enter a command: search - 0500000000 - -

Enter a command: edit-contact "Vasilij Olexandrovich Melnik" email vasilij.olexandrovich.melnik@gmail.com
Email updated.
```
