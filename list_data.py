#!/usr/bin/env python3
import pandas as pd
import json as js
from pprint import pprint

ingredients = pd.read_csv('ingredients.csv', index_col=0)
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
print(ingredients)
print()
recipies = None
with open('recipies.json') as json_file:
    recipies = js.load(json_file)

#Maybe add brand name with type in ingredients.csv
print("Recipie                                 Cost    Protein      Carbs       Fats  Calories    Serves")
print("_________________________________________________________________________________________________")
for recipie in recipies.items():
    cost = 0
    protein = 0
    carbs = 0
    fats = 0
    calories = 0
    for ingredient in recipie[1]["Ingredients"]:
        ingredient_data = ingredients.loc[ingredient["Name"]]
        fraction_used = ingredient["Amount"] / ingredient_data["Serving Size"] / ingredient_data["Servings per Item"]
        cost += ingredient_data["Cost (cents)"] * fraction_used
        protein += ingredient_data["Protein (g)"] * fraction_used
        carbs += ingredient_data["Carbs (g)"] * fraction_used
        fats += ingredient_data["Fats (g)"] * fraction_used
        calories += ingredient_data["Calories"] * fraction_used
    cost = int(cost)
    dollars = cost // 100
    cents = cost % 100
    recipie_name = recipie[0]
    recipie_name_length = 30
    if len(recipie_name) >= recipie_name_length:
        recipie_name = recipie_name[:recipie_name_length - 3] + "..."
    serves = recipie[1]["Servings"]
    dollar_format = "$" + str(dollars)

    print(("{:<" + str(recipie_name_length) + "s}{: >11s}.{:>02d}{: >10.2f}g{: >10.2f}g{: >10.2f}g{: >10.2f}{: >10d}").format(recipie_name, dollar_format, cents, protein, carbs, fats, calories, serves))
#Recipies format:
#
#    "Simple" : {
#        "Ingredients" : [
#            {
#                "Name" : "Bananas",
#                "Amount" : 1,
#                "Units" : "None"
#            },
#            {
#                "Name" : "Apples",
#                "Amount" : 2,
#                "Units" : "None"
#            },
#            {
#                "Name" : "Pistachios",
#                "Amount" : 1,
#                "Units" : "cup"
#            }
#        ],
#        "Servings" : 1
#    }
