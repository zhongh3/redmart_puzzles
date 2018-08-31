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

    file.close()

    return ski_map, row, column


def main():
    # ski_map is a list of lists (similar to a matrix) with size row x column, where each item is an Area
    ski_map, row, column = prepare_map("input.txt")

    max_length = -1
    max_drop = -1

    def visit_area(area, x, y):
        # an helper function to update path_length and bottom_height
        def update_parameters(new_length, new_bottom):
            if area.path_length < new_length:
                area.path_length = new_length
                area.bottom_height = new_bottom
            elif area.path_length == new_length:
                area.bottom_height = min(new_bottom, area.bottom_height)

        # if an Area has already been visited, the parameters are up-to-date
        if area.b_visited:
            return

        # start to visit neighbours
        # 1. North
        if x == 0 or area.height <= ski_map[x - 1][y].height:
            area.path_length = 1
            area.bottom_height = area.height
        else:
            visit_area(ski_map[x - 1][y], x - 1, y)
            area.path_length = ski_map[x - 1][y].path_length + 1
            area.bottom_height = ski_map[x - 1][y].bottom_height

        # 2. East
        if y == (column - 1) or area.height <= ski_map[x][y + 1].height:
            east_length = 1
            east_bottom = area.height
        else:
            visit_area(ski_map[x][y + 1], x, y + 1)
            east_length = ski_map[x][y + 1].path_length + 1
            east_bottom = ski_map[x][y + 1].bottom_height

        update_parameters(east_length, east_bottom)

        # 3. South
        if x == (row - 1) or area.height <= ski_map[x + 1][y].height:
            south_length = 1
            south_bottom = area.height
        else:
            visit_area(ski_map[x + 1][y], x + 1, y)
            south_length = ski_map[x + 1][y].path_length + 1
            south_bottom = ski_map[x + 1][y].bottom_height

        update_parameters(south_length, south_bottom)

        # 4. West
        if y == 0 or area.height <= ski_map[x][y - 1].height:
            west_length = 1
            west_bottom = area.height
        else:
            visit_area(ski_map[x][y - 1], x, y - 1)
            west_length = ski_map[x][y - 1].path_length + 1
            west_bottom = ski_map[x][y - 1].bottom_height

        update_parameters(west_length, west_bottom)

        area.b_visited = True

        return

    for i in range(row):
        for j in range(column):
            a = ski_map[i][j]
            visit_area(a, i, j)
            if a.path_length >= max_length:
                max_length = a.path_length
                drop = a.height - a.bottom_height
                if drop > max_drop:
                    max_drop = drop

            print(a)

    print("max length = {}, max drop = {}".format(max_length, max_drop))

    return


if __name__ == "__main__":
    main()



