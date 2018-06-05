# coding=utf-8
from __future__ import division
from copy import deepcopy
import random
import math
import time

def sa(items_w,serve_matrix,cpu_total, mem_total):
    vm_number=len(items_w)
    time_start = time.time()

    ## 初始化
    S0=items_w
    my_list_items, list_items, other_list_items, total_ratio, last_one,serve_vector= first_fit(S0, serve_matrix, cpu_total, mem_total) #零表示资源显示，1表示标号显示

    time_end = time.time()
    delta_time=time_end - time_start
    print('single cost',delta_time )
    goal0 = total_ratio
    max_goal=goal0

    ##模拟退火算法找最优解
    T = 100.0 # 模拟退火初始温度#
    Tmin = 1 # 模拟退火终止温度
    r = 0.93 #温度下降系数
    S=S0
    max_S=S0
    count=0
    obj=[]
    while T > Tmin:
        count+=1
        # 产生新解S1，S是旧解
        randn = [random.randint(0, vm_number-1) for _ in range(2)]
        S1=deepcopy(S)
        S1[randn[0]], S1[randn[1]] = S1[randn[1]], S1[randn[0]]
        my_list_items, list_items, other_list_items, total_ratio, last_one,serve_vector = first_fit(S1, serve_matrix, cpu_total, mem_total)
        goal =  total_ratio

        ## 更新状态，如果没什么改进，就在原来S上继续迭代
        # 如果分数更低，则保存结果
        if  goal > max_goal:
            max_goal=deepcopy(goal)
            S = S1 ##状态不变
            max_S = deepcopy(S)
            max_serve_vector = serve_vector

        # 如果分数更高，则以一定概率保存结果，防止优化陷入局部最优解
        # elif math.exp(float(max_goal - goal) / T) >= random.random():
        elif random.random()>0.95:
            max_goal = deepcopy(goal)
            S = S1
        # print(math.exp(float(max_goal - goal) / T) )
        #默认在S状态继续随机改变
        ## 记录最优值
        if count==1 or max_goal>obj[-1]:
            obj.append(max_goal)
        else:
            obj.append(obj[-1])
        T = r * T# 一次循环结束，温度降低
    print('迭代次数')
    print(count)
    # print('迭代goal变化过程')
    # print(obj)
    print('max_goal')
    print(max_goal)
    my_list_items, list_items, other_list_items, max_goal, last_one,max_serve_vector=first_fit(max_S, serve_matrix, cpu_total, mem_total)
    print('取最优放置的max_goal')
    print(max_goal)
    return my_list_items, list_items, other_list_items,max_serve_vector,max_goal,last_one


def greedy(items_w,serve_matrix,cpu_total, mem_total,time_start):

    ## 初始化
    S0=items_w
    my_list_items, list_items, other_list_items, goal0, last_one,serve_vector= first_fit(S0, serve_matrix, cpu_total, mem_total)
    max_goal=goal0
    max_S=S0

    ##暴力搜索
    # if len(items_w) < 2000:
    #     T = 1000 # 迭代次数
    # else:
    #     T = 500  # 迭代次数
    T = 1500  # 迭代次数
    count=0
    obj=[]
    S = deepcopy(S0)
    while count < T:
        time_end = time.time()
        delta_time = time_end - time_start

        if delta_time > 86:
            print('迭代终止时间')
            print(delta_time)
            break
        count += 1
        # 产生新解S1，S是旧解
        random.shuffle(S)
        my_list_items, list_items, other_list_items, goal, last_one, serve_vector = first_fit(S, serve_matrix, cpu_total, mem_total)

        ## 更新状态，如果没什么改进，就在原来S上继续迭代
        # 如果分数更低，则保存结果
        if  goal > max_goal:
            max_goal= goal
            max_S = deepcopy(S)
            max_count=count
            obj.append(max_goal)

    # print('最优解的迭代次数')
    # print(max_count)
    # print('迭代goal变化过程')
    # print(obj)
    print('没有超时的总迭代次数')
    print(count)
    print('max_goal')
    print(max_goal)
    my_list_items, list_items, other_list_items, max_goal, last_one, max_serve_vector=first_fit(max_S, serve_matrix, cpu_total, mem_total)
    print('取最优放置的max_goal')
    print(max_goal)
    return my_list_items, list_items, other_list_items, max_serve_vector,max_goal,last_one


class Bin:
    def __init__(self):
        self.list = []

    def addItem(self, item):
        self.list.append(item)

    def sum(self):
        total = 0
        for elem in self.list:
            total += elem
        return total

    def show(self):
        return self.list


def first_fit(list_items, serve_matrix, cpu_total, mem_total):#resource =1 表示按CPU，=0表示MEM
    CPU_TOTAL=cpu_total
    MEM_TOTAL=mem_total

    list_bins = [Bin()]  # CPU
    my_list_bins = [Bin()]  # 标号
    other_list_bins = [Bin()]  # MEM

    ## 判断剩余资源CPU/MEM决定新开什么类型的箱子
    resource_ratio = mem_total / cpu_total  # 剩余资源的比例
    max_serve = len(serve_matrix)
    min = abs(serve_matrix[0][2] - resource_ratio)  # 初始化最适合的MEM/CPU
    serve_vector = []  ## 箱子的编号，如果总数1，则标号只有1，总数为2，编号1,2.总数为3，编号1,2,3
    if max_serve == 1:
        serve_vector.append(1)
    else:
        location = 0
        for i in range(1, max_serve):
            if abs(serve_matrix[i][2] - resource_ratio) < min:
                min = abs(serve_matrix[i][2] - resource_ratio)
                location = i
        serve_vector.append(location + 1)

    for item in list_items:
        alloc_flag = False
        for i in range(len(list_bins)):
            max_size=serve_matrix[serve_vector[i]-1][0]
            max_other_size=serve_matrix[serve_vector[i]-1][1]
            if list_bins[i].sum() + item[1] <= max_size and \
                    other_list_bins[i].sum() + item[2] <= max_other_size:
                    list_bins[i].addItem(item[1])
                    my_list_bins[i].addItem(item[0])
                    other_list_bins[i].addItem(item[2])
                    cpu_total-=item[1]
                    mem_total-=item[2]
                    alloc_flag = True
                    break


        if not alloc_flag:
            bin_new = Bin()
            bin_new.addItem(item[1])
            bin_my = Bin()
            bin_my.addItem(item[0])
            bin_other = Bin()
            bin_other.addItem(item[2])

            list_bins.append(bin_new)
            my_list_bins.append(bin_my)
            other_list_bins.append(bin_other)

            ## 判断剩余资源CPU/MEM决定新开什么类型的箱子
            resource_ratio=mem_total/cpu_total #剩余资源的比例
            max_serve=len(serve_matrix)
            min = abs(serve_matrix[0][2] - resource_ratio) #初始化最适合的MEM/CPU
            # serve_vector=[] ## 箱子的编号，如果总数1，则标号只有1，总数为2，编号1,2.总数为3，编号1,2,3
            if max_serve==1:
                serve_vector.append(1)
            else:
                location = 0
                for i in range(1,max_serve):
                    if abs(serve_matrix[i][2] - resource_ratio) < min:
                        min=abs(serve_matrix[i][2] - resource_ratio)
                        location=i
                serve_vector.append(location+1)
            #print(serve_vector)

    list_item = [] #cpu
    for list_bin in list_bins:
        list_item.append(list_bin.show())
    my_list_item = [] #标号
    for my_bin in my_list_bins:
        my_list_item.append(my_bin.show())
    other_list_item = [] #mem
    for other_bin in other_list_bins:
        other_list_item.append(other_bin.show())


    ## 计算资源效率
    cpu=[] ##箱子的总资源
    mem=[]
    for i in range(len(serve_vector)):
        ##CPU
        cpu.append(serve_matrix[serve_vector[i] - 1][0])
        mem.append(serve_matrix[serve_vector[i] - 1][1])
    cpu_ratio = CPU_TOTAL / sum(cpu)
    mem_ratio = MEM_TOTAL / sum(mem)
    last_one=( sum(list_item[-1])/cpu[-1] + sum(other_list_item[-1])/mem[-1] )/2
    total_ratio=(cpu_ratio+mem_ratio)/2
    return my_list_item,list_item,other_list_item,total_ratio,last_one,serve_vector ##结果标号

