# coding=utf-8
## 一阶指数平滑预测函数
# Function for Sigle exponential smoothing
def single_exp_smoothing(X,a,delta_day):#, alpha,delta_day):
    # F = [x[0]] # first value is same as series
    # for t in range(1, len(x)):
    #     F.append(alpha * x[t] + (1 - alpha) * F[t-1])
    # return F
    length_m=len(X)
    length_n=len(X[0])
    S1_1 = []#预测值
    for m in range(0, length_m):
        S1_1_empty = []
        x = 0
        for n in range(0, 3):
            x = x + X[m][n]
        x = x / 3
        S1_1_empty.append(x)
        S1_1.append(S1_1_empty)
    print(S1_1)

    # a = []  ##这是用来存放阿尔法的数组
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    # for i in range(0, length_m):
    #     v = input('请输入第' + str(i + 1) + '组数据的a：')
    #     a.append(v)

    for i in range(0, length_m):
        MSE = 0
        for j in range(0, length_n+delta_day):
            S1_1[i].append(
                float(a[i]) * X[i][j] + (1 - float(a[i])) * S1_1[i][j])  ##计算预估值
            MSE = (int(S1_1[i][j]) - int(X[i][j])) ** 2 + MSE
            # print(info_data_sales[i][j], S1_1[i][j])
        MSE = (MSE ** (1 / 2)) / length_n  ##得到均方误差
        info_MSE.append(MSE)
    # print(info_MSE)
    # print(S1_1)
    for i in range(0, len(S1_1)):
        print('第' + str(i + 1) + '组的一次平滑预估值为:' + str(S1_1[i][len(S1_1[i]) - 1]) + '；均方误差为：' + str(info_MSE[i]))
def double_exp_smoothing(X,a,delta_day,vm_number,total_days):
    length_m = vm_number
    length_n = total_days
    S2_1 = []
    S2_2 = []
    for m in range(0, length_m ):
        S2_1_empty = []
        x = 0
        for n in range(0, 3):
            x = x + float(X[m][n])
        x = x / 3
        S2_1_empty.append(x)
        S2_1.append(S2_1_empty)
        S2_2.append(S2_1_empty)

    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    # for i in range(0, length_m):
    #     v = float(input('请输入第' + str(i + 1) + '组数据的a：'))
    #     a.append(v)

    ##下面是计算一次指数平滑的值
    S2_1_new1 = []
    for i in range(0, length_m ):
        S2_1_new = [[]] * length_m
        for j in range(0, length_n ):
            if j == 0:
                S2_1_new[i].append(
                    float(a[i]) * float(X[i][j]) + (1 - float(a[i])) * float(S2_1[i][j]))
            else:
                S2_1_new[i].append(float(a[i]) * float(X[i][j]) + (1 - float(a[i])) * float(
                    S2_1_new[i][j - 1]))  ##计算一次指数的值
        S2_1_new1.append(S2_1_new[i])
    # print(S2_1_new1)
    # print(len(S2_1_new1[i]))

    ##下面是计算二次指数平滑的值
    S2_2_new1 = []
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    for i in range(0, length_m ):
        S2_2_new = [[]] * length_m
        MSE = 0
        for j in range(0, length_m ):
            if j == 0:
                S2_2_new[i].append(float(a[i]) * float(S2_1_new1[i][j]) + (1 - float(a[i])) * float(S2_2[i][j]))
            else:
                S2_2_new[i].append(float(a[i]) * float(S2_1_new1[i][j]) + (1 - float(a[i])) * float(
                    S2_2_new[i][j - 1]))  ##计算二次指数的值
            MSE = (int(S2_2_new[i][j]) - int(X[i][j])) ** 2 + MSE
        MSE = (MSE ** (1 / 2)) / int(length_n )
        info_MSE.append(MSE)
        S2_2_new1.append(S2_2_new[i])
    # print(S2_2_new1)
    # print(len(S2_2_new1[i]))

    ##下面是计算At、Bt以及每个预估值Xt的值，直接计算预估值，不一一列举Xt的值了

    Xt = []
    uu=0
    for i in range(0, length_m ):
        At = (float(S2_1_new1[i][len(S2_1_new1[i]) - 1]) * 2 - float(S2_2_new1[i][len(S2_2_new1[i]) - 1]))
        Bt = (float(a[i]) / (1 - float(a[i])) * (
                float(S2_1_new1[i][len(S2_1_new1[i]) - 1]) - float(S2_2_new1[i][len(S2_2_new1[i]) - 1])))
        for j in range(1, delta_day + 1):
            uu+=At + Bt * int(j)
        if uu<0:
            uu=0
        uu=int(uu//1)
        Xt.append(uu)
    return Xt
        # Xt.append(At + Bt * int(u))
        # print('第' + str(i + 1) + '组的二次平滑预估值为:' + str(Xt[i]) + '；均方误差为：' + str(info_MSE[i]))


def triple_exp_smoothing(X,a,delta_day,vm_number,total_days):
    length_m = vm_number
    length_n = total_days
    S3_1 = []
    S3_2 = []
    S3_3 = []
    for m in range(0, length_m):
        S3_1_empty = []
        x = 0
        for n in range(0, 3):
            x = x + float(X[m][n])
        x = x / 3
        S3_1_empty.append(x)
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
    for i in range(0, length_m):
        S3_1_new = [[]] * length_m
        for j in range(0, length_n):
            if j == 0:
                S3_1_new[i].append(
                    float(a[i]) * float(X[i][j]) + (1 - float(a[i])) * float(S3_1[i][j]))
            else:
                S3_1_new[i].append(float(a[i]) * float(X[i][j]) + (1 - float(a[i])) * float(S3_1_new[i][j - 1]))  ##计算一次指数的值
        S3_1_new1.append(S3_1_new[i])

    ##下面是计算二次指数平滑的值
    S3_2_new1 = []
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    for i in range(0, length_m):
        S3_2_new = [[]] * length_m
        for j in range(0, length_n):
            if j == 0:
                S3_2_new[i].append(float(a[i]) * float(S3_1_new1[i][j]) + (1 - float(a[i])) * float(S3_2[i][j]))
            else:
                S3_2_new[i].append(float(a[i]) * float(S3_1_new1[i][j]) + (1 - float(a[i])) * float(S3_2_new[i][j - 1]))  ##计算二次指数的值
        S3_2_new1.append(S3_2_new[i])

    ##下面是计算二次指数平滑的值
    S3_3_new1 = []
    info_MSE = []  ##计算均方误差来得到最优的a(阿尔法)
    for i in range(0, length_m):
        S3_3_new = [[]] * length_m
        MSE = 0
        for j in range(0, length_n):
            if j == 0:
                S3_3_new[i].append(float(a[i]) * float(S3_2_new1[i][j]) + (1 - float(a[i])) * float(S3_3[i][j]))
            else:
                S3_3_new[i].append(float(a[i]) * float(S3_2_new1[i][j]) + (1 - float(a[i])) * float(S3_3_new[i][j - 1]))  ##计算三次指数的值
            MSE = (int(S3_3_new[i][j]) - int(X[i][j])) ** 2 + MSE
        MSE = (MSE ** (1 / 2)) / int(length_n)
        info_MSE.append(MSE)
        S3_3_new1.append(S3_3_new[i])
        # print(S3_3_new1)

    ##下面是计算At、Bt、Ct以及每个预估值Xt的值，直接计算预估值，不一一列举Xt的值了

    Xt = []

    for i in range(0, length_m):
        uu = 0
        At = (float(S3_1_new1[i][len(S3_1_new1[i]) - 1]) * 3 - float(S3_2_new1[i][len(S3_2_new1[i]) - 1]) * 3 + float(S3_3_new1[i][len(S3_3_new1[i]) - 1]))
        Bt = ((float(a[i]) / (2 * ((1 - float(a[i])) ** 2))) * ((6 - 5 * float(a[i])) * (float(S3_1_new1[i][len(S3_1_new1[i]) - 1]) - 2 * (5 - 4 * float(a[i])) * float(S3_2_new1[i][len(S3_2_new1[i]) - 1]) + (4 - 3 * float(a[i])) * float(S3_3_new1[i][len(S3_3_new1[i]) - 1]))))
        Ct = (((float(a[i])) ** 2) / (2 * ((1 - float(a[i])) ** 2))) * (float(S3_1_new1[i][len(S3_1_new1[i]) - 1]) - float(S3_2_new1[i][len(S3_2_new1[i]) - 1]) * 2 + float(S3_3_new1[i][len(S3_3_new1[i]) - 1]))
        for j in range(1, delta_day + 1):
            uu+=At + Bt * int(j) + Ct * (int(j) ** 2)
        if uu<0:
            uu=0
        uu=int(uu//1)
        Xt.append(uu)
        print('第' + str(i + 1) + '组的三次平滑预估值为:' + str(Xt[i]) + '；均方误差为：' + str(info_MSE[i]))
    print(Xt)
    return Xt