import pandas as pd
import numpy as np
from sklearn.manifold import TSNE 
from scipy.spatial.distance import cdist

df = pd.read_csv("data/cosmetics.csv")

def categories():

    categories = df['Label'].unique()
    return categories

def brands(category):

    category_subset = df[df['Label'] == category]
    brands = sorted(category_subset['Brand'].unique())
    return brands,category_subset

def products(brand,category_subset):
    category_brand_subset = category_subset[category_subset['Brand'] == brand]
    products = sorted(category_brand_subset['Name'].unique() )
    return products


def oh_encoder(tokens,N,ingredient_idx):
    x = np.zeros(N)
    for ingredient in tokens:
        # Get the index for each ingredient
        idx = ingredient_idx[ingredient]
        # Put 1 at the corresponding indices
        x[idx] = 1
    return x

def closest_point(point, points):
    """ Find closest point from a list of points. """
    return points[cdist([point], points).argmin()]

def recommend(category,product):

    if category is not None:
        category_subset = df[df['Label'] == category]

    if product is not None:
        #skincare_type = category_subset[category_subset[str(skin_type)] == 1]

        # Reset index
        category_subset = category_subset.reset_index(drop=True)

        # Display data frame
        #st.dataframe(category_subset)

        # Initialize dictionary, list, and initial index
        ingredient_idx = {}
        corpus = []
        idx = 0

    # For loop for tokenization
        for i in range(len(category_subset)):    
            ingredients = category_subset['Ingredients'][i]
            ingredients_lower = ingredients.lower()
            tokens = ingredients_lower.split(', ')
            corpus.append(tokens)
            for ingredient in tokens:
                if ingredient not in ingredient_idx:
                    ingredient_idx[ingredient] = idx
                    idx += 1

                    
        # Get the number of items and tokens 
        M = len(category_subset)
        N = len(ingredient_idx)

        # Initialize a matrix of zeros
        A = np.zeros((M,N))

        # Make a document-term matrix
        i = 0
        for tokens in corpus:
            A[i, :] = oh_encoder(tokens,N,ingredient_idx)
            i +=1

    model = TSNE(n_components = 2, learning_rate = 150, random_state = 42)
    tsne_features = model.fit_transform(A)

    # Make X, Y columns 
    category_subset['X'] = tsne_features[:, 0]
    category_subset['Y'] = tsne_features[:, 1]

    target = category_subset[category_subset['Name'] == product]

    target_x = target['X'].values[0]
    target_y = target['Y'].values[0]

    df1 = pd.DataFrame()
    df1['point'] = [(x, y) for x,y in zip(category_subset['X'], category_subset['Y'])]

    category_subset['distance'] = [cdist(np.array([[target_x,target_y]]), np.array([product]), metric='euclidean') for product in df1['point']]

    # arrange by descending order
    top_matches = category_subset.sort_values(by=['distance'])

    # Compute ingredients in common
    target_ingredients = target.Ingredients.values
    c1_list = target_ingredients[0].split(",")
    c1_list = [x.strip(' ') for x in c1_list]
    c1_set = set(c1_list)

    top_matches['Ingredients in common'] = [c1_set.intersection( set([x.strip(' ')for x in product.split(",")]) ) for product in top_matches['Ingredients']]

    # Select relevant columns
    top_matches = top_matches[['Label', 'Brand', 'Name', 'Price', 'Ingredients','Ingredients in common']]
    top_matches = top_matches.reset_index(drop=True)
    top_matches = top_matches.drop(top_matches.index[0])
    
    return top_matches.head(5)

# print(recommend('Cleanser','Bergamot Herbal Extract Toner'))
# a,b = brands('Cleanser')
# print(b)
# print(products('BOSCIA',b))
# print(categories())
