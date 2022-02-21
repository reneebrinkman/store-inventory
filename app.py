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
    product = session.query(Product).filter(Product.product_id==product_id).first()

    print(f'''
    \n***** PRODUCT DETAILS *****
    \r{product.product_name}
    \r${product.product_price / 100}
    \rIn Stock: {product.product_quantity}
    \rLast Updated: {product.date_updated.strftime("%B %d, %Y")}''')


def add_product():
    pass


def backup_db():
    pass


def check_id(choice, options):
    try:
        product_id = int(choice)
    except ValueError:
        input('The ID should be a number. Press enter to try again.')
        return
    else:
        if product_id in options:
            return product_id
        else:
            input(f'Your choices are {options}. Press enter to try again.')
            return


def search_id():
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
    while True:
        choice = menu()
        if choice == 'v':
            product_id = search_id()
            view_product(product_id)
            input('\nPress enter to continue.')
        elif choice == 'a':
            pass
        elif choice == 'b':
            pass
        else:
            return


if __name__ == '__main__':
    Base.metadata.create_all(engine)
    #add_csv()
    app()
