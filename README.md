# Attempt to Solve Coding Puzzles from RedMart

## Skiing in Singapore (http://geeks.redmart.com/2015/01/07/skiing-in-singapore-a-coding-diversion/):

### Description:
In digital form the map looks like the number grid below.

```
4 4 
4 8 7 3
2 5 9 3 
6 3 2 5 
4 4 1 6
```

The first line (4 4) indicates that this is a **4x4** map. Each number represents the elevation of that area of the mountain. From each area (i.e. box) in the grid you can go north, south, east, west - but only if the elevation of the area you are going into is less than the one you are in. I.e. you can only ski downhill. You can start anywhere on the map and you are looking for a starting point with the longest possible path down as measured by the number of boxes you visit. And if there are several paths down of the same length, you want to take the one with the steepest vertical drop, i.e. the largest difference between your starting elevation and your ending elevation.

On this particular map the longest path down is of length=5 and it’s highlighted in bold below: **9-5-3-2-1**.

There is another path that is also length five: **8-5-3-2-1**. However the tie is broken by the first path being steeper, dropping from 9 to 1, a drop of 8, rather than just 8 to 1, a drop of 7.

Your challenge is to write a program in your favorite programming language to find the longest (and then steepest) path on this map specified in the format above. It’s 1000x1000 in size, and all the numbers on it are between 0 and 1500.

### Instructions:
1. The default map is from _./input.txt_. To change the input file, please replace the _./input.txt_ or change the source code in _main()_:
```python
ski_map, row, column = prepare_map("input.txt")
```
2. As the challenge is to find the longest (and then steepest) path on this map, the solution only provides the length of the path and its steepness (i.e. the drop from the starting area to the ending area). It didn't record the entire path. The results are printed as (take the example from the **Description**)
```
Results: max length = 5, drop = 8
```
3. To print debugging logs, simply change logging level from **logging.INFO** to **logging.DEBUG**:
```python
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(funcName)s - %(lineno)d - %(message)s')
```
