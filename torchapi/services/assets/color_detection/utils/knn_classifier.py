import csv
import random
import math
import operator
import cv2
import os

path=os.path.dirname(__file__)

# calculation of euclidean distance
def calculateEuclideanDistance(variable1, variable2, length):
    distance = 0
    for x in range(length):
        distance += pow(variable1[x] - variable2[x], 2)
    return math.sqrt(distance)


# get k nearest neigbors
def kNearestNeighbors(training_feature_vector, testInstance, k):
    distances = []
    length = len(testInstance)
    for x in range(len(training_feature_vector)):
        dist = calculateEuclideanDistance(testInstance,
                training_feature_vector[x], length)
        if (dist == 0):
            distances.append((training_feature_vector[x], dist))
        distances.append((training_feature_vector[x], dist))
    distances.sort(key=operator.itemgetter(1))
    neighbors = []
    for x in range(k):
        neighbors.append(distances[x][0])
    return neighbors


# votes of neighbors
def responseOfNeighbors(neighbors):
    all_possible_neighbors = {}
    for x in range(len(neighbors)):
        response = neighbors[x][-1]
        if response in all_possible_neighbors:
            all_possible_neighbors[response] += 1
        else:
            all_possible_neighbors[response] = 1
    sortedVotes = sorted(all_possible_neighbors.items(),
                         key=operator.itemgetter(1), reverse=True)
    return sortedVotes[0][0]


# Load image feature data to training feature vectors and test feature vector
def loadDataset(
    training_file,
    test_file,
    training_feature_vector=[],
    test_feature_vector=[],
    ):
    try:
        with open(os.path.join(path, training_file)) as csvfile:
            lines = csv.reader(csvfile)
            dataset = list(lines)
            for x in range(len(dataset)):
                for y in range(3):
                    dataset[x][y] = float(dataset[x][y])
                training_feature_vector.append(dataset[x])
    except:
        raise Exception("Traininig file could not load: "+training_file)

    try:
        
        with open(os.path.join(path, test_file)) as csvfile:
            lines = csv.reader(csvfile)
            dataset = list(lines)
            for x in range(len(dataset)):
                for y in range(3):
                    dataset[x][y] = float(dataset[x][y])
                test_feature_vector.append(dataset[x])
    except:
        raise Exception("Test file could not load: "+test_file)


def classify(training_data, test_data):
    training_feature_vector = []  # training feature vector
    test_feature_vector = []  # test feature vector
    loadDataset(training_data,test_data, training_feature_vector, test_feature_vector)
    classifier_prediction = []  # predictions
    k = 3  # K value of k nearest neighbor
    for x in range(len(test_feature_vector)):
        neighbors = kNearestNeighbors(training_feature_vector, test_feature_vector[x], k)
        result = responseOfNeighbors(neighbors)
        classifier_prediction.append(result)
    return classifier_prediction[0]
