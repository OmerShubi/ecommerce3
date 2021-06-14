import pandas as pd
import ex3_206348187_312236219 as ex3

data = pd.read_csv('Ex3_data.csv')

######### Part A ##################
k=4
years = list(range(2012,2017))
# outcome = ex3.comb_vcg(data,k,years)
# print(outcome)
########## Part B ##################
type = ex3.Type("vw",2015,1700,data)
type.cars_num = 20
type.buyers_num = 100
print(type.cdf(6500))
print('You achieved an expected average profit of', int((type.exp_rev()/type.cars_num)-type.avg_buy()), 'per car')
type.cars_num = 1
type.buyers_num = 2
print('expected revenue in a one car auction with two buyers:', type.exp_rev())
print('Adding a median reserve price makes it', type.exp_rev_median(2))
print('And with a third buyer that is', type.exp_rev_median(3))










