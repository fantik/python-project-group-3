from collections import UserDict
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich import print
import pickle
import os

console = Console()

FILE_NAME = "addressbook.pkl"

#Serialization
def save_data(book, filename=FILE_NAME):
  with open(filename, "wb") as f:
    pickle.dump(book, f)


def load_data(filename=FILE_NAME):
  if os.path.exists(filename):
    try:
      with open(filename, "rb") as f:
        return pickle.load(f)
    except Exception:
      return AddressBook()
  return AddressBook()

#FIELD
class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

#NAME
class Name(Field):
  def __init__(self,value):
    #checking for empty value
    if value == '' or value is None:
      raise ValueError("Name can't be empty")
    #calling parent Field class to store value
    Field.__init__(self, value)

#PHONE
class Phone(Field):
  def __init__(self, value):
    #checking value length
    if len(value) != 10:
      raise ValueError("[red]Phone must be 10 digits[/red]")
    
    if not value.isdigit():
      raise ValueError("[red]Phone must have only digits[/red]")
    
    Field.__init__(self, value)

#BIRTHDAY
class Birthday(Field):
  def __init__(self, value):
    try:
      parsed_date = datetime.strptime(value, "%d.%m.%Y")
      super().__init__(parsed_date)
    except ValueError:
      raise ValueError("[red]Invalid date format. Use DD.MM.YYYY[/red]")

#RECORD
class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    #simple adding to list
    def add_phone(self, phone):
      self.phones.append(Phone(phone))

    #simple removeing phone from the list
    def remove_phone(self, phone):
      for ph in self.phones:
        if ph.value == phone:
          self.phones.remove(ph)
          return
      raise ValueError('[red]Phone not found[/red]')
    
    #finding old phobe and replace with new one
    def edit_phone(self, old_phone, new_phone):
      for i in range(len(self.phones)):
        if self.phones[i].value == old_phone:
          self.phones[i] = Phone(new_phone)
          return
      raise ValueError("[red]Old phone not found[/red]")
    
    #simple finding phpone
    def find_phone(self, phone):
      for ph in self.phones:
         if ph.value == phone:
            return ph.value
      return ValueError("[red]The phone was not found in the list[/red]")
    
    #Adding birthday
    def add_birthday(self, birthday):
      self.birthday = Birthday(birthday)

    def __str__(self):
        phones = '; '.join(p.value for p in self.phones)
        birthday = (
            self.birthday.value.strftime("%d.%m.%Y")
            if self.birthday else "None"
        )
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"


#ADRESS_BOOK
class AddressBook(UserDict):
  def add_record(self, record):
     self.data[record.name.value] = record

  def find(self, name):
     return self.data.get(name)
  
  def delete(self, name):
    if name in self.data:
      del self.data[name]
    else:
      raise ValueError("[red]Record not found[/red]")
    
  def get_upcoming_birthdays(self):
    results = []
    today = datetime.today().date()

    for record in self.data.values():
      if not record.birthday:
         continue
      # get user day of birth  and replaced with current year
      birthday = record.birthday.value.date()
      birthday_this_year = birthday.replace(year=today.year)


      # compare dates and add aditional one if condition is True 
      if birthday_this_year < today:
        birthday_this_year = birthday.replace(year=today.year + 1)

      # difference betwen dates
      day_difference = (birthday_this_year - today).days
      if 0 <= day_difference <= 7:
        birth_date = birthday_this_year

        # here we add aditional days if it 5 = Saturday or 6 = Sunday
        if birth_date.weekday() == 5:
          birth_date = birth_date.replace(days= +2)
        elif birth_date.weekday() == 6:
          birth_date = birth_date.replace(days= +1)

        results.append({"name": record.name.value, "congratulation_date": birth_date.strftime("%d.%m.%Y")})

    return results
  

#parse input
def parse_input(user_input):
  cmd, *args = user_input.split()
  cmd = cmd.strip().lower()
  return cmd, *args

#Error handler
def input_error(func):
  def wrapper(*args, **kwargs):
    try:
      return func(*args, **kwargs)
    except Exception as e:
      return str(e)
  return wrapper


#add contact
@input_error
def add_contact(args, book):
  name, phone, *_ = args
  record = book.find(name)

  if not record:
    record = Record(name)
    book.add_record(record)
    message = "[green]Contact added.[/green]"
  else:
    message = "[green]Contact updated.[/green]"

  record.add_phone(phone)
  return message


#change contact
@input_error
def change_contact(args, book):

  name, old_phone, new_phone = args
  record = book.find(name)

  if record is None:
    raise KeyError
  
  record.edit_phone(old_phone, new_phone)
  return "[green]Contact changed.[/green]"

#show phone
@input_error
def show_phone(args, book):

  name = args[0]
  record = book.find(name)

  if record is None:
    return "[red]Contact not found[red]"

  phones = "; ".join(phone.value for phone in record.phones)
  return f"[green]The {name.capitalize()}'s phones are:  {phones}[/green]"

#show all
@input_error
def show_all(book):

  if not book.data:
    return "[red]No contacts found[/red]"

  table = Table(title="Contacts")
  table.add_column("Name", style="cyan")
  table.add_column("Phones", style="green")
  table.add_column("Birthday", style="yellow")

  for record in book.data.values():
    phones = "; ".join(phone.value for phone in record.phones)

    birthday = (
      record.birthday.value.strftime("%d.%m.%Y")
      if record.birthday else "-"
    )

    table.add_row(
      record.name.value,
      phones,
      birthday
    )

  console.print(table)

#Add birthday
@input_error
def add_birthday(args, book):

  name, birthday = args
  record = book.find(name)

  if record is None:
    raise KeyError

  record.add_birthday(birthday)
  return "[green]Birthday added.[/green]"

#show birthday
@input_error
def show_birthday(args, book):

  name = args[0]
  record = book.find(name)

  if record is None:
    raise KeyError

  if record.birthday is None:
    return "[red]Birthday not set[/red]"

  return (
    f"[green]{name}'s birthday: [/green]"
    f"[green]{record.birthday.value.strftime('%d.%m.%Y')}[/green]"
  )

#show birthdays
@input_error
def birthdays(book):

  upcoming = book.get_upcoming_birthdays()

  if not upcoming:
    return "[yellow]No upcoming birthdays[/yellow]"

  table = Table(title="Upcoming birthdays")
  table.add_column("Name", style="cyan")
  table.add_column("Congratulations date", style="green")

  for item in upcoming:
    table.add_row(
      item["name"],
      item["congratulation_date"]
    )

  console.print(table)



def main():
  #Load Book Data
  book = load_data()

  commands = {
    "hello": lambda args: "How can I help you?",
    "add": lambda args: add_contact(args, book),
    "change": lambda args: change_contact(args, book),
    "phone": lambda args: show_phone(args, book),
    "all": lambda args: show_all(book),
    "add-birthday": lambda args: add_birthday(args, book),
    "show-birthday": lambda args: show_birthday(args, book),
    "birthdays": lambda args: birthdays(book),
  }

  print("[cyan]Welcome to the assistant bot![/cyan]")

  try:
    while True:
      user_input = input("Enter a command: ")
      command, *args = parse_input(user_input)

      if command in ["close", "exit"]:
        print("[cyan]Good bye![/cyan]")
        break

      handler = commands.get(command)

      if handler:
        result = handler(args)

        if result is not None:
          print(result)

      else:
        print("[red]Invalid command.[/red]")
  finally:
    #Save Book Data
    save_data(book)


if __name__ == "__main__":
  main()
