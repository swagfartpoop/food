#!/usr/bin/env python3
import pandas as pd
import json as js
import numpy as np
from collections import namedtuple, defaultdict
import random as rd
from pprint import pprint

ingredients = pd.read_csv('ingredients.csv', index_col=0)
pd.set_option('display.max_rows', None)
#pd.set_option('display.max_columns', None)
recipies = None
with open('recipies.json') as json_file:
    recipies = js.load(json_file)

class Parameter(namedtuple('Parameter', 'weight center left right')):
    __slots__ = ()
    def __repr__(self):
        return str(tuple(self))

    def cost(self, value):
        return self.weight * (
            np.exp(
                -self.left * (value - self.center)
            )
            +
            np.exp(
                self.right * (value - self.center)
            )
        )

def cost_function(ingredient_vals, params):
    cost = 1.0
    for i in range(len(ingredient_vals)):
        cost += params[i].cost(ingredient_vals[i])
    return cost

class Shopping_List:
    def __init__(self, item_info):
        self.items      = defaultdict(lambda : 0.0)
        self.cost       = 0.0
        self.protein    = 0.0
        self.carbs      = 0.0
        self.fats       = 0.0
        self.calories   = 0.0
        self.variety    = defaultdict(lambda : 0.0)
        self.item_info  = item_info

    def __repr__(self):
        self.calculate_data()
        return '\n'.join([
            "Cost        {: >7.2f}".format(self.cost / 100.0),
            "Protein (g) {: >7.2f}".format(self.protein),
            "Carbs (g)   {: >7.2f}".format(self.carbs),
            "Fats (g)    {: >7.2f}".format(self.fats),
            "Calories    {: >7.2f}".format(self.calories),
        ])

    def calculate_data(self):
        self.cost = 0.0
        self.protein = 0.0
        self.carbs = 0.0
        self.fats = 0.0
        self.calories = 0.0
        for item in self.items.items():
            amount = 1.0 - int(1.0 - item[1])
            self.cost       +=  amount * self.item_info[item[0]]['cost']
            self.protein    += item[1] * self.item_info[item[0]]['protein']
            self.carbs      += item[1] * self.item_info[item[0]]['carbs']
            self.fats       += item[1] * self.item_info[item[0]]['fats']
            self.calories   += item[1] * self.item_info[item[0]]['calories']

    def add_item(self, item, amount):
        self.items[item] += amount

    def remove_item(self, item, amount):
        self.items[item] -= amount

    def can_remove_items(self, params):
        for k in self.cur_dir(params)[1:]:
            if k < 0:
                return True
        return False

    def select_random_item(self, params):
        cur_direction = self.cur_dir(params)
        item_names = list(self.item_info.keys())
        weights = []
        for item in item_names:
            weights.append(
                  cur_direction[0] * self.item_info[item]['cost'] * (np.modf(self.items[item])[0] > 0.0001)
                + cur_direction[1] * self.item_info[item]['protein']
                + cur_direction[2] * self.item_info[item]['carbs']
                + cur_direction[3] * self.item_info[item]['fats']
                + cur_direction[4] * self.item_info[item]['calories']
            )
        min_weight = min(weights)
        weights = [ k - min_weight for k in weights ]
        return rd.choices(item_names, weights)[0]

    def remove_bad_items(self, params):
        #if self.can_remove_item(params):
        #    print(self)
        #    pprint(self.items)
        while self.can_remove_items(params):
            temp_direction = self.cur_dir(params)
            cur_direction = np.array([ -min(0.0, k) for k in temp_direction[1:] ])
            mag = np.sqrt(sum(k ** 2 for k in cur_direction))
            cur_direction /= mag
            item_list = list(item_dict.items())
            weights = []
            for item in item_list:
                weights.append(
                    cur_direction[0] * item[1]['protein']
                    + cur_direction[1] * item[1]['carbs']
                    + cur_direction[2] * item[1]['fats']
                    + cur_direction[3] * item[1]['calories']
                )
            min_weight = min(weights)
            weights = [ k - min_weight for k in weights ]
            cur_item = rd.choices(item_list, weights)[0]
            self.remove_item(cur_item[0], self.items[cur_item[0]])
            #print(self)
            #pprint(self.items)
            #print(cur_item[0])

    def cost_function(self, params):
        variety = sum(4.0 * ((k - 1) // 2) ** 2 for k in self.variety.values())
        return cost_function(
            [
                self.cost,
                self.protein,
                self.carbs,
                self.fats,
                self.calories,
                variety,
            ],
            params
        )

    def cur_dir(self, params):
        self.calculate_data()
        direction = np.array([
            -0.5,
            1.0 - (self.protein  / params[1].center),
            1.0 - (self.carbs    / params[2].center),
            1.0 - (self.fats     / params[3].center),
            1.0 - (self.calories / params[4].center),
        ])
        mag = np.sqrt(sum(k ** 2 for k in direction))
        direction /= mag
        return direction

no_recipies = True

timeframe = 7.0 # days in week
default_cost        = Parameter(1.0, timeframe *    0.0, 0.001, 0.001)
default_protein     = Parameter(1.0, timeframe *  187.5, 0.001, 0.001)
default_carbs       = Parameter(1.0, timeframe *  450.0, 0.001, 0.001)
default_fats        = Parameter(1.0, timeframe *  112.5, 0.001, 0.001)
default_calories    = Parameter(1.0, timeframe * 3000.0, 0.007, 0.007)
default_variety     = Parameter(0.0, timeframe *    1.0, 0.100, 0.100)
default_params = [
    default_cost,
    default_protein,
    default_carbs,
    default_fats,
    default_calories,
    default_variety
]

if no_recipies:
    item_dict = {}
    for index, ingredient in ingredients.iterrows():
        servings = ingredient["Servings per Item"]
        amount = 1.0 / servings
        cost = ingredient["Cost (cents)"] * amount
        protein = ingredient["Protein (g)"]
        carbs = ingredient["Carbs (g)"]
        fats = ingredient["Fats (g)"]
        calories = ingredient["Calories"]
        item_dict[ingredient["Name"]] = {
            'amount' : amount,
            'cost' : cost,
            'protein' : protein,
            'carbs' : carbs,
            'fats' : fats,
            'calories' : calories,
            'item name' : index
        }
    shopping_list = Shopping_List(item_dict)
    total_cost_function = float('inf')
    for i in range(0, 10000):
        cur_item = shopping_list.select_random_item(default_params)
        shopping_list.add_item(cur_item, item_dict[cur_item]['amount'])
        shopping_list.remove_bad_items(default_params)
        total_cost_function = shopping_list.cost_function(default_params)
    print(shopping_list)
    pprint(shopping_list.items)
    print(shopping_list.cost_function(default_params))
    print(default_params)
