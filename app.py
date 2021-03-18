
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


###################################################
###################################################
###################################################
#   getIngredients()
###################################################
###################################################
##################################################

def getIngredients(capture_list): 
    
    #######################################
    # consider separating this part into a function

    # recipe_ids_list = [1554861, 1560677]
    recipe_ingredients = []
    
    print('######### in getIngredients ############') 
    print(capture_list)
    # ingredients stuff
    for result in capture_list:
        try:
            recipe_id = result['id']
            recipe_title = result['title']        
            analyzedInstructions = result['analyzedInstructions']
            
        except Exception as e:
            print('--- error with something ---')
            print(e)
            continue 

        instruction_steps = analyzedInstructions[0]['steps']        # Brooke addition

        counter = 0                                                 # Brooke addition

        # INSTRUCTIONS ##############################
        for item in instruction_steps:                              # Brooke addition
            counter = counter + 1                                   # Brooke addition
            step = item['step']                                     # Brooke addition
            numbered_step = f'{counter}. {step}'                    # Brooke addition
            recipe_steps.append(numbered_step)                      # Brooke addition
        
        # INGREDIENTS ###############################
        for instruction in analyzedInstructions:
            
            steps = instruction['steps']
            
            for step in steps:
                
                ingredients = step['ingredients']
                
                for ingredient in ingredients:
                    
                    ingredient_name = ingredient['name']
                    
                    recipe_ingredient = {
                        'recipe_id': recipe_id,
                        'recipe_title': recipe_title,
                        'ingredient_name': ingredient_name
                    }

                    recipe_ingredients.append(recipe_ingredient)

    ingredients_df = pd.DataFrame(recipe_ingredients)

    # dedupe ingredients df
    # ingredients_df.drop_duplicates()
    ingredients_df.drop_duplicates(subset=['ingredient_name'], inplace=True)

    cloud_engine = create_engine(f"mysql://{remote_db_user}:{remote_db_pwd}@{remote_db_endpoint}:{remote_db_port}/{remote_db_name}")

    cloud_conn = cloud_engine.connect()

    #%% Querying the database
    query = '''
            SELECT DISTINCT
                ingredient,
                price,
                title,
                size
            FROM
                products_subset
            '''

    products_subset = pd.read_sql(query, cloud_conn)    

    # Renamed to GROCERY DF for clarity
    # Cut down to a single return for each ingredient
    grocery_df = products_subset
    grocery_df.drop_duplicates(subset='ingredient', keep='first', inplace=True)
    grocery_df = grocery_df.rename(columns={"title": "ingredient_title"})
    # print(len(grocery_df))
    # grocery_df.head()

    recipe_ingredients_df = ingredients_df
    recipe_ingredients_df = recipe_ingredients_df.rename(columns={"ingredient_name": "ingredient"})
    # recipe_ingredients_df.head()

    print('###### WHAT PYTHON THJINKS ARE THE DF KEYS ################')
    print(recipe_ingredients_df.keys())
    print(grocery_df.keys())
    

    final_final_grocery_list_df = pd.merge(recipe_ingredients_df, grocery_df, how="inner", on=["ingredient", "ingredient"])

    cloud_conn.close()

    return final_final_grocery_list_df



###################################################
#####################
#####################
#   getRecipeMetadata
##################################################
##################################################
##################################################

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











###################################################
#####################
#####################
#   getQuantities
##################################################
##################################################
##################################################

def getQuantities(query, cuisine):
    
    #######################################
    # consider separating this part into a function
    url = "https://spoonacular-recipe-food-nutrition-v1.p.rapidapi.com/recipes/searchComplex"

    url3 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={headers2}"
    
    # these will come from form controls
    query = query
    cuisine = cuisine
    type_of_recipe = 'main course'
    ranking = "2"
    minCalories = "150"
    maxCalories = "1500"
    minFat = "5"
    maxFat = "100"
    minProtein = "5"
    maxProtein = "100"
    minCarbs = "5"
    maxCarbs = "100"
    
    querystring = {"limitLicense": "<REQUIRED>",
        "offset": "0",
        "number": "10",
        "query": query,
        "cuisine": cuisine,
        #"includeIngredients": "onions, lettuce, tomato",
        #"excludeIngredients": "coconut, mango",
        #"intolerances": "peanut, shellfish",
        "type": type_of_recipe,
        "ranking": ranking,
        "minCalories": minCalories,
        "maxCalories": maxCalories,
        "minFat": minFat,
        "maxFat": maxFat,
        "minProtein": minProtein,
        "maxProtein": maxProtein,
        "minCarbs": minCarbs,
        "maxCarbs": maxCarbs,
        "instructionsRequired": "True",
        "addRecipeInformation": "True",
        "fillIngredients": "True",
    }
    
    headers = {
        'x-rapidapi-key': x_rapidapi_key,
        'x-rapidapi-host': x_rapidapi_host
        }

    headers2 = spoonacular_API               # PartDeux Addition
    
    response = requests.get(url, headers=headers, params=querystring)
    
    response_json = response.json()
    
    results = response_json['results']
    
    # consider making everything above part of a separate function
    #######################################

    # recipe_metadata_list = []
    
    # create an Empty DataFrame object with column headers    
    column_names = ["recipe_id", "recipe_title", "ingredient_id", "ingredient", "amount_unit", "amount", "unit"]
    recipe_quantities_df = pd.DataFrame(columns = column_names)
    
    # ingredients stuff
    for result in results:
        try:
            recipe_id = result['id']
            print(recipe_id)
            recipe_title = result['title']

            response2 = requests.get(url3)
            json_data2 = response2.json()
            df2 = pd.DataFrame(json_data2["extendedIngredients"])
            df3 = df2[['id', 'name', 'original', 'amount', 'unit']]
            df4 = df3.rename(columns={"id": "ingredient_id", "name": "ingredient", "original": "amount_unit"})
            df4.insert(0, "recipe_id", recipe_id)
            df4.insert(1, "recipe_title", recipe_title)
            
        except Exception as e:
            print('--- error with something ---')
            print(result.keys())
            continue

        recipe_quantities_df.merge(df4, how='outer')

        # recipe_quantities_etal = {
        #    'recipe_id': recipe_id,
        #    'recipe_title': recipe_title            
        #}

        # will need to rename this
        # recipe_metadata_list.append(recipe_metadata)

    # recipe_metadata_df = pd.DataFrame(recipe_metadata_list)

    # dedupe ingredients df
    # recipe_quantities_df.drop_duplicates(inplace=True)

    return recipe_quantities_df




###################################################
#####################
#####################
#   Connect to Database
##################################################
##################################################
##################################################

cloud_engine = create_engine(f"mysql://{remote_db_user}:{remote_db_pwd}@{remote_db_endpoint}:{remote_db_port}/{remote_db_name}")

cloud_conn = cloud_engine.connect()

#%% Querying the database
query = '''
        SELECT DISTINCT
            ingredient,
            price,
            title,
            size
        FROM
            products_subset
        '''

products_subset = pd.read_sql(query, cloud_conn)

products_subset.head()

cloud_conn.close()



#######################################################################################

def test_MAJOR(recipe_ids_list = [1554861,1560677,1571559]):

    # import requests
    import pandas as pd
    import numpy as np
    import json
    import sqlalchemy
    from sqlalchemy import create_engine
    from flask import Flask, request, render_template, jsonify
    import pymysql
    pymysql.install_as_MySQLdb()
    #from config import remote_db_endpoint, remote_db_port, remote_db_name, remote_db_user, remote_db_pwd
    #from config import x_rapidapi_key, x_rapidapi_host, spoonacular_API

    import pprint
    # import urllib.request

    #**************************************************************************************

    

    capture_list = []
    for recipe_id in recipe_ids_list:
        url2 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={spoonacular_API}"    
        response = requests.get(url2)
        response_json = response.json()
        capture_list.append(response_json)

    capture_list

    print(json.dumps(capture_list, indent=4, sort_keys=True))

    recipe_ingredients = []
    recipe_steps = []

    # ingredients stuff
    for result in capture_list:                         ################ NOT SURE BUT PROBABLY
        try:
            recipe_id = result['id']
            recipe_title = result['title']        
            analyzedInstructions = result['analyzedInstructions']

        except Exception as e:
            print('--- error with something ---')
            print(e)
            continue 

        instruction_steps = analyzedInstructions[0]['steps']        # Brooke addition

        counter = 0                                                 # Brooke addition

        # INSTRUCTIONS ##############################
        for item in instruction_steps:                              # Brooke addition
            counter = counter + 1                                   # Brooke addition
            step = item['step']                                     # Brooke addition
            numbered_step = f'{counter}. {step}'                    # Brooke addition
            recipe_steps.append(numbered_step)                      # Brooke addition

        # INGREDIENTS ###############################
        for instruction in analyzedInstructions:

            steps = instruction['steps']

            for step in steps:

                ingredients = step['ingredients']

                for ingredient in ingredients:

                    ingredient_name = ingredient['name']

                    recipe_ingredient = {
                        'recipe_id': recipe_id,
                        'recipe_title': recipe_title,
                        'ingredient_name': ingredient_name
                    }

                    recipe_ingredients.append(recipe_ingredient)

    ingredients_df = pd.DataFrame(recipe_ingredients)

    # dedupe ingredients df
    # ingredients_df.drop_duplicates()
    ingredients_df.drop_duplicates(subset=['ingredient_name'], inplace=True)

    ingredients_df

    ######################## KEEP FOR POSSIBLE USE WITH FUNCTION
    # return ingredients_df

    cloud_engine = create_engine(f"mysql://{remote_db_user}:{remote_db_pwd}@{remote_db_endpoint}:{remote_db_port}/{remote_db_name}")

    cloud_conn = cloud_engine.connect()

    #%% Querying the database
    query = '''
            SELECT DISTINCT
                ingredient,
                price,
                title,
                size
            FROM
                products_subset
            '''

    products_subset = pd.read_sql(query, cloud_conn)

    products_subset

    len(products_subset)

    # Renamed to GROCERY DF for clarity
    # Cut down to a single return for each ingredient
    grocery_df = products_subset
    grocery_df.drop_duplicates(subset='ingredient', keep='first', inplace=True)
    grocery_df = grocery_df.rename(columns={"title": "ingredient_title"})
    print(len(grocery_df))
    grocery_df.head()

    recipe_ingredients_df = ingredients_df
    recipe_ingredients_df = recipe_ingredients_df.rename(columns={"ingredient_name": "ingredient"})
    recipe_ingredients_df.head()

    new_df = pd.merge(recipe_ingredients_df, grocery_df, how="inner", on=["ingredient", "ingredient"])
                                                                        
    new_df.head()

    return new_df

test_MAJOR()

########################################################################################
def metadataForCards(recipe_ids_list = [1554861,1560677,1571559]):

    capture_list = []
    for recipe_id in recipe_ids_list:
        url2 = f"https://api.spoonacular.com/recipes/{recipe_id}/information?apiKey={spoonacular_API}"    
        response = requests.get(url2)
        response_json = response.json()
        capture_list.append(response_json)

    capture_list

    #print(json.dumps(capture_list, indent=4, sort_keys=True))

    recipe_meta = []


# ingredients stuff
    for result in capture_list:                         
        try:
            recipe_id = result['id']
            recipe_title = result['title']        
            analyzedInstructions = result['analyzedInstructions']
            cooking_minutes = result['cookingMinutes']
            image = result['image']
            servings = result['servings']

        except Exception as e:
            print('--- error with something ---')
            print(e)
            continue 

        instruction_steps = analyzedInstructions[0]['steps']   
        recipe_steps = []

        counter = 0                                                 

    # INSTRUCTIONS ##############################
        for item in instruction_steps:                              
            counter = counter + 1                                   
            step = item['step']                                     
            numbered_step = f'{counter}. {step}'                    
            recipe_steps.append(numbered_step)                      

    # INFO ###############################
        recipe_info = {
        'recipe_id': recipe_id,
        'recipe_title': recipe_title,
        'cooking_minutes': cooking_minutes,
        'image': image,
        'servings': servings,
        'steps': recipe_steps}

        recipe_meta.append(recipe_info)

    for_cards_df = pd.DataFrame(recipe_meta)



    return for_cards_df




app = Flask(__name__)

@app.route('/')
def home():
    
    return render_template('index.html')

@app.route('/about')
def about():
    
    return render_template('about.html')

@app.route('/products')
def plots():
    
    return render_template('products.html')

@app.route('/store')
def store():
    
    return render_template('store.html')

@app.route('/lastPage')
def printpage():
    
    return render_template('last_page.html')

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
