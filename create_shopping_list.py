from list import *
from store import *
import getpass

def add_item(input_item):

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

    store = store.Store(StoreName.ICA_Maxi, Location.Hogsbo)
    shopping_list = List(store)
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
        found = add_item(input_item)

        if not found:
            print(input_item + " not found!")
            add_item_bool = input("Do you want to add it?, y/n\n")
            if add_item_bool == 'y':
                next_to_item = input("Which item is it next to?\n")
                sucess = store.add_item(input_item, next_to_item.strip().lower())
                while not sucess:
                    next_to_item = input("Could not find " + next_to_item + ", try another item\n")
                    sucess = store.add_item(input_item, next_to_item.strip().lower())

                add_item(input_item)
                print(input_item + " successfully added to database and shopping list!")

    shopping_list.sort_items()
    shopping_list.print_list()

    # Ask user if he/she wants to send an email with the shopping list
    send_email = input("Do you want to send the shopping list by email, y/n?\n").lower()
    if send_email == 'y':
        user_email = input("Sender gmail address: ")
        user_password = getpass.getpass(prompt='Your email password: ')
        receiver_email = input("Receiver email address: ")
        shopping_list.send_email(user_email, user_password, receiver_email)

    quit()
