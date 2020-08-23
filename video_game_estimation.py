import pydotplus
import collections
import csv
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn import tree
import math

new_label_names = []

class Tree:
    def __init__(self):
        self.left = None
        self.right = None
        self.content = None
        self.rest = None
        self.restName = None
        self.end = None

    def setRestName(self):
        for i in range(36):
            if self.rest == i:
                if i < 24:
                    self.restName = "If platform == " + str(new_label_names[i])
                else:
                    self.restName = "If genre == " + str(new_label_names[i])

    def display(self):
        lines, _, _, _ = self._display_aux()
        for line in lines:
            print(line)

    def _display_aux(self):
        """Returns list of strings, width, height, and horizontal coordinate of the root."""
        # No child.
        if self.right is None and self.left is None:
            line = 'Value = %.5s' % self.content
            width = len(line)
            height = 1
            middle = width // 2
            return [line], width, height, middle

        # Only left child.
        if self.right is None:
            lines, n, p, x = self.left._display_aux()
            s = '%s' % self.rest
            u = len(s)
            first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s
            second_line = x * ' ' + '/' + (n - x - 1 + u) * ' '
            shifted_lines = [line + u * ' ' for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, n + u // 2

        # Only right child.
        if self.left is None:
            lines, n, p, x = self.right._display_aux()
            s = '%s' % self.rest
            u = len(s)
            first_line = s + x * '_' + (n - x) * ' '
            second_line = (u + x) * ' ' + '\\' + (n - x - 1) * ' '
            shifted_lines = [u * ' ' + line for line in lines]
            return [first_line, second_line] + shifted_lines, n + u, p + 2, u // 2

        # Two children.
        left, n, p, x = self.left._display_aux()
        right, m, q, y = self.right._display_aux()
        self.setRestName()
        s = '%s' % self.restName
        u = len(s)
        first_line = (x + 1) * ' ' + (n - x - 1) * '_' + s + y * '_' + (m - y) * ' '
        second_line = x * ' ' + '/' + (n - x - 1 + u + y) * ' ' + '\\' + (m - y - 1) * ' '
        if p < q:
            left += [n * ' '] * (q - p)
        elif q < p:
            right += [m * ' '] * (p - q)
        zipped_lines = zip(left, right)
        lines = [first_line, second_line] + [a + u * ' ' + b for a, b in zipped_lines]
        return lines, n + m + u, max(p, q) + 2, n + u // 2

def add_new_attribute(array ,data):
    outputArray = array
    canAdd = True
    for i in range(len(array)):
        if array[i] == data:
            canAdd = False
    if canAdd:
        outputArray.append(data)
    return outputArray

def calculate_avg_std_cv(array):
    size = len(array)
    if size != 0:
        total = 0
        for i in range(size):
            total += array[i]
        average = total / size
        std_total = 0
        for i in range(size):
            std_total += math.pow((array[i] - average), 2)
        std = math.sqrt(std_total / size)
        cv = (std / average) * 100
        return average, std, cv
    else:
        return 0,0,0

def generateTree(tree, X, Y, indexTable):
    print(len(indexTable))
    if len(indexTable) > 5:
        root_avg, root_std, root_cv = calculate_avg_std_cv(Y)
        max_reduc = 0
        max_reduc_index = -1
        chosen_part_X = []
        chosen_part_Y = []
        right_avg = 0
        for i in range(len(X[0])):
            firstPart_Y = []
            secondPart_Y = []
            firstPart_X = []
            secondPart_X = []
            for j in range(len(X)):
                if X[j][i] == 1:
                    firstPart_Y.append(Y[j])
                    firstPart_X.append(X[j])
                else:
                    secondPart_Y.append(Y[j])
                    secondPart_X.append(X[j])
            avg1, std1, cv1 = calculate_avg_std_cv(firstPart_Y)
            avg2, std2, cv2 = calculate_avg_std_cv(secondPart_Y)
            std_of_2_att = ((len(firstPart_Y) / len(Y)) * std1) + ((len(secondPart_Y) / len(Y)) * std2)
            reduction = root_std - std_of_2_att
            if reduction > max_reduc:
                max_reduc = reduction
                max_reduc_index = i
                right_avg = avg1
                chosen_part_X = secondPart_X
                chosen_part_Y = secondPart_Y
        tree.rest = indexTable[max_reduc_index]
        tree.right = Tree()
        print("right avg=", right_avg)
        tree.right.content = right_avg
        tree.right.end = 1
        chosen_part_X, indexTable = resize_X(chosen_part_X, max_reduc_index, indexTable)
        tree.left = Tree()
        tree.left.end = 0
        generateTree(tree.left, chosen_part_X, chosen_part_Y, indexTable)
        return tree
    else:
        tree.end = 1

def resize_X(array, index, indexTable):
    print("Chosen Index =", indexTable[index])
    indexTable.pop(index)
    resized_X = []
    for i in range(len(array)):
        content = []
        for j in range(len(array[i])):
            if j != index:
                content.append(array[i][j])
        resized_X.append(content)
    return resized_X, indexTable



def guess(node, inputPlatform, inputGenre):
    inputGenre += 24
    current = -1
    counter = 0
    result = 0
    while current != 1:
        counter += 1
        if int(node.rest) == int(inputPlatform) or int(node.rest) == int(inputGenre):
            node = node.right
            result = node.content
        else:
            node = node.left
        current = node.end
    # print("counter =",counter)
    return result

def mainFunc():
    isFieldType = True
    fieldNames = []
    tempData = []
    X = []

    with open('vgsales.csv', 'rt')as file:
        raw_data = csv.reader(file)
        dataCount = 0
        total_NA_sales = 0
        total_EU_sales = 0
        total_JP_sales = 0
        na_sales = []
        eu_sales = []
        jp_sales = []
        platforms = []
        genres = []
        publishers = []
        platform_count = 0
        genre_count = 0
        publisher_count = 0
        for row in raw_data:
            if isFieldType:
                for i in range(len(row)):
                    if i == 2 or i == 4 or i == 6 or i == 7 or i == 8:
                        fieldNames.append(row[i])
                isFieldType = False
            else:
                na_sale = float(row[6])
                eu_sale = float(row[7])
                jp_sale = float(row[8])
                if na_sale > 0 and eu_sale > 0 and jp_sale > 0 and row[2] != 'N/A' and row[4] != 'N/A' \
                        and row[2] != 'Unknown' and row[4] != 'Unknown':
                    total_NA_sales += na_sale
                    total_EU_sales += eu_sale
                    total_JP_sales += jp_sale
                    na_sales.append(na_sale)
                    eu_sales.append(eu_sale)
                    jp_sales.append(jp_sale)
                    dataCount += 1
                    final_row = []
                    add_new_attribute(platforms, row[2])
                    add_new_attribute(genres, row[4])
                    final_row.append(row[2])
                    final_row.append(row[4])
                    # final_row.append(na_sale)
                    # final_row.append(eu_sale)
                    # final_row.append(jp_sale)
                    X.append(final_row)

            # print(row)
    # print("Total NA sales =", total_NA_sales)
    print("Data count =", dataCount)
    na_average = total_NA_sales / dataCount
    eu_average = total_EU_sales / dataCount
    jp_average = total_JP_sales / dataCount
    # print("Average =", na_average)
    print(fieldNames)

    print(platforms)
    print(len(platforms))
    print(genres)
    print(len(genres))

    for i in range(len(platforms)):
        new_label_names.append(platforms[i])
    for i in range(len(genres)):
        new_label_names.append(genres[i])

    new_X = []
    for i in range(len(X)):
        new_row = []
        for j in range(len(platforms)):
            if X[i][0] == platforms[j]:
                new_row.append(1)
            else:
                new_row.append(0)
        for j in range(len(genres)):
            if X[i][1] == genres[j]:
                new_row.append(1)
            else:
                new_row.append(0)
        new_X.append(new_row)

    # root_avg, root_std, root_cv = calculate_avg_std_cv(na_sales)
    # print(root_std)

    indexTable = []
    for i in range(len(new_X[0])):
        indexTable.append(i)
    root = Tree()
    root = generateTree(root, new_X, na_sales, indexTable)
    root.display()
    print(root.right.content)

    inputPlatform = input("Input platform : ")
    inputGenre = input("Input genre : ")
    platformCode = -1
    genreCode = -1
    for i in range(36):
        if inputPlatform == new_label_names[i]:
            platformCode = i
        if inputGenre == new_label_names[i]:
            genreCode = i
    result = guess(root, platformCode, genreCode)
    print("For {} and {} predicted sale = {}".format(inputPlatform, inputGenre, result))


mainFunc()
