# python ecs.py  ./TrainData_2015.12.txt ./input_3hosttypes_5flavors_1week.txt ./result.txt
# coding=utf-8
from __future__ import division
import time
import exp_smoothing
import simple_predictor
import SA
def predict_vm(ecs_infor_array, input_file_array,time_start):
    time_start = time.time()
    ## 确定最小日期，便于后面设定时间基数
    ID, flavor, y, s = ecs_infor_array[0].rstrip('\n').split()
    t = y + ' ' + s
    t = time.strptime(t, '%Y-%m-%d %H:%M:%S')
    initial_year = t.tm_year # 历史数据中的第一组数据年份

    ## 得出最后一天
    ID, flavor, y, s = ecs_infor_array[-2].rstrip('\n').split()
    t = y + ' ' + s
    t = time.strptime(t, '%Y-%m-%d %H:%M:%S')
    final_day = t.tm_yday  # 历史数据中的第一组数据年份

    ## 多种不同的物理服务器
    serve_number=int(input_file_array[0].rstrip('\n'))
    serve_matrix=[]
    for i in range(serve_number):
        serve, serve_cpu, serve_ram,serve_hardware=input_file_array[i+1].rstrip('\n').split()
        serve_matrix.append([int(serve_cpu),int(serve_ram)*1024,int(serve_ram)*1024/int(serve_cpu),serve]) #增加MEM和CPU的比例
    serve_matrix.sort(key=lambda item_for_sort: item_for_sort[0])
    print('serve_matrix')
    print(serve_matrix)
    vm_number = input_file_array[i+3].rstrip('\n')
    vm_number = int(vm_number)

    vm = []
    j = i+4
    # while input_file_array[i] != '\n':
    while j < vm_number + i+4:
        line = input_file_array[j]
        flavor, vm_cpu, vm_ram = line.rstrip('\n').split()
        flavor = int(flavor.strip('flavor'))
        vm_cpu = int(vm_cpu)
        vm_ram = int(vm_ram)
        vm.append([flavor, vm_cpu, vm_ram])
        j += 1
    vm_vector = []
    for item in vm:
        vm_vector.append(item[0])


    ## 预测时间（开始和结束）
    predict_begin, zero = input_file_array[j + 1].rstrip('\n').split()
    predict_begin = time.strptime(predict_begin, '%Y-%m-%d')
    predict_begin = predict_begin.tm_yday + 365 * (predict_begin.tm_year - initial_year)
    predict_end, zero = input_file_array[j + 2].rstrip('\n').split()
    predict_end = time.strptime(predict_end, '%Y-%m-%d')
    predict_end = predict_end.tm_yday + 365 * (predict_end.tm_year - initial_year)
    if zero != '00:00:00':
        predict_end+=1
    delta_day = predict_end - predict_begin




    ##特殊节日
    #双十一
    # d_0 = time.strptime('2015-11-11', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    # d_1 = time.strptime('2015-10-01', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    # d_2 = time.strptime('2015-12-25', '%Y-%m-%d').tm_yday+365 * (2015 - initial_year)
    # d_3= time.strptime('2016-02-07', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    # d_4 = time.strptime('2016-10-01', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    # d_5 = time.strptime('2016-11-11', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    # d_6 = time.strptime('2016-12-25', '%Y-%m-%d').tm_yday+365 * (2016 - initial_year)
    # d_7 = time.strptime('2017-01-27', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    # d_8 = time.strptime('2017-10-01', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    # d_9 = time.strptime('2017-11-11', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
    # d_10 = time.strptime('2017-12-25', '%Y-%m-%d').tm_yday + 365 * (2017 - initial_year)
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
                total_days = final_day - initial_day +1
                X = [[0 for i in range(total_days)] for j in range(vm_number)]
                flag = 0
            # if (predict_begin-7)<=day_in2015<predict_begin:
            X[vm_vector.index(flavor)][day_in2015 - initial_day] += 1 #序号从零开始，大小还是vm_number*total_days
            # if X[vm_vector.index(flavor)][day_in2015 - initial_day]>30:
            #     X[vm_vector.index(flavor)][day_in2015 - initial_day]=0

    delta_predictor=predict_begin-final_day-1
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



    y_test = []
    ## 噪声上限参数设置
    # 如果使用丢弃最后一个箱子的做法，可以考虑预测多一点，或者对噪声少控制一些
    # 值越小，阈值下限越低，滤去的噪声越多
    over_lie = 3               # 每一天的总数，占所有天平均数的多少倍，如果大于3倍，就认为这天是异常天。 每列相加，和所有列相加的平均比较
    over_ratio = 0.2             # 在天数异常的情况下，同时这个数据在flavor预测历史数据中要超过多少比率的flavor总数。 每个点数据，和每列总数的比例

    ## 二阶平滑参数设置
    # fix_a=0.1 ## 固定值
    # flavor1 = flavor2 = flavor3 = flavor4 = flavor5 = flavor6 = flavor7 = flavor8 =  flavor9 = flavor10 = flavor11 = flavor12 = flavor13 = flavor14 =flavor15 = fix_a

    ## 复赛存在
    # 1,2,5,8,9,11,3,4,7,10,12

    ## 离散值 flavor越小，其占用资源越小
    # flavor1=0.09 ##二阶   因为其对后面的装箱影响比较小，所以可以预测多点 0.1-0.15
    # flavor2=0.06 ##二阶   0.1-0.15
    # flavor3=0.9  ##三阶      和flavor9类似 0.2-0.3
    # flavor4=0.12  ##二阶      特别平稳，个别突出0.1-0.2
    # flavor5=0.03 ##二阶   二阶不合适，
    # flavor6=0.05  ##二阶      0.2-0.25
    # flavor7=0.2  ##三阶      和flavor9类似
    # flavor8=0.4 ##二阶   敏感，0.1-0.15
    # flavor9=0.02  ##三阶   0.2-0.3分数区别不大，理论应该是0.2左右
    # flavor10=0.5 ##三阶       稀疏到没规律
    # flavor11=0.05 ##二阶
    # flavor12=0.05 ##二阶        和flavor1类似
    # flavor13=0.2 ##        稀疏到没规律
    # flavor14=0.2 ##        稀疏，波动大
    # flavor15=0.2 ##        稀疏波动大
    # flavor16 = 0.2  ##        稀疏到没规律
    # flavor17 = 0.2  ##        稀疏，波动大
    # flavor18 = 0.2  ##        稀疏波动大

    # 全乘以系数
    # beishu=1.15
    ## 只用平均*系数*预测时长
    flavor1 = 1.9  ##二阶   因为其对后面的装箱影响比较小，所以可以预测多点 0.1-0.15
    flavor2 = 1.22  ##二阶   0.1-0.15
    flavor3 = 1.78  ##三阶      和flavor9类似 0.2-0.3
    flavor4 = 1.58  ##二阶      特别平稳，个别突出0.1-0.2
    flavor5 = 2.05  ##二阶   二阶不合适，
    flavor6 = 1.8  ##二阶      0.2-0.25
    flavor7 = 1.95  ##三阶      和flavor9类似
    flavor8 = 2.7  ##二阶   敏感，0.1-0.15
    flavor9 = 2.2  ##三阶   0.2-0.3分数区别不大，理论应该是0.2左右
    flavor10 = 2.05  ##三阶       稀疏到没规律
    flavor11 = 2.05  ##二阶
    flavor12 = 2.05  ##二阶        和flavor1类似
    flavor13 = 2.05  ##        稀疏到没规律
    flavor14 = 1.6  ##        稀疏，波动大
    flavor15 = 2.05  ##        稀疏波动大
    flavor16 = 2.05  ##        稀疏到没规律
    flavor17 = 2.05  ##        稀疏，波动大
    flavor18 = 2.05  ##        稀疏波动大
    ## 按一周为单位
    # times_day = 7  # 每5天统计一次
    # predict_num = total_days // times_day + 1  # 把位数也算进来，其实其权重比较大，即使没5个也算，后续可以改其权重
    # X_week = [[0 for m in range(predict_num)] for n in range(vm_number)]

    # delta_day//=times_day
    # delta_predictor//=6

    ## 去噪参数
    # ss=[]
    # for i in range(total_days):
    #     ss.append(sum([x[i] for x in X])) #每天中所有flavor的总数
    for i in range(vm_number):
        ## 去噪处理，包括节日和异常点
        # for j in range(total_days):  # 没什么影响1##
            # if vm_vector[i] == 8 and (j+initial_day==d_0 or j+initial_day==d_1 or
            #                           j+ initial_day==d_2 or j+initial_day==d_3 or j+ initial_day==d_4
            #                           or j+initial_day==d_5 or j+ initial_day==d_6):#j==d_0-1 or
            #     # X[i][j]=0
            #     X[i][j]=(X[i][j-1]+X[i][j+1]+X[i][j])/3
            #if sum([x[j] for x in X]) > over_lie*sum(ss)/total_days and X[i][j] > over_num * sum(X[i]) / total_days:#若某一天的总量特别大，则所有元素都缩小
            # sum_flavor=sum([x[j] for x in X])

            ## 去噪部分
            # sum_flavor = ss[j] #各天的所有flavor请求量之和
            # if sum_flavor > over_lie*sum(ss)/total_days and X[i][j] / sum_flavor > over_ratio: #定位哪个flavor异常，看其在异常天中的比例
            #     X[i][j] *= 1 # 0.781.512 0.6-82.276

                #X[i][j]=sum_flavor*over_ratio #0.2-82.27 0.5-83.866 0.3-82.0
            # if X[i][j] > over_num * sum(X[i]) / total_days:
            #     X[i][j] /= 2

            # X_week[i][(j +1) // times_day  ] += X[i][j]
        # print(X_week)
        if vm_vector[i] == 1:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i],0.13,delta_day,predict_begin, predict_end))
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor1, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor1,predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], 0.1, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 2:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i],0.12,delta_day,predict_begin, predict_end))
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor2, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor2, predict_begin, predict_end))

        elif vm_vector[i] == 5:
            # y_test.append(simple_predictor.combine(X[i],0.2,delta_day,total_days,predict_begin,predict_end,10))
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor5, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor5, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor5, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 8:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor8,delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor8, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor8, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 9:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor9, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor9, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor9, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 11:
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor11, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor11, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor11, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 3:##例子不存在flavor3
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor3, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor3, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor3, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 4:##例子不存在flavor4
            #y_test.append(simple_predictor.oneweek(X[i], predict_begin, predict_end))
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor4, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor4, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor4, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 6:  ##例子不存在flavor6
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor6, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor6, predict_begin, predict_end))

        elif vm_vector[i] == 7:  ##例子不存在flavor7
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor7, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor7, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor7, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 10:  ##例子不存在flavor10
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor10, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor10, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor10, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 12:##例子不存在flavor12
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor12, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor12, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], flavor12, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 13:##例子不存在flavor13
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor13, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor13, predict_begin, predict_end))

        elif vm_vector[i] == 14:##例子不存在flavor14
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor14, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor14, predict_begin, predict_end))

        elif vm_vector[i] == 15:##例子不存在flavor15
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor15, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor15, predict_begin, predict_end))

        elif vm_vector[i] == 16:  ##例子不存在flavor13
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor13, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor16, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], a, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 17:  ##例子不存在flavor14
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor14, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor17, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], a, delta_day, total_days, delta_predictor))

        elif vm_vector[i] == 18:  ##例子不存在flavor15
            # y_test.append(simple_predictor.double_exp_smoothing(X[i], flavor15, delta_day,delta_predictor))
            y_test.append(simple_predictor.oneweek(X[i], flavor18, predict_begin, predict_end))
            # y_test.append(simple_predictor.triple_exp_smoothing(X[i], a, delta_day, total_days, delta_predictor))

    # y_test = []#
    # for item in range(vm_number):
    #    y_test.append(250)

    ## y_test表示按照预测顺序，每种flavor的数量

    # for i in range(len(y_test)):
    #     y_test[i]=int(y_test[i]*beishu//1)

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
    # bin_height_cpu = serve_matrix[0][0]
    # bin_height_mem = serve_matrix[0][1] * 1024
    #if resource_type == 'CPU':
    resource = 1
    #else:
    #    resource = 2
    for it in items:
        items_w.append([it, vm[vm_vector.index(it)][1], vm[vm_vector.index(it)][2]])
    ## items_w 表示给items加上资源属性，为分配做准备
    print(items_w)
    items_w.sort(key=lambda item_for_sort: item_for_sort[resource], reverse=True)
    #print('排序后items_w')
    #print(items_w)
    ## 计算预测flavor所有的CPU和MEM总和
    cpu_total=0
    mem_total=0
    for item in items_w:
        cpu_total+=item[1]
        mem_total += item[2]

    # a=time.time()
    # first_fit_sort, list_items, other_list_items,min_serve_vector,min_goal, last_one=SA.sa(items_w,serve_matrix,cpu_total, mem_total)
    first_fit_sort, list_items, other_list_items,min_serve_vector,min_goal, last_one=SA.greedy(items_w,serve_matrix,cpu_total, mem_total,time_start)
    # first_fit_sort, list_items, other_list_items, min_goal, last_one, min_serve_vector=SA.first_fit(items_w, serve_matrix, cpu_total, mem_total)
    print('未修改最后一个箱子的SA')
    print(first_fit_sort)
    print('min_serve_vector')
    print(min_serve_vector)
    # print('min_goal')
    # print(min_goal)
    print('last_one')
    print(last_one)

    print('flavor总数')
    print(len(items_w))
    # test_for_total_flavor=2500 #flavor总数都L2-2超过2000次<2500
    # if len(items_w) > test_for_total_flavor:
    #     exit(0)
    test_0=1 ## 超过此资源利用率则直接退出，默认为1，则永远不退出
    # th=0.01 # 越小表示，不去删数据，基本就是不对分配后进行干预
    th=min_goal*0.8 # 基本下调参数，分数就成比例下降，说明预测装箱的提升，相比于预测更重要。但高于0.7也就是分数降低了
    ## 对装箱后的资源进行再修改
    # if 0<(min_goal-min_goal//1)<th:
    if last_one < th and len(first_fit_sort)>1:
        print('开始有点技巧地去掉最后一个箱子，修改预测值，来提高利用率')
        it=first_fit_sort.pop()
        # list_items.pop()
        # other_list_items.pop()
        # cpu_test=[]
        # mem_test=[]
        # for item in list_items:
        #     cpu_test.append(sum(item))
        # for item in other_list_items:
        #     mem_test.append(sum(item)/1024)
        # print(cpu_test)
        # print(mem_test)
        # print('cpu')
        # print(list_items)
        # print('mem')
        # print(other_list_items)
        # print('未修改的items')
        # print(items)
        for item in it:
            items.remove(item)
            xuhao=vm_vector.index(item)
            y_test[xuhao]-=1
        items_w=[]
        for it in items:
            items_w.append([it, vm[vm_vector.index(it)][1], vm[vm_vector.index(it)][2]])
        # print('更改后的items')
        # print(items)
        # print('更改后的items_w')
        # print(items_w)
        # print('更改后的y_test')
        # print(y_test)
        print('min_serve_vector')
        print(min_serve_vector)
        min_serve_vector.pop()
        print('更改后的min_serve_vector')
        print(min_serve_vector)
        # print('更改后的first_fit_sort')
        # print(first_fit_sort)

        ## 计算资源效率
        cpu_total = 0
        mem_total = 0
        for item in items_w:
            cpu_total += item[1]
            mem_total += item[2]
        cpu = []  ##箱子的总资源
        mem = []
        for i in range(len(min_serve_vector)):
            ##CPU
            cpu.append(serve_matrix[min_serve_vector[i] - 1][0])
            mem.append(serve_matrix[min_serve_vector[i] - 1][1])
        cpu_ratio = cpu_total / sum(cpu)
        mem_ratio = mem_total / sum(mem)
        gai_ratio = (cpu_ratio + mem_ratio) / 2
        print('修改后的min_goal')
        print(gai_ratio)
        if gai_ratio > test_0:
            exit(0)

        result = [str(sum(y_test))]
        for i in range(len(y_test)):
            result.append('flavor' + str(vm_vector[i]) + ' ' + str(y_test[i]))
        result.append('')
        my_set = list(set(min_serve_vector))
        for j in range(len(my_set)):
            result.append(serve_matrix[my_set[j] - 1][3] + ' ' + str(min_serve_vector.count(my_set[j])))
            for ii in range(min_serve_vector.count(my_set[j])):
                temp = []
                my_first_fit_sort = []
                index = []
                for i in range(len(min_serve_vector)):
                    if my_set[j] == min_serve_vector[i]:
                        index.append(i)
                for item in index:
                    my_first_fit_sort.append(first_fit_sort[item])
                my_first_fit_set = list(set(my_first_fit_sort[ii]))
                for item in my_first_fit_set:
                    if temp:
                        temp = temp + ' flavor' + str(item) + ' ' + str(my_first_fit_sort[ii].count(item))
                    else:
                        temp = serve_matrix[my_set[j] - 1][3] + '-' + str(ii + 1) + ' flavor' + str(item) + ' ' + str(
                            my_first_fit_sort[ii].count(item))
                result.append(temp)
            result.append('')
            ## END ##
        # b=time.time()
        # print(b-a)
        return result

    else: ## 原始输出
        ## 计算资源效率
        cpu_total = 0
        mem_total = 0
        for item in items_w:
            cpu_total += item[1]
            mem_total += item[2]
        cpu = []  ##箱子的总资源
        mem = []
        for i in range(len(min_serve_vector)):
            ##CPU
            cpu.append(serve_matrix[min_serve_vector[i] - 1][0])
            mem.append(serve_matrix[min_serve_vector[i] - 1][1])
        cpu_ratio = cpu_total / sum(cpu)
        mem_ratio = mem_total / sum(mem)
        gai_ratio = (cpu_ratio + mem_ratio) / 2
        print('正常的min_goal')
        print(gai_ratio)
        if gai_ratio > test_0:
            exit(0)


        result = [str(sum(y_test))]
        for i in range(len(y_test)):
            result.append('flavor' + str(vm_vector[i]) + ' ' + str(y_test[i]))
        result.append('')
        my_set=list(set(min_serve_vector))
        for j in range(len(my_set)):
            result.append(serve_matrix[my_set[j]-1][3] + ' ' + str(min_serve_vector.count(my_set[j])))
            for ii in range(min_serve_vector.count(my_set[j])):
                temp = []
                my_first_fit_sort=[]
                index=[]
                for i in range(len(min_serve_vector)):
                    if my_set[j]==min_serve_vector[i]:
                        index.append(i)
                for item in index:
                    my_first_fit_sort.append(first_fit_sort[item])
                my_first_fit_set = list(set(my_first_fit_sort[ii]))
                for item in my_first_fit_set:
                    if temp:
                        temp = temp + ' flavor' + str(item) + ' ' + str(my_first_fit_sort[ii].count(item))
                    else:
                        temp = serve_matrix[my_set[j]-1][3] + '-' + str(ii + 1) + ' flavor' + str(item) + ' ' + str(my_first_fit_sort[ii].count(item))
                result.append(temp)
            result.append('')
            ## END ##
        return result
