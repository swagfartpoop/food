#!/usr/bin/env python3
import pandas as pd
import json as js
from pprint import pprint

ingredients = pd.read_csv('ingredients.csv', index_col=0)
print(ingredients)
recipies = None
with open('recipies.json') as json_file:
    recipies = js.load(json_file)

#Maybe add brand name with type in ingredients.csv
for recipie in recipies.items():
    cost = 0
    protein = 0
    carbs = 0
    for ingredient in recipie[1]["Ingredients"]:
        ingredient_data = ingredients.loc[ingredient["Name"]]
        fraction_used = ingredient["Amount"] / ingredient_data["Serving Size"]
        cost += ingredient_data["Cost (cents)"] * fraction_used
        protein += ingredient_data["Protein (g)"] * fraction_used
        carbs += ingredient_data["Carbs (g)"] * fraction_used
    cost = int(cost)
    dollars = cost // 100
    cents = cost % 100

    print("{:<20s}${:>01d}.{:>02d}\t{}g\t{}g".format(recipie[0] + ":", dollars, cents, protein, carbs))
#Apple
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
#        "Happiness" : 100
#    }
