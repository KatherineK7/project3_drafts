
import os
import requests
import pandas as pd
import json
import sqlalchemy
from sqlalchemy import create_engine
from flask import Flask, request, render_template, jsonify
import pymysql
pymysql.install_as_MySQLdb()

is_heroku = False
if 'IS_HEROKU' in os.environ:
    is_heroku = True
    remote_db_endpoint = os.environ.get('remote_db_endpoint')
    remote_db_port = os.environ.get('remote_db_port')
    remote_db_name = os.environ.get('remote_db_name')
    remote_db_user = os.environ.get('remote_db_user')
    remote_db_pwd = os.environ.get('remote_db_pwd')
    x_rapidapi_key = os.environ.get('x_rapidapi_key')
    x_rapidapi_host = os.environ.get('x_rapidapi_host')
    spoonacular_API = os.environ.get('spoonacular_API')
else:
    from config import remote_db_endpoint, remote_db_port, remote_db_name, remote_db_user, remote_db_pwd
    from config import x_rapidapi_key, x_rapidapi_host, spoonacular_API


def getRecipeMetadata(query, cuisine, type_of_recipe, calories, cookingMinutes): 
    
    #######################################
    # consider separating this part into a function
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/searchComplex"
    
    # these will come from form controls
    query = query
    cuisine = cuisine
    type_of_recipe = type_of_recipe
    calories = calories
    cookingMinutes = cookingMinutes
    # ranking = "2"
    minCalories = "0"
    maxCalories = "15000"
    # minFat = "5"
    # maxFat = "100"
    # minProtein = "5"
    # maxProtein = "100"
    # minCarbs = "5"
    # maxCarbs = "100"
    
    querystring = {"limitLicense": "<REQUIRED>",
        "offset": "0",
        "number": "10",
        "query": query,
        "cuisine": cuisine,
        "cookingMinutes": cookingMinutes,                   # NEW
        "calories": calories,                               # NEW
        #"includeIngredients": "onions, lettuce, tomato",
        #"excludeIngredients": "coconut, mango",
        #"intolerances": "peanut, shellfish",
        "type": type_of_recipe,
        # "ranking": ranking,
        "minCalories": minCalories,
        "maxCalories": maxCalories,
        # "minFat": minFat,
        # "maxFat": maxFat,
        # "minProtein": minProtein,
        # "maxProtein": maxProtein,
        # "minCarbs": minCarbs,
        # "maxCarbs": maxCarbs,
        "instructionsRequired": "True",
        "addRecipeInformation": "True",
        "fillIngredients": "True",
    }
    print(querystring)
    
    headers = {
        'x-rapidapi-key': x_rapidapi_key,
        'x-rapidapi-host': x_rapidapi_host
        }
    
    response = requests.get(url, headers=headers, params=querystring)
    
    response_json = response.json()
    
    results = response_json['results']
    
    # consider making everything above part of a separate function
    #######################################

    recipe_metadata_list = []
    # recipe_steps = []
    
    # ingredients stuff
    for result in results:
        try:
            recipe_id = result['id']
            recipe_title = result['title']        
            cooking_minutes = result['cookingMinutes']
            health_score = result['healthScore']
            source_url = result['sourceUrl']
            image = result['image']
            likes = result['aggregateLikes']                # Brooke modification / previously, it had been 'likes'
            # cuisine = result['cuisines'][0]                 # Brooke addition (my slicing may not work; my method used a df)
            calories_serving = result['calories']           # Brooke addition
            carbohydrates_serving = result['carbs']         # Brooke addition
            servings = result['servings']                   # Brooke addition

            analyzedInstructions = result['analyzedInstructions']
            
        except Exception as e:
            print('--- error with something ---')
            print(result.keys())
            continue

        # 'directions': recipe_steps
        # # we need to figure out what this block is...
        # for result in results:
        #     servings = result['servings']     


        instruction_steps = analyzedInstructions[0]['steps']        # Brooke addition

        counter = 0
        
        recipe_steps = []                                                 # Brooke addition

        for item in instruction_steps:                              # Brooke addition
            counter = counter + 1                                   # Brooke addition
            step = item['step']                                     # Brooke addition
            numbered_step = f'{counter}. {step}'                    # Brooke addition
            recipe_steps.append(numbered_step)                      # Brooke addition
                    
        recipe_metadata = {
            'recipe_id': recipe_id,
            'recipe_title': recipe_title,
            'cooking_minutes': cooking_minutes,
            'health_score': health_score,
            'source_url': source_url,
            'image': image,
            'likes': likes,
            'calories_serving': calories_serving,
            'carbohydrates_serving': carbohydrates_serving,
            'servings': servings,
            'recipe_steps': recipe_steps
        }

        # will need to rename this
        recipe_metadata_list.append(recipe_metadata)

    recipe_metadata_df = pd.DataFrame(recipe_metadata_list)

    # dedupe ingredients df
    # recipe_metadata_df.drop_duplicates(inplace=True)

    return recipe_metadata_df




app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/about')
def about():
    
    return render_template('about.html')

@app.route('/api/ingredients')
def ingredients():
    
    recipe_ids = request.args.get('recipe_ids')

    recipe_ids_list = recipe_ids.split(',')
   
    capture_list = []

    for recipe_id in recipe_ids_list:
        url2 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={spoonacular_API}"    
        response = requests.get(url2)
        response_json = response.json()
        capture_list.append(response_json)
    
    # getIngredients(capture_list)

    #print(ingredients_json)
    return jsonify(capture_list)


@app.route('/api/getIngredientList')
def getIngredientList():
    
    recipe_ids = request.args.get('recipe_ids')

    capture_list = recipe_ids.split(',')
    
    # capture_list = []
   
    # for recipe_id in recipe_ids_list:
    #     url2 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={spoonacular_API}"    
    #     response = requests.get(url2)
    #     response_json = response.json()
    #     capture_list.append(response_json)

    grocery_df = test_MAJOR(capture_list)

    #grocery_df = getIngredients(recipe_ids_list)
    
    grocery_json = grocery_df.to_json(orient='records')
    
    return grocery_json

@app.route('/api/getCards')
def getCards():
    
    recipe_ids = request.args.get('recipe_ids')

    capture_list = recipe_ids.split(',')
    
    # capture_list = []
   
    # for recipe_id in recipe_ids_list:
    #     url2 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={spoonacular_API}"    
    #     response = requests.get(url2)
    #     response_json = response.json()
    #     capture_list.append(response_json)

    cards_df = metadataForCards(capture_list)

    #grocery_df = getIngredients(recipe_ids_list)
    
    cards_json = cards_df.to_json(orient='records')
    
    return cards_json



@app.route('/api/grocerylist')
def groceries():

    recipe_ids = request.args.get('recipe_ids')

    recipe_ids_list = recipe_ids.split(',')

    for recipe_id in recipe_ids_list:   
        grocery_df = getIngredients(recipe_id)
        # loop through these and come up with a way to combine the results
        print('################### THIS SHOULD BE COMING BACK! ####################')
        print(grocery_df.to_json(orient='records'))
        # add all of that to some dictionary then send it back
    
    grocery_json = grocery_df.to_json(orient='records')
    
    return grocery_json

@app.route('/api/recipemetadata')
def recipemetadata():
    
    query = request.args.get('query')
    cuisine = request.args.get('cuisine')
    cookingMinutes = request.args.get('cookingMinutes')
    calories = request.args.get('calories')
    type_of_recipe = request.args.get('type_of_recipe')
    
    print(query, cuisine, cookingMinutes, type_of_recipe, calories)

    recipe_df = getRecipeMetadata(query, cuisine, type_of_recipe, calories, cookingMinutes)    
    
    recipe_json = recipe_df.to_json(orient='records')
    
    return recipe_json

@app.route('/api/recipequantities')
def recipequantities():
    
    query = request.args.get('query')
    cuisine = request.args.get('cuisine')
    
    recipe_df = getQuantities(query, cuisine)
    
    recipe_json = recipe_df.to_json(orient='records')
    
    return recipe_json

@app.route('/ingredientsWithPrices')
def productsFromScrape():
    products_json = products_subset.to_json(orient='records')
    return(products_json)

if __name__ == '__main__':
    app.run(debug=True)
