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
| Add contacts (name, address, phone, email, birthday) | ❌     |
| Search contacts by criteria (e.g. name)              | ❌     |
| Edit and delete contacts                             | ❌     |
| Show upcoming birthdays (N days range)               | ❌     |
| Validate phone number and email                      | ❌     |

### 📝 Notes Management

| Requirement                | Status |
| -------------------------- | ------ |
| Add textual notes          | ❌     |
| Search, edit, delete notes | ❌     |

### 💾 Data Persistence

| Requirement                    | Status |
| ------------------------------ | ------ |
| Store all data locally on disk | ❌     |
| Persist data across restarts   | ❌     |

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
- Rich (CLI UI)
- Pickle (data serialization)
- OOP architecture (UserDict-based storage)

---

## 📁 Project Structure

```
python-project-group-3/
├── main.py              # CLI entry point
├── models.py            # Field, Record, AddressBook
├── storage.py           # save/load persistence
├── handlers.py          # Command handlers and input parsing
├── requirements.txt     # Dependencies
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

### 2. Create virtual environment

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run application

```bash
python3 main.py
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

| Command  | Example                             |
| -------- | ----------------------------------- |
| `add`    | `add John 1234567890`               |
| `change` | `change John 1234567890 0987654321` |
| `phone`  | `phone John`                        |
| `all`    | Show all contacts                   |

### Birthdays

| Command         | Example                        |
| --------------- | ------------------------------ |
| `add-birthday`  | `add-birthday John 01.01.2000` |
| `show-birthday` | `show-birthday John`           |
| `birthdays`     | Show upcoming birthdays        |

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
Enter a command: add John 1234567890
Contact added.

Enter a command: add-birthday John 01.01.2000
Birthday added.

Enter a command: birthdays
```
