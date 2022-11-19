import connector

from privileges import *

class PrivilegeError(Exception):
    pass

class Employee:
    def __init__(self, employee_id, username, password, name, phone_number, department, address=None):
        self._employee_id = employee_id
        self._username = username
        self._password = password
        self._name = name
        self._phone_number = phone_number
        self._address = address
        self._department = department

    def get_employee_id(self):
        return self._employee_id

    def get_username(self):
        return self._username
    
    def get_password(self):
        return self._password

    def set_password(self, password):
        self._password = password

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name
    
    def get_phone_number(self):
        return self._phone_number

    def set_phone_number(self, phone_number):
        self._phone_number = phone_number

    def get_address(self):
        return self._address

    def set_address(self, address):
        self._address = address

    def get_department(self):
        return self._department

    def set_department(self, department):
        self._department = department

    def get_info_privilege(self):
        return INFO_PRIVILEGES[self.get_department()]

    def get_edit_privilege(self):
        return EDIT_PRIVILEGES[self.get_department()]

    def add_product(self, name, category, price, description=None):
        user_privilege = self.get_edit_privilege()
        if not user_privilege&CATALOG:
            raise PrivilegeError("User don't have catalog edit privilege")
        
        product_id=connector.add_product(name=name, category=category, price=price, description=description)
        new_product = Product(product_id=product_id, name=name, category=category, price=price, description=description)
        
        return new_product

    def _get_queried_columns(self):
        privilege_column = {
            PRODUCT_NAME:'name',
            PRODUCT_CATEGORY:'category',
            PRODUCT_PRICE:'price',
            PRODUCT_STOCK:'stock',
            PRODUCT_DESCRIPTION:'description'
        }
        user_privilege = self.get_info_privilege()
        queried_columns = ('product_id',)+tuple(column for privilege, column in privilege_column.items() if user_privilege&privilege)

        return queried_columns

    def _get_edit_columns(self):
        privilege_column = {
            PRODUCT_NAME:'name',
            PRODUCT_CATEGORY:'category',
            PRODUCT_PRICE:'price',
            PRODUCT_STOCK:'stock',
            PRODUCT_DESCRIPTION:'description'
        }
        user_privilege = self.get_edit_privilege()
        edited_columns = tuple(column for privilege, column in privilege_column.items() if user_privilege&privilege)

        return edited_columns

    def show_product_information(self, product_id):
        product = Product(**connector.get_product_information(product_id))
        queried_columns = {column:product[column] for column in self._get_queried_columns()}

        row = "{:<20}"*len(queried_columns)
        print(row.format(*map(str, queried_columns)))
        print(row.format(*map(str, queried_columns.values())))
    

    def show_catalog(self):
        queried_columns = self._get_queried_columns()
        row = "{:<20}"*len(queried_columns)
        print(row.format(*map(str, queried_columns)))

        catalog = connector.get_catalog(queried_columns)
        for values in catalog:
            print(row.format(*map(str, values)))


    def show_transactions(self):
        user_privilege = self.get_info_privilege()
        if not user_privilege&TRANSACTION:
            raise PrivilegeError("User don't have the privilege to view transaction history")

        pad = 20
        transactions = connector.get_transactions()
        print(f"{'transaction_id':<{pad}}{'employee_id':<{pad}}{'type':<{pad}}{'receipt_number':<{pad}}{'date':<{pad}}")
        for transaction in transactions:
            transaction_id, employee_id, _type, receipt_number, date = transaction
            print(f"{transaction_id:<{pad}}{employee_id:<{pad}}{_type:<{pad}}{str(receipt_number):<{pad}}{date.strftime('%Y-%m-%d %H:%M:%S'):<{pad}}")

    def register_account(self, username, password, name, phone_number, department, address=None):
        user_privilege = self.get_edit_privilege()
        if not user_privilege&REGISTRATION:
            raise PrivilegeError("User don't have the privilege to register an employee account")

        employee_id = connector.register(username=username, password=password, name=name, phone_number=phone_number, department=department, address=address)
        new_employee = Employee(employee_id=employee_id, username=username, password=password, name=name, phone_number=phone_number, department=department, address=address)
        return new_employee

    def do_transaction(self, receipt_number, transaction_details, transaction_type):
        user_privilege = self.get_edit_privilege()
        if not user_privilege%TRANSACTION:
            raise PrivilegeError("User don't have the privilge to do transaction")
        connector.transact(self.get_employee_id(), receipt_number, transaction_details, transaction_type)

    def edit_product(self, product_id, name=None, category=None, price=None,  description=None):
        edit_columns = self._get_edit_columns()
        if not edit_columns:
            raise PrivilegeError("User don't have the privilege to edit product")
        
        connector.edit_product_information(product_id, name, category, price, description)

    
class Transaction:
    def __init__(self, transaction_id, employee_id, type, date, receipt_number=None):
        self.transaction_id = transaction_id
        self.employee_id = employee_id
        self.type = type
        self.receipt_number = receipt_number
        self.date = date

    @property
    def transaction_id(self):
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self._transaction_id = value

    @property
    def employee_id(self):
        return self._employee_id

    @employee_id.setter
    def employee_id(self, value):
        self._employee_id = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = value

    @property
    def receipt_number(self):
        return self._receipt_number

    @receipt_number.setter
    def receipt_number(self, value):
        self._receipt_number = value

    @property
    def date(self):
        return self._date

    @date.setter
    def date(self, value):
        self._date = value


class Product:
    def __init__(self, product_id, name, category, price=0, stock=0, description=None):
        self._product_id = product_id
        self._name = name
        self._category = category
        self._price = price
        self._stock = stock
        self._description = description

    @property
    def product_id(self):
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        self._price = value

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        self._stock = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    def __iter__(self):
        return iter((self.product_id, self.name, self.category, self.price, self.stock, self.description))

    def __getitem__(self, attribute):
        return getattr(self, attribute)

class Transaction_Detail:
    def __init__(self, transaction_id, product_id, quantity):
        self._transaction_id = transaction_id
        self._product_id = product_id
        self._quantity = quantity

    @property
    def transaction_id(self):
        return self._transaction_id

    @transaction_id.setter
    def transaction_id(self, value):
        self._transaction_id = value

    @property
    def product_id(self):
        return self._product_id

    @product_id.setter
    def product_id(self, value):
        self._product_id = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        self._quantity = value