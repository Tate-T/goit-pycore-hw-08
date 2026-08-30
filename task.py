
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


class Phone(Field):
    def __init__(self, value):
        if not self.validate_phone(value):
            raise ValueError("Phone number must contain exactly 10 digits")

        super().__init__(value)

    @staticmethod
    def validate_phone(value):
        return value.isdigit() and len(value) == 10


class Birthday(Field):
    def __init__(self, value):
        try:
            birthday_date = datetime.strptime(value, "%d.%m.%Y")
            super().__init__(birthday_date)
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

    def __str__(self):
        return self.value.strftime("%d.%m.%Y")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        for current_phone in self.phones:
            if current_phone.value == phone:
                self.phones.remove(current_phone)
                return

        raise ValueError("Phone number not found")

    def edit_phone(self, old_phone, new_phone):
        for current_phone in self.phones:
            if current_phone.value == old_phone:
                current_phone.value = Phone(new_phone).value
                return

        raise ValueError("Phone number not found")

    def find_phone(self, phone):
        for current_phone in self.phones:
            if current_phone.value == phone:
                return current_phone

        return None

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        birthday = f", birthday: {self.birthday}" if self.birthday else ""

        return (
            f"Contact name: {self.name.value}, "
            f"phones: {'; '.join(phone.value for phone in self.phones)}"
            f"{birthday}"
        )

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            birthday = record.birthday.value.date()

            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1
                )

            if today <= birthday_this_year <= today + timedelta(days=7):
                checking_weekday = birthday_this_year.weekday()

                if checking_weekday == 5:  
                    birthday_this_year += timedelta(days=2)

                elif checking_weekday == 6:  
                    birthday_this_year += timedelta(days=1)

                upcoming_birthdays.append(
                    {
                        "name": record.name.value,
                        "congratulation_date": birthday_this_year.strftime(
                            "%d.%m.%Y"
                        ),
                    }
                )

        return upcoming_birthdays

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)

        except ValueError as error:
            return str(error)

        except KeyError:
            return "Contact not found."

        except IndexError:
            return "Give me command arguments please."

    return inner

def parse_input(user_input: str):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()

    return cmd, args

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args[:2]

    record = book.find(name)
    is_new_record = record is None

    message = "added" if is_new_record else "updated"

    if is_new_record:
        record = Record(name)
        book.add_record(record)

    record.add_phone(phone)

    return f"Contact {message}."


@input_error
def change_contact(args, book: AddressBook):
    name, old_phone, new_phone = args[:3]

    record = book.find(name)

    if record is None:
        return (
            f'Contact "{name}" not found. '
            'If you want to add a new contact, use the "add" command.'
        )

    record.edit_phone(old_phone, new_phone)

    return "Contact updated."


@input_error
def show_phone(args, book: AddressBook):
    name = args[0]

    record = book.find(name)

    if record is None:
        return f'Contact "{name}" not found.'

    return ", ".join(str(phone) for phone in record.phones)


@input_error
def show_all(book: AddressBook):
    if not book.data:
        return "Address book is empty."

    return "\n".join(str(record) for record in book.values())


@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args[:2]

    record = book.find(name)

    if record is None:
        return f'Contact "{name}" not found.'

    record.add_birthday(birthday)

    return "Contact updated."


@input_error
def show_birthday(args, book: AddressBook):
    name = args[0]

    record = book.find(name)

    if record is None:
        return "Contact not found."

    if record.birthday is None:
        return f'Contact "{name}" does not have a birthday.'

    return f'Birthday of "{record.name}": {record.birthday}'


def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()

    if not upcoming_birthdays:
        return "No upcoming birthdays."

    result = []

    for birthday in upcoming_birthdays:
        result.append(
            f"{birthday['name']}: "
            f"{birthday['congratulation_date']}"
        )

    return "\n".join(result)


def help():
    commands = [
        "help",
        "hello",
        "add {name} {phone}",
        "change {name} {old_phone} {new_phone}",
        "phone {name}",
        "show {name}",
        "add-birthday {name} {birthday}",
        "show-birthday {name}",
        "birthdays",
        "all",
        "close",
        "exit",
    ]

    return "Available commands:\n  " + "\n  ".join(commands)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as file:
        pickle.dump(book, file)


def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as file:
            return pickle.load(file)

    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()

    print("Welcome to the assistant bot!")

    while True:
        user_input = input("Enter a command: ").strip()

        if not user_input:
            print("Enter a command please.")
            continue

        command, args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command in ["show", "phone"]:
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            print(birthdays(book))

        elif command == "help":
            print(help())

        else:
            print(
                'Invalid command. '
                'Type "help" to see the list of available commands.'
            )


if __name__ == "__main__":
    main()