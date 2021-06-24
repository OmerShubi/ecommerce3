import pandas as pd
import ex3_206348187_312236219 as ex3

data = pd.read_csv('Ex3_data.csv')

######### Part A ##################
# k = 4
# years = list(range(2012, 2017))
# outcome = ex3.proc_vcg(data, k, years)
# print(outcome)
# ########## Part B ##################
type = ex3.Type("vw", 2015, 1700, data)
# type.cars_num = 20
# type.buyers_num = 100
# print('You achieved an expected average profit of', int((type.exp_rev() / type.cars_num) - type.avg_buy()), 'per car')
# type.cars_num = 1
# type.buyers_num = 2
# print('expected revenue in a one car auction with two buyers:', type.exp_rev())
# print('Adding a median reserve price makes it', type.exp_rev_median(2))
# print('And with a third buyer that is', type.exp_rev_median(3))

type.cars_num = 1
type.buyers_num = 2
print(type.reserve_price())
# type.cars_num = 3
# type.buyers_num = 5
# print(type.reserve_price())

"""
{'id_11522': 650, 'id_30613': 9300, 'id_98522': 700, 'id_76134': 2350, 'id_77276': 3500, 'id_17396': 650, 'id_95188': 450, 'id_63328': 1650, 'id_59901': 11100, 'id_83077': 2800, 'id_50387': 8500, 'id_8507': 1400, 'id_17779': 1650, 'id_5036': 1200, 'id_83685': 3500, 'id_86530': 8500, 'id_68225': 1400, 'id_34365': 1650, 'id_19677': 1200, 'id_89085': 3500}
You achieved an expected average profit of 3245 per car
expected revenue in a one car auction with two buyers: 8851.282219927441
Adding a median reserve price makes it 7060.459979612362
And with a third buyer that is 8509.284208858995
"""
