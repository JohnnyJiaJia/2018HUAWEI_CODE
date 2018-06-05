# python ecs.py  ./TrainData_2015.1.1_2015.2.19.txt ./input_5flavors_cpu_7days.txt ./result.txt
# coding=utf-8
from __future__ import division
import time
import exp_smoothing
import simple_predictor
import SA
def predict_vm(ecs_infor_array, input_file_array):
    ## 确定最小日期，便于后面设定时间基数
    ID, flavor, y, s = ecs_infor_array[0].rstrip('\n').split()
    t = y + ' ' + s
    t = time.strptime(t, '%Y-%m-%d %H:%M:%S')
    initial_year = t.tm_year # 历史数据中的第一组数据年份

    first = input_file_array[0].rstrip('\n').split()
    serve_cpu = int(first[0])
    serve_ram = int(first[1])
    vm_number = input_file_array[2].rstrip('\n')
    vm_number = int(vm_number)

    vm = []
    i = 3
    # while input_file_array[i] != '\n':
    while i < vm_number + 3:
        line = input_file_array[i]
        flavor, vm_cpu, vm_ram = line.rstrip('\n').split()
        flavor = int(flavor.strip('flavor'))
        vm_cpu = int(vm_cpu)
        vm_ram = int(vm_ram)
        vm.append([flavor, vm_cpu, vm_ram])
        i += 1
    vm_vector = []
    for item in vm:
        vm_vector.append(item[0])
    resource_type = input_file_array[i + 1].rstrip('\n')

    ## 预测时间（开始和结束）
    predict_begin, zero = input_file_array[i + 3].rstrip('\n').split()
    predict_begin = time.strptime(predict_begin, '%Y-%m-%d')
    predict_begin = predict_begin.tm_yday + 365 * (predict_begin.tm_year - initial_year)
    predict_end, zero = input_file_array[i + 4].rstrip('\n').split()
    predict_end = time.strptime(predict_end, '%Y-%m-%d')
    predict_end = predict_end.tm_yday + 365 * (predict_end.tm_year - initial_year)
    delta_day = predict_end - predict_begin

    ##特殊节日
    #双十一
    d_0 = time.strptime('2015-11-11', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    d_1 = time.strptime('2015-10-01', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    d_2 = time.strptime('2015-12-25', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    d_3= time.strptime('2016-02-07', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    d_4 = time.strptime('2016-10-01', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    d_5 = time.strptime('2016-11-11', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    d_6 = time.strptime('2016-12-25', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    d_7 = time.strptime('2017-01-27', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    d_8 = time.strptime('2017-10-01', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    d_9 = time.strptime('2017-11-11', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    d_10 = time.strptime('2017-12-25', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    ## 根据所有历史数据(天)的指数预测
    flag = 1
    for line in ecs_infor_array:
        line = line.rstrip('\n')  # 去除换行符
        ID, flavor, y, s = line.split()  # 将每一行的字符串按照空格分割开来
        t = y + ' ' + s
        t = time.strptime(t, '%Y-%m-%d %H:%M:%S')
        day_in2015 = t.tm_yday + 365 * (t.tm_year - initial_year)
        flavor = flavor.strip('flavor')  # 去除flavor字符，只保留数字
        flavor = int(flavor)
        ## 读取数据过程中，直接选取并叠加入X_test，形成一个长为vm_number的一维数组

        if vm_vector.count(flavor) != 0:  # 如果属于预测范围
            if flag == 1:
                initial_day = day_in2015 # 除了第一年的年份，第一组历史数据的天也为后续预测设置序列长度提供参考
                total_days = predict_begin - initial_day
                X = [[0 for i in range(total_days)] for j in range(vm_number)]
                flag = 0
            # if (predict_begin-7)<=day_in2015<predict_begin:
            X[vm_vector.index(flavor)][day_in2015 - initial_day] += 1 #序号从零开始，大小还是vm_number*total_days
            # if X[vm_vector.index(flavor)][day_in2015 - initial_day]>30:
            #     X[vm_vector.index(flavor)][day_in2015 - initial_day]=0
    #print(X)
    ## 全用二阶指数平滑，参数统一设置
    #A=[0,0,0.9,0,0,0,0,0,0,0,0,0,0,0,0]
    # A=[0.15]*15
    # A = [float(x * 1) for x in A]
    # a=[]
    # for item in vm_vector:
    #     a.append(A[item-1])
    # print(a)
    # y_test=exp_smoothing.double_exp_smoothing(X,a,delta_day,vm_number,total_days)

    ## 初赛不存在flavor 3,4,6,7,10,12,13,14,15
    # 1,2,5,8,9,11

    y_test = []
    ## 噪声上限参数设置
    # 如果使用丢弃最后一个箱子的做法，可以考虑预测多一点，或者对噪声少控制一些
    # 值越小，阈值下限越低，滤去的噪声越多
    over_lie = 3.5               # 每一天的总数，占所有天平均数的多少倍，如果大于3倍，就认为这天是异常天。 每列相加，和所有列相加的平均比较
    over_ratio = 0.2             # 在天数异常的情况下，同时这个数据在flavor预测历史数据中要超过多少比率的flavor总数。 每个点数据，和每列总数的比例

    ## 二阶平滑参数设置
    # fix_a=0.1 ## 固定值
    # flavor1 = flavor2 = flavor3 = flavor4 = flavor5 = flavor6 = flavor7 = flavor8 =  flavor9 = flavor10 = flavor11 = flavor12 = flavor13 = flavor14 =flavor15 = fix_a

    ## 离散值 flavor越小，其占用资源越小
    flavor1=0.10 ##确定   因为其对后面的装箱影响比较小，所以可以预测多点 0.1-0.15
    flavor2=0.12 ##确定   0.1-0.15
    flavor3=0.2  ##      和flavor9类似 0.2-0.3
    flavor4=0.1  ##      特别平稳，个别突出0.1-0.2
    flavor5=0.05 ##确定   0.1-81.56重点关注，flavor可能预测数据刚好在密集区，所以一般可设置0.05-0.1
    flavor6=0.2  ##       0.2-0.25
    flavor7=0.2  ##       和flavor9类似
    flavor8=0.1 ##确定   敏感，0.1-0.15
    flavor9=0.3  ##确定   0.2-0.3分数区别不大，理论应该是0.2左右
    flavor10=0.2 ##       稀疏到没规律
    flavor11=0.1 ##确定
    flavor12=0.1 ##        和flavor1类似
    flavor13=0.2 ##        稀疏到没规律
    flavor14=0.2 ##        稀疏，波动大
    flavor15=0.2 ##        稀疏波动大
    ss=[]
    for i in range(total_days):
        ss.append(sum([x[i] for x in X])) #每天中所有flavor的总数
    for i in range(vm_number):
        ## 去噪处理，包括节日和异常点
        for j in range(total_days):  # 没什么影响1##
            # if vm_vector[i] == 8 and (j+initial_day==d_0 or j+initial_day==d_1 or
            #                           j+ initial_day==d_2 or j+initial_day==d_3 or j+ initial_day==d_4
            #                           or j+initial_day==d_5 or j+ initial_day==d_6):#j==d_0-1 or
            #     # X[i][j]=0
            #     X[i][j]=(X[i][j-1]+X[i][j+1]+X[i][j])/3
            #if sum([x[j] for x in X]) > over_lie*sum(ss)/total_days and X[i][j] > over_num * sum(X[i]) / total_days:#若某一天的总量特别大，则所有元素都缩小
            sum_flavor=sum([x[j] for x in X]) #各天的所有flavor请求量之和
            if sum_flavor > over_lie*sum(ss)/total_days and X[i][j] / sum_flavor > over_ratio: #定位哪个flavor异常，看其在异常天中的比例
                X[i][j] *= 0.8
                #X[i][j]=sum_flavor*over_ratio #0.2-82.27 0.5-83.866 0.3-82.0
            # if X[i][j] > over_num * sum(X[i]) / total_days:
            #     X[i][j] /= 2

        if vm_vector[i] == 1:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i],0.13,delta_day,predict_begin, predict_end))
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor1, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 2:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i],0.12,delta_day,predict_begin, predict_end))
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor2, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 5:
            # y_test.append(simple_predictor.combine(X[i],0.2,delta_day,total_days,predict_begin,predict_end,10))
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor5, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 8:
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor8,delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 9:
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor9, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 11:
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor11, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 3:##例子不存在flavor3
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor3, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 4:##例子不存在flavor4
            #y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor4, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 6:  ##例子不存在flavor6
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor6, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 7:  ##例子不存在flavor7
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor7, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 10:  ##例子不存在flavor10
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor10, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 12:##例子不存在flavor12
            y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor12, delta_day))
            # y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 13:##例子不存在flavor13
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor13, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 14:##例子不存在flavor14
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor14, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

        elif vm_vector[i] == 15:##例子不存在flavor15
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor15, delta_day))
            y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))

    # y_test = []#
    # for item in range(vm_number):
    #    y_test.append(5)

    ## y_test表示按照预测顺序，每种flavor的数量
    print('y_test')
    print(y_test)
    flavor_total_number = sum(y_test)

    items = []
    for i in range(len(y_test)):
        if y_test[i] != 0:
            for j in range(y_test[i]):
                index_vm = vm_vector[i]
                items.append(index_vm)
    print('vm_vector')
    print(vm_vector)
    ## items表示把y_test中的标号表示出来，如果是多个就把标号多次打印
    print(items)
    ##
    items_w = []
    bin_height_cpu = serve_cpu
    bin_height_mem = serve_ram * 1024
    if resource_type == 'CPU':
        resource = 1
    else:
        resource = 2
    for it in items:
        items_w.append([it, vm[vm_vector.index(it)][1], vm[vm_vector.index(it)][2]])
    ## items_w 表示给items加上资源属性，为分配做准备
    print(items_w)
    items_w.sort(key=lambda item_for_sort: item_for_sort[resource], reverse=True)
    #print('排序后items_w')
    #print(items_w)
    first_fit_sort,min_goal=SA.sa(items_w,bin_height_cpu, bin_height_mem,resource)
    print('未修改最后一个箱子的SA')
    print(first_fit_sort)

    # th=0.01 # 越小表示，不去删数据，基本就是不对分配后进行干预
    th=0.65 # 基本下调参数，分数就成比例下降，说明预测装箱的提升，相比于预测更重要。但高于0.7也就是分数降低了
    ## 对装箱后的资源进行再修改
    if 0<(min_goal-min_goal//1)<th:
        print('开始有点技巧地去掉最后一个箱子，修改预测值，来提高利用率')
        it=first_fit_sort.pop()
        print('未修改的items')
        print(items)
        for item in it:
            items.remove(item)
            xuhao=vm_vector.index(item)
            y_test[xuhao]-=1
        print('更改后的items')
        print(items)

        print('更改后的y_test')
        print(y_test)

        result = [str(sum(y_test))]
        for i in range(len(y_test)):
            result.append('flavor' + str(vm_vector[i]) + ' ' + str(y_test[i]))
        result.append('')
        result.append(str(len(first_fit_sort)))
        for i in range(len(first_fit_sort)):
            temp = []
            first_fit_set = set(first_fit_sort[i])
            for item in first_fit_set:
                if temp:
                    temp = temp + ' flavor' + str(item) + ' ' + str(first_fit_sort[i].count(item))
                else:
                    temp = str(i + 1) + ' flavor' + str(item) + ' ' + str(first_fit_sort[i].count(item))
            result.append(temp)
            ## END ##
        return result

    else: ## 原始输出
        result = [str(flavor_total_number)]
        for i in range(len(y_test)):
            result.append('flavor' + str(vm_vector[i]) + ' ' + str(y_test[i]))
        result.append('')
        result.append(str(len(first_fit_sort)))
        for i in range(len(first_fit_sort)):
            temp = []
            first_fit_set = set(first_fit_sort[i])
            for item in first_fit_set:
                if temp:
                    temp = temp + ' flavor' + str(item) + ' ' + str(first_fit_sort[i].count(item))
                else:
                    temp = str(i + 1) + ' flavor' + str(item) + ' ' + str(first_fit_sort[i].count(item))
            result.append(temp)
            ## END ##
        return result
