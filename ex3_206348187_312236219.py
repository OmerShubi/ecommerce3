import pandas as pd
import math
from itertools import permutations

########## Part A ###############
CARS = ['bmw', 'vw', 'ford', 'kia', 'ferrari']
YEARS = [2012, 2013, 2014, 2015, 2016]


def opt_bnd(data, k, years):
    optimal_bundle_indices = list()
    optimal_bundle_value = 0
    for _ in range(k):
        best_sigma_indices = list()
        best_sigma_value = float('inf')
        for permutation in permutations(CARS, 5):
            sigma = {p: years[indx] for indx, p in enumerate(permutation)}
            best_bundle_indices = []
            sigma_value = 0
            for car, year in sigma.items():
                car_year_df = data.loc[(data['brand'] == car) & (data['year'] == year)]
                best_bundle_indices.append(car_year_df.value.idxmin())
                sigma_value += car_year_df.value.min()

            if sigma_value < best_sigma_value:
                best_sigma_indices = best_bundle_indices
                best_sigma_value = sigma_value

        data.drop(best_sigma_indices, inplace=True)
        optimal_bundle_indices.extend(best_sigma_indices)
        optimal_bundle_value += best_sigma_value

    # returns the optimal bundle of cars for that k and list of years and their total cost.
    return {"cost": int(optimal_bundle_value), "bundle": optimal_bundle_indices}


def comb_vcg(data, k, years):
    # runs the VCG procurement auction
    prices = {}

    output = opt_bnd(data=data.copy().set_index('id'), k=k, years=years)
    for user_id in output['bundle']:
        world_value_with_user = output['cost'] - data.loc[data['id'] == user_id, 'value'].values
        data_without_user = data.copy().set_index('id')
        data_without_user.drop(user_id, inplace=True)
        user_output = opt_bnd(data=data_without_user, k=k, years=years)
        world_value_without_user = user_output['cost']
        prices[user_id] = -(world_value_with_user - world_value_without_user)[0]

    return prices


########## Part B ###############
def extract_data(brand, year, size, data):
    relevant_data = data.loc[(data['brand'] == brand) & (data['year'] == year) & (data['engine_size'] == size)]
    # extract the specific data for that type
    return list(relevant_data.value.values)


class Type:
    cars_num = 0
    buyers_num = 0

    def __init__(self, brand, year, size, data):
        self.brand = brand
        self.year = year
        self.size = size
        self.original_data = data
        self.data = extract_data(brand, year, size, data)

    def avg_buy(self):
        # runs a procurement vcg auction for buying cars_num cars on the given self.data.
        # returns the average price paid for a winning car.
        cost = sorted(self.data)[self.cars_num] # TODO is this okay??

        purchased_cars = sorted(self.data)[:self.cars_num]

        # runs the VCG procurement auction
        costs = []
        for car_value in purchased_cars:
            world_value_with_user = sum(purchased_cars) - car_value
            data_without_car = self.data.copy()
            data_without_car.remove(car_value)
            purchased_cars_without_car = sorted(data_without_car)[:self.cars_num]
            world_value_without_user = sum(purchased_cars_without_car)
            cost = -(world_value_with_user - world_value_without_user)
            costs.append(cost)

        cost2 = sum(costs) / len(costs)
        assert cost2 == cost, "Mismatch in cost calculation!"
        return cost2

    def cdf(self, x):
        # return F(x) for the histogram self.data
        df = pd.DataFrame(sorted(self.data))

        if x < df.min().iloc[0]:
            return 0
        elif x >= df.max().iloc[0]:
            return 1
        else:
            value_below = df[df <= x].max().iloc[0]
            value_above = df[df > x].min().iloc[0]

            base_cdf = (df <= x).sum().iloc[0] / len(df)
            addition_cdf = (1 / len(df)) * (x - value_below) / (value_above - value_below)
            return base_cdf + addition_cdf

    def os_cdf(self, r, n, x):
        # CDF at point x of the r out of n order statistic of F_X
        F_x_r = 0
        F_x = self.cdf(x)

        for j in range(r, n + 1):
            F_x_r += math.comb(n, j) * (F_x ** j) * ((1 - F_x) ** (n - j))
        # The r out of n order statistic CDF
        return F_x_r

    def exp_rev(self):
        """
        n = num buyers
        r = num buyers - num cars

        if n>r? 0

        Computes E[r] by sum_0_infty of (1-F_X_r)

        :return:
        """
        res = 0
        x = 0
        r = self.buyers_num - self.cars_num
        n = self.buyers_num
        if r < 0:
            return 0
        while True:
            F_x_r = self.os_cdf(r, n, x)
            res += 1 - F_x_r
            if F_x_r == 1:
                break
            else:
                x += 1
        # returns the expected revenue in future auction for cars_num items and buyers_num buyers

        return res * self.cars_num

    def exp_rev_median(self, n):
        """
         r =
            x_(2), if x_(2)>=Z ; P(X_(2) >Z)
            Z, if X_(3)>=Z and X_(2) < Z
            0, else

         n=2
         (1-FX_1(Z)) *  E(F_X_1 | data >= Z) +
                      FX_1(Z) * (1-FX_2(Z)) * Z

         n=3
         (1-FX_2(Z)) *  E(F_X_2 | data >= Z) +
                      FX_2(Z) * (1-FX_3(Z)) * Z

        (1-FX_(n-1)(Z)) *  E(F_X_[n-1] | data >= Z) +
                      FX_(n-1)(Z) * (1-FX_(n)(Z)) * Z


        :param n:
        :return:
        """
        self.buyers_num = n
        Z = pd.Series(self.data).median()
        FX_n_1 = self.os_cdf(r=n - 1, n=n, x=Z)
        FX_n = self.os_cdf(r=n, n=n, x=Z)

        above_Z = Type(brand=self.brand,
                       data=self.original_data,
                       year=self.year,
                       size=self.size)
        above_Z.cars_num = 1
        above_Z.buyers_num = n

        above_Z.data = [x for x in above_Z.data if x >= Z]
        res = (1 - FX_n_1) * above_Z.exp_rev() + FX_n_1 * (1 - FX_n) * Z
        return res

    ########## Part C ###############

    def reserve_price(self):
        # returns your suggestion for a reserve price based on the self_data histogram.
        return 0
