# coding=utf-8
from __future__ import division
import random
import math
def sa(items_w,bin_height_cpu, bin_height_mem,resource):
    vm_number=len(items_w)
    ## 初始化
    S0=items_w
    first_fit_sort0 = first_fit(S0, bin_height_cpu, bin_height_mem, 0, resource) #零表示资源显示，1表示标号显示
    serve_number0=len(first_fit_sort0)
    # goal0 = binpack_goal(first_fit_sort0, resource, bin_height_cpu, bin_height_mem)
    if resource == 1:
        goal0 = serve_number0 - 1 + float(sum(first_fit_sort0[-1])) / bin_height_cpu
    else:
        goal0 = serve_number0 - 1 + float(sum(first_fit_sort0[-1])) / bin_height_mem

    min_server = serve_number0
    min_goal=goal0
    result0 = first_fit(S0, bin_height_cpu, bin_height_mem, 0, resource)
    print('初始化的资源利用率')
    print(binpack_goal(result0, resource, bin_height_cpu, bin_height_mem))

    ##模拟退火算法找最优解
    T = 100.0 # 模拟退火初始温度#
    Tmin = 1# 模拟退火终止温度
    # if vm_number<50:
    #     r=0.9999
    # else:
    r = 0.998#温度下降系数
    S=S0
    min_S=S0
    count=0
    obj=[]
    while T > Tmin:
        count+=1
        # 产生新解S1，S是旧解
        randn = [random.randint(0, vm_number-1) for _ in range(2)]
        S1=S
        S1[randn[0]], S1[randn[1]] = S1[randn[1]], S1[randn[0]]
        first_fit_sort = first_fit(S1, bin_height_cpu, bin_height_mem, 0, resource)
        serve_number = len(first_fit_sort)
        # goal = binpack_goal(first_fit_sort, resource, bin_height_cpu, bin_height_mem)
        if resource == 1:
            goal = serve_number - 1 + float(sum(first_fit_sort[-1])) / bin_height_cpu

        else:
            goal = serve_number - 1 + float(sum(first_fit_sort[-1])) / bin_height_mem


        ## 更新状态，如果没什么改进，就在原来S上继续迭代
        # 如果分数更低，则保存结果
        if  goal < min_goal:
            min_server = serve_number
            min_goal=goal
            S = S1 ##状态不变
            min_S = S
        # 如果分数更高，则以一定概率保存结果，防止优化陷入局部最优解
        elif math.exp(float(min_goal - goal) / T) >= random.random():
            min_goal = goal
            min_server = serve_number
            S = S1
        #print(math.exp(float(min_goal - goal) / T))
        #默认在S状态继续随机改变
        ## 记录最优值
        if count==1 or min_goal<obj[-1]:
            obj.append(min_goal)
        else:
            obj.append(obj[-1])
        T = r * T# 一次循环结束，温度降低
    print('迭代次数')
    print(count)
    print('迭代goal变化过程')
    print(obj)
    print('所需要的服务器最小值')
    print(min_server)
    result=first_fit(min_S, bin_height_cpu, bin_height_mem, 0, resource)
    print('真实资源利用率')
    print(binpack_goal(result,resource, bin_height_cpu, bin_height_mem))
    return first_fit(min_S, bin_height_cpu, bin_height_mem, 1, resource),min_goal

def binpack_goal(first_fit_sort,resource, bin_height_cpu, bin_height_mem):
    if resource == 1:
        bin_height = bin_height_cpu
    else:
        bin_height = bin_height_mem
    result = 0
    for i in range(len(first_fit_sort)):
        result += sum(first_fit_sort[i])
    result = float(result) / len(first_fit_sort) / bin_height
    return result


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


def first_fit(list_items, bin_height_cpu, bin_height_mem, choose, resource):
    list_bins = [Bin()]

    my_list_bins = [Bin()]

    other_list_bins = [Bin()]

    if resource == 1:
        max_size = bin_height_cpu
        other_size = bin_height_mem
    else:
        max_size = bin_height_mem
        other_size = bin_height_cpu

    for item in list_items:
        alloc_flag = False

        for i in range(len(list_bins)):
            if list_bins[i].sum() + item[resource] <= max_size:
                if other_list_bins[i].sum() + item[3 - resource] <= other_size:
                    list_bins[i].addItem(item[resource])
                    my_list_bins[i].addItem(item[0])
                    other_list_bins[i].addItem(item[3 - resource])
                    alloc_flag = True
                    break

        if not alloc_flag:
            bin_new = Bin()
            bin_new.addItem(item[resource])
            list_bins.append(bin_new)
            bin_my = Bin()
            bin_my.addItem(item[0])
            my_list_bins.append(bin_my)
            bin_other = Bin()
            bin_other.addItem(item[3 - resource])
            other_list_bins.append(bin_other)

    list_items = []
    for list_bin in list_bins:
        list_items.append(list_bin.show())
    my_list_items = []
    for my_bin in my_list_bins:
        my_list_items.append(my_bin.show())
    other_list_items = []
    for other_bin in other_list_bins:
        other_list_items.append(other_bin.show())
    if choose == 1:
        return my_list_items
    elif choose == 2:
        return other_list_items
    else:
        return list_items
