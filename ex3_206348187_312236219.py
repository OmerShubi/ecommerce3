import pandas as pd
import math
from itertools import permutations, product # TODO allowed?

########## Part A ###############
CARS = ['bmw', 'vw', 'ford', 'kia', 'ferrari']
YEARS = [2012, 2013, 2014, 2015, 2016]
def opt_bnd(data, k, years):
    optimal_bundle_indices = list()
    optimal_bundle_value = 0
    for _ in range(k):
        best_sigma = list()
        best_sigma_value = float('inf')
        for permutation in permutations(CARS, 5):
            sigma = {p: years[indx] for indx, p in enumerate(permutation)}
            # df = pd.DataFrame()
            dfs = []
            for car, year in sigma.items():
                car_year_df = data.loc[(data['brand'] == car) & (data['year'] == year)]
                best_bundle_indices.append(car_year_df.value.idxmin())
                sigma_value += car_year_df.value.min()

            if sigma_value < best_sigma_value:
                best_sigma = best_bundle_indices
                best_sigma_value = sigma_value


        data.drop(best_sigma, inplace=True)
        optimal_bundle_indices.extend(best_sigma)
        optimal_bundle_value+=best_sigma_value
        pass


    # returns the optimal bundle of cars for that k and list of years and their total cost.
    return {"cost": optimal_bundle_value, "bundle": optimal_bundle_indices}


def comb_vcg(data, k, years):
    #runs the VCG procurement auction
    prices = {}

    output = opt_bnd(data=data.copy().set_index('id'), k=k, years=years)
    for user in output['bundle']:
        world_value_with_user = output['cost'] - data.loc[data['id']==user, 'value'].values
        data_without_user = data.copy().set_index('id')
        data_without_user.drop(user, inplace=True)
        user_output = opt_bnd(data=data_without_user, k=k, years=years)
        world_value_without_user = user_output['cost']
        prices[user] = -(world_value_with_user - world_value_without_user)[0] # TODO Okay?
        pass

    return prices


########## Part B ###############
def extract_data(brand, year, size, data):
    relevant_data = data.loc[(data['brand']==brand) & (data['year']==year) & (data['engine_size']==size)]
    #extract the specific data for that type
    return list(relevant_data.value.values)




class Type:
    cars_num = 0
    buyers_num = 0

    def __init__(self, brand, year, size, data):
        self.data = extract_data(brand, year, size, data)

    def avg_buy(self):
        # TODO is this okay??
        # runs a procurement vcg auction for buying cars_num cars on the given self.data.
        # returns the average price paid for a winning car.
        purchased_cars = sorted(self.data)[:self.cars_num]

        # runs the VCG procurement auction
        costs = []
        for car_value in purchased_cars:
            world_value_with_user = sum(purchased_cars) - car_value
            data_without_car = self.data.copy()
            data_without_car.remove(car_value)
            purchased_cars_without_car = sorted(data_without_car)[:self.cars_num]
            world_value_without_user = sum(purchased_cars_without_car)
            cost = -(world_value_with_user-world_value_without_user)
            costs.append(cost)

        return sum(costs) / len(costs)

    def cdf(self, x):
        # return F(x) for the histogram self.data
        df = pd.DataFrame(sorted(self.data))
        indx_below = (df-x).idxmin()
        indx_above = (x-df).idxmin()
        value_below = df[indx_below]
        value_above = df[indx_above]
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

