import logging
# change logging level from INFO to DEBUG to print debugging logs
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s - %(lineno)d - %(message)s')

class Area:
    # an Area is a point on the Map
    def __init__(self, x=-1, y=-1, height=-1):
        # the location coordinates (x, y) corresponding to the
        # row (x) and column (y) numbers on the Map (both 0-indexed)
        self.x = x
        self.y = y

        # height: corresponding to the value read from the Map
        self.height = height

        # b_visited: a boolean, keeping track of whether the Area has been visited
        self.b_visited = False

        # path_length: the longest length starting from the current Area
        # the default value '0' indicates that the Area hasn't been visited
        # the min path length of an visited Area is "1", which means it's the lowest among the neighbours,
        # it can only visit itself
        self.path_length = 0

        # bottom_height: the height of the lowest Area that can be visited from the current Area
        # i.e. the end of the path starting from current Area
        # the default value '-1' indicates that the Area hasn't been visited
        self.bottom_height = -1

    def __str__(self):
        return "Area ({}, {}) - Height={}, Visited?={}, Path Length={}, Bottom Height={}"\
            .format(self.x, self.y, self.height, self.b_visited, self.path_length, self.bottom_height)

    def update_parameters(self, new_length, new_bottom):
        # update both path length and bottom height if the new path length is longer
        # when the old and new path lengths are equal, break tie with smaller bottom height
        if self.path_length < new_length:
            self.path_length = new_length
            self.bottom_height = new_bottom
        elif self.path_length == new_length:
            self.bottom_height = min(new_bottom, self.bottom_height)


def prepare_map(file_name):
    # parse input file to get the height of each Area
    logging.info("Input File: \"./{}\"".format(file_name))

    # open the input file for reading
    file = open(file_name, "r")

    # the 1st line of the input file indicates the size of the map (row and column)
    row, column = map(int, file.readline().strip().split(" "))

    logging.info("Map Size: row = {}, column = {}".format(row, column))

    # ski_map is a list of lists where each entry is an Area object
    # the indexes of the entry denotes the location on the map
    # i.e. area = ski_map[i][j] ==> area.x = i; area.y = j
    ski_map = []

    for i in range(row):
        input_row = list(map(int, file.readline().strip().split(" ")))

        if len(input_row) != column:
            raise Exception("Line {} of input file has incorrect no. of values.".format(i + 2))

        area_row = []
        for j in range(column):
            # range check for height -> [0, 1500]
            if input_row[j] < 0 or input_row[j] > 1500:
                raise Exception("Area({}, {}) - Height = {} is out of range".format(i, j, input_row[j]))
            area_row.append(Area(i, j, input_row[j]))

        ski_map.append(area_row)

    file.close()

    return ski_map, row, column


def main():
    def visit_area(area):

        def compare_with_neighbour(area, neighbour):
            # update path_length and bottom_height of current area after comparing with neighbour area
            if area.height <= neighbour.height:
                # the base case:
                # the new path length is '1' (the current area itself)
                # the new bottom height is the height of the current area itself
                area.update_parameters(1, area.height)
            else:
                visit_area(neighbour)   # recursive call
                new_length = neighbour.path_length + 1
                new_bottom = neighbour.bottom_height
                area.update_parameters(new_length, new_bottom)

        # if an Area has already been visited, the parameters are up-to-date
        if area.b_visited:
            return

        # start to visit neighbours in clockwise order: N -> E -> S -> W
        # 1. North
        if area.x == 0:  # there's no neighbour to the North of current area -> the base case
            area.update_parameters(1, area.height)
        else:
            neighbour = ski_map[area.x - 1][area.y]
            compare_with_neighbour(area, neighbour)

        # 2. East
        if area.y == (column - 1):  # there's no neighbour to the East of current area -> the base case
            area.update_parameters(1, area.height)
        else:
            neighbour = ski_map[area.x][area.y + 1]
            compare_with_neighbour(area, neighbour)

        # 3. South
        if area.x == (row - 1):  # there's no neighbour to the South of current area -> the base case
            area.update_parameters(1, area.height)
        else:
            neighbour = ski_map[area.x + 1][area.y]
            compare_with_neighbour(area, neighbour)

        # 4. West
        if area.y == 0:  # there's no neighbour to the West of current area -> the base case
            area.update_parameters(1, area.height)
        else:
            neighbour = ski_map[area.x][area.y - 1]
            compare_with_neighbour(area, neighbour)

        # all neighbours have been visited, the current area has been updated/visited as well
        area.b_visited = True

        return area.height - area.bottom_height

    # ski_map is a list of lists with size row x column, where each entry is an Area
    # the indexes of each Area in ski_map is their location on the map
    ski_map, row, column = prepare_map("input.txt")

    # the minimum of max_length should be '1' and max_drop should be '0'
    # init both to negative values and update them accordingly
    max_length = -1
    max_drop = -1

    for i in range(row):
        for j in range(column):
            area = ski_map[i][j]
            drop = visit_area(area)
            if max_length < area.path_length:
                logging.debug(area)
                max_length = area.path_length
                max_drop = drop
            elif max_length == area.path_length:
                # break tie with larger drop
                logging.debug(area)
                max_drop = max(drop, max_drop)

    print("Results: max length = {}, max drop = {}".format(max_length, max_drop))


if __name__ == "__main__":
    main()



