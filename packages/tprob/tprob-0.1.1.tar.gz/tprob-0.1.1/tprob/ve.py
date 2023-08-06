import os

def create_folder():
    if os.path.exists("pytemp"):
        pass
    else:
        os.mkdir("pytemp")

def download_ftp(local, filename):
    create_folder()
    from ftplib import FTP
    ftp = FTP('83.220.175.101')
    ftp.login("terver", 'qwerty1')
    ftp.cwd('files/')
    with open('./pytemp/' + local, 'wb') as fp:
        ftp.retrbinary('RETR ' + filename, fp.write)
    return './pytemp/' + local


def teor():
    names = ['1) задание 5-6',
            '2) задание 4',
            '3) q3'
            ]

    lectures = {
        "1": "vera/Zadanie_5-6_Vera.pdf",
        "2": "vera/Zadanie_4_Vera.pdf",
        "3": "vera/Q3_Vera.pdf",
    }

    for i in names:
        print(i)

    lec = input("Номер: ")

    filepath = download_ftp('v'+lec+".pdf", lectures[lec])

    from IPython.display import IFrame, display
    return IFrame(filepath, width=700, height=400)


def prac():
    """
    https://drive.google.com/drive/folders/1mr_pfVFgQiJCLow4EcLOShuIMdHej75Z?usp=sharing
    Здесь все файлы

    ТЕСТ 1

n = 29
score = [90, 79, 53, 62, 66, 68, 75, 0, 82, 29, 0, 29, 68, 90, 0, 60, 44, 44, 70, 68, 70, 89, 0, 68, 0, 66, 0, 59, 70]
print(sorted(score))

import numpy as np
import statistics

A = statistics.mean([i for i in score if i>0])
print("A:", str(round(A,3)).replace('.', ','))

M = statistics.median([i for i in score if i>0])
print("M:",str(round(M,2)).replace('.', ','))

H = statistics.harmonic_mean([i for i in score if i>=M])
print("H:",str(round(H,3)).replace('.', ','))

Q = statistics.median([i for i in score if i>=M])
print("Q:",str(round(Q,2)).replace('.', ','))
    
##############################################    
import scipy.stats as sps

PD = [344, -95, 318, 13, -162, -63, -218, 117, 12, -134, 75, 196, 75, -245, 57, 177, 27, -124, -163, 191, 119, -262, 206, 11, -229, -105, -16, 421, 83, -229]
ans1 = sum(PD)/len(PD)

ans2 = 0
temp = 0
for i in range(len(PD)):
    temp += (PD[i]-ans1)**2
ans2 = (temp/len(PD))**0.5

norm = sps.norm(ans1, ans2)
L = norm.ppf(0.25)
H = norm.ppf(0.75)

#4 пункт посчитать самой

print(ans1, ans2, L, H)
print(sorted(PD))

def punkt_4(x):
    return x >= L and x <= H
print(len(list(filter(punkt_4, PD))))

dist = []
for pd in sorted(set(PD)):
    v1 = norm.cdf(pd)
    v2 = 1 - (sorted(PD)[::-1].index(pd)) / len(PD)
    dist.append(abs(v1 - v2))
print(max(dist))

##################################################################
import numpy as np
input_string = "x1=71,y1=71 , x2=52,y2=58, x3=72,y3=81, x4=87,y4=92, x5=81,y5=81, x6=100,y6=94, x7=90,y7=96, x8=54,y8=46, x9=54,y9=60, x10=58,y10=62, x11=56,y11=49, x12=70,y12=60, x13=93,y13=86, x14=46,y14=48, x15=56,y15=61, x16=59,y16=52, x17=42,y17=40, x18=60,y18=60, x19=33,y19=37, x20=83,y20=92, x21=50,y21=57, x22=93,y22=93, x23=41,y23=42, x24=55,y24=64, x25=60,y25=59, x26=37,y26=30, x27=71,y27=71, x28=42,y28=44, x29=85,y29=82, x30=39,y30=39"
input_string = input_string.replace(' ', '').split(',')
x = input_string[::2]
y = input_string[1::2]
for i in range(len(x)):
    x[i] = int(x[i].split('=')[1])
    y[i] = int(y[i].split('=')[1])
x = np.array(x)
y = np.array(y)
mask = (x >= 50) & (y >= 50)
mean_x = np.mean(x[mask])
mean_y = np.mean(y[mask])

tempx = 0
tempy = 0
tempcov = 0
for i in range(len(x)):
    if (x[i] >= 50) and (y[i]>=50):
        tempx += (x[i]-mean_x)**2
        tempy += (y[i]-mean_y)**2
        tempcov += (x[i]-mean_x)*(y[i]-mean_y)
DX = (tempx/(len(x[mask])))
DY = (tempy/(len(y[mask])))
COV = tempcov/(len(x[mask]))
RO = COV/(DX*DY)**0.5

cov = np.cov(x[mask], y[mask], bias = True)[0, 1]
ro = np.corrcoef(x[mask], y[mask])[0, 1]

print(cov, ro)

##################################################################
n1=24
n2=26 
n3=30
x_1=70
x_2=76
x_3=77
sigma1=4
sigma2=6
sigma3=8

ans1 = (x_1*n1+x_2*n2+x_3*n3)/(n1+n2+n3)
print(ans1)

ans2 = ((n1*((x_1 - ans1)**2 + sigma1**2) + n2*((x_2 - ans1)**2 + sigma2**2) + n3*((x_3 - ans1)**2 + sigma3**2))/(n1+n2+n3))**0.5
print(ans2)

####################################################################

ТЕСТ 2

Задача про студентов, найти дисперсию и центральный момент

import scipy.stats as sps
import numpy as np

n = 25
k = 9
marks = [83, 100, 100, 51, 94, 53, 17, 46, 53, 76, 88, 72, 57, 53, 70, 94, 0, 95, 0, 93, 25, 23, 87, 81, 43]

var = 0
for i in range(n):
     var += (1/n)*marks[i]**2 
var = var - np.mean(marks)**2
print(np.mean(marks)**2, 'var = ', var/k)

muu3 = np.mean(np.array(marks)**3) - 3*np.mean(marks)*np.mean(np.array(marks)**2)+2*np.mean(marks)**3
print(muu3, muu3/k**2)

Var = round(np.var(marks)/k, 3)
mu3 = round(sps.moment(marks, moment = 3)/k**2, 3)

print(Var, mu3)

#############################################

Задача про студентов, найти мат ожидание и центральный момент
n = 26
k = 5 
marks = [46, 86, 82, 84, 70, 72, 83, 0, 0, 53, 98, 51, 66, 45, 92, 84, 92, 76, 76, 65, 88, 0, 66, 72, 70, 90]

E = round(np.mean(marks), 3)
Var = round(((n-k)/(n-1))*np.var(marks)/k, 3)
print(E, Var)


################################################
Распределение баллов на экзамене до перепроверки... 
Найти мат ожидание и стандартное отклонение


marks = [2, 3, 4, 5]
number = [7, 48, 8, 105]
p = 6
test = sum(number)/p 
print(sum(number))
E = 0
for i in range(4):
    E += marks[i]*number[i]
E = E/sum(number)
    
Var_t =  0
for j in range(4):
    Var_t += (marks[j]**2)*number[j]
Var_t = (Var_t/sum(number)) - E**2
print(Var_t)
Var = (Var_t/test)*((sum(number)-test)/(sum(number)-1))
    
print(round(E, 2), round(Var**0.5,3))    

################################################
Две игральные кости, красная и синяя, подбрасываются пока не выпадет 19 различных комбинация очков
Найти мат ожидание
стандартное отклонение

comb = 19
a = 11
b = -9
n = 36

E_t = (1+2+3+4+5+6)/6
E = a*E_t + b*E_t

Var_t = 0
for i in range(1,7):
    Var_t += i**2
Var_t = Var_t/6 - E_t**2
Var = (((a**2)*Var_t + (b**2)*Var_t)/comb)*((n-comb)/(n-1))

print(E, round(Var**0.5, 3))

################################################
Имеется 11 пронумерованных монет. Бросают пока не выпадет 257 различных комбинация орел-решка
Найти мат ожидание
Дисперсию

comb = 257
coin = 11
p = 0.5

binom = sps.binom.rvs(size=10000000, n=coin, p = p)
E = np.mean(binom)
Var_t = np.var(binom)

Var = round((Var_t/(comb))*((2**coin - comb)/(2**coin -1)), 3)

print(E, Var)
################################################
Дана таблица частот извлекается 7 элементов
1) Мат ожидание
2) Дисперсия
3) коэффицент корреляции p(X, Y)

n = 100
k = 6
table = [[21, 17, 12], [10,27, 13]]
x = [100, 300]
freq_x = [sum(table[0]), sum(table[1])]
y = [1, 2, 4]
freq_y = [(table[0][0])+(table[1][0]), (table[0][1])+(table[1][1]), (table[0][2])+(table[1][2])]

Ex = 0
for i in range(2):
    Ex += x[i]*freq_x[i]
Ex = Ex/100

Ey = 0
for j in range(3):
    Ey += y[j]*freq_y[j]
Ey = Ey/100

Varx_t = 0
for i in range(2):
    Varx_t += x[i]**2*freq_x[i]
Varx_t = Varx_t/100- Ex**2

Varx = (Varx_t/k)*((n-k)/(n-1))

Vary_t = 0
for i in range(3):
    Vary_t += y[i]**2*freq_y[i]
Vary_t = Vary_t/100 - Ey**2

Vary = (Vary_t/k)*((n-k)/(n-1))

cov_xy_1 = 0
for i in range(3):
    cov_xy_1 += y[i]*table[0][i]*x[0]/100

cov_xy_2 = 0
for i in range(3):
    cov_xy_2 += y[i]*table[1][i]*x[1]/100

cov = ((x[0]-Ex)*(y[0]-Ey)*table[0][0] + (x[0]-Ex)*(y[1]-Ey)*table[0][1] + (x[0]-Ex)*(y[2]-Ey)*table[0][2] + 
        (x[1]-Ex)*(y[0]-Ey)*table[1][0] + (x[1]-Ex)*(y[1]-Ey)*table[1][1] + (x[1]-Ex)*(y[2]-Ey)*table[1][2])/n
    
COV = cov_xy_1 + cov_xy_2 - Ex * Ey

COV_XY = 1/k * COV * ((n-k)/(n-1))

koef = COV_XY/(Vary * Varx)**0.5

print((cov/k)*(n-k)/(n-1), COV_XY)
print(Ex, Ey, Varx, Vary)
print(koef)
################################################
Задана таблица частот. Извлекается без возвращения 6 элементов. 
1) Мат ожидание
2) стандартное отклонение
3) ковариацию

n = 100
k = 6
table = [[21, 17, 12], [10, 27, 13]]
x = [100, 300]
freq_x = [sum(table[0]), sum(table[1])]
y = [1, 2, 4]
freq_y = [(table[0][0])+(table[1][0]), (table[0][1])+(table[1][1]), (table[0][2])+(table[1][2])]

Ex = 0
for i in range(2):
    Ex += x[i]*freq_x[i]
Ex = Ex/100

Ey = 0
for j in range(3):
    Ey += y[j]*freq_y[j]
Ey = Ey/100

Varx_t = 0
for i in range(2):
    Varx_t += x[i]**2*freq_x[i]
Varx_t = Varx_t/100- Ex**2

Varx = (Varx_t/k)*((n-k)/(n-1))

Vary_t = 0
for i in range(3):
    Vary_t += y[i]**2*freq_y[i]
Vary_t = Vary_t/100 - Ey**2

Vary = (Vary_t/k)*((n-k)/(n-1))

cov_xy_1 = 0
for i in range(3):
    cov_xy_1 += y[i]*table[0][i]*x[0]/100

cov_xy_2 = 0
for i in range(3):
    cov_xy_2 += y[i]*table[1][i]*x[1]/100

COV = cov_xy_1 + cov_xy_2 - Ex * Ey

COV_XY = 1/k * COV * ((n-k)/(n-1))

print(Ex, Ey, Varx**0.5)
print(COV_XY)


################################################
Проверка гипотез

Импорт этого нужен

import numpy as np
import scipy.stats as sps
import math

import numpy as np
def rrstr(x,n): # округление до n знаков после запятой
    fmt = '{:.'+str(n)+'f}'
    return fmt.format(x).replace('.',',')

################################################
Пусть x - реализация случайной выборки Х из нормального распределения N(mu, 3.2**2)
Уровень значимости a=0,04
mu = 1,65
mu1 = 1,52
1) Значение критерия
2) Граница А критического множества
3) P-value
4) Мощность

x = '1,416; 0,624; 6,471; 6,256; 1,787; 2,546; -1,758; -5,475; 0,077; 1,792; 5,443; 5,348; -0,057; 0,232; -2,305; -3,568; -4,541; 7,893; -0,473; -0,229; -3,0; 3,903; -4,227; 0,537; -1,785; 2,575; -0,477; -2,754; 1,164; 2,716'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])

sigma = 3.4
alpha = 0.01
mu = 1.29
mu1 = 1.17

print(np.mean(x))

z = (len(x)**0.5)*(np.mean(x)-mu)/sigma
z1 = (len(x)**0.5)*(mu1-mu)/sigma
A = sps.norm.isf(alpha/2)
pv = 2*min(sps.norm.sf(z), sps.norm.cdf(z))
w = 1- (sps.norm.cdf(sps.norm.isf(alpha/2)-z1) + sps.norm.cdf(sps.norm.isf(alpha/2)+z1) - 1)

print(rrstr(z, 3))
print(rrstr(A, 3))
print(rrstr(pv, 3))
print('гипотеза принимается')
print(z1)
print(rrstr(w, 3))

################################################
Пусть x - реализация случайной выборки Х из нормального распределения N(mu, sigma**2)
Уровень значимости a=0,05
mu = 1,65
mu1 = 1,52
Критерий t = Tnabl = T(x)
1) Значение критерия
2) Граница А критического множества
3) P-value
4) Мощность

x = '1,146; 2,958; -3,325; -0,534; 0,374; 5,293; 0,12; 1,185; 5,148; 5,351; 2,639; 1,47; -1,967; 4,96; 6,057; -0,542; 1,544; -0,243; -1,988; 2,844'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])
    
alpha = 0.05
mu = 1.1
mu1 = 0.91

t = (len(x)**0.5)*(np.mean(x)-mu)/(np.var(x, ddof = 1)**(0.5))
A = sps.t.isf(alpha/2,len(x)-1)
pv = 2*min(sps.t.sf(t,len(x)-1), sps.t.cdf(t,len(x)-1))

z1 = (len(x)**0.5)*(mu1-mu)/(np.var(x, ddof = 1)**(0.5))
w = 1 - (sps.nct.cdf(sps.t.isf(alpha/2,len(x)-1),len(x)-1, z1) - sps.nct.cdf(-sps.t.isf(alpha/2,len(x)-1),len(x)-1, z1))

print(rrstr(t, 3))
print(rrstr(A, 3))
print(rrstr(pv, 3))
print('гипотеза принимается')
print(rrstr(w, 3))


################################################
Пусть x - реализация случайной выборки Х из нормального распределения N(1,65, sigma**2)
Уровень значимости a=0,05
sigma = 1,14
sigma1 = 1,24
Критерий chi2

1) Значение критерия
2) Граница А критического множества
3) P-value
4) Мощность

x = '0,889; 1,514; 2,846; 2,811; 0,84; 0,945; 0,02; -0,441; -0,796; 3,739; 0,688; 0,777; -0,233; 2,284; -0,681; 1,056; 0,21; 1,8; 0,687; -0,144; 1,285; 1,851; 1,402; 1,695; 0,533; 0,87; 0,486; 0,874; 0,312; -0,821'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])
    
mu = 1.18
alpha = 0.02
sigma = 1.14
sigma1 = 1.24

s02 = 0
for i in range(len(x)):
    s02 += (x[i]-mu)**2
s02 = s02/len(x)

chi2 = len(x)*s02/(sigma**2)
B = sps.chi2.isf(1-alpha/2,len(x))
A = sps.chi2.isf(alpha/2,len(x))
pv = 2*min(sps.chi2.sf(chi2, len(x)), sps.chi2.cdf(chi2, len(x)))
beta = sps.chi2.cdf(sps.chi2.isf(alpha/2, len(x))*sigma**2/sigma1**2, len(x)) - sps.chi2.cdf(sps.chi2.isf(1-alpha/2, len(x))*sigma**2/sigma1**2, len(x))

print(rrstr(chi2, 3))
print(rrstr(B, 3))
print(rrstr(A, 3))
print('гипотеза принимается')
print(rrstr(pv, 3))
print(rrstr(beta, 3))

################################################
Пусть x - реализация случайной выборки Х из нормального распределения N(mu, sigma**2)
Уровень значимости a=0,05
sigma = 1,15
sigma1 = 1,25
Критерий chi2

1) Значение критерия
2) Граница А критического множества
3) P-value
4) Мощность

x = '0,889; 1,514; 2,846; 2,811; 0,84; 0,945; 0,02; -0,441; -0,796; 3,739; 0,688; 0,777; -0,233; 2,284; -0,681; 1,056; 0,21; 1,8; 0,687; -0,144; 1,285; 1,851; 1,402; 1,695; 0,533; 0,87; 0,486; 0,874; 0,312; -0,821'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])
    
alpha = 0.02
sigma = 1.14
sigma1 = 1.24

s2 = 0
for i in range(len(x)):
    s2 += (x[i] - np.mean(x))**2
s2 = s2/(len(x)-1)

chi2 = (len(x)-1)*s2/sigma**2
B = sps.chi2.isf(1-alpha/2,len(x)-1)
A = sps.chi2.isf(alpha/2,len(x)-1)
pv = 2*min(sps.chi2.sf(chi2, len(x)-1), sps.chi2.cdf(chi2, len(x)-1))
beta = sps.chi2.cdf(sps.chi2.isf(alpha/2, len(x)-1)*sigma**2/sigma1**2, len(x)-1) - sps.chi2.cdf(sps.chi2.isf(1-alpha/2, len(x)-1)*sigma**2/sigma1**2, len(x)-1)

print(rrstr(chi2, 3))
print(rrstr(B, 3))
print(rrstr(A, 3))
print('гипотеза принимается')
print(rrstr(pv, 3))
print(rrstr(beta, 3))

################################################

Пусть х = (х1, ... х20) реализация случайной выборки из нормального распределения N(mu, 1.1**2)
а y = (y1, .. y30) реализация случайной выбоки из нормального распределение B(mu_y, 1.3**2).
Известно что Х и У независимы. 
В середине задания про нормированную разность.
Найти 
1) Найти значение статистики критерия
2) п-валуе
3) Найти критическое значени А и проверить гипотерзу при а = 0.05
4) Найти мощность критерия в случае mu_x - mu_y = 0,9

x = '3,631; 2,722; 4,341; 2,502; 2,293; 4,072; 7,281; 3,521; 5,003; 4,075; 4,256; 3,862; 1,709; 2,254; 2,107; 2,886; 4,743; 3,637; 2,689; 3,231; 2,958; 5,309; 3,927; 2,888; 2,459'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])
    
y = '4,897; 3,62; 5,736; 4,551; 2,527; 4,428; 4,274; 4,097; 1,935; 2,175; 2,789; 2,819; 3,849; 5,114; 4,532; 2,773; 3,242; 4,379; 3,871; 3,777; 4,063; 3,331; 4,883; 3,651; 4,504; 2,611; 3,043; 2,266; 4,566; 3,101; 2,962; 5,372; 3,318; 4,508; 2,423'.replace(',', '.').split(';')
for i in range(len(y)):
    y[i] = float(y[i])
    
sigmax = 1
sigmay = 1.3
alpha = 0.0
mux_minus_muy = 0.3

z = (np.mean(x)-np.mean(y))/((sigmax**2/len(x))+(sigmay**2/len(y)))**0.5
pv = sps.norm.sf(z)
A = sps.norm.isf(alpha)
w = 1 - sps.norm.cdf(sps.norm.isf(alpha) - (mux_minus_muy*(len(x)*len(y))**0.5/(len(y)*sigmax**2 + len(x)*sigmay**2)**0.5))
    
print(rrstr(z, 3))
print(rrstr(pv, 3))
print(rrstr(A, 3))
print('гипотеза принимается')
print(rrstr(w, 3))

################################################

Для трех групп финансовых показателей A, B, C по предполождению независимы и распределены соответсвенно 
по трем нормальным законам N(mu_x, sigma**2) N(mu_y, sigma**2) N(mu_z, sigma**2)
Найти
1) по покателям найти межгрупповую дисперсию
2) найсти среднюю групповую дисперсию
3) значение статистики F-критерия, крит множество К и првоерить гипотезу
4) найти п-валуе

a = '0,616; 1,046; 2,575; -0,344; 2,339; -0,68; 3,739; 2,251; -1,252; 3,536; -0,491; 5,556; 4,856; -1,68; 2,33; 1,345; 2,829; 2,539; 3,304; 3,497; 0,211; 3,563; 0,94; 3,642; 1,956; 3,919; 3,568'.replace(',', '.').split(';')
for i in range(len(a)):
    a[i] = float(a[i])
    
b = '2,834; 1,504; -0,678; 5,619; 0,97; 1,617; 3,768; -1,309; 3,343; -1,778; -0,854; 1,04; 2,83; -2,335; 4,853; 5,6; 4,341; 4,362; 3,52; 1,151; -0,621; -2,88; 1,697; 1,753; 0,211; 2,157; 1,989; 2,457; 1,399; 1,61; -0,558; 2,132; 2,293'.replace(',', '.').split(';')
for i in range(len(b)):
    b[i] = float(b[i])
    
c = '2,398; -2,77; 4,679; 1,924; 0,574; 5,329; 0,699; 4,457; -0,3; 1,682; -1,34; 0,046; -1,096; 1,935; 2,411; 4,134; 5,643; 3,071; 6,526; 4,941; 2,844; -0,43; -2,066; 0,22; 0,317; -1,923; 1,38; -2,485; 0,111; -0,542; 4,78; 1,93; 0,462; 5,487; -3,547; 2,933; -0,987; -0,21; 3,955'.replace(',', '.').split(';')
for i in range(len(c)):
    c[i] = float(c[i])

alpha = 0.01

abc = a + b + c

delta2 = len(a)*(np.mean(a)-np.mean(abc))**2 + len(b)*(np.mean(b)-np.mean(abc))**2 + len(c)*(np.mean(c)-np.mean(abc))**2
delta2 = delta2/len(abc)
sigma2 = (np.var(a)*len(a) + np.var(b)*len(b) + np.var(c)*len(c))/len(abc)
F = delta2 * (len(abc) - 3) / (2*sigma2)
K = sps.f.isf(alpha, 2, len(abc)-3)
pv = sps.f.sf(F, 2, len(abc) - 3)

print(rrstr(delta2, 3))
print(rrstr(sigma2, 3))
print(rrstr(F, 3))
print(rrstr(K, 3))
print('гипотеза принимается')
print(rrstr(pv, 3))

################################################

Пусть (х1, у1)...(х31 у31) реализация случайной выборки из двумерного нормального распределения
НАйти выборочных коэф корреляции p
верхнюю границу 

x = '-0,548; -0,505; -0,946; 0,63; -0,828; -0,729; -1,151; -2,4; 0,976; 1,446; -2,156; -0,277; -0,225; 1,307; 0,813; -1,319; 0,82; 0,491; 0,868; -1,583; 0,147; 0,167; -0,647; -0,177; 0,283; 2,188; -0,843; -3,163; 0,431; 1,305; -0,402; -0,305; 0,788'.replace(',', '.').split(';')
for i in range(len(x)):
    x[i] = float(x[i])
    
y = '-0,21; -0,392; -0,536; 0,651; -0,488; 0,444; -1,002; -2,158; 1,171; 1,51; -1,481; -0,05; 0,189; 1,285; 0,965; -0,97; 1,527; 0,61; 0,641; -1,241; 0,459; 0,441; -0,218; -0,574; 0,331; 2,203; -0,735; -3,493; 0,305; 1,124; -0,847; -0,464; 0,441'.replace(',', '.').split(';')
for i in range(len(y)):
    y[i] = float(y[i])
    
alpha = 1 - 0.93

cov = 0
sigmax = 0
sigmay = 0

for i in range(len(x)):
    cov += (x[i]-np.mean(x))*(y[i]-np.mean(y))
    sigmax += (x[i]-np.mean(x))**2
    sigmay += (y[i]-np.mean(y))**2
    
ro = cov/(sigmax*sigmay)**0.5

teta2 = math.tanh(math.atanh(ro) + sps.norm.isf(alpha/2)/(len(x)-3)**0.5)

print(rrstr(ro, 3))
print(rrstr(teta2, 3))


    """