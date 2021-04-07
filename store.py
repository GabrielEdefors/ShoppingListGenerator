from pathlib import Path
from enum import Enum
import collections
import ntpath
import os
import csv
import Levenshtein
from distutils.dir_util import copy_tree


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

    def __init__(self, **kwargs):

        self.name = ''
        self.location = ''
        self.data_path = ''
        self.departments = []

        if not kwargs:
            return

        for key, value in kwargs.items():
            if key == 'name':
                self.name = value
            elif key == 'location':
                self.location = value
            elif key == 'path':
                self.data_path = value
                full_name = ntpath.split(value)[-1]
                self.name = full_name.split('_')[0]
                self.location = full_name.split('_')[-1]

        if not self.data_path:
            self.initiate_repository(Path.cwd().joinpath('database', self.name + '_' + self.location))
            self.data_path = Path.cwd().joinpath('database', self.name + '_' + self.location)

    def initiate_repository(self, path):
        os.mkdir(path)

    def new_department(self, name, index, item):
        path = self.data_path.joinpath(str(index) + '_' + name + '.csv')
        with open(path, "w") as new_csv:
            new_csv.write(item + '\n')

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
                    distance = Levenshtein.distance(next_to.lower().rstrip(), article)
                    if distance < 2:
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
