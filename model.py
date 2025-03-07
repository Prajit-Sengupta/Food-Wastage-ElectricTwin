import pandas as pd
import numpy as np
from datetime import datetime, date, timedelta
from flask import Flask, render_template, request
import os
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Embedding, Flatten, Dot, Dense, Concatenate
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

app = Flask(__name__)

# Data paths
INVENTORY_FILE = 'inventory.csv'
RECIPE_FILE = 'recipes.csv'  # Changed to load real recipes
USER_FILE = 'users.csv'
INTERACTIONS_FILE = 'interactions.csv'
DEFAULT_EXPIRATION_DAYS = 7
NUM_RECOMMENDATIONS = 4  # Number of recipes to recommend
EXPIRATION_THRESHOLD = 14  # Recommend items expiring within 14 days

# --- Data Loading and Preprocessing ---

def load_inventory(filepath=INVENTORY_FILE):
    try:
        inventory = pd.read_csv(filepath)
        if 'expiration_date' in inventory.columns:
            inventory['expiration_date'] = pd.to_datetime(inventory['expiration_date'], errors='coerce')
            inventory['expiration_date'] = inventory['expiration_date'].fillna(pd.to_datetime(date.today()) + pd.to_timedelta(DEFAULT_EXPIRATION_DAYS, unit='D'))
        else:
            inventory['expiration_date'] = pd.to_datetime(date.today()) + pd.to_timedelta(DEFAULT_EXPIRATION_DAYS, unit='D')
        return inventory
    except FileNotFoundError:
        print(f"Error: Inventory file not found at {filepath}")
        return pd.DataFrame()

def load_recipes(filepath=RECIPE_FILE):
    try:
        recipes = pd.read_csv(filepath)
        return recipes
    except FileNotFoundError:
        print(f"Error: Recipe file not found at {filepath}")
        return pd.DataFrame()

def load_users(filepath=USER_FILE):
    try:
        users = pd.read_csv(filepath)
        return users
    except FileNotFoundError:
        print(f"Error: User file not found at {filepath}")
        return pd.DataFrame()

def load_interactions(filepath=INTERACTIONS_FILE):
    try:
        interactions = pd.read_csv(filepath)
        return interactions
    except FileNotFoundError:
        print(f"Error: Interactions file not found at {filepath}")
        return pd.DataFrame()

def create_ingredient_list(recipes):
    """Creates a list of all unique ingredients."""
    all_ingredients = set()
    for _, recipe in recipes.iterrows():
        ingredients = recipe['ingredients'].split(',')
        all_ingredients.update(ingredients)
    return sorted(list(all_ingredients))

# --- Model Building ---

def create_embedding_model(num_users, num_recipes, embedding_size=50, l2_reg=1e-6):
    """Creates a collaborative filtering model with user and recipe embeddings."""
    # User input and embedding
    user_input = Input(shape=(1,), name='user_input')
    user_embedding = Embedding(num_users, embedding_size, name='user_embedding', embeddings_regularizer=l2(l2_reg))(user_input)
    user_vec = Flatten(name='user_vec')(user_embedding)

    # Recipe input and embedding
    recipe_input = Input(shape=(1,), name='recipe_input')
    recipe_embedding = Embedding(num_recipes, embedding_size, name='recipe_embedding', embeddings_regularizer=l2(l2_reg))(recipe_input)
    recipe_vec = Flatten(name='recipe_vec')(recipe_embedding)

    # Dot product of user and recipe embeddings
    dot_product = Dot(axes=1, name='dot_product')([user_vec, recipe_vec])

    # Concatenate embeddings and add dense layers
    concat = Concatenate()([user_vec, recipe_vec])
    dense1 = Dense(128, activation='relu')(concat)
    dense2 = Dense(32, activation='relu')(dense1)
    output = Dense(1, activation='sigmoid')(dense2)  # Sigmoid for rating prediction (0-1)

    model = Model(inputs=[user_input, recipe_input], outputs=output)
    model.compile(optimizer=Adam(learning_rate=0.001), loss='binary_crossentropy', metrics=['accuracy'])
    return model

def train_model(model, interactions_df, user_id_col, recipe_id_col, rating_col, test_size=0.2):
    """Trains the collaborative filtering model."""
    # Split data into training and testing sets
    train_df, test_df = train_test_split(interactions_df, test_size=test_size, random_state=42)

    user_train = train_df[user_id_col].values
    recipe_train = train_df[recipe_id_col].values
    rating_train = train_df[rating_col].values

    user_test = test_df[user_id_col].values
    recipe_test = test_df[recipe_id_col].values
    rating_test = test_df[rating_col].values

    # Train the model
    print("Training with: num_users=", model.get_layer('user_embedding').input_dim, ", num_recipes=", model.get_layer('recipe_embedding').input_dim)
    model.fit([user_train, recipe_train], rating_train, epochs=10, batch_size=64, validation_data=([user_test, recipe_test], rating_test))
    return model

def create_user_recipe_interactions(users, recipes, inventory):
    """Creates synthetic user-recipe interaction data with a very strong expiration bias."""
    interactions = []
    for user_id in users['user_id']:
        for recipe_id in recipes['recipe_id']:
            # Simulate a rating based on ingredient overlap and expiration dates
            recipe_ingredients = set(recipes.loc[recipes['recipe_id'] == recipe_id, 'ingredients'].iloc[0].split(','))
            available_ingredients = set(inventory['item'])
            common_ingredients = recipe_ingredients.intersection(available_ingredients)

            # VERY Strong Expiration Bias
            expiring_bonus = 0
            expiring_ingredients = []
            for ingredient in common_ingredients:
                ingredient_data = inventory[inventory['item'] == ingredient].iloc[0]
                expiration_date = ingredient_data['expiration_date']

                time_until_expiration = (expiration_date - datetime.now()).days
                if time_until_expiration <= EXPIRATION_THRESHOLD:  # Only consider items expiring soon
                    bonus = max(0, 50 * np.exp(-time_until_expiration / 1))  # Even stronger bias
                    expiring_bonus += bonus
                    expiring_ingredients.append((ingredient, time_until_expiration))
                else:
                  expiring_ingredients.append((ingredient, time_until_expiration)) #Always keep a log of expiring

            overlap_score = len(common_ingredients) / len(recipe_ingredients) if recipe_ingredients else 0
            rating = min(1.0, overlap_score + (expiring_bonus / 100))  # Normalize
            interactions.append({'user_id': user_id, 'recipe_id': recipe_id, 'rating': rating, 'expiring_ingredients': expiring_ingredients})

    return pd.DataFrame(interactions)

def get_user_recommendations(model, user_id, num_recipes, recipes, inventory, interactions):  # ADDED INTERACTIONS HERE
    """Recommends recipes for a given user, highlighting expiring ingredients."""
    recipe_ids = recipes['recipe_id'].values
    user_input = np.full(len(recipe_ids), user_id)  # User input for all recipes

    # Predict ratings for all recipes for the user
    predictions = model.predict([user_input, recipe_ids])
    predicted_ratings = predictions.flatten()

    # Create a DataFrame to store recipe IDs and predicted ratings
    recommendations_df = pd.DataFrame({'recipe_id': recipe_ids, 'predicted_rating': predicted_ratings})

    # Sort recipes by predicted rating in descending order
    recommendations_df = recommendations_df.sort_values(by='predicted_rating', ascending=False)

    # Get the top N recommended recipe IDs
    top_recipe_ids = recommendations_df['recipe_id'].head(num_recipes).tolist()
    recommended_recipes = recipes[recipes['recipe_id'].isin(top_recipe_ids)]

    # Highlight expiring ingredients and sort by expiration date
    recommendations = []
    for _, recipe in recommended_recipes.iterrows():
        expiring_info = interactions[(interactions['recipe_id'] == recipe['recipe_id']) & (interactions['user_id'] == user_id)]['expiring_ingredients'].iloc[0]
        expiring_info = [(item, days) for item, days in expiring_info if days <= EXPIRATION_THRESHOLD]  # Filter expiring ingredients to those soon to expire

        if expiring_info:
            expiring_info.sort(key=lambda x: x[1])  # Sort by expiration date (days)
            expiring_ingredients_text = ", ".join([f"{item} ({days} days)" for item, days in expiring_info])
            recommendations.append({
                'name': recipe['name'],
                'expiring_ingredients': expiring_ingredients_text
            })
        else:
            recommendations.append({
                'name': recipe['name'],
                'expiring_ingredients': "No expiring ingredients (within the next 14 days) in this recipe."
            })

    return recommendations
# --- Flask Routes ---

@app.route('/', methods=['GET'])
def index():
    inventory = load_inventory()
    recipes = load_recipes()
    users = load_users()

    # Ensure data is loaded
    if inventory.empty or recipes.empty or users.empty:
        return "Error: Could not load data. Check file paths and format."

    # Create IDs, important to be zero-based for the embedding layer
    recipes['recipe_id'] = range(0, len(recipes))
    users['user_id'] = range(0, len(users))
    inventory['inventory_id'] = range(1, len(inventory) + 1)

    # --- Data Preprocessing for the Model ---
    num_users = len(users)
    num_recipes = len(recipes)

    # Force generation of interactions file again.
    if os.path.exists(INTERACTIONS_FILE):
       os.remove(INTERACTIONS_FILE)

    interactions = load_interactions()  # Load again
    if interactions.empty:  # Create a new one if empty
        interactions = create_user_recipe_interactions(users, recipes, inventory)

    # Ensure ids are int, or the embedding layer will not work.
    interactions['recipe_id'] = interactions['recipe_id'].astype(int)
    interactions['user_id'] = interactions['user_id'].astype(int)

    # Model Training
    model = create_embedding_model(num_users, num_recipes)
    print("Creating model with: num_users=", num_users, ", num_recipes=", num_recipes)
    model = train_model(model, interactions, 'user_id', 'recipe_id', 'rating')

    # Provide a value when creating. INTERACTIONS ADDED HERE
    user_id = 0  # Default user
    recommendations = get_user_recommendations(model, user_id, NUM_RECOMMENDATIONS, recipes, inventory, interactions)

    return render_template('index.html', recommendations=recommendations)

# --- Main ---
if __name__ == '__main__':
    # Create dummy CSV files if they don't exist
    if not os.path.exists(INVENTORY_FILE):
        import pandas as pd
        import datetime
        import random

        def generate_inventory(num_items=150):
            items = [
                "apple", "banana", "orange", "milk", "eggs", "bread", "chicken", "tomatoes", "onions", "garlic",
                "broccoli", "carrots", "potatoes", "beef", "cheese", "spinach", "cucumber", "bell peppers", "zucchini",
                "mushrooms", "salmon", "rice", "pasta", "beans", "lentils", "yogurt", "butter", "cream cheese", "sour cream",
                "lettuce", "cabbage", "avocado", "corn", "peas", "green beans", "pork", "turkey", "shrimp", "tofu",
                "almonds", "walnuts", "cashews", "peanuts", "oats", "flour", "sugar", "salt", "pepper", "olive oil",
                "vinegar", "mustard", "ketchup", "mayonnaise", "soy sauce", "honey", "maple syrup", "jam", "jelly",
                "peanut butter", "chocolate", "coffee", "tea", "juice", "soda", "cereal", "crackers", "cookies", "chips",
                "pretzels", "popcorn", "canned tomatoes", "canned beans", "canned corn", "canned tuna", "canned soup",
                "broth", "frozen peas", "frozen spinach", "frozen berries", "pizza dough", "bagels", "muffins", "croissants",
                "donuts", "cake mix", "frosting", "sprinkles", "baking powder", "baking soda", "yeast", "cornstarch",
                "vanilla extract", "cinnamon", "nutmeg", "ginger", "cloves", "cumin", "paprika", "chili powder", "oregano",
                "basil", "thyme", "rosemary", "parsley", "cilantro", "lemons", "limes", "grapes", "strawberries",
                "blueberries", "raspberries", "blackberries", "peaches", "plums", "cherries", "kiwi", "pineapple", "mango",
                "watermelon", "cantaloupe", "honeydew", "coconut", "dates", "raisins", "dried cranberries", "sunflower seeds",
                "pumpkin seeds", "chia seeds", "sesame seeds", "poppy seeds"
            ]

            inventory_data = []
            today = datetime.date.today()
            for i in range(num_items):
                item = random.choice(items)
                expiration_date = today + datetime.timedelta(days=random.randint(1, 30))  # Expiration within 30 days
                inventory_data.append({'item': item, 'expiration_date': expiration_date.strftime('%Y-%m-%d')})

            df = pd.DataFrame(inventory_data)
            df.to_csv("inventory.csv", index=False)
            print("inventory.csv generated successfully.")
        generate_inventory()
    if not os.path.exists(RECIPE_FILE):
        # Load real recipes from a CSV file
        dummy_recipes = pd.DataFrame({
            'name': ['Scrambled Eggs', 'Chicken Sandwich', 'Tomato Soup', 'Garlic Bread', 'Onion Soup', 'Broccoli Cheese Soup', 'Spinach Salad'],
            'ingredients': ['eggs,milk', 'chicken,bread,tomatoes', 'tomatoes,onions,garlic', 'bread,garlic', 'onions,broth', 'broccoli,cheese,broth', 'spinach,cheese,tomatoes']
        })
        dummy_recipes.to_csv(RECIPE_FILE, index=False)

    if not os.path.exists(USER_FILE):
        dummy_users = pd.DataFrame({'user_id': [0], 'preferences': ['general']})
        dummy_users.to_csv(USER_FILE, index=False)

    if not os.path.exists(INTERACTIONS_FILE):
        dummy_interactions = pd.DataFrame({'user_id': [], 'recipe_id': [], 'rating': []})
        dummy_interactions.to_csv(INTERACTIONS_FILE, index=False)

    app.run(debug=True)