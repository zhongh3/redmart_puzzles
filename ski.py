import sys

class Area:
    # an Area is a point on the Map
    def __init__(self, x=-1, y=-1, height=-1):
        # the location coordinates (x, y) corresponding to the
        # row (x) and column (y) numbers on the Map (both 0-indexed)
        # TODO: the position can be tracked by the indexes of the Area in ski_map
        # TODO: keep x & y for easier debugging first, can be removed later
        self.x = x
        self.y = y

        # height: corresponding to the value read from the Map
        self.height = height

        # path_length: the longest length starting from the current Area
        # the default value '1' refers to the Area itself,
        # i.e. if the Area is the lowest among the neighbours, can only visit the Area itself
        self.path_length = 1

        # bottom_height: the height of the lowest Area that can be visited from the current Area
        # i.e. the end of the path starting from current Area
        # the default value '-1' indicates that the Area hasn't been visited
        self.bottom_height = -1

    def __str__(self):
        return "Area ({}, {}) - Height={}, Path Length={}, Bottom Height={}" \
            .format(self.x, self.y, self.height, self.path_length, self.bottom_height)


def prepare_map(file_name):
    # parse input file and convert every input value to an Area
    # open the input file for reading
    file = open(file_name, "r")

    # the 1st line of the input file indicates the size of the map (row and column)
    row, column = map(int, file.readline().strip().split(" "))

    print("row = {}, column = {}".format(row, column))

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

    return ski_map, row, column


def main():
    # ski_map is a list of lists (similar to a matrix) with size row x column, where each item is an Area
    ski_map, row, column = prepare_map("input.txt")

    for i in range(row):
        for j in range(column):
            print(ski_map[i][j])


if __name__ == "__main__":
    main()



