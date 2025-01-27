from abc import ABC, abstractmethod
from collections import UserDict
from datetime import datetime, timedelta
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass

class Birthday(Field):
    def __init__(self, value):
        if value:
            try:
                datetime.strptime(value, "%d.%m.%Y")
            except ValueError:
                raise ValueError("Birthday must be in format DD.MM.YYYY")
        self.value = value

    def __repr__(self):
        return self.value if self.value else "No birthday"

class Phone(Field):
    def __init__(self, number):
        if not isinstance(number, str) or not number.isdigit() or len(number) != 10:
            raise ValueError("The phone number must be a string of 10 digits")
        super().__init__(number)


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = Birthday(None)

    def add_phone(self, number):
        phone = Phone(number)
        self.phones.append(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def remove_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                self.phones.remove(phone)
                return True
        return False

    def edit_phone(self, old_number, new_number):
        if self.find_phone(old_number):
            self.add_phone(new_number)
            self.remove_phone(old_number)
            return True
        else:
            raise ValueError(f"Old number {old_number} not found")

    def find_phone(self, number):
        for phone in self.phones:
            if phone.value == number:
                return phone
        return None

    def __str__(self):
        birthday_str = f", birthday: {self.birthday.value}" if self.birthday else ""
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}{birthday_str}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name, None)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record with name {name} not found.")

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday and record.birthday.value:
                try:
                    birthday_date = datetime.strptime(record.birthday.value, "%d.%m.%Y")
                except ValueError:
                    continue

                this_year_birthday = birthday_date.replace(year=today.year)

                if this_year_birthday < today:
                    this_year_birthday = this_year_birthday.replace(year=today.year + 1)

                if this_year_birthday.weekday() == 5:
                    this_year_birthday += timedelta(days=2)
                elif this_year_birthday.weekday() == 6:
                    this_year_birthday += timedelta(days=1)
                days_until_birthday = (this_year_birthday - today).days

                if 0 <= days_until_birthday <= 7:
                    upcoming_birthdays.append({
                        "name": record.name.value,
                        "birthday": this_year_birthday.strftime("%d.%m.%Y"),
                    })

        return upcoming_birthdays

    def __str__(self):
        if not self.data:
            return "The address book is empty."
        return "\n".join(str(record) for record in self.data.values())

# Базовий клас View
class View(ABC):
    @abstractmethod
    def show_message(self, message):
        pass

    @abstractmethod
    def get_input(self, prompt):
        pass

    @abstractmethod
    def show_contacts(self, contacts):
        pass


class ConsoleView(View):
    def show_message(self, message):
        print(message)

    def get_input(self, prompt):
        return input(prompt)

    def show_contacts(self, contacts):
        if not contacts:
            print("The address book is empty.")
        else:
            for contact in contacts:
                print(contact)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

# Основна програма
def main():
    book = load_data()
    view = ConsoleView()

    view.show_message("Welcome to the assistant bot!")
    commands_list = {
        "hello": "Greets the user.",
        "add": "Add a new contact or phone number to an existing contact. Usage: add [name] [phone]",
        "change": "Change an existing phone number for a contact. Usage: change [name] [old_phone] [new_phone]",
        "phone": "Show phone numbers of a specific contact. Usage: phone [name]",
        "all": "Display all contacts in the address book.",
        "birthdays": "Show contacts with upcoming birthdays in the next 7 days.",
        "add-birthday": "Add a birthday to a contact. Usage: add-birthday [name] [DD.MM.YYYY]",
        "show-birthday": "Show the birthday of a specific contact. Usage: show-birthday [name]",
        "commands": "Return all available commands.",
        "close/exit": "Save the address book and exit the program."
    }
    while True:
        user_input = view.get_input("Enter a command: ").strip().lower()
        if user_input in ["close", "exit"]:
            save_data(book)
            view.show_message("Good bye!")
            break
        elif user_input == "hello":
            view.show_message("How can I help you?")
        elif user_input == "add":
            name = view.get_input("Enter name: ")
            phone = view.get_input("Enter phone: ")
            record = book.find(name)
            if not record:
                record = Record(name)
                book.add_record(record)
                view.show_message("Contact added.")
            record.add_phone(phone)
            view.show_message("Phone added to the contact.")
        elif user_input == "all":
            view.show_contacts(book.data.values())
        elif user_input == "commands":
            view.show_message("Available commands:")
            for command, description in commands_list.items():
                view.show_message(f"- {command}: {description}")
        else:
            view.show_message("Invalid command.")

if __name__ == "__main__":
    main()
