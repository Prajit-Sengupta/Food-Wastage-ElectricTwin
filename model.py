import pandas as pd
from datetime import datetime, date
from flask import Flask, render_template, request
import os
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Data paths (relative to your project directory)
INVENTORY_FILE = 'inventory.csv'
RECIPE_FILE = 'recipes.csv'
DEFAULT_EXPIRATION_DAYS = 7  # Default if no expiration is provided

# Data Loading and Preprocessing

def load_inventory(filepath=INVENTORY_FILE):
    try:
        inventory = pd.read_csv(filepath)
        # Convert 'expiration_date' to datetime objects
        if 'expiration_date' in inventory.columns:
            inventory['expiration_date'] = pd.to_datetime(inventory['expiration_date'], errors='coerce')
            inventory['expiration_date'] = inventory['expiration_date'].fillna(pd.to_datetime(date.today()) + pd.to_timedelta(DEFAULT_EXPIRATION_DAYS, unit='D')) #Fill NaN with a default date
        else:
            #If the expiration_date column doesn't exists, fill it with a default expiration.
            inventory['expiration_date'] = pd.to_datetime(date.today()) + pd.to_timedelta(DEFAULT_EXPIRATION_DAYS, unit='D')

        return inventory
    except FileNotFoundError:
        print(f"Error: Inventory file not found at {filepath}")
        return pd.DataFrame()  # Return an empty DataFrame

def load_recipes(filepath=RECIPE_FILE):
    try:
        recipes = pd.read_csv(filepath)
        return recipes
    except FileNotFoundError:
        print(f"Error: Recipe file not found at {filepath}")
        return pd.DataFrame()

def calculate_priority_score(expiration_date):
    """Calculates a priority score based on how close the expiration date is."""
    time_until_expiration = (expiration_date - datetime.now()).days
    #Sooner expiration gets a higher score
    if time_until_expiration <= 0:
      return 100 #Highest priority
    return max(0, 100 - (time_until_expiration * 5)) # Adjust scaling as needed


def create_ingredient_vector(ingredients, all_ingredients):
    """Creates a binary vector representing the presence of each ingredient in a recipe."""
    vector = [1 if ingredient in ingredients else 0 for ingredient in all_ingredients]
    return vector

def find_best_matches(inventory_items, inventory, recipes):
    """Finds the best recipe matches based on available inventory, including considering expiration dates."""
    inventory['priority_score'] = inventory['expiration_date'].apply(calculate_priority_score)
    inventory = inventory[inventory['item'].isin(inventory_items)]  # Filter inventory based on user input.

    # Create a list of all unique ingredients across all recipes
    all_ingredients = set()
    for _, recipe in recipes.iterrows():
        ingredients = recipe['ingredients'].split(',')
        all_ingredients.update(ingredients)
    all_ingredients = sorted(list(all_ingredients))

    # Create ingredient vectors for each recipe
    recipe_vectors = {}
    for _, recipe in recipes.iterrows():
        recipe_vectors[recipe['name']] = create_ingredient_vector(recipe['ingredients'].split(','), all_ingredients)

    # Create an ingredient vector for the user's inventory
    inventory_vector = create_ingredient_vector(inventory['item'].tolist(), all_ingredients)

    # Calculate cosine similarity between the inventory vector and each recipe vector
    recipe_scores = {}
    for recipe_name, recipe_vector in recipe_vectors.items():
        similarity = cosine_similarity([inventory_vector], [recipe_vector])[0][0]
        recipe_scores[recipe_name] = similarity

    # Sort recipes by similarity score
    sorted_recipes = sorted(recipe_scores.items(), key=lambda x: x[1], reverse=True)

    # Consider expiration dates and calculate a final score
    final_scores = {}
    for recipe_name, similarity_score in sorted_recipes:
        recipe_ingredients = recipes[recipes['name'] == recipe_name]['ingredients'].iloc[0].split(',')
        expiring_ingredient_score = 0
        for ingredient in recipe_ingredients:
            if ingredient in inventory['item'].values:
                ingredient_data = inventory[inventory['item'] == ingredient].iloc[0]
                expiring_ingredient_score += ingredient_data['priority_score']

        # Combine similarity score and expiration score (adjust weights as needed)
        final_score = (0.7 * similarity_score) + (0.3 * expiring_ingredient_score)  #Example weights
        final_scores[recipe_name] = final_score

    # Sort recipes by final score
    sorted_recipes = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_recipes


# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    inventory = load_inventory()
    recipes = load_recipes()

    if inventory.empty or recipes.empty:
        return "Error: Could not load inventory or recipe data.  Check file paths and format."

    if request.method == 'POST':
        inventory_items = request.form.getlist('inventory_items')
        if not inventory_items:
            recommendations = []  # No items selected, so no recommendations.
        else:
            recommendations = find_best_matches(inventory_items, inventory, recipes)
    else:
        recommendations = []  # No recommendations initially.

    return render_template('index.html', inventory=inventory['item'].tolist(), recommendations=recommendations)


if __name__ == '__main__':
    # Create dummy CSV files if they don't exist
    if not os.path.exists(INVENTORY_FILE):
        dummy_inventory = pd.DataFrame({
            'item': ['milk', 'eggs', 'bread', 'chicken', 'tomatoes'],
            'expiration_date': [date.today() + pd.to_timedelta(2, unit='D'),
                                 date.today() + pd.to_timedelta(1, unit='D'),
                                 date.today() + pd.to_timedelta(5, unit='D'),
                                 date.today() + pd.to_timedelta(0, unit='D'),
                                 date.today() + pd.to_timedelta(7, unit='D')]
        })
        dummy_inventory.to_csv(INVENTORY_FILE, index=False)

    if not os.path.exists(RECIPE_FILE):
        dummy_recipes = pd.DataFrame({
            'name': ['Scrambled Eggs', 'Chicken Sandwich', 'Tomato Soup'],
            'ingredients': ['eggs,milk', 'chicken,bread,tomatoes', 'tomatoes']
        })
        dummy_recipes.to_csv(RECIPE_FILE, index=False)

    app.run(debug=True)