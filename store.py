from pathlib import Path
from enum import Enum
import collections
import ntpath
import os
import csv


class Location(Enum):
    Hogsbo = 1


class StoreName(Enum):
    ICA_Maxi = 1


class StorageUnit(Enum):
    kg = 1
    st = 2
    liter = 3
    gram = 4


class Store:

    def __init__(self, name: StoreName, location: Location):
        self.name = name
        self.location = location
        self.data_path = Path.cwd().joinpath('database', self.name.name + '_' + self.location.name)

        # Read the departments for the specific store
        self.departments = []
        self.add_departments()

    def add_departments(self):
        for _, path in enumerate(os.scandir(self.data_path)):
            _, department = ntpath.split(path)
            position, name = department.split('_')
            department = Department(name.replace('.csv', ''), (int(position)-1))

            with open(path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=';')

                for i, row in enumerate(csv_reader):

                    article = row[0]
                    unit = StorageUnit.st

                    item = StoreItem(article, unit, i)

                    # Add items to current department
                    department.add_item(item)

                # Add department to store
                self.departments.append(department)

        # Finally sort the departments
        self.departments.sort(key=lambda x: x.position)

    def print_store(self):

        print('\n')
        for department in self.departments:

            # Section header
            print(str(department.name))

            # Items
            for item, amount in department.items.items():
                print(item.article.capitalize(), item.unit)

            print('\n')

    def add_item(self, new_article, next_to):

        found = False
        for _, path in enumerate(os.scandir(self.data_path)):
            _, department = ntpath.split(path)

            with open(path, 'r') as file:
                csv_reader = csv.reader(file, delimiter=';')

                for i, row in enumerate(csv_reader):
                    article = row[0]
                    if article == next_to:
                        new_item_index = i + 1
                        found = True
                        break
            if found:
                break

        if not found:
            sucess = False
        else:

            # Read the current list
            new_department_list = []
            with open(path, 'r') as file:
                csv_reader = csv.reader(file)
                for i, row in enumerate(csv_reader):
                    new_department_list.append(row[0])

            # Insert new item
            new_department_list.insert(new_item_index, new_article)

            # Write to csv again
            with open(path, "w") as outfile:
                for row in new_department_list:
                    outfile.write(row + '\n')

            # Read in the departments again
            self.departments = []
            self.add_departments()
            sucess = True

        return sucess

class StoreItem:

    def __init__(self, article, unit, position):
        self.article = article
        self.unit = unit
        self.position = position

    def __hash__(self):
        return hash(self.article)

    def __eq__(self, other):
        return self.article == other


class Department:

    def __init__(self, name, position):
        self.name = name
        self.position = position
        self.items = collections.defaultdict(float)

    def add_item(self, item: StoreItem, comment=''):
        self.items[item] = comment

    def remove_items(self):
        self.items = collections.defaultdict(float)
