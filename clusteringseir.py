#############################################################################################################
#### Proyecto creado por Claudio Quevedo Gallardo, estudiante de Ing. Civil en Bioinformática, Utal 2020.####
#33##########################################################################################################
import pandas as pd
import pymongo
from pymongo import MongoClient
import pprint
from sklearn.metrics import pairwise_distances_argmin
from pandas import DataFrame
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin_min
from sklearn.preprocessing import Normalizer


def find_clusters(X, n_clusters, rseed=2):
    # 1. Randomly choose clusters
    rng = np.random.RandomState(rseed)
    i = rng.permutation(X.shape[0])[:n_clusters]
    centers = X[i]
    while True:
        # 2a. Assign labels based on closest center
        labels = pairwise_distances_argmin(X, centers)
        # 2b. Find new centers from means of points
        new_centers = np.array([X[labels == i].mean(0)
                                for i in range(n_clusters)])
        # 2c. Check for convergence
        if np.all(centers == new_centers):
            break
        centers = new_centers
    return centers, labels

client = MongoClient('localhost',27017)
db = client['SEIR']
principal_estadisticas = db['principal_estadisticas']
principal_cluster = db['principal_cluster']
records = []

for data in principal_estadisticas.find({}):
    records.append([data['comuna'],data['maxS']/data['poblacion'],
    data['maxE']/data['poblacion'],data['maxI']/data['poblacion'],
    data['maxR']/data['poblacion'], data['maxDia']])

df = DataFrame(records, columns=['comuna','maxS','maxE','maxI','maxR','maxDia'])
X = np.array(df[['maxS','maxE','maxI','maxR','maxDia']])
transformer = Normalizer().fit(X)
normX = transformer.transform(X)

n_clusters = 4
centroids, labels = find_clusters(normX, n_clusters)

extrema = []
alta = []
media = []
baja = []

for cluster,comuna in zip(labels,records):
    if (cluster == 0):
        extrema.append([comuna[0],comuna[1],comuna[2],comuna[3],comuna[4],comuna[5]])
        a = principal_cluster.insert_one({'comuna':comuna[0], 'necesidad':'EXTREMA'})
    elif (cluster == 1):
        alta.append([comuna[0],comuna[1],comuna[2],comuna[3],comuna[4],comuna[5]])
        a = principal_cluster.insert_one({'comuna':comuna[0], 'necesidad':'ALTA'})
    elif (cluster == 2):
        media.append([comuna[0],comuna[1],comuna[2],comuna[3],comuna[4],comuna[5]])
        a = principal_cluster.insert_one({'comuna':comuna[0], 'necesidad':'MEDIA'})
    else:
        baja.append([comuna[0],comuna[1],comuna[2],comuna[3],comuna[4],comuna[5]])
        a = principal_cluster.insert_one({'comuna':comuna[0], 'necesidad':'BAJA'})


print("\nComunas con extrema necesidad de instrumentación médica.\n")
for comuna in extrema:
    print(comuna[0])

print("\nComunas con alta necesidad de instrumentación médica.\n")
for comuna in alta:
    print(comuna[0])

print("\nComunas con media necesidad de instrumentación médica.\n")
for comuna in media:
    print(comuna[0])

print("\nComunas con baja necesidad de instrumentación médica.\n")
for comuna in baja:
    print(comuna[0])

#oo = principal_cluster.find({'necesidad': 'ALTA'})
#for a in oo:
#    pprint.pprint(a)
