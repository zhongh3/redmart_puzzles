import pandas as pd
import csv
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
num_rows = None  # set to None to read the whole file


class Product:
    def __init__(self, record=None):
        self.p_id = int(record.iloc[Idx.p_id])         # product id
        self.value = int(record.iloc[Idx.price])       # price (cent)
        self.weight = int(record.iloc[Idx.weight])     # weight (g)
        self.volume = int(record.iloc[Idx.volume])     # volume (cm3)
        self.unit_price = record.iloc[Idx.unit_price]  # price per cubic centimeter = price/volume (cent/cm3)

    def __str__(self):
        return "Product ID: {} - $={}, Weight={}, Volume={}, Unit$={}".\
            format(self.p_id, self.value, self.weight, self.volume, self.unit_price)

    def __lt__(self, other):
        # define a way to sort products by "unit price" first and break tie by "volume" and then "weight"

        if self.unit_price < other.unit_price:
            # higher unit price wins
            return True

        if self.unit_price == other.unit_price:
            if self.volume < other.volume:
                # with same unit price, bigger volume wins
                return True
            elif self.volume == other.volume and self.weight > other.weight:
                # with same unit price and volume, lighter weight wins
                return True

        # if all 3 values are the same, the order of the 2 products doesn't matter for our use case
        # default self < other to 'False'
        return False


class BestState:
    def __init__(self, space, min_volume):
        self.space = 0 if space == 0 else space + min_volume - 1
        self.id_sum = 0
        self.value = 0
        self.weight = 0

    def __lt__(self, other):
        # compare 2 BestStates by value and break tie by weight
        if self.value < other.value:
            # higher value wins
            return True
        if self.value == other.value and self.weight > other.weight:
            # with same value, lighter weight wins
            return True

        # if 2 BestState have the same value and weight
        # default self < other to 'False'
        return False

    def __set_state(self, state):
        self.id_sum = state.id_sum
        self.value = state.value
        self.weight = state.weight

    def update_state(self, state1, state2, product):
        if product.volume > self.space:
            self.__set_state(state1)
        elif state2.value + product.value > state1.value or \
                (state2.value + product.value == state1.value and state2.weight + product.weight < state1.weight):
                self.id_sum = state2.id_sum + product.p_id
                self.value = state2.value + product.value
                self.weight = state2.weight + product.weight
        else:
            self.__set_state(state1)


class Basket:
    def __init__(self, space, name=""):
        self.name = name
        self.items = []
        self.num_items = 0  # number of items in the basket
        self.capacity = space  # the total capacity of the basket (cm3)
        self.volume = 0  # the total volume of products in the basket (cm3)
        self.value = 0  # the total value of all products in the basket (cent)
        self.weight = 0  # the total weight of all products in the basket (gram)
        self.id_sum = 0  # the sum of product ID of all products in the basket

    def add_a_product(self, product):
        if self.capacity - self.volume >= product.volume:
            self.items.append(product)
            self.num_items += 1
            self.volume += product.volume
            self.value += product.value
            self.weight += product.weight
            self.id_sum += product.p_id
        else:
            print("Failed to add product ID = {}, volume = {} into the basket - remaining space = {}".
                  format(product.p_id, product.volume, self.capacity - self.volume))

    def __str__(self):
        return "{} - total {} products, total volume = {}, total value={}, " \
               "total weight={}, ID sum={}, space left={}".\
            format(self.name, self.num_items, self.volume, self.value,
                   self.weight, self.id_sum, self.capacity - self.volume)

    def print_content(self):
        # to print detailed information of the basket, including all products in the basket
        print("{} - total {} products, total volume = {}, total value={}, "
              "total weight={}, ID sum={}, space left={}".
              format(self.name, self.num_items, self.volume, self.value,
                     self.weight, self.id_sum, self.capacity - self.volume))

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
        unit_prices.append(inputs.iloc[i, Idx.price] / volumes[i])

    min_volume = min(volumes)
    logging.info("min volume = {}".format(min_volume))

    # add volume and unit price as new columns of inputs
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

        # the product can fit into the tote, add it to the candidate list
        products.append(Product(inputs.iloc[i]))

    logging.info("total no. of candidate products = {}".format(len(products)))

    products.sort(reverse=True)  # sort products by unit price in descending order

    return products, min_volume


def write_to_csv(products, num_lines):
    # utility function to output candidate products to csv
    # num_lines: the number of products to write to csv

    with open('candidate_products.csv', 'w') as csv_file:
        csv_writer = csv.writer(csv_file,)
        csv_writer.writerow(["index", "product id", "value", "volume", "weight", "unit price"])
        for i in range(num_lines + 1):
            csv_writer.writerow([i, products[i].p_id, products[i].value,
                                 products[i].volume, products[i].weight, products[i].unit_price])


def main():
    products, min_volume = process_input("./products.csv")

    max_num = tote_volume//min_volume
    logging.info("max number of products in the tote = {}".format(max_num))

    # products are already sorted according to unit price, volume and weight
    # since there are only maximum of max_num products that can fit into the tote,
    # search the top candidates (e.g. choose 3 times of the max_num) instead of the complete list
    products = products[0: max_num * 3]  # to search the whole list, skip this line

    # write_to_csv(products, len(products)-1)

    # originally: need a table of size (len(products) + 1) x (tote_volume - 1) to save the BestStates
    # optimization: (saving in both computation time and space)
    #   reduce the table size by (min_volume - 1) columns, since nothing can fit if the space is less than min_volume
    # finally: table size = (len(products) + 1) x (tote_volume - min_volume + 2)
    table = [[BestState(i, min_volume) for i in range(tote_volume - min_volume + 2)] for j in range(len(products) + 1)]

    for i in range(1, len(table)):
        for j in range(1, tote_volume - min_volume + 2):
            x = j - products[i-1].volume
            table[i][j].update_state(table[i-1][j], table[i-1][max(0, x)], products[i-1])

    final = table[len(products)][tote_volume - min_volume + 1]

    # the sum of IDs is already obtained in the "final" BestState
    logging.info("best total value = {}, weight = {}, ID sum = {}".
                 format(final.value, final.weight, final.id_sum))

    # to obtain details of products in the tote
    tote = Basket(tote_volume, "TOTE")

    j = tote_volume - min_volume + 1
    for i in range(len(products), 0, -1):
        if table[i][j].value != table[i-1][j].value:
            tote.add_a_product(products[i-1])
            x = j - products[i-1].volume
            j = max(0, x)

    print(tote)
    # tote.print_content()  # to print details of content in the tote


if __name__ == "__main__":
    main()
