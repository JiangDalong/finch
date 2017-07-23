from scipy.spatial.distance import correlation 
import numpy as np
import pandas as pd


def similarity(user1, user2):
    user1 = np.array(user1) - np.nanmean(user1)
    user2 = np.array(user2) - np.nanmean(user2)
    commons = [i for i in range(len(user1)) if user1[i]>0 and user2[i]>0]
    if len(commons) == 0:
        return 0
    else:
        r1 = np.array([user1[i] for i in commons])
        r2 = np.array([user2[i] for i in commons])
        return correlation(r1, r2)


def nearest_ratings(active_user, top_k, rating_matrix):
    sim_matrix = pd.DataFrame(index=rating_matrix.index, columns=['similarity'])
    for u in rating_matrix.index:
        sim_matrix.loc[u] = similarity(rating_matrix.loc[active_user], rating_matrix.loc[u])
    sim_matrix.sort_values(['similarity'], ascending=[0], inplace=True)

    neighbour_sims = sim_matrix[:top_k]
    neighbour_ratings = rating_matrix.loc[neighbour_sims.index]

    predicted_item_ratings = pd.DataFrame(index=rating_matrix.columns, columns=['rating'])
    for i in rating_matrix.columns:
        # predicted_item_rating = np.nanmean(rating_matrix.loc[active_user])
        predicted_item_rating = 0
        for u in neighbour_ratings.index:
            if rating_matrix.loc[u, i] > 0:
                weight = neighbour_sims.loc[u, 'similarity']
                predicted_item_rating += (rating_matrix.loc[u, i] - np.nanmean(rating_matrix.loc[u])) * weight
        predicted_item_ratings.loc[i, 'rating'] = predicted_item_rating
    return predicted_item_ratings


def recommender(active_user, top_n, rating_matrix, movie_info):
    predicted_item_ratings = nearest_ratings(active_user, 10, rating_matrix)
    
    movies_watched = list(rating_matrix.loc[active_user].loc[rating_matrix.loc[active_user]>0].index)
    
    predicted_item_ratings.drop(movies_watched, inplace=True)

    recommendations = predicted_item_ratings.sort_values(['rating'], ascending=[0])[:top_n]

    titles = movie_info.loc[movie_info.itemid.isin(recommendations.index)]
    
    return list(titles.title)
