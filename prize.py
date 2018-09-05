import pandas as pd
import numpy as np
from enum import IntEnum

import logging
# change logging level from INFO to DEBUG to print debugging logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s - %(lineno)d - %(message)s')


class Idx(IntEnum):
    p_id = 0
    price = 1
    length = 2
    width = 3
    height = 4
    weight = 5
    volume = 6
    unit_price = 7


# The tote’s usable space is 45 centimeters long, 30 wide and 35 high
tote_volume = 45 * 30 * 35  # 47250 cm3

# To control the number of rows to read from the input file (for debugging use)
num_rows = 10  # set to None to read the whole file


class Product:
    def __init__(self, record=None):
        self.p_id = int(record.iloc[Idx.p_id])         # product id
        self.price = int(record.iloc[Idx.price])       # price (cent)
        self.length = int(record.iloc[Idx.length])     # length (cm)
        self.width = int(record.iloc[Idx.width])       # width (cm)
        self.height = int(record.iloc[Idx.height])     # height (cm)
        self.weight = int(record.iloc[Idx.weight])     # weight (g)
        self.volume = int(record.iloc[Idx.volume])     # volume (cm3)
        self.unit_price = record.iloc[Idx.unit_price]  # price per cubic centimeter = price/volume (cent/cm3)

    def __str__(self):
        return "Product ID: {} - $={}, L={}, W={}, H={}, Weight={}, V={}, Unit$ = {}".\
            format(self.p_id, self.price, self.length, self.width,
                   self.height, self.weight, self.volume, self.unit_price)

    def __lt__(self, other):
        # define a way to sort products by "unit price" first and break tie by "volume" and then "weight"

        if self.unit_price < other.unit_price:
            # higher unit price wins
            return True

        if self.unit_price == other.unit_price:
            if self.volume < other.volume:
                # with same unit price, bigger volume is preferred
                return True
            elif self.volume == other.volume and self.weight > other.weight:
                # with same unit price and volume, lighter weight is preferred
                return True

        # if all 3 values are the same, the order of the 2 products doesn't matter for our use case
        # default self < other to 'False' in this case

        # TODO: remove later
        if self.unit_price == other.unit_price and self.volume == other.volume and self.weight == other.weight:
            logging.info("Product ID {} and ID {} share same unit price, volume and weight".
                         format(self.p_id, other.p_id))

        return False


class Basket:
    # a basket is a collection of products who can fit into the tote all together
    def __init__(self, first):
        self.b_id = first.p_id  # use the ID of the first product as the ID of the basket
        self.volume = tote_volume  # total volume of the basket (cm3)

        self.items = [first]  # first is the 1st product added into the basket
        self.num_items = len(self.items)  # number of items in the basket
        self.space = self.volume - first.volume  # remaining space in the basket (cm3)
        self.value = first.price  # the total value of all products in the basket
        self.weight = first.weight  # the total weight of all products in the basket

    def add_product(self, new_product):
        if self.space >= new_product.volume:  # only add the new product if it fits into the basket
            self.items.append(new_product)
            self.num_items += 1
            self.space -= new_product.volume
            self.value += new_product.price
            self.weight += new_product.weight
        else:
            raise Exception("Failed to add new product (ID={})into the basket ID={}".format(new_product.p_id, self.b_id))

        logging.debug("Added new product (ID={})into the basket ID={}".format(new_product.p_id, self.b_id))

    def __str__(self):
        return "Basket ID: {} - no. of products={}, remaining space={}, total value={}, total weight={}".\
            format(self.b_id, self.num_items, self.space, self.value, self.weight)

    def print_content(self):
        # to print all products in the basket
        print("Basket ID: {} - total {} products".format(self.b_id, self.num_items))
        for i in range(self.num_items):
            print("{} - {}".format(i + 1, self.items[i]))


def process_input(csv_file_name):

    # input csv file format (no header):
    # |     0      |   1   |    2   |   3   |   4    |   5    |
    # | product ID | price | length | width | height | weight |
    # |     /      | cents |   cm   |  cm   |   cm   |   g    |
    # ---------------------------------------------------------
    inputs = pd.read_csv(csv_file_name, header=None, names=list(range(6)), nrows=num_rows)  # DataFrame

    row, column = inputs.shape
    logging.info("'{}' - row = {}, column = {}".format(csv_file_name, row, column))

    # calculate volume and unit prices for all the products
    volumes = []
    unit_prices = []
    for i in range(row):
        volumes.append(inputs.iloc[i, Idx.length] * inputs.iloc[i, Idx.width] * inputs.iloc[i, Idx.height])
        unit_prices.append(inputs.iloc[i, Idx.price]/volumes[i])

    min_volume = min(volumes)
    logging.info("min volume = {}".format(min_volume))

    # add volume and unit prices as 2 new columns of inputs
    inputs[Idx.volume] = pd.Series(volumes, index=inputs.index)
    inputs[Idx.unit_price] = pd.Series(unit_prices, index=inputs.index)

    # updated format of inputs
    # |     0      |   1   |    2   |   3   |   4    |   5    |    6   |     7      |
    # | product ID | price | length | width | height | weight | volume | unit price |
    # |     /      | cents |   cm   |  cm   |   cm   |   g    |   cm3  |  cent/cm3  |
    # -------------------------------------------------------------------------------

    products = []  # a list contains all candidate products (i.e. products that can fit into the tote individually)
    for i in range(row):
        # dimensions is a list containing length, width and height of a product, sorted in ascending order
        dimensions = sorted([inputs.iloc[i, Idx.length], inputs.iloc[i, Idx.width], inputs.iloc[i, Idx.height]])

        # Assume that the orientation of a product doesn't matter
        # (i.e. no request to place the product upright always).
        # For simplicity, only consider the potential rotation of the product be 90, 180, 270 degrees.
        if dimensions[0] > 30 or dimensions[1] > 35 or dimensions[2] > 45:
            # the product doesn't fit into the tote
            continue

        products.append(Product(inputs.iloc[i]))

    logging.info("total no. of candidate products = {}".format(len(products)))

    products.sort(reverse=True)  # sort products by unit price in descending order

    return products, min_volume


def main():
    products, min_volume = process_input("./products.csv")

    for item in products:
        print(item)


if __name__ == "__main__":
    main()
