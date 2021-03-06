from list import *
from store import *
import getpass
import Levenshtein
import os
import getpass

def add_item(input_item, store, shopping_list):

    # Loop trough the items of the store and look for similar items
    found = False
    for department in store.departments:
        if found: break
        for store_item in department.items:
            if found: break

            # If the article provided is sufficiently close to an existing
            distance = Levenshtein.distance(input_item.lower().rstrip(), store_item.article)
            if distance < 2:
                # Add the item to the category
                shopping_list.categories[department.position].add_item(store_item, note=note)
                found = True

    return found

if __name__ == '__main__':

    print("Welcome! These are the existing stores")

    database_path = Path.cwd().joinpath('database')
    for i, path in enumerate(os.scandir(database_path)):
        full_name = ntpath.split(path)[-1]
        name = full_name.split('_')[0]
        location = full_name.split('_')[-1]
        print(str(i) + ": " + name + ' ' + location)

    choose_existing_store = input("Do you want to choose any of the stores above? y/n\n")
    current_store = Store()
    if choose_existing_store == 'y':
        store_index = int(input("Existing store number\n"))

        for i, path in enumerate(os.scandir(database_path)):
            if i == store_index:
                current_store = store.Store(path=path.path)

                # Read the departments for the specific store
                current_store.add_departments()
    else:
        print("Ok, please add a new store")
        new_store_name = input("New store name\n")
        new_store_location = input("New store location\n")
        current_store = store.Store(name=new_store_name, location=new_store_location)

        # Add departments
        counter = 0
        while True:
            last_department = input("Please provide a department name, type done when done!\n")

            if last_department == 'done':
                break

            first_item = input("Type in one item in the department\n")

            current_store.new_department(last_department, counter, first_item)
            counter += 1

        # Read the departments for the specific store
        current_store.add_departments()

    shopping_list = List(current_store)

    while True:

        input_str = input("Input article on the format (article_name, amount or comment), type done to exit\n")

        try:
            input_item, note = input_str.split(',')
        except ValueError:
            if input_str == 'done':
                break
            else:
                input_item = input_str
                note = ''

        # Add item
        found = add_item(input_item, current_store, shopping_list)

        if not found:
            print(input_item + " not found!")
            add_item_bool = input("Do you want to add it?, y/n\n")
            if add_item_bool == 'y':

                # Prompt for where the item is placed
                want_to_see_department = input("Do you want to see department items? y/n\n").strip().lower()
                if want_to_see_department == 'y':

                    # Print available departments
                    shopping_list.print_section_names()
                    department_number = int(input('Please choose one department number\n').strip())

                    current_store.print_department_items(department_number)

                next_to_item = input("Which item is it next to?\n").strip().lower()
                before_or_after_result = input("1, before or 2, after?\n").strip()

                # Check if before or after
                sucess = False
                if before_or_after_result == '2':
                    before_after = Preposition.after
                    sucess = current_store.add_item(input_item, next_to_item, before_after)
                else:
                    before_after = Preposition.before
                    sucess = current_store.add_item(input_item, next_to_item, before_after)

                while not sucess:
                    next_to_item = input("Could not find " + next_to_item + ", try another item\n")
                    sucess = store.add_item(input_item, next_to_item.strip().lower())

                add_item(input_item, current_store, shopping_list)
                print(input_item + " successfully added to database and shopping list!")

            else:
                print('Ok, item not added to list!')

    shopping_list.sort_items()
    shopping_list.print_list()

    # Ask user if he/she wants to send an email with the shopping list
    send_email = input("Do you want to send the shopping list by email, y/n?\n").lower()
    if send_email == 'y':
        user_email = input("Sender gmail address: \n")
        user_password = getpass.getpass()
        receiver_email = input("Receiver email address: ")
        shopping_list.send_email(user_email, user_password, receiver_email)

    os.startfile(shopping_list.output_path)
    quit()
