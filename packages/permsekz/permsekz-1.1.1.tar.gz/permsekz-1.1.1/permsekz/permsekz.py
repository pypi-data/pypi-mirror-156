def lib4():
    print('''
import pandas as pd
import numpy as np
import scipy.stats as stats
import math
import statistics
import scipy

import matplotlib.ticker as ticker
from matplotlib import rcParams
rcParams['font.family']='serif'
rcParams['font.sans-serif']=['Times']
from IPython.display import display, Math, Latex
from matplotlib.font_manager import FontProperties
from sympy import * 
import locale as loc
from sympy import symbols, simplify, oo, pi, integrate, init_session
init_printing(use_unicode=True,use_latex=True)
    ''')
    return

def chet1():
    print('''
from statistics import mean
from numpy import std
from statistics import NormalDist
import scipy.stats as sps

pd = [-9, 9, -138, -145, 186, 78, 34, -37, -19, -68, -82, 158, 96,
      -189, 24, 84, -99, 125, -39, 26, 62, -91, 239, -211, 2, 129, 2, -16]
one = mean(pd)
two = std(pd)
norm = NormalDist(one, two)
L = norm.quantiles(n=4)[0]
H = norm.quantiles(n=4)[2]
four = len([x for x in pd if L <= x <= H])
print(one)
print(two)
print(L)
print(H)
print(four)
print(pd.cdf(2))    
    ''')
    return


def chet2():
    print('''
n = 5
x = np.array([200, 300])
y = np.array([2, 4, 5])
cell1 = np.array([13, 11, 10])
cell2 = np.array([30, 13, 23])

N = 100
Y = cell1 + cell2  # частотное распр Y
EY = (y * Y).sum() / N

EX = sum([sum(cell1)*x[0], sum(cell2)*x[1]]) / N
X = [sum(cell1), sum(cell2)]
VarX = 1/N * sum([(x[i] - EX)**2*X[i] for i in range(2)]) / n * (N-n) / (N-1)
sigma = VarX**0.5

lazy = (x[0]-EX)*(y[0]-EY)*cell1[0] + (x[0]-EX)*(y[1]-EY)*cell1[1] + (x[0]-EX)*(y[2]-EY)*cell1[2] + (x[1]-EX)*(y[0]-EY)*cell2[0] + (x[1]-EX)*(y[1]-EY)*cell2[1] + (x[1]-EX)*(y[2]-EY)*cell2[2]
cov = 1/N * lazy
Cov = cov/n * (N-n) / (N-1)

EY = str(round(EY,5)).replace('.', ',')
sigma = str(round(sigma,5)).replace('.', ',')
Cov = str(round(Cov,5)).replace('.', ',')

print('Математическое ожидание:', EY)
print('Стандартное отклонение:', sigma)
print('Ковариация:', Cov)

import pandas as pd
index = [str(i) for i in y]
columns = [str(i) for i in x]
df = pd.DataFrame(zip(cell1,cell2), index=index, columns =columns)
df.T  # для проверки, так ли ввели значения
    ''')
    return


def chet3():
    print('''
n = 7
x = [100, 400]
y = [1,2,3]
cell1 = [11,32,11]
cell2 = [24,11,11]


N = 100
EX = 1/N * sum([sum(cell1)*x[0], sum(cell2)*x[1]])

Y = [cell1[i]+cell2[i] for i in range(3)] # частотное распр Y
EY = 1/N * sum([y[i]*Y[i] for i in range(3)])
vary = 1/N * sum([(y[i] - EY)**2*Y[i] for i in range(3)])
VarY = vary/n * (N-n) / (N-1) 

lazy = (x[0]-EX)*(y[0]-EY)*cell1[0] + (x[0]-EX)*(y[1]-EY)*cell1[1] + (x[0]-EX)*(y[2]-EY)*cell1[2] + (x[1]-EX)*(y[0]-EY)*cell2[0] + (x[1]-EX)*(y[1]-EY)*cell2[1] + (x[1]-EX)*(y[2]-EY)*cell2[2]
cov = 1/N * lazy
Cov = cov/n * (N-n) / (N-1)
X = [sum(cell1), sum(cell2)]
VarX = 1/N * sum([(x[i] - EX)**2*X[i] for i in range(2)]) / n * (N-n) / (N-1)
rho = Cov/ (VarX*VarY)**0.5

EX = str(round(EX,5)).replace('.', ',')
VarY = str(round(VarY,5)).replace('.', ',')
rho = str(round(rho,5)).replace('.', ',')

print('Математическое ожидание:', EX)
print('Дисперсия:', VarY)
print('Коэффициент корреляции:', rho)

import pandas as pd
index = [str(i) for i in y]
columns = [str(i) for i in x]
df = pd.DataFrame(zip(cell1,cell2), index=index, columns =columns)
df.T # для проверки, так ли ввели значения
    ''')
    return


def chet4():
    print('''
k = 13  # сколько монет
n = 208  # различных комбинаций 

p = q = 0.5  # вероятность орла и решки const
EX = k*p
EX = str(round(EX, 5)).replace('.', ',')
print('Мат ожидание:', EX)

var = k*p*q
N = 2**k
var = var/n*(N-n)/(N-1)
var = str(round(var,5)).replace('.', ',')
print("Дисперсия:",var)
    ''')
    return


def chet5():
    print('''
fear_string = input()  # Прямо копируем и вставляем весь текст задания 
not_fear_list = [x.split('=') for x in fear_string.split(': ')[3].split('. ')[0].split(',')]
not_fear_dict = {x[0].replace(' ', ''):int(x[1]) for x in not_fear_list}

x = [item for key, item in not_fear_dict.items() if key[0] == 'x']
y = [item for key, item in not_fear_dict.items() if key[0] == 'y']
x_1 = [x[i] for i in range(len(x)) if x[i] >= 50 and y[i] >= 50]
y_1 = [y[i] for i in range(len(y)) if x[i] >= 50 and y[i] >= 50]
cov = str(round(np.cov(x_1, y_1, bias = True)[0,1], 2)).replace('.', ',')
coef_co = str(round(np.corrcoef(x_1, y_1)[0,1], 4)).replace('.', ',')

print(f'Ковариация: {cov}')
print(f'Коэффициент корреляции: {coef_co}')
    ''')
    return


def chet6():
    print('''
n = np.array([24, 26, 20, 29, 30]) №менять
x = np.array([73, 75, 76, 79, 71]) "менять
s = np.array([3, 6, 5, 7, 8]) "менять
N = sum(n)
x_1 = x * n
r = sum(x_1) / N

M = s**2 + x**2
M_all = sum(M*n) / N
s_all = np.sqrt(M_all - r**2)

print(f'Ср знач {round(r, 3)}, ст отклон {round(s_all, 5)}')
    ''')
    return


def chet7():
    print('''
import numpy as np
from scipy import stats

N = 25  # Кол студентов 
n = 7  # Сколько раз встречается 
score = [57, 60, 58, 78, 5, 74, 86, 100, 94, 57, 51, 86, 31, 75, 4, 83, 0, 73, 
         93, 51, 93, 36, 73, 70, 72]

var = str(round(np.var(score)/n, 5)).replace('.', ',')
m = str(round(stats.moment(score, moment=3)/n**2, 5)).replace('.', ',')

print(f'Дисперсия: {var}')
print(f'Центральный момент: {m}')
    ''')
    return


def chet8():
    print('''
import numpy as np
from scipy import stats

N = 27  # Кол студентов 
n = 7  # Сколько раз встречается 
score = [87, 91, 32, 5, 77, 76, 91, 0, 70, 0, 84, 71, 94, 93, 92, 11, 40, 76, 
         62, 71, 35, 94, 75, 6, 0, 32, 97] №менять все три

e = str(round(np.mean(score), 5)).replace('.', ',')
var = str(round(np.var(score)/n*(N-n)/(N-1), 5)).replace('.', ',')

print(f'Мат ожидание: {e}')
print(f'Дисперсия: {var}')

# (1/N * sum(i**2 for i in score) - (1/N * sum(score))**2)/n * (N-n)/(N-1)   #для промежуточных вычислений
    ''')
    return


def chet9():
    print('''
number = [7, 48, 8, 105] "менять
n = 6 "менять


score = [2,3,4,5] "менять
N = sum(number)
n1 = N/n
e = sum([score[i]*number[i] for i in range(4)])/N

v = 1/N*sum([(score[i]**2*number[i]) for i in range(4)])-e**2
var = v*(N-n1)/(n1*(N-1))
e = str(round(e,5)).replace('.', ',')
var = str(round(var**0.5,5)).replace('.', ',')

print('Мат ожидание:', e)
print('Стандартное отклонение:', var)
    ''')
    return


def chet10():
    print('''
from statistics import mean
from statistics import median
from statistics import harmonic_mean
from statistics import geometric_mean
import numpy as np
import statistics

n = 29 №№менять

marks = [90, 79, 53, 62, 66, 68, 75, 0, 82, 29, 0, 29, 68, 90, 0, 60, 44, 44, 
         70, 68, 70, 89, 0, 68, 0, 66, 0, 59, 70] №№менять
marks_P = [marks[i] for i in range(len(marks)) if marks[i] > 0]
A = mean(marks_P)
M = median(marks_P)
marks_HG = [marks[i] for i in range(len(marks)) if marks[i]>=M]
H = harmonic_mean(marks_HG)
G = geometric_mean(marks_HG)
Q = median(marks_HG)
if H > Q:
    N = [marks[i] for i in range(len(marks)) if marks[i] <= H and marks[i] >= Q]
else:
    N = [marks[i] for i in range(len(marks)) if marks[i] <= Q and marks[i] >= H]
    
print(round(A, 1))
print(round(M, 1))
print(round(H,1))
print(round(G,1))
print(round(Q,1))
print(len(N))
    ''')
    return

def chet11():
    print('''
n = 19
a = 11
b = -9 #все три переменные менять


ER = 1/ 6 * sum(range(1,7))
EB = ER
EX = (a * ER + b * EB) 

N = 6**2
varR = varB = 1/6 * sum(i**2 for i in range(1,7)) - ER**2
varX = a**2 * varR + b**2 * varB
varX = varX/n*(N-n)/(N-1)
varX = varX**0.5

EX = str(round(EX,5)).replace('.', ',')
varX = str(round(varX,5)).replace('.', ',')

print('Математическое ожидание:', EX)
print('Стандартное отклонение:', varX)
    ''')
    return


def lib5():
    print('''
import numpy as np
from scipy import stats
import scipy
from scipy.special import erf
import math
    ''')
    return


def pyat1():
    print('''
    код:  #(общая функция для всех данных
def fmt(data):     
    a=data.replace(',','.')
    b=a.split(';')
    c=list(map(float, list(b)))
    return c
#################
sigma_1 = 1.0**2     #цифра в скобке у Х - МЕНЯТЬ
sigma_2 = 1.7**2     #цифра в скобке у У - МЕНЯТЬ 

alpha = 0.02            #уровень значимости - МЕНЯТЬ
delta = 0.4               # разница между mu_x-mu_y (записана в п.4)) - МЕНЯТЬ 

data_x = '3,124; 3,62; 3,684; 4,058; 3,124; 4,163; 5,046; 2,456; 4,699; 2,299; 2,552; 4,552; 3,741; 4,47; 4,517; 4,59; 5,726; 3,359; 4,248; 6,275'  - МЕНЯТЬ
data_x = fmt(data_x)     #форматируем данные для Х

data_y = '4,351; 5,334; 1,776; 4,059; 6,458; 6,497; 4,594; 2,359; 2,896; 6,181; 4,441; 1,283; 5,091; 4,866; 4,988; 5,631; 2,898; 4,263; 2,76; 3,39; 4,892; 1,837; 2,921; 5,115; 4,765; 6,259; 2,94; 4,409; 4,15; 5,673; 3,861; 4,054; 2,241; 4,055; 4,129' - МЕНЯТЬ
data_y = fmt(data_y)    #форматируем данные для У

Z = stats.norm()
n = len(data_x)
m = len(data_y)

z_nabl = (np.mean(data_x) - np.mean(data_y)) / np.sqrt( sigma_1/n + sigma_2/m )
W = 1 - Z.cdf(Z.isf(alpha) - np.sqrt(n*m)/np.sqrt(m*sigma_1 + n*sigma_2)*delta)  # то, что вычитается #есть бетта.

print(f'статистика критерия Zнабл = {str(round(z_nabl,3)).replace(".", ",")}')
print(f'p-value = {str(round(Z.sf(z_nabl),3)).replace(".", ",")}')
print(f'Значение критической области А = {str(round(Z.isf(alpha),3)).replace(".", ",")}')
print(f'мощность критерия = {str(round(W,3)).replace(".", ",")}')

    ''')
    return


def pyat2():
    print('''
    код:  #(общая функция для всех данных
def fmt(data):
    a=data.replace(',','.')
    b=a.split(';')
    c=list(map(float, list(b)))
    return c
#################
alpha = 0.03 -МЕНЯТЬ
data_a = '-0,183; -0,661; -2,312; -0,285; 1,393; -0,579; -2,374; 1,328; 4,501; 5,307; 0,555; -0,395; 2,862; 1,512; 1,321; 0,955; 3,262; 1,003; -1,199; -1,007; 3,486; -4,325; 2,757; 0,385; 3,231; 3,379; -0,843; 2,591; 3,516; 0,866; -0,892; 2,364; -1,33; 0,653; 2,205' -МЕНЯТЬ
data_a = fmt(data_a)

data_b = '1,693; 0,576; 3,265; 1,188; 1,373; 1,847; -1,722; -1,715; 2,458; 1,369; -0,328; 5,515; -1,18; 1,209; 2,581; 4,151; 4,444; -2,527; 0,649; 2,412; 4,279; 5,512; -3,823; 3,456; 1,098; -0,032; -1,543; 0,953; -1,153; 5,137; 2,027; 1,903; -1,048' - МЕНЯТЬ
data_b = fmt(data_b)

data_c = '-0,401; 1,65; 1,458; -1,735; 0,235; -1,048; -1,676; 0,599; -1,937; 2,471; -0,665; 2,325; -0,403; -1,594; -0,115; 3,511; 0,357; -0,048; 0,982; 3,901; 1,876; -0,338; 4,111; -2,462; 3,311; -0,006; 0,898; 2,707; -1,516; -2,199; 5,264' - МЕНЯТЬ
data_c = fmt(data_c)

F = stats.norm()
a = len(data_a)
b = len(data_b)
c = len(data_c)
n = a+b+c

k = data_a + data_b + data_c
s_m = (np.mean(data_a) - np.mean(k))**2/n*a + (np.mean(data_b) - np.mean(k))**2/n*b + (np.mean(data_c) - np.mean(k))**2/n*c
s =  sum((data_a-np.mean(data_a))**2)/n+sum((data_c-np.mean(data_c))**2)/n+sum((data_b-np.mean(data_b))**2)/n
f = stats.f_oneway(data_a,data_b,data_c)[0]
f_pv = stats.f_oneway(data_a,data_b,data_c)[1]

print(f'Межгрупповая дисперсия = {str(round(s_m,3)).replace(".", ",")}')
print(f'Средняя групповая дисперсия  = {str(round(s,3)).replace(".", ",")}')
print(f'Значение статистики критерия = {str(round(f,3)).replace(".", ",")}')
print(f'p-value = {str(round(f_pv,3)).replace(".", ",")}')
    ''')
    return


def pyat3():
    print('''
def fmt(data):
    a=data.replace(',','.')
    b=a.split(';')
    c=list(map(float, list(b)))
    return c
###########
mu = 1.83       #менять
alpha = 0.03   #менять
sigma = 1.13  #менять
sigma1 = 1.23  #менять
x = '0,185; 1,269; 2,034; 1,356; 2,498; -0,185; 1,665; 0,436; 0,226; 0,556; 0,858; 1,273; -0,107; 2,228; 1,736; -0,526; 2,892; 3,352; 2,542; 1,007; 0,0; 2,402; 0,754; 2,591; 1,445; 2,314; 1,613; 2,008; 1,222; 3,228; 1,353; 1,664; 3,338; -0,313; -0,226; 2,305; -0,116; 3,406; 0,743; 0,365; 3,383; 2,883; 3,32; 2,234; 0,237' #менять

x=np.array(fmt(x))
n = len(x)
chi = 1/sigma**2 * sum((i-mu)**2 for i in x)
X = stats.chi2(len(x))
A = X.isf(1-alpha/2)
B = X.isf(alpha/2)
pv = 2*X.cdf(chi)

chi2_nabl = np.sum((x - mu)**2)/sigma**2                              #chi2_nabl  и chi считают одно и то же - значения одинак.
CHI2 = stats.chi2(len(x))
chi = str(round(chi,3)).replace('.', ',')
A = str(round(A,3)).replace('.', ',')
B = str(round(B,3)).replace('.', ',')
pv = str(round(2*min(CHI2.cdf(chi2_nabl),CHI2.sf(chi2_nabl)),3)).replace('.', ',')
b=str(round(CHI2.cdf((sigma**2/sigma1**2)*CHI2.isf(alpha/2)) - CHI2.cdf((sigma**2/sigma1**2)*CHI2.isf(1-alpha/2)),3)).replace('.', ',')

print('Значение статистики критерия:', chi)
print('Граница А критического множества:', A)
print('Граница B критического множества:', B)
print('P значение критерия:', pv)
print('веротяность ошибки второго рода =',b)
''')
    return


def pyat4():
    print('''
data = pd.read_csv('ds6.4.0.csv', header=None, decimal=',', sep=';',encoding='cp1251') #, encoding='cp1251'

x = np.array(data[0].dropna())  # Удаляем NaN
y = np.array(data[1].dropna())
z = np.array(data[2].dropna())
xyz = np.concatenate([x, y, z])  # Объединяем в один массив данных

n_i = np.array([len(x), len(y), len(z)])
N = sum(n_i)  # Объем выборки 
mu = np.array([x.mean(), y.mean(), z.mean()])  # Выборочное среднее для каждого показателя
Ex = (mu * n_i / N).sum()  # Общее выборочное среднее
inter_var = (n_i * (mu - Ex)**2).sum() / N
print(f'Межгрупповая дисперсия: {inter_var}')

var = np.array([x.var(), y.var(), z.var()])  # Выборочная дисперсия для каждого показателя
intr_var = (n_i * var).sum() / N  # Средняя групповая выборочная дисперсия 
print(f'Средняя групповая дисперсия: {intr_var}')

j = 0.95  # Из условия 
alpha = 1 - j
distribution = stats.t(N-3)  # k = 3
mse = N * intr_var / (N-3)  # MSE найдем через среднюю групповую дисперсию
delta = distribution.isf(alpha/2) * (mse/n_i[0])**0.5
left = mu[0] - delta
right = mu[0] + delta
print(f'Доверительный интервал для ожидаемого значения показателя x: ({left}; {right})')
delta = distribution.isf(alpha/2) * (mse/n_i[1])**0.5
left = mu[1] - delta
right = mu[1] + delta
print(f'Доверительный интервал для ожидаемого значения показателя y: ({left}; {right})')
delta = distribution.isf(alpha/2) * (mse/n_i[2])**0.5
left = mu[2] - delta
right = mu[2] + delta
print(f'Доверительный интервал для ожидаемого значения показателя z: ({left}; {right})')
k = 3
MSTR = N * inter_var / (k-1)
MSE = N * intr_var / (N-k)
F =  MSTR / MSE
print(f'Значение статистики F: {F}')
alpha = 0.05
distribution = stats.f(k-1, N-k)
crit = distribution.isf(alpha)
print(f'Критическая точка: {crit}')
pv = distribution.sf(F)
print(f'p-value = {pv}') #когда pv<уровня значимости - гипотеза отвергается
''')
    return


def pyat5():
    print('''
sigma = 3.4  # В начале условия N(mu, 3.4^2)
alpha = 0.01
mu0 = 1.29  # Гипотеза H_0
mu1 = 1.17  # Гипотеза H_1 для мощности
x = '1,416; 0,624; 6,471; 6,256; 1,787; 2,546; -1,758; -5,475; 0,077; 1,792;\
     5,443; 5,348; -0,057; 0,232; -2,305; -3,568; -4,541; 7,893; -0,473; -0,229;\
    -3,0; 3,903; -4,227; 0,537; -1,785; 2,575; -0,477; -2,754; 1,164; 2,716'

x = [float(i.replace(',', '.')) for i in x.split(';')]
n = len(x)
ex = np.mean(x)
z = (n)**0.5*(ex-mu0)/sigma
A = stats.norm.isf(alpha/2)
pv = 2*(1 - scipy.stats.norm.cdf(abs(z)))
laplace = lambda x: erf(x/2**0.5)/2
delta = np.sqrt(n)*(mu0-mu1)/sigma
power = 1 - (laplace(A + delta) + laplace(A - delta))

z = str(round(z,5)).replace('.', ',')
A = str(round(A,5)).replace('.', ',')
pv = str(round(pv,5)).replace('.', ',')
power = str(round(power,5)).replace('.', ',')

print('Значение статистики критерия:', z)
print('Граница А критического множества:', A)
print('P-значение критерия:', pv)
print('Мощность критерия:', power)
    ''')
    return


def pyat6():
    print('''
alpha = 0.04    #МЕНЯТЬ
mu0 = 1.14      #МЕНЯТЬ
mu1 =0.98       #МЕНЯТЬ
x = '-4,655; 0,881; 1,331; -0,268; 2,698; 3,262; -3,462; -1,749; -1,656; -6,111; -2,229; -0,034; 1,042; 7,418; 2,496; 1,657; 0,59; 5,74; 1,565; -4,124; 0,269; -5,14; -3,959; -1,413; 2,021; -1,267; 4,512; 7,725; 2,988; 2,524'    #МЕНЯТЬ
x = [float(i.replace(',', '.')) for i in x.split(';')]
n = len(x)
ex = np.mean(x)
s2 = 1/(n-1) * sum((i-ex)**2 for i in x)
t = (ex - mu0)/s2**0.5 * n**0.5 
A = stats.t.isf(alpha/2, n-1)
pv = 2 * min(stats.t.sf(t, n-1), stats.t.cdf(t, n-1))
delta = np.sqrt(n) * (mu1 - mu0)/np.sqrt(s2)
power = 1 - (stats.nct.cdf(A, n-1, delta) - stats.nct.cdf(-A, n-1, delta) )

t = str(round(t,3)).replace('.', ',')
A = str(round(A,3)).replace('.', ',')
pv = str(round(pv,3)).replace('.', ',')
power = str(round(power,3)).replace('.', ',')

print('Значение статистики критерия:', t)
print('Граница А критического множества:', A)
print('P-значение критерия:', pv)
print('Мощность критерия:', power)

    ''')
    return


def pyat7():
    print('''
alpha = 0.02
H0 = 1.14
H1 = 1.24
data = '0,889; 1,514; 2,846; 2,811; 0,84; 0,945; 0,02; -0,441; -0,796; 3,739; \
     0,688; 0,777; -0,233; 2,284; -0,681; 1,056; 0,21; 1,8; 0,687; -0,144; \
     1,285; 1,851; 1,402; 1,695; 0,533; 0,87; 0,486; 0,874; 0,312; -0,821'
data = data.replace(',','.')
data = data.replace(';',',')
data = np.array(list(map(lambda x: float(x),data.split(', '))))

chi2_nabl = ((len(data)-1)*np.var(data,ddof = 1))/H0**2
print('статистика критерия  = ',round(chi2_nabl,4))

CHI2 = stats.chi2(len(data)-1)
print(f'границы критического множества:\nA = {round(CHI2.isf(1-alpha/2),4)}\nB = {round(CHI2.isf(alpha/2),4)}')

print('p-value =',round(2*min(CHI2.cdf(chi2_nabl),CHI2.sf(chi2_nabl)),4))
print('веротяность ошибки второго рода =',round(CHI2.cdf((H0**2/H1**2)*CHI2.isf(alpha/2)) - CHI2.cdf((H0**2/H1**2)*CHI2.isf(1-alpha/2)),4))
    ''')
    return

def shestng():
    print('''
x = '
y = '
j = 0.93

# решено
import math
import scipy.stats
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
import pandas as pd
import numpy as np
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
print(f'p = {round(p, 5)}\n s = {round(s, 5)}')
    ''')
    return
