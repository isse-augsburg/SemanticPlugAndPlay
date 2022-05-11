import numpy as np


def calculate_string_array_similarity(list_of_strings_one: list, list_of_strings_two: list, level_of_wrongness: float = 0.5) -> float:
    """Check confidence for two sets of Properties

        creates a union, calculates two Vectors according to the input lists.
        These Vectors take into account how "near" these strings, using Levenshtein.

        Example: list1 = ["hey"], list2 = ["hey","ciao"]
        union = ["hey", "ciao"]
        vectorOne = [0.8, 0]
        vectorTwo = [1, 1]
        calculates the cosine distance between the resulting vectors

        :param list_of_strings_one: is the first list of strings
        :param list_of_strings_two: is the second list of strings
        :param level_of_wrongness: a threshold, words can have same literals (high Levenshtein) but are too different
        :return: a number between 0 and 1, depending on similarity of strings

    """
    # @TODO levelOFWrongness should be dependend on difference in size between @Queried and @Actual
    # print("HELLO: {} | {}".format(QueriedProperties, ActualProperties))
    # create a union list with both Properties
    union = []
    for listElementOne in list_of_strings_one:
        if listElementOne not in union:
            union += [listElementOne]

    for listElementTwo in list_of_strings_two:
        if listElementTwo not in union:
            union += [listElementTwo]

    vecorOne = np.zeros(shape=(len(union)))
    vecorTwo = np.zeros(shape=(len(union)))

    # calculate Vectors with confidence of a word inside union
    for i, union_element in enumerate(union):
        levensteinForeachWord = []
        for listElementOne in list_of_strings_one:
            levensteinForeachWord += [levenshtein_ratio_and_distance(union_element, listElementOne)]
        if max(levensteinForeachWord) > level_of_wrongness:
            vecorOne[i] = max(levensteinForeachWord)

        levensteinForeachWord.clear()
        for listElementTwo in list_of_strings_two:
            levensteinForeachWord += [levenshtein_ratio_and_distance(union_element, listElementTwo)]
        if max(levensteinForeachWord) > level_of_wrongness:
            vecorTwo[i] = max(levensteinForeachWord)
    # Calculate the cosine similarity
    return (vecorOne @ vecorTwo.T / (np.linalg.norm(vecorOne) * np.linalg.norm(vecorTwo)))


def levenshtein_ratio_and_distance(s: str, t: str, ratio_calc=True):
    """ levenshtein_ratio_and_distance:
        Calculates levenshtein distance between two strings.
        If ratio_calc = True, the function computes the
        levenshtein distance ratio of similarity between two strings
        For all i and j, distance[i,j] will contain the Levenshtein
        distance between the first i characters of s and the
        first j characters of t
    """
    # Initialize matrix of zeros
    # Set all to lower (Case insensitive)
    s = s.lower()
    t = t.lower()
    rows = len(s) + 1
    cols = len(t) + 1
    distance = np.zeros((rows, cols), dtype=int)

    # Populate matrix of zeros with the indeces of each character of both strings
    for i in range(1, rows):
        for k in range(1, cols):
            distance[i][0] = i
            distance[0][k] = k

    # Iterate over the matrix to compute the cost of deletions,insertions and/or substitutions
    for col in range(1, cols):
        for row in range(1, rows):
            if s[row - 1] == t[col - 1]:
                cost = 0  # If the characters are the same in the two strings in a given position [i,j] then the cost is 0
            else:
                # In order to align the results with those of the Python Levenshtein package, if we choose to calculate the ratio
                # the cost of a substitution is 2. If we calculate just distance, then the cost of a substitution is 1.
                if ratio_calc == True:
                    cost = 2
                else:
                    cost = 1
            distance[row][col] = min(distance[row - 1][col] + 1,  # Cost of deletions
                                     distance[row][col - 1] + 1,  # Cost of insertions
                                     distance[row - 1][col - 1] + cost)  # Cost of substitutions
    if ratio_calc == True:
        # Computation of the Levenshtein Distance Ratio
        Ratio = ((len(s) + len(t)) - distance[row][col]) / (len(s) + len(t))
        return Ratio
    else:
        # print(distance) # Uncomment if you want to see the matrix showing how the algorithm computes the cost of deletions,
        # insertions and/or substitutions
        # This is the minimum number of edits needed to convert string a to string b
        return "The strings are {} edits away".format(distance[row][col])