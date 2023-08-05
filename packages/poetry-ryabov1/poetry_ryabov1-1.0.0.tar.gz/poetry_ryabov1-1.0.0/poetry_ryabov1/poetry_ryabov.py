def shestng():
    print('''
x = '
y = '
j = 0.93

# решено
import math
x = [float(i.replace(',', '.')) for i in x.split(';')]
y = [float(i.replace(',', '.')) for i in y.split(';')]

p = np.corrcoef(x,y)[0][1]
z = stats.norm.isf((1-j)/2)
high = math.tanh(math.atanh(p) + 1/(len(x)-3)**0.5 * z)

p = str(p).replace('.', ',')
high = str(high).replace('.', ',')
print(f'Выборочный к кор: {p}')
print(f'Верхняя граница: {high}')
    ''')
    return

def shestg():
    print('''
data = pd.read_csv('ds6.4.0.csv', header = None, names = ['x', 'y'], decimal=',', sep=';', encoding='cp1251')

x = np.array(data['x'])
y = np.array(data['y'])
n = data.shape[0]

#muX = np.mean(x)
#muY = np.mean(y)
muX = 3
muY = 4

from numpy import pi, sqrt, e
from functools import reduce
p = Symbol('p')
s = Symbol('s')

lnL = - (ln(2*pi) + ln(s**2) +1/2 * ln(1-p**2)) + (2*p/(2*s**2*(1-p**2)) * sum((x-muX)*(y-muY))  - 1/(2*s**2*(1-p**2))*sum((x-muX)**2+(y-muY)**2)) *1/n

lnL

- (ln(2*pi) + ln(s**2) +1/2 * ln(1-p**2))

 ((2*p * sum((x-muX)*(y-muY))  - 1*sum((x-muX)**2+(y-muY)**2)) *1/n)/(2*s**2*(1-p**2))

# Прямо то, что у него
- (ln(2*pi) + ln(s**2) +1/2 * ln(1-p**2)) + ((2*p * sum((x-muX)*(y-muY))  - 1*sum((x-muX)**2+(y-muY)**2)) *1/n)/(2*s**2*(1-p**2))

lnL_div_n = - (ln(2*pi) + ln(s**2) +1/2 * ln(1-p**2)) + ((2*p * sum((x-muX)*(y-muY))  - 1*sum((x-muX)**2+(y-muY)**2)) *1/n)/(2*s**2*(1-p**2))
lnLprime_p = lnL_div_n.diff(p)
lnLprime_s = lnL_div_n.diff(s)

lnLprime_p 
lnLprime_s

f = (lnLprime_p, lnLprime_s)
p, s = nsolve(f, [p, s], [-0.9, 0.1], verify=False, solver='bisect', maxsteps=13)
print(f'p = {round(p, 5)}\ns = {round(s, 5)}')
    ''')
    return