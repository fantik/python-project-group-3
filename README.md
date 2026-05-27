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
| Search contacts by criteria (exact name)             | ✅     |
| Edit contacts                                        | ✅     |
| Delete contacts                                      | ✅     |
| Show upcoming birthdays (N days range)               | ✅     |
| Validate phone number and email                      | ✅     |

### 📝 Notes Management

| Requirement                | Status |
| -------------------------- | ------ |
| Add textual notes          | ❌     |
| Search, edit, delete notes | ❌     |

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

---

## 🏆 Bonus Evaluation Checklist

| Requirement                   | Status |
| ----------------------------- | ------ |
| Add tags to notes             | ❌     |
| Search and sort notes by tags | ❌     |

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

### 4. Run application

```bash
uv run python main.py
```

### 5. Run tests

```bash
uv run python -m unittest discover -s tests
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
| `exit`/`close` | Exit app    |

### Contacts

| Command        | Example                                 |
| -------------- | --------------------------------------- |
| `add`          | `add "Vasilij Olexandrovich Melnik" 0500000000`                   |
| `add-address`  | `add-address "Vasilij Olexandrovich Melnik" Petržílkova 2583/15, 158 00 Praha 13-Stodůlky`    |
| `add-email`    | `add-email "Vasilij Olexandrovich Melnik" vasilij.melnik@example.com`       |
| `edit-contact` | `edit-contact "Vasilij Olexandrovich Melnik" email vasilij.olexandrovich.melnik@gmail.com` |
| `remove-contact` | `remove-contact "Vasilij Olexandrovich Melnik"` |
| `phone`        | `phone "Vasilij Olexandrovich Melnik"`                            |
| `show-contact` | `show-contact "Vasilij Olexandrovich Melnik"`                     |
| `all`          | Show all contacts                       |

### Birthdays

| Command         | Example                        |
| --------------- | ------------------------------ |
| `add-birthday`  | `add-birthday "Vasilij Olexandrovich Melnik" 06.09.1996` |
| `show-birthday` | `show-birthday "Vasilij Olexandrovich Melnik"`           |
| `birthdays`     | `birthdays` or `birthdays 14`  |

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

Enter a command: edit-contact "Vasilij Olexandrovich Melnik" email vasilij.olexandrovich.melnik@gmail.com
Email updated.
```
