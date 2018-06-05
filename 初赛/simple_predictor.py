# coding=utf-8
from __future__ import division
## 增量预测
def cumsum(X,a,delta_day,total_days,predict_begin):
    s=0
    for i in range(delta_day):
        s+=sum(X)/total_days*(i+predict_begin)*a
        s=int(s//1)
        if s<0:
            s=0
    return s

def oneweek(X,predict_begin,predict_end):
    # 根据前一周预测
    #s=sum(X[-(predict_end - predict_begin):])
    #delta = (predict_end - predict_begin) / 7
    #s = int(s * delta * divid // 1)
    s=sum(X[-10:])
    delta = float(predict_end - predict_begin) / 7
    divid = 0.9  # 起到加权的作用
    s = int(float(s) *delta*divid // 1)
    if s < 0:
        s = 0
    return s

def combine(X,a,delta_day,total_days,predict_begin,predict_end,th):
    # 根据前一周预测
    s = sum(X[-7:])
    if s>th:
        ss = 0
        for i in range(delta_day):
            ss += sum(X) / total_days * (i + predict_begin) * a
            ss = int(ss // 1)
    else:
        delta = (predict_end - predict_begin) / 7
        divid = 0.95  # 起到加权的作用
        ss = int(s * delta * divid // 1)
    if ss < 0:
        ss = 0
    return ss

# coding=utf-8
## 一阶指数平滑预测函数
def single_exp_smoothing(X,a,delta_day):#, alpha,delta_day):
    # F = [x[0]] # first value is same as series
    # for t in range(1, len(x)):
    #     F.append(alpha * x[t] + (1 - alpha) * F[t-1])
    # return F
    length_n=len(X)
    S1_1 = []#预测值
    S1_1_empty = []
    x = 0
    for n in range(0, 3):
        x = x + X[n]
    x = float(x) / 3
    S1_1_empty=x
    S1_1.append(S1_1_empty)
    y = []
    for i in range(delta_day):
        for j in range(1, length_n+i):
            S1_1.append(float(a) * X[j] + (1 - float(a)) * S1_1[j-1])  ##计算预估值
        X.append(S1_1[-1])
        y.append(S1_1[-1])
    s=sum(y)
    ss = int(s // 1)
    if ss < 0:
        ss = 0
    return ss

def double_exp_smoothing(X, a, delta_day):##
    delta = 1#(predict_end - predict_begin) / 7
    length_n = len(X)
    S2_1 = []
    S2_2 = []

    x = 0
    for n in range(0, 3):
        x = x + float(X[n])
    x = x / 3
    S2_1_empty = x
    S2_1.append(S2_1_empty)
    S2_2.append(S2_1_empty)

    ##下面是计算一次指数平滑的值
    S2_1_new1 = []
    for j in range(0, length_n):
        if j == 0:
            # print(a)
            # print(X[j])
            # print(S2_1[j])
            S2_1_new1.append(float(a) * float(X[j]) + (1 - float(a)) * float(S2_1[j]))
        else:
            S2_1_new1.append(float(a) * float(X[j]) + (1 - float(a)) * float(S2_1_new1[j - 1]))  ##计算一次指数的值

    ##下面是计算二次指数平滑的值#
    S2_2_new1 = []
    # a=b
    for j in range(0, length_n):
        if j == 0:
            S2_2_new1.append(float(a) * float(S2_1_new1[j]) + (1 - float(a)) * float(S2_2[j]))
        else:
            S2_2_new1.append(float(a) * float(S2_1_new1[j]) + (1 - float(a)) * float(S2_2_new1[j - 1]))  ##计算二次指数的值

    ##下面是计算At、Bt、Ct以及每个预估值Xt的值，直接计算预估值，不一一列举Xt的值了

    Xt = []
    uu = 0
    At = (float(S2_1_new1[len(S2_1_new1) - 1]) * 2 - float(S2_2_new1[len(S2_2_new1) - 1]))
    Bt = (float(a) / (1 - float(a)) * (float(S2_1_new1[len(S2_1_new1) - 1]) - float(S2_2_new1[len(S2_2_new1) - 1])))
    for j in range(1, delta_day + 1):
        uu += At + Bt * int(j)
    if uu < 0:
        uu = 0
    uu = int(uu*delta // 1)
    # Xt.append(uu)
    # print(Xt)
    return uu

def triple_exp_smoothing(X,a,b,c,delta_day,total_days):
    length_n = total_days
    S3_1 = []
    S3_2 = []
    S3_3 = []

    
    x = 0
    for n in range(0, 3):
        x = x + float(X[n])
    x = x / 3
    S3_1_empty=x
    S3_1.append(S3_1_empty)
    S3_2.append(S3_1_empty)
    S3_3.append(S3_1_empty)
    # print(S3_1)
    # a = []  ##这是用来存放阿尔法的数组
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    # for i in range(0, length_m):
    #     v = float(input('请输入第' + str(i + 1) + '组数据的a：'))
    #     a.append(v)

    ##下面是计算一次指数平滑的值
    S3_1_new1 = []
    for j in range(0, length_n):
        if j == 0:
            print(a)
            print(X[j])
            print(S3_1[j])
            S3_1_new1.append(float(a) * float(X[j]) + (1 - float(a)) * float(S3_1[j]))
        else:
            S3_1_new1.append(float(a) * float(X[j]) + (1 - float(a)) * float(S3_1_new1[j - 1]))  ##计算一次指数的值

    ##下面是计算二次指数平滑的值#
    S3_2_new1 = []
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    for j in range(0, length_n):
        if j == 0:
            S3_2_new1.append(float(b) * float(S3_1_new1[j]) + (1 - float(b)) * float(S3_2[j]))
        else:
            S3_2_new1.append(float(b) * float(S3_1_new1[j]) + (1 - float(b)) * float(S3_2_new1[j - 1]))  ##计算二次指数的值

    ##下面是计算二次指数平滑的值
    S3_3_new1 = []
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)

    MSE = 0
    for j in range(0, length_n):
        if j == 0:
            S3_3_new1.append(float(c) * float(S3_2_new1[j]) + (1 - float(c)) * float(S3_3[j]))
        else:
            S3_3_new1.append(float(c) * float(S3_2_new1[j]) + (1 - float(c)) * float(S3_3_new1[j - 1]))  ##计算三次指数的值
        MSE = (int(S3_3_new1[j]) - int(X[j])) ** 2 + MSE
    MSE = (MSE ** (1 / 2)) / int(length_n)
    info_MSE.append(MSE)
    # print(S3_3_new1)

    ##下面是计算At、Bt、Ct以及每个预估值Xt的值，直接计算预估值，不一一列举Xt的值了

    Xt = []
    uu = 0
    At = (float(S3_1_new1[len(S3_1_new1) - 1]) * 3 - float(S3_2_new1[len(S3_2_new1) - 1]) * 3 + float(S3_3_new1[len(S3_3_new1) - 1]))
    Bt = ((float(a) / (2 * ((1 - float(a)) ** 2))) * ((6 - 5 * float(a)) * (float(S3_1_new1[len(S3_1_new1) - 1]) - 2 * (5 - 4 * float(a)) * float(S3_2_new1[len(S3_2_new1) - 1]) + (4 - 3 * float(a)) * float(S3_3_new1[len(S3_3_new1) - 1]))))
    Ct = (((float(a)) ** 2) / (2 * ((1 - float(a)) ** 2))) * (float(S3_1_new1[len(S3_1_new1) - 1]) - float(S3_2_new1[len(S3_2_new1) - 1]) * 2 + float(S3_3_new1[len(S3_3_new1) - 1]))
    for j in range(1, delta_day + 1):
        uu+=At + Bt * int(j) + Ct * (int(j) ** 2)
    if uu<0:
        uu=0
    uu=int(uu//1)
    #Xt.append(uu)
    #print(Xt)
    return uu