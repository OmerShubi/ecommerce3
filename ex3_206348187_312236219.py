import pandas as pd
import math
from itertools import permutations

########## Part A ###############
CARS = ['bmw', 'vw', 'ford', 'kia', 'ferrari']
YEARS = [2012, 2013, 2014, 2015, 2016]
def opt_bnd(data, k, years):
    available_data = data.copy()
    for _ in range(k):
        for permutation in permutations(CARS, 5):
            sigma = {p: years[indx] for indx, p in enumerate(permutation)}
            for indx, (car, year) in enumerate(sigma.items()):
                car_year_df = pd.DataFrame(available_data.loc[(available_data['brand']==car) & (available_data['year']==year)].id)
                if indx == 0:
                    df = car_year_df.copy()
                else:
                    df = df.merge(car_year_df, how='cross')
            pass


    # returns the optimal bundle of cars for that k and list of years and their total cost.
    return {"cost": 0, "bundle": []}


def comb_vcg(data, k, years):
    #runs the VCG procurement auction
    output = opt_bnd(data=data, k=k, years=years)
    return {'id':0}


########## Part B ###############
def extract_data(brand, year, size, data):
    #extract the specific data for that type
    return []




class Type:
    cars_num = 0
    buyers_num = 0

    def __init__(self, brand, year, size, data):
        self.data = extract_data(brand, year, size, data)

    def avg_buy(self):
        # runs a procurement vcg auction for buying cars_num cars on the given self.data.
        # returns the average price paid for a winning car.
        return 0

    def cdf(self, x):
        # return F(x) for the histogram self.data
        return 1


    def os_cdf(self, r, n, x):
        #The r out of n order statistic CDF
        return 1

    def exp_rev(self):
        # returns the expected revenue in future auction for cars_num items and buyers_num buyers

        return 0

    def exp_rev_median(self, n):
        
        return 0

    ########## Part C ###############

    def reserve_price(self):
        # returns your suggestion for a reserve price based on the self_data histogram.
        return 0

