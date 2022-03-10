"""app.py

Main module for inventory application.
"""
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import csv
import datetime


# initialize sqlite database
engine = create_engine('sqlite:///inventory.db', echo=False)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Product(Base):
    """class Product(Base)

    Product model class
    """
    __tablename__ = 'products'

    product_id = Column(Integer, primary_key=True)
    product_name = Column('Name', String)
    product_quantity = Column('Quantity', Integer)
    product_price = Column('Price', Integer)
    date_updated = Column('Last Updated', DateTime)


def clean_price(price_str):
    """clean_price(price_str)

    Takes a string containing a price that may have a dollar sign in front,
    removes the dollar sign, and returns an integer of the value in cents
    """
    price_split = price_str.lstrip('$').split('.')
    price_int = int(''.join(price_split))
    return price_int


def clean_date(date_str):
    """clean_date(date_str)

    Takes a string containing the date in m/d/yyyy format and converts it to a date object
    """
    date_split = date_str.split('/')
    month = int(date_split[0])
    day = int(date_split[1])
    year = int(date_split[2])

    return datetime.datetime(year, month, day)


def check_duplicates():
    """check_duplicates()

    Check every product in the database and remove duplicates with the same
    name, regardless of the values of other fields. Always keeps the more
    recently updated product.
    """
    data = session.query(Product).all()
    for product in data:
        product_duplicate = session.query(Product).filter(
            Product.product_id!=product.product_id).filter(
                Product.product_name==product.product_name).one_or_none()
        if product_duplicate is not None:
            if product.date_updated > product_duplicate.date_updated:
                session.delete(product_duplicate)
            elif product.date_updated < product_duplicate.date_updated:
                session.delete(product)
    session.commit()


def add_csv():
    """add_csv()

    Imports records from a csv file, cleans the data, and adds them to them
    database.
    """
    with open('inventory.csv') as csvfile:
        data = csv.reader(csvfile)
        for count, row in enumerate(data):
            if count > 0:
                name = row[0]
                price = clean_price(row[1])
                quantity = int(row[2])
                date_updated = clean_date(row[3])

                new_product = Product(
                    product_name=name,
                    product_quantity=quantity,
                    product_price=price,
                    date_updated=date_updated)
                session.add(new_product)
        session.commit()
    check_duplicates()


def view_product(product_id):
    """view_product(product_id)

    Queries the database for details about a specific product and prints it to
    the user in a friendly format.
    """
    product = session.query(Product).filter(Product.product_id==product_id).first()

    print(f'''
    \n***** PRODUCT DETAILS *****
    \r{product.product_name}
    \r${product.product_price / 100}
    \rIn Stock: {product.product_quantity}
    \rLast Updated: {product.date_updated.strftime("%B %d, %Y")}''')


def add_product():
    """add_product()

    Prompts the user for information about a product. If the product already
    exists, updates the product with the given information, if the product
    doesn't exist, creates a new one.
    """
    product_name = input("\nPlease enter the product's name: ")

    quantity = input('Please enter the quantity: ')
    quantity_invalid = True
    while quantity_invalid:
        try:
            product_quantity = int(quantity)
        except ValueError:
            print('Invalid quantity entry. Must be a number. Please try again.')
            quantity = input("Please enter the quantity: ")
        else:
            quantity_invalid = False

    price = input("Please enter the product's price: ")
    price_invalid = True
    while price_invalid:
        try:
            product_price = clean_price(price)
        except ValueError:
            print('Invalid price entry. Must be a number. Please try again.')
            price = input("Please enter the product's price: ")
        else:
            price_invalid = False

    date_updated = datetime.datetime.now()

    duplicate_product = session.query(Product).filter(Product.product_name==product_name).one_or_none()
    if duplicate_product == None:
        new_product = Product(
            product_name=product_name,
            product_quantity=product_quantity,
            product_price=product_price,
            date_updated=date_updated)
        session.add(new_product)
        print(f'\n{product_name} has been added to the inventory database!')
    else:
        # update existing product
        duplicate_product.product_quantity = product_quantity
        duplicate_product.product_price = product_price
        duplicate_product.date_updated = date_updated
        print(f'\n{product_name} has been updated in the inventory database!')

    session.commit()


def backup_db():
    """backup_db()

    Backs up the contents of the database to a csv file.
    """
    header_labels = [
        'product_name',
        'product_price',
        'product_quantity',
        'date_updated'
    ]

    data = session.query(Product).all()

    with open('backup.csv', 'w') as csvfile:
        writer = csv.writer(csvfile)

        writer.writerow(header_labels)

        for product in data:
            row = [
                product.product_name,
                f'${product.product_price / 100}',
                product.product_quantity,
                product.date_updated.strftime('%m/%d/%Y')
            ]

            writer.writerow(row)

    print('\nDatabase backup created successfully!')


def check_id(choice, options):
    """check_id(choice, options)

    Checks user input to make sure they entered a valid product id number that
    exists in the database.
    """
    try:
        product_id = int(choice)
    except ValueError:
        input('The ID should be a number. Press enter to try again.')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'\nInvalid ID. Your choices are {options}.\nPress enter to try again.')
            return


def search_id():
    """search_id()

    Shows a list of product id numbers and asks the user to enter one of them.
    """
    id_options = []
    for product in session.query(Product):
        id_options.append(product.product_id)
    while True:
        id_choice = input(f'''
        \nChoices: {id_options}
        \rProduct ID: ''')
        id_choice = check_id(id_choice, id_options)
        if type(id_choice) == int:
            return id_choice


def menu():
    """menu()

    Displays the main menu and asks the user for a menu selection. Also checks
    whether the user's selection is valid
    """
    while True:
        print('''
            \nSTORE INVENTORY
            \rv) View Product Details
            \ra) Add Product
            \rb) Backup Database
            \rq) Exit''')
        choice = input('What would you like to do? ')
        if choice in ['v', 'a', 'b', 'q']:
            return choice
        else:
            input('''
            \rPlease choose one of the options above.
            \rPress enter to try again.''')


def app():
    """app()

    Main app logic; handles each possible menu selection and calls the right
    function that will handle the dirty work
    """
    while True:
        choice = menu()
        if choice == 'v':
            product_id = search_id()
            view_product(product_id)
            input('\nPress enter to continue.')
        elif choice == 'a':
            add_product()
            input('\nPress enter to continue.')
        elif choice == 'b':
            backup_db()
            input('\nPress enter to continue.')
        else:
            return


if __name__ == '__main__':
    Base.metadata.create_all(engine)

    if session.query(Product).all() == []:
        add_csv()

    app()
