import pickle
from collections import UserDict
from datetime import datetime, timedelta
from pathlib import Path


file_path = Path('database.bin')


class Field:
    def __init__(self, value):
        self.value = value  # Ініціалізація значення поля.

    def __str__(self):
        return str(self.value)  # Повернення значення поля у вигляді рядка.


class Name(Field):
    pass  # Пустий клас, який успадковується від Field.


class Phone(Field):
    def __init__(self, value):
        self.__value = None  # Приватне поле для зберігання номера телефону.
        self.value = value  # Встановлення значення через setter.

    @property
    def value(self):
        return self.__value  # Getter для значення номера телефону.

    @value.setter
    def value(self, value):
        if len(value) == 10 and value.isdigit():  # Перевірка на правильний формат номера телефону.
            self.__value = value
        else:
            raise ValueError("Invalid phone format")  # Виняток, якщо формат неправильний.


class Birthday(Field):
    def __init__(self, value):
        date_format = "%d.%m.%Y"  # Формат дати.
        try:
            self.date = datetime.strptime(value, date_format).date()  # Парсинг дати.
            super().__init__(value)  # Виклик конструктора батьківського класу.
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")  # Виняток при неправильному форматі дати.


class Record:
    def __init__(self, name):
        self.name = Name(name)  # Ім'я контакту.
        self.phones = []  # Список номерів телефону.
        self.birthday = None  # День народження.

    def add_phone(self, phone_number):
        self.phones.append(Phone(phone_number))  # Додавання номера телефону.

    def remove_phone(self, phone_number):
        self.phones = [p for p in self.phones if str(p) != phone_number]  # Видалення номера телефону.

    def edit_phone(self, old_number, new_number):
        for phone in self.phones:
            if str(phone) == old_number:
                phone.value = new_number  # Зміна номера телефону.
                return
        raise ValueError("Phone number not found")  # Виняток, якщо номер не знайдено.

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)  # Додавання дня народження.

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(p.value for p in self.phones)}"  # Повернення рядка з інформацією про контакт.


class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record  # Додавання запису в адресну книгу.

    def find(self, name):
        return self.data.get(name)  # Пошук запису за ім'ям.

    def delete(self, name):
        if name in self.data:
            del self.data[name]  # Видалення запису з адресної книги.

    @staticmethod
    def find_next_weekday(d, weekday):
        """
        Функція для знаходження наступного заданого дня тижня після заданої дати.
        d: datetime.date - початкова дата.
        weekday: int - день тижня від 0 (понеділок) до 6 (неділя).
        """
        days_ahead = weekday - d.weekday()  # Різниця між поточним днем тижня та бажаним днем тижня.
        if days_ahead <= 0:  # Якщо день народження вже минув у цьому тижні.
            days_ahead += 7
        return d + timedelta(days_ahead)  # Повернення дати наступного заданого дня тижня.

    def get_upcoming_birthdays(self, days=7) -> list:
        today = datetime.today().date()  # Поточна дата.
        upcoming_birthdays = []

        for user in self.data.values():
            if user.birthday is None:
                continue
            birthday_this_year = user.birthday.date.replace(year=today.year)  # Дата народження в поточному році.

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(
                    year=today.year + 1)  # Дата народження в наступному році.

            if 0 <= (birthday_this_year - today).days <= days:
                if birthday_this_year.weekday() >= 5:  # субота або неділя
                    birthday_this_year = self.find_next_weekday(
                        birthday_this_year, 0
                    )  # Понеділок

                congratulation_date_str = birthday_this_year.strftime("%Y.%m.%d")
                upcoming_birthdays.append(
                    {
                        "name": user.name.value,
                        "congratulation_date": congratulation_date_str,
                    }
                )

        return upcoming_birthdays  # Повернення списку наближених днів народження.


def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            return "Name not found. Please, check and try again."  # Повідомлення при відсутності запису з таким ім'ям.
        except ValueError as e:
            return e  # Повідомлення про помилку введення.
        except IndexError:
            return "Enter correct information."  # Повідомлення про неправильну інформацію.

    return inner


@input_error
def add_contact(args, book: AddressBook):
    name, phone, *_ = args  # Витягуємо ім'я та номер телефону з аргументів функції.
    record = book.find(name)  # Пошук запису з вказаним ім'ям в адресній книзі.
    message = "Contact updated."  # Повідомлення за замовчуванням для випадку, коли контакт буде оновлено.

    if record is None:   # Якщо запис не знайдено, створюємо новий і додаємо його до адресної книги.
        record = Record(name)
        book.add_record(record)
        message = "Contact added."

    if phone:  # Якщо вказаний номер телефону, додаємо його до контакту.
        record.add_phone(phone)

    return message  # Повертаємо повідомлення про успішне додавання або оновлення контакту.


@input_error
def change_contact(args, book):
    name, old_phone, new_phone, *_ = args  # Витягуємо ім'я, старий та новий номер телефону з аргументів функції.
    record = book.find(name)  # Пошук запису з вказаним ім'ям в адресній книзі.
    if record:  # Якщо знайдено відповідний запис, змінюємо номер телефону.
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."
    else:
        raise KeyError  # Виняток, якщо запис з вказаним ім'ям не знайдено.


@input_error
def show_phone(args, book):
    (name,) = args
    record = book.find(name)
    if record:
        return "; ".join([str(phone) for phone in record.phones])  # Повернення номерів телефону для вказаного контакту.
    else:
        raise KeyError


def show_all(book):
    return "\n".join([str(record) for record in book.data.values()])  # Повернення рядка з усією інформацією про всі контакти.


def parse_input(user_input):
    cmd, *args = user_input.split()  # Розбиваємо введений рядок на команду та аргументи.
    cmd = cmd.strip().lower()  # Перетворюємо команду у нижній регістр і видаляємо зайві пробіли.
    return cmd, *args  # Повертаємо команду та аргументи.


@input_error
def add_birthday(args, book):
    # Витягуємо ім'я та день народження з аргументів функції.
    name = args[0]
    birthday = args[1]
    # Пошук запису з вказаним ім'ям в адресній книзі.
    record = book.find(name)
    # Якщо знайдено відповідний запис, додаємо день народження.
    if record:
        record.add_birthday(birthday)
        return "Birthday added."
    else:
        raise KeyError  # Виняток, якщо запис з вказаним ім'ям не знайдено.


@input_error
def show_birthday(args, book):
    (name,) = args  # Витягуємо ім'я з аргументів функції.
    # Пошук запису з вказаним ім'ям в адресній книзі.
    record = book.find(name)
    # Повернення рядка з датою народження для вказаного контакту.
    return str(record.birthday)


def load_data():
    if file_path.is_file():
        with open(file_path, 'rb') as file:
            return pickle.load(file)
    else:
        return AddressBook()


def save_data(data_book):
    with open(file_path, 'wb') as file:
        pickle.dump(data_book, file)


def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            save_data(book)  # Call save_data function to serialize and save data
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))

        elif command == "show-birthday":
            print(show_birthday(args, book))

        elif command == "birthdays":
            birthdays = book.get_upcoming_birthdays()
            if not len(birthdays):
                print("There are no upcoming birthdays.")
                continue
            for day in birthdays:
                print(f"{day}")

        else:
            print("Invalid command.")



if __name__ == "__main__":
    main()











