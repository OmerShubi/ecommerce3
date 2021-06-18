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


def proc_vcg(data, k, years):
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
        cost = sorted(self.data)[self.cars_num]

        return cost

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
            addition_cdf = ((1 / len(df)) * (x - value_below)) / (value_above - value_below)
            return base_cdf + addition_cdf

    def os_cdf(self, r, n, x):
        # CDF at point x of the r out of n order statistic of F_X
        F_x_r = 0
        F_x = self.cdf(x)

        for j in range(r, n + 1):
            F_x_r += math.comb(n, j) * (F_x ** j) * ((1 - F_x) ** (n - j))
        # The r out of n order statistic CDF
        return F_x_r

    def _exp_rev_inner(self, r, n):
        """
        n = num buyers
        r = num buyers - num cars

        if n>r? 0

        Computes E[r] by sum_0_infty of (1-F_X_r)

        :return:
        """
        res = 0
        x = 0

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

        return res

    def exp_rev(self):
        """
        n = num buyers
        r = num buyers - num cars

        if n>r? 0

        Computes E[r] by sum_0_infty of (1-F_X_r)

        :return:
        """
        r = self.buyers_num - self.cars_num
        n = self.buyers_num
        res = self._exp_rev_inner(r, n) * self.cars_num

        return res

    def exp_rev_median(self, n):
        """

        :param n:
        :return:
        """

        self.buyers_num = n
        Z = pd.Series(self.data).median()

        F_Z = self.cdf(Z)  # P(X<=Z)

        above_Z = Type(brand=self.brand,
                       data=self.original_data,
                       year=self.year,
                       size=self.size)

        above_Z.data = [x for x in above_Z.data if x >= Z]

        if n==2:
            res = ((1-F_Z) ** 2) * above_Z._exp_rev_inner(r=1, n=2) + 2 * (1-F_Z) * F_Z * Z

        if n==3:
            res = 0
            # 1 above
            res += 3 * (F_Z ** 2) * (1 - F_Z) * Z

            # 2 above
            res += 3 * (1 - F_Z) ** 2 * F_Z * above_Z._exp_rev_inner(r=1, n=2)

            # 3 above
            res += (1 - F_Z) ** 3 * above_Z._exp_rev_inner(r=2, n=3)

        return res

    ########## Part C ###############
    def _revenue_per_Z(self, Z):
        b = self.buyers_num
        c = self.cars_num
        F_Z = self.cdf(Z)
        above_Z = Type(brand=self.brand,
                       data=self.original_data,
                       year=self.year,
                       size=self.size)

        above_Z.data = [x for x in above_Z.data if x >= Z]

        price = 0

        for k in range(1, b+1):
            prob = math.comb(b, k) * ((1 - F_Z) ** k) * (F_Z ** (b - k))
            if k <= c:
                price += prob * k * Z
            else:
                price += prob * c * above_Z._exp_rev_inner(r=k-c, n=k)

        return price  # 2700

    def reserve_price(self):
        # returns your suggestion for a reserve price based on the self_data histogram.
        min_bound = int(self._exp_rev_inner(r=self.buyers_num-self.cars_num, n=self.buyers_num))
        max_bound = int(self._exp_rev_inner(r=self.buyers_num, n=self.buyers_num))

        max_rev = -1 * float('inf')
        print(f"Looking for z in range {min_bound}-{max_bound}")

        for z in range(min_bound, max_bound, 100):

            rev = self._revenue_per_Z(z)
            if rev > max_rev:
                max_rev = rev
                best_Z = z
                print(f"found better z: {best_Z} with rev {max_rev}")

        return best_Z #2700


