import pandas as pd
import numpy as np
import scipy.sparse as sparse
import query
import json
from sklearn.metrics.pairwise import cosine_similarity
from SPARQLWrapper import SPARQLWrapper, JSON

# Movielens userID
userID = 107493

# Item based collaborative filtering, creating sparse matrix
data = pd.read_csv('datasets/ratings.csv', sep = ',', encoding= 'iso-8859-1')

users = list(np.sort(data.userId.unique()))    # get all unique users
movies = list(np.sort(data.movieId.unique()))  # ger all unique movies
rating = list(data.rating.astype(float))       # get ratings
rows = data.userId.astype(pd.api.types.CategoricalDtype(categories = users)).cat.codes      # Get the associated row indices
cols = data.movieId.astype(pd.api.types.CategoricalDtype(categories = movies)).cat.codes    # Get the associated column indices

# Create the rating matrix as a sparse matrix, each row is a user and each column is a movie
rating_matrix = sparse.csr_matrix((rating, (rows, cols)), shape = (len(users), len(movies)  )  )

# create the item similarity matrix
# items = movies = columns -> transpose
sim_matrix = cosine_similarity(rating_matrix.transpose(), dense_output=False)

# execute SPARQL query...
#results = query.get_results()

# ... or open stored query result
with open('jsons/queryResult.json') as json_file:
    results = json.load(json_file)

# process imdbId list, removing the "tt" at the beginning
imdbIDlist = []
for elem in results["results"]["bindings"]:
    imdbIDlist.append(elem["imdbID"]["value"][2:])

# get movieID list from imdbID list
links = pd.read_csv('datasets/links.csv', sep = ',', 
        dtype=str, usecols=[0,1]).set_index('imdbId').to_dict()

movieIDlist = []
for imdbID in imdbIDlist:
    try:
        movieIDlist.append(links["movieId"][imdbID])
    except:
        #print("Missing imdbID in links: {id}".format(id=imdbID))
        pass

# get ratings given by the user we want to give recommendations to
userRatings = rating_matrix[users.index(userID)].toarray()[0]

# Predict rating from userId for a certain movie, given the topN most similar movies
def predict_rating(colIndex):
    # Do not recommend already rated items
    # give them the lowest rating
    if int(userRatings[colIndex]) <> 0:
        return 0

    # pairs (0,index) -> cosine, sorted by cosine, ignore cut first since it's the movie itself (cosine = 1)
    mostSimilar = dict(sorted(sim_matrix.getrow(colIndex).todok().items(), key=lambda x: x[1], reverse=True)[1:])
    #print(mostSimilar.items()[:10])
    num = 0
    den = 0
    i = 0
    for mv in mostSimilar.items():
        rating = userRatings[mv[0][1]]
        #ignore non rated items for predicting the score
        if (rating > 0):
            num += rating * mv[1]
            den += mv[1]
            i += 1
        #use no more than the ten most similar rated
        if (i>10):
            break
    return num/den

recommendedRatings = {}

# For each recommended movie, predict its rating 
for i in movieIDlist:
    recommendedRatings[i] = predict_rating(movies.index(int(i)))

titles = pd.read_csv('datasets/movies.csv', sep = ',', 
        dtype=str, usecols=[0,1]).set_index('movieId').to_dict()

lst = sorted(recommendedRatings.items(), key=lambda x: x[1], reverse=True)[:10]

# Replace movieId with title
titlesRating = {}
for i in lst:
    titlesRating[titles["title"][i[0]]] = i[1]

print (titlesRating)