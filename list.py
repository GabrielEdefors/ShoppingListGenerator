from pathlib import Path
from enum import Enum
from datetime import datetime
import collections
import store
import smtplib
from email.message import EmailMessage


class Location(Enum):
    Hogsbo = 1


class StoreName(Enum):
    ICA_Maxi = 1


class List:

    def __init__(self, store):
        self.store = store
        self.date = datetime.today().strftime('%Y-%m-%d')

        self.name = 'SHOPPING LIST ' + str(self.date) + ' ' + store
        self.output_path = Path.cwd().joinpath('output', self.name + '.txt')

        # Create categories from departments
        self.categories = []
        for department in store.departments:
            self.categories.append(Category(department))

    def __str__(self):
        return self.name + ' - ' + self.store.name + ' ' + self.store.location

    def sort_items(self):
        self.categories.sort(key=lambda x: x.position)
        for category in self.categories:
            category.sort_items()

    def print_list(self):
        page_width = 50
        with open(self.output_path, 'w') as file:
            self.print_section(file, page_width, str(self))
            file.write('\n')
            for category in self.categories:

                if category.items.items():
                    # Section header
                    self.print_section(file, page_width, str(category.name).capitalize())

                    # Items
                    for item, amount in category.items.items():
                        column_string = self.format_columns([item.article.capitalize(), str(amount)])
                        file.write(column_string)

                    file.write('\n')
                else:
                    continue

    def send_email(self, user_email, user_password, receiver_email):

        msg = EmailMessage()
        msg['Subject'] = str(self)
        msg['From'] = user_email
        msg['To'] = receiver_email
        msg.add_attachment(open(self.output_path, "r").read(), filename=str(self) + 'txt')

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:

            try:
                smtp.login(user_email, user_password)
            except smtplib.SMTPException:
                print('Could not log in')

            smtp.send_message(msg)




    @staticmethod
    def print_section(file, page_width, section_text):
        file.write('=' * page_width + '\n' + section_text + '\n' + '=' * page_width + '\n')

    @staticmethod
    def format_columns(items):
        column_width = 25
        column_string = ''
        for i, item in enumerate(items):
            if i < 2:
                column_string += f'{item:<{column_width}}'
            else:
                column_string += f'{item:<{5}}'
        return column_string + '\n'


class Category:

    def __init__(self, department):
        self.name = department.name
        self.position = department.position
        self.items = collections.defaultdict(float)

    def add_item(self, item: store.StoreItem, note):
        self.items[item] = note

    def sort_items(self):
        self.items = {k: v for k, v in sorted(self.items.items(), key=lambda item: item[0].position)}
