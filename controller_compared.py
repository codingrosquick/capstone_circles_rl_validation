# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# In this part, we compare the performance of the two controllers, we input two potential
# bagfiles and will output the comparisons of the 5 metrics with respect the two controllers
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************

# ***************************************************************************************
# ***************************************************************************************
# Experiment configuration:
# python 3.8, bagpy 0.4.8, matplotlib, numpy, pandas
# ***************************************************************************************
# ***************************************************************************************

import bagpy
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes
from bagpy import bagreader
import pandas as pd
from detect_events import *
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
import os
import math

def read_bagfiles_and_topics(file_path):
    ##############################################################################################
    # This function use bagreader to decode the bagfile, and return some topics and readerble data
    ##############################################################################################
    # input:
    # file_path: string
    ##############################################################################################
    # output:
    # topics_num[int], topics_name[list], bag
    ##############################################################################################
    bag = bagreader(file_path)
    print(bag.topic_table)

    topics_num, _ = bag.topic_table.values.shape
    topics_name = []
    for i in range(topics_num):
        topics_name.append(bag.topic_table.values[i][0])
    return topics_num, topics_name, bag

def transfer_format(bag, topics_name, topics_num):
    ##############################################################################################
    # This function transfer the bag format data to csv data for later analysis
    ##############################################################################################
    # input:
    # bag, topics_name [list], topics_num [int]
    ##############################################################################################
    # output:
    # data [list]: dimension = number of topics
    ##############################################################################################
    ##Read the data in pandas DataFrame
    data = []
    for i in range(topics_num):
        topic_name = topics_name[i]
        data.append(pd.read_csv(bag.message_by_topic(topic_name)))
        log = 'Read INFO of ', topic_name + ' ' + str(i+1) + '/' + str(topics_num)
        print(log)
        # print(b.message_by_topic(topics_name[i]))
        # print(data)
    return data

def find_topic(topic, topics_name):
    ##############################################################################################
    # This function find special topics given the name, and return it as its index in the csv list
    ##############################################################################################
    # input:
    # topic [str], topics_name [list]
    ##############################################################################################
    # output:
    # index [int]: the index of that topic in the whole list
    ##############################################################################################
    topic = '/' + topic
    index = np.where(np.array(topics_name) == topic)[0]
    return index

def transfer_length(allowed_control, lead_dis):
    ##############################################################################################
    # This function align the data of two different topics with different sample rate：
    # This method use l1-norm to find the position of one value should be located in which entry
    # of a whole one dimention array, for-loop is not a great choice because it is not efficient
    # and need lot of computing and time. Here I use vector substraction and then find the index of
    # the minimal entry of the difference.
    ##############################################################################################
    # input:
    # allowed_control [array]: this is the array I tend to adjust its sample rate
    # lead_dis [array]: this is the array the top one should follow to have the same sample rate
    ##############################################################################################
    # output:
    # allowed_control_: the adjusted new array
    ##############################################################################################
    length, _ = lead_dis.shape
    length_, _ = allowed_control.shape
    allowed_control_ = np.zeros([length, 2])
    allowed_control_[:, 0] = lead_dis[:, 0]

    for i in range(length_):
        # build the new array
        x = np.ones(length) * allowed_control[i, 0]
        y = lead_dis[:, 0]

        #find the mininal entry of the l1 norm between the two factor
        dis = np.abs(x - y)
        idx = np.argmin(dis)

        # five the index of that value
        allowed_control_[idx, 1] = allowed_control[i, 1]

    for i in  range(length):
        if i == 0:
            continue
        else:
            if allowed_control_[i, 1] == 0:
                ii = i
                while allowed_control_[ii, 1] == 0 and ii != 0:
                    ii = ii - 1
                    if i - ii > 5:
                        break
                allowed_control_[i, 1] = allowed_control_[ii, 1]



    return allowed_control_


def plot_compared(data1,
                  data2,
                  length,
                  file_name = 'default',
                  x_lable = 'Time',
                  y_label = 'Lead distance',
                  color1 = 'blue',
                  color2 = 'red',
                  linewidth = 1):
    ##############################################################################################
    # This is the funtion used to visualize the results, which can have double axis among the same plots
    ##############################################################################################
    # input:
    # data1 [array]
    # data2 [array]
    # length [int]
    # file_name = 'default',
    # x_lable [string],
    # y_label [string],
    # color1 = 'blue',
    # color2 = 'red',
    # linewidth [int]
    ##############################################################################################
    # output:
    # an plot saved in the target path
    ##############################################################################################
    fig, ax = plt.subplots(figsize=[15, 4])
    ax.plot(data1[0 : length, 0], data1[0 : length, 1], label = 'Real', color = color1,linewidth= linewidth)
    ax.plot(data1[0 : length, 0], data2[0 : length, 1], label = 'Simulation', color = color2, linewidth= linewidth)
    ax.set_xlabel(x_lable)
    ax.set_ylabel(y_label)
    ax.set_title(file_name)
    ax.legend()
    path = './Result/' + file_name + '.png'
    plt.savefig(path)
    print('Result is saved in ' + path)
    # plt.close()

def plot(data,
         length,
         file_name = 'default',
         x_lable = 'Time',
         y_label = 'Lead distance',
         color1 = 'green',
         linewidth = 1
         ):
    ##############################################################################################
    # This is the funtion used to visualize the results, which can have only one axis
    ##############################################################################################
    # input:
    # data [array]
    # length [int]
    # file_name = 'default',
    # x_lable [string],
    # y_label [string],
    # color1 = 'blue',
    # linewidth [int]
    ##############################################################################################
    # output:
    # an plot saved in the target path
    ##############################################################################################
    fig, ax = plt.subplots(figsize=[15, 4])
    ax.plot(data[0, 0: length], data[1, 0: length], label='Difference', color=color1, linewidth=linewidth)
    ax.set_xlabel(x_lable)
    ax.set_ylabel(y_label)
    ax.set_title(file_name)
    ax.legend()
    path = './Result/' + file_name + '.png'
    plt.savefig(path)
    print('Result is saved in ' + path)
    # plt.close()

def Var_lead(lead_dis, allowed_control, path_save):
    # clip the allowed_control
    t_allowed_c = np.where(allowed_control == True)[0]
    total_interval, _ = allowed_control.shape
    total_time = lead_dis[-1, 0] - lead_dis[0, 0]
    clips = []
    time_control = 0
    start_curr = t_allowed_c[0]
    for i in np.arange(0, len(t_allowed_c) - 1, 1):
        if t_allowed_c[i + 1] - t_allowed_c[i] == 1 and i != len(t_allowed_c) - 2:
            continue
        else:
            stop_curr = t_allowed_c[i]
            time_period_ = [allowed_control[start_curr, 0], allowed_control[stop_curr, 0]]
            time_control = time_control + time_period_[1] - time_period_[0]
            clips.append(time_period_)
            start_curr = t_allowed_c[i + 1]

    # Align their length
    allowed_control_ = np.zeros(lead_dis.shape, dtype=int)
    allowed_control_[:, 0] = lead_dis[:, 0]
    clips_indexs = []
    for clip in clips:
        vector1 = np.ones(lead_dis.shape[0]) * clip[0]
        index1 = np.argmin(abs(lead_dis[:, 0] - vector1))
        vector2 = np.ones(lead_dis.shape[0]) * clip[1]
        index2 = np.argmin(abs(lead_dis[:, 0] - vector2))
        if index2 == index1:
            continue
        clips_indexs.append([index1, index2])

        allowed_control_[index1: index2, 1] = 1

    allowed_control = allowed_control_

    # calculate the var
    num = 0
    var = 0
    for clips_index in clips_indexs:
        num = num + 1
        lead_dis_clip = lead_dis[clips_index[0]: clips_index[1], 1]
        var = var + np.var(lead_dis_clip)
    var_control = var / num

    var_total = np.var(lead_dis[:, 1])


    U_lead = var_control / var_total / time_control * (total_time - time_control)

    fig = plt.figure(figsize=[15, 10])
    ax_cof = HostAxes(fig, [0.1, 0.1, 0.7, 0.8])
    # parasite addtional axes, share x
    ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)  # allowed_control

    # append axes
    ax_cof.parasites.append(ax_temp)

    # invisible right axis of ax_cof
    ax_cof.axis['right'].set_visible(False)
    ax_cof.axis['top'].set_visible(False)
    ax_temp.axis['right'].set_visible(True)
    ax_temp.axis['right'].major_ticklabels.set_visible(True)
    ax_temp.axis['right'].label.set_visible(True)

    # set label for axis
    ax_cof.set_ylabel('Lead_distance (m)')
    ax_cof.set_xlabel('Time (s)')
    ax_temp.set_ylabel('allowed_control')


    fig.add_axes(ax_cof)


    ax_temp.plot(lead_dis[:, 0], allowed_control[:, 1], label="allowed_contro", color='red',
                               linestyle='--')
    ax_cof.plot(lead_dis[:, 0], lead_dis[:, 1], label="lead_distance", color='black')

    ax_cof.legend()


    ax_temp.axis['right'].label.set_color('red')

    ax_temp.axis['right'].major_ticks.set_color('red')

    ax_temp.axis['right'].major_ticklabels.set_color('red')

    ax_temp.axis['right'].line.set_color('red')


    name = '2.1 Variance of lead distance'
    # plt.show()

    path = './Result/controller' + str(path_save) + '/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    return var_control, var_total, U_lead


def S_SG(vel, allowed_control,
         sg_velocity_thresh, sg_time_thresh_min, sg_time_thresh_max, path_save):
    # clip the allowed_control
    t_allowed_c = np.where(allowed_control == True)[0]
    total_interval, _ = allowed_control.shape
    clips = []
    time_control = 0
    start_curr = t_allowed_c[0]
    for i in np.arange(0, len(t_allowed_c) - 1, 1):
        if t_allowed_c[i + 1] - t_allowed_c[i] == 1 and i != len(t_allowed_c) - 2:
            continue
        else:
            stop_curr = t_allowed_c[i]
            time_period_ = [allowed_control[start_curr, 0], allowed_control[stop_curr, 0]]
            time_control = time_control + time_period_[1] - time_period_[0]
            clips.append(time_period_)
            start_curr = t_allowed_c[i + 1]

    # Align their length [clips_index -> allowed control]
    allowed_control_ = np.zeros(vel.shape, dtype=int)
    allowed_control_[:, 0] = vel[:, 0]
    clips_indexs = []
    for clip in clips:
        vector1 = np.ones(vel.shape[0]) * clip[0]
        index1 = np.argmin(abs(vel[:, 0] - vector1))
        vector2 = np.ones(vel.shape[0]) * clip[1]
        index2 = np.argmin(abs(vel[:, 0] - vector2))
        if index2 == index1:
            continue
        clips_indexs.append([index1, index2])

        allowed_control_[index1: index2, 1] = 1

    allowed_control = allowed_control_

    # find the stops and goes
    t_sg = np.where(vel[:, 1] <= sg_velocity_thresh)[0]
    total_time = vel[-1, 0] - vel[0, 0]
    total_interval, _ = vel.shape
    clips = []

    if t_sg != []:
        start_curr = t_sg[0]
        for i in np.arange(0, len(t_sg) - 1, 1):
            if t_sg[i + 1] - t_sg[i] == 1 and i != len(t_sg) - 2:
                continue
            else:
                stop_curr = t_sg[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                clips.append([start_curr, stop_curr])
                start_curr = t_sg[i + 1]

    ### filter the lead_distance clips [clips_filter -> stops and goes]
    clips_filter = []
    if clips != []:
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = abs(point2 - point1) / total_interval * total_time
            if difference > sg_time_thresh_min and  difference < sg_time_thresh_max:
                clips_filter.append(list)

    stop_go = np.zeros(vel.shape, dtype=int)
    stop_go[:, 0] = vel[:, 0]
    clips_indexs = []
    if clips_filter != []:
        for clip_filter in clips_filter:
            stop_go[clip_filter[0] : clip_filter[1], 1] = 1



    # n/T
    n_total = len(clips_filter)
    SG_p = n_total / total_time

    n_control = 0
    for clip_filter in clips_filter:
        for clip_control in clips_indexs:
            if clip_filter[0] >= clip_control[0] and clip_filter[0] <= clip_control[1]:
                n_control = n_control + 1

    SG = n_control / time_control
    if SG_p == 0:
        S_SG = 0
    else:
        S_SG = SG / SG_p

    fig = plt.figure(figsize=[15, 10])
    ax_cof = HostAxes(fig, [0.1, 0.1, 0.7, 0.8])
    # parasite addtional axes, share x
    ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)  # allowed_control

    ax_cp = ParasiteAxes(ax_cof, sharex=ax_cof)  # cmd_v

    # append axes
    ax_cof.parasites.append(ax_temp)

    ax_cof.parasites.append(ax_cp)

    # invisible right axis of ax_cof
    ax_cof.axis['right'].set_visible(False)
    ax_cof.axis['top'].set_visible(False)
    ax_temp.axis['right'].set_visible(True)
    ax_temp.axis['right'].major_ticklabels.set_visible(True)
    ax_temp.axis['right'].label.set_visible(True)

    # set label for axis
    ax_cof.set_ylabel('velocity (m/s)')
    ax_cof.set_xlabel('Time (s)')
    ax_temp.set_ylabel('allowed_control')

    ax_cp.set_ylabel('stop and go')

    # load_axisline = ax_load.get_grid_helper().new_fixed_axis
    cp_axisline = ax_cp.get_grid_helper().new_fixed_axis
    # wear_axisline = ax_wear.get_grid_helper().new_fixed_axis

    # ax_load.axis['right2'] = load_axisline(loc='right', axes=ax_load, offset=(40, 0))
    ax_cp.axis['right3'] = cp_axisline(loc='right', axes=ax_cp, offset=(80, 0))
    # ax_wear.axis['right4'] = wear_axisline(loc='right', axes=ax_wear, offset=(120, 0))

    fig.add_axes(ax_cof)


    curve_temp, = ax_temp.plot(allowed_control[:, 0], allowed_control[:, 1], label="allowed_control", color='red',
                               linestyle='--')
    curve_cof, = ax_cof.plot(vel[:, 0], vel[:, 1], label="velocity", color='black')

    # curve_load, = ax_load.plot(lead_dis[:, 0], vel[:, 1], label="val", color='green')
    curve_cp, = ax_cp.plot(stop_go[:, 0], stop_go[:, 1], label="stop and go", color='green', linestyle = ':')

    ax_cof.legend()


    ax_temp.axis['right'].label.set_color('red')
    # ax_load.axis['right2'].label.set_color('green')
    ax_cp.axis['right3'].label.set_color('green')
    # ax_wear.axis['right4'].label.set_color('blue')

    ax_temp.axis['right'].major_ticks.set_color('red')
    # ax_load.axis['right2'].major_ticks.set_color('green')
    ax_cp.axis['right3'].major_ticks.set_color('green')
    # ax_wear.axis['right4'].major_ticks.set_color('blue')

    ax_temp.axis['right'].major_ticklabels.set_color('red')
    # ax_load.axis['right2'].major_ticklabels.set_color('green')
    ax_cp.axis['right3'].major_ticklabels.set_color('green')
    # ax_wear.axis['right4'].major_ticklabels.set_color('blue')

    ax_temp.axis['right'].line.set_color('red')
    # ax_load.axis['right2'].line.set_color('green')
    ax_cp.axis['right3'].line.set_color('green')
    # ax_wear.axis['right4'].line.set_color('blue')

    name = '2.2 Average stop and goes within control'
    # plt.show()

    path = './Result/controller' + str(path_save) + '/' + name + '.png'
    plt.savefig(path)

    return SG, SG_p, S_SG

def Var_vel(vel, allowed_control, path_save):
    # clip the allowed_control
    total_time = vel[-1, 0] - vel[0, 0]
    t_allowed_c = np.where(allowed_control == True)[0]
    total_interval, _ = allowed_control.shape
    clips = []
    time_control = 0
    start_curr = t_allowed_c[0]
    for i in np.arange(0, len(t_allowed_c) - 1, 1):
        if t_allowed_c[i + 1] - t_allowed_c[i] == 1 and i != len(t_allowed_c) - 2:
            continue
        else:
            stop_curr = t_allowed_c[i]
            time_period_ = [allowed_control[start_curr, 0], allowed_control[stop_curr, 0]]
            time_control = time_control + time_period_[1] - time_period_[0]
            clips.append(time_period_)
            start_curr = t_allowed_c[i + 1]

    # Align their length
    allowed_control_ = np.zeros(vel.shape, dtype=int)
    allowed_control_[:, 0] = vel[:, 0]
    clips_indexs = []
    for clip in clips:
        vector1 = np.ones(vel.shape[0]) * clip[0]
        index1 = np.argmin(abs(vel[:, 0] - vector1))
        vector2 = np.ones(vel.shape[0]) * clip[1]
        index2 = np.argmin(abs(vel[:, 0] - vector2))
        if index2 == index1:
            continue
        clips_indexs.append([index1, index2])

        allowed_control_[index1: index2, 1] = 1

    allowed_control = allowed_control_

    # calculate the var
    num = 0
    var = 0
    for clips_index in clips_indexs:
        num = num + 1
        vel_clip = vel[clips_index[0]: clips_index[1], 1]
        var = var + np.var(vel_clip)
    var_control = var / num

    var_total = np.var(vel[:, 1])


    S_vel = var_control / var_total / time_control * (total_time - time_control)

    fig = plt.figure(figsize=[15, 10])
    ax_cof = HostAxes(fig, [0.1, 0.1, 0.7, 0.8])
    # parasite addtional axes, share x
    ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)  # allowed_control

    # append axes
    ax_cof.parasites.append(ax_temp)

    # invisible right axis of ax_cof
    ax_cof.axis['right'].set_visible(False)
    ax_cof.axis['top'].set_visible(False)
    ax_temp.axis['right'].set_visible(True)
    ax_temp.axis['right'].major_ticklabels.set_visible(True)
    ax_temp.axis['right'].label.set_visible(True)

    # set label for axis
    ax_cof.set_ylabel('Velocity (m)')
    ax_cof.set_xlabel('Time (s)')
    ax_temp.set_ylabel('allowed_control')


    fig.add_axes(ax_cof)


    ax_temp.plot(vel[:, 0], allowed_control[:, 1], label="allowed_control", color='red',
                               linestyle='--')
    ax_cof.plot(vel[:, 0], vel[:, 1], label="velocity", color='blue')

    ax_cof.legend()


    ax_temp.axis['right'].label.set_color('red')

    ax_temp.axis['right'].major_ticks.set_color('red')

    ax_temp.axis['right'].major_ticklabels.set_color('red')

    ax_temp.axis['right'].line.set_color('red')


    name = '2.3 Velocity stability within the control'
    # plt.show()

    path = './Result/controller' + str(path_save) + '/' + name + '.png'
    plt.savefig(path)
    # plt.close()

    return var_control, var_total, S_vel

def Var_accel(accel, allowed_control, path_save):
    total_time = accel[-1, 0] - accel[0, 0]
    # clip the allowed_control
    t_allowed_c = np.where(allowed_control == True)[0]
    total_interval, _ = allowed_control.shape
    clips = []
    time_control = 0
    start_curr = t_allowed_c[0]
    for i in np.arange(0, len(t_allowed_c) - 1, 1):
        if t_allowed_c[i + 1] - t_allowed_c[i] == 1 and i != len(t_allowed_c) - 2:
            continue
        else:
            stop_curr = t_allowed_c[i]
            time_period_ = [allowed_control[start_curr, 0], allowed_control[stop_curr, 0]]
            time_control = time_control + time_period_[1] - time_period_[0]
            clips.append(time_period_)
            start_curr = t_allowed_c[i + 1]

    # Align their length
    allowed_control_ = np.zeros(accel.shape, dtype=int)
    allowed_control_[:, 0] = accel[:, 0]
    clips_indexs = []
    for clip in clips:
        vector1 = np.ones(accel.shape[0]) * clip[0]
        index1 = np.argmin(abs(accel[:, 0] - vector1))
        vector2 = np.ones(accel.shape[0]) * clip[1]
        index2 = np.argmin(abs(accel[:, 0] - vector2))
        if index2 == index1:
            continue
        clips_indexs.append([index1, index2])

        allowed_control_[index1: index2, 1] = 1

    allowed_control = allowed_control_

    # calculate the var
    num = 0
    var = 0
    for clips_index in clips_indexs:
        num = num + 1
        accel_clip = accel[clips_index[0]: clips_index[1], 1]
        var = var + np.var(accel_clip)
    var_control = var / num

    var_total = np.var(accel[:, 1])


    S_accel = var_control / var_total / time_control * (total_time - time_control)

    fig = plt.figure(figsize=[15, 10])
    ax_cof = HostAxes(fig, [0.1, 0.1, 0.7, 0.8])
    # parasite addtional axes, share x
    ax_temp = ParasiteAxes(ax_cof, sharex=ax_cof)  # allowed_control

    # append axes
    ax_cof.parasites.append(ax_temp)

    # invisible right axis of ax_cof
    ax_cof.axis['right'].set_visible(False)
    ax_cof.axis['top'].set_visible(False)
    ax_temp.axis['right'].set_visible(True)
    ax_temp.axis['right'].major_ticklabels.set_visible(True)
    ax_temp.axis['right'].label.set_visible(True)

    # set label for axis
    ax_cof.set_ylabel('Acceleration (m/s)')
    ax_cof.set_xlabel('Time (s)')
    ax_temp.set_ylabel('allowed_control')


    fig.add_axes(ax_cof)


    ax_temp.plot(accel[:, 0], allowed_control[:, 1], label="allowed_control", color='red',
                               linestyle='--')
    ax_cof.plot(accel[:, 0], accel[:, 1], label="acceleration ", color='purple')

    ax_cof.legend()


    ax_temp.axis['right'].label.set_color('red')

    ax_temp.axis['right'].major_ticks.set_color('red')

    ax_temp.axis['right'].major_ticklabels.set_color('red')

    ax_temp.axis['right'].line.set_color('red')


    name = '2.4 Acceleration stability within the control'
    # plt.show()

    path = './Result/controller' + str(path_save) + '/' + name + '.png'
    plt.savefig(path)
    return var_control, var_total, S_accel

def US_controller(U_lead, s_sg, S_vel, S_accel,
                  lmd1 = 1/3,
                  lmd2 = 1/3,
                  lmd3 = 1/3,
                  alpha = 1/2):

    U_score = 1/U_lead

    S_score = lmd1 * 1/ (s_sg + 0.001) + lmd2 * 1/ (S_vel + 0.001) + lmd3 * 1/ (S_accel + 0.001)

    Score = alpha * U_score + (1 - alpha) * S_score

    return U_score, S_score, Score

class Eval_Controller():
    def __init__(self, data,
                  topics_name,
                  path,
                  lmd1 = 1/3,
                  lmd2 = 1/3,
                  lmd3 = 1/3,
                  alpha = 1/2,
                  sg_velocity_thresh = 10,
                  sg_time_thresh_min = 3,
                  sg_time_thresh_max = 120):

        self.lmd1 = lmd1
        self.lmd2 = lmd2
        self.lmd3 = lmd3

        self.alpha = alpha

        self.sg_velocity_thresh = sg_velocity_thresh
        self.sg_time_thresh_min = sg_time_thresh_min
        self.sg_time_thresh_max = sg_time_thresh_max

        self.data_s = data
        self.topics_name_s = topics_name

        self.path_save = path

    #### 1 comparison of variance of lead distance within control
    def V_lead(self):
        index_allowed_control = find_topic('car/panda/controls_allowed', self.topics_name_s)
        allowed_control = np.array(self.data_s[index_allowed_control[0]])

        index_lead_dis = find_topic('lead_dist', self.topics_name_s)
        lead_dis = np.array(self.data_s[index_lead_dis[0]])

        var_control, var_total, U_lead = Var_lead(lead_dis, allowed_control, path_save=self.path_save)

        self.allowed_control = allowed_control

        self.U_lead = U_lead

        return var_control, var_total, U_lead

        #### 2 comparison of the average stop and goes within control
    def S_SG(self):
        index_vel = find_topic('vel', self.topics_name_s)
        vel = np.array(self.data_s[index_vel[0]])

        self.vel = vel

        sg, sg_p, s_sg = S_SG(vel, self.allowed_control, self.sg_velocity_thresh, self.sg_time_thresh_min, self.sg_time_thresh_max, path_save=self.path_save)

        self.s_sg = s_sg

        return sg, sg_p, s_sg

    #### 3 comparison of velocity stability within the control analysis
    def S_vel(self):

        var_vel, var_vel_, s_vel = Var_vel(self.vel, self.allowed_control, path_save=self.path_save)
        self.s_vel = s_vel
        return var_vel, var_vel_, s_vel

    #### 4 comparison of acceleration stability within the control analysis
    def S_accel(self):

        index_accel = find_topic('accel', self.topics_name_s)
        accel = np.array(self.data_s[index_accel[0]])
        var_accel, var_accel_, s_accel = Var_accel(accel, self.allowed_control, path_save=self.path_save)
        self.accel = accel
        self.s_accel = s_accel

        return  var_accel, var_accel_, s_accel


    #### 5 comparison of uniform score and the stability score of the controller
    def US_controller(self):
        U_score, S_score, Score = US_controller(self.U_lead, self.s_sg, self.s_vel, self.s_accel)

        return U_score, S_score, Score


def main():
    ## read the bagfile
    bagfile1_path = '../bagfile/0802/2021_08_02_13_33_16_2T3H1RFV8LC057037following_real_vehicle_rl0719_enable_true.bag'
    print('Read the first bagfile from: ' + bagfile1_path)
    topics_num_1,topics_name_1, bag_1 = read_bagfiles_and_topics(bagfile1_path)

    ## read the bagfile
    bagfile2_path = '../bagfile/0802/2021_08_02_16_39_50_2T3H1RFV8LC057037following_real_vehicle_rl0719_enable_true.bag'
    print('Read the second bagfile from: ' + bagfile2_path)
    topics_num_2, topics_name_2, bag_2 = read_bagfiles_and_topics(bagfile2_path)

    # 0                                /accel  ...    205.281128
    # 1        /car/hud/cruise_cancel_request  ...      0.023581
    # 2              /car/hud/mini_car_enable  ...     68.678019
    # 3        /car/libpanda/controls_allowed  ...      0.855918
    # 4           /car/panda/controls_allowed  ...      0.854910
    # 5   /car/panda/gas_interceptor_detected  ...      0.854993
    # 6                 /car/panda/gps_active  ...      1.000035
    # 7                            /cmd_accel  ...    263.875684
    # 8                              /cmd_vel  ...     19.972876
    # 9                             /commands  ...    100.026328
    # 10                           /highbeams  ...      0.999613
    # 11                           /lead_dist  ...     25.561386
    # 12                       /lead_dist_869  ...     78.112038
    # 13                             /msg_467  ...    162.708666
    # 14                             /msg_921  ...    133.008943
    # 15                              /region  ...     19.974446
    # 16                             /rel_vel  ...     25.600156
    # 17                              /rosout  ...    249.727844
    # 18                          /rosout_agg  ...  24385.488372
    # 19                      /steering_angle  ...    101.994115
    # 20                         /timheadway1  ...     19.971735
    # 21                            /track_a0  ...     20.010992
    # 22                            /track_a1  ...     20.023220
    # 23                           /track_a10  ...     20.064264
    # 24                           /track_a11  ...     20.065560
    # 25                           /track_a12  ...     20.050069
    # 26                           /track_a13  ...     20.061481
    # 27                           /track_a14  ...     20.060282
    # 28                           /track_a15  ...     20.067288
    # 29                            /track_a2  ...     20.030296
    # 30                            /track_a3  ...     20.025132
    # 31                            /track_a4  ...     20.042644
    # 32                            /track_a5  ...     20.032449
    # 33                            /track_a6  ...     20.044655
    # 34                            /track_a7  ...     20.052465
    # 35                            /track_a8  ...     20.056157
    # 36                            /track_a9  ...     20.060282
    # 37                               /v_ref  ...     19.997444
    # 38                                 /vel  ...     50.207735

    data_1 = transfer_format(bag_1, topics_name_1, topics_num_1)
    data_2 = transfer_format(bag_2, topics_name_2, topics_num_2)

    #### parameter and threshold assignment
    lmd1 = 1/3
    lmd2 = 1/3
    lmd3 = 1/3

    alpha = 1/2

    sg_velocity_thresh = 10
    sg_time_thresh_min = 3
    sg_time_thresh_max = 120

    Eval_Controller1 = Eval_Controller(data = data_1,
                                       path = 1,
                                       topics_name = topics_name_1,
                                       lmd1 = lmd1,
                                       lmd2 = lmd2,
                                       lmd3 = lmd3,
                                       alpha = alpha,
                                       sg_velocity_thresh = sg_velocity_thresh,
                                       sg_time_thresh_min = sg_time_thresh_min,
                                       sg_time_thresh_max = sg_time_thresh_max)
    Eval_Controller2 = Eval_Controller(data = data_2,
                                       path = 2,
                                       topics_name = topics_name_2,
                                       lmd1 = lmd1,
                                       lmd2 = lmd2,
                                       lmd3 = lmd3,
                                       alpha = alpha,
                                       sg_velocity_thresh = sg_velocity_thresh,
                                       sg_time_thresh_min = sg_time_thresh_min,
                                       sg_time_thresh_max = sg_time_thresh_max)

    #### 1. compare the variance of lead disatnce
    var_control1, var_total1, U_lead1 = Eval_Controller1.V_lead()
    var_control2, var_total2, U_lead2 = Eval_Controller2.V_lead()

    print('#' * 100)
    print('Variance of the lead distance comparison of controllers analysis results : ')
    print('Var_{lead} of controller 1 = ', var_control1)
    print('Var_{lead}^{\prime} of controller 1 = ', var_total1)
    print('U  of controller 1 = ', U_lead1)
    print('#' * 100)
    print('Var_{lead} of controller 2 = ', var_control2)
    print('Var_{lead}^{\prime} of controller 2 = ', var_total2)
    print('U of controller 2 = ', U_lead2)
    print('#' * 100)
    print('Figure is saved in ./Results')
    if U_lead1 > U_lead2:
        key_word = 'controller 2 '
    else:
        key_word = 'controller 1'
    print('As for the variance of the lead distance,  ' + key_word + 'performs better on control the flows of the car, which can better keep an uniform distance of the ego car and lead car.')
    print('Variance of the lead distance comparison of controllers analysis finished ! ')
    print('*' * 120)

    #### 2. compare the stops and goes
    sg1, sg_p1, s_sg1 = Eval_Controller1.S_SG()
    sg2, sg_p2, s_sg2 = Eval_Controller2.S_SG()

    print('#' * 100)
    print('Stops and goes comparison of controllers analysis begins ! ')
    print('SG of controller 1 = ', sg1)
    print('SG^{\prime} of controller 1  = ', sg_p1)
    print('S_{SG} of controller 1  = ', s_sg1)
    print('#' * 100)
    print('SG of controller 2 = ', sg2)
    print('SG^{\prime} of controller 2  = ', sg_p2)
    print('S_{SG} of controller 2  = ', s_sg2)
    print('#' * 100)
    print('Figure is saved in ./Result')
    if s_sg1 > s_sg2:
        key_word = 'controller 2 '
    elif s_sg1 == s_sg2:
        key_word = 'controller 1 and controller 2 '
    else:
        key_word = 'controller 2 '

    print('As for the stops and goes control,  ' + key_word + 'performs better on control the stops and goes of the controller, which means the vehicle with such controller has less stops and goes within the control')
    print('Variance of the lead distance comparison of controllers analysis finished ! ')
    print('Stops and goes comparison of controllers analysis finished !')
    print('*' * 120)

    #### 3. compare the stability of the velocity
    var_vel1, var_vel_1, S_vel1 = Eval_Controller1.S_vel()
    var_vel2, var_vel_2, S_vel2 = Eval_Controller2.S_vel()
    print('#' * 100)
    print('Stability of velocity control comparison of the controllers analysis begins ! ')
    print('Var_{vel} of controller 1 = ', var_vel1)
    print('Var_{vel}^{\prime} of controller 1 = ', var_vel_1)
    print('S_{vel} of controller 1 = ', S_vel1)
    print('#' * 100)
    print('Var_{vel} of controller 2 = ', var_vel2)
    print('Var_{vel}^{\prime} of controller 2 = ', var_vel_2)
    print('S_{vel} of controller 2 = ', S_vel2)
    print('Figure is saved in ./Results')
    if S_vel1 > S_vel2:
        key_word = 'controller 2 '
    else:
        key_word = 'controller 1'
    print('As for the stability of the velocity control, ' + key_word + 'performs better, which means this controller can better control the velocity of the vehicle (more stable)')
    print('Stability of velocity control comparison of the controllers analysis finished !')
    print('*' * 120)

    #### 4. compare the stability of the acceleration
    var_accel1, var_accel_1, S_accel1 = Eval_Controller1.S_accel()
    var_accel2, var_accel_2, S_accel2 = Eval_Controller2.S_accel()

    print('#' * 100)
    print('Stability of acceleration control comparison of the controllers analysis begins ! ')
    print('Var_{accel} of controller 1 = ', var_accel1)
    print('Var_{accel}^{\prime} of controller 1 = ', var_accel_1)
    print('S_{vel} of controller 1 = ', S_accel1)
    print('#' * 100)
    print('Var_{vel} of controller 2 = ', var_accel2)
    print('Var_{vel}^{\prime} of controller 2 = ', var_accel_2)
    print('S_{vel} of controller 2 = ', S_accel2)
    print('Figure is saved in ./Results')
    if S_accel1 > S_accel2:
        key_word = 'controller 2 '
    else:
        key_word = 'controller 1'
    print(
        'As for the stability of the acceleration control, ' + key_word + 'performs better, which means this controller can better control the acceleration of the vehicle (more stable)')
    print('Stability of acceleration control comparison of the controllers analysis finished !')
    print('*' * 120)

    #### 5. Compare the uniform and stability of the controller
    U_score1, S_score1, Score1 = Eval_Controller1.US_controller()
    U_score2, S_score2, Score2 = Eval_Controller2.US_controller()

    print('#' * 100)
    print('Uniform and Stability comparison of the controller analysis begins ! ')
    print('U_score of controller 1 = ', U_score1)
    print('S_score of controller 1 = ', S_score1)
    print('Score of controller 1 = ', Score1)
    print('#' * 100)
    print('U_score of controller 2 = ', U_score2)
    print('S_score of controller 2 = ', S_score2)
    print('Score of controller 2 = ', Score2)
    if Score1 > Score2:
        key_word = 'controller 1 '
    else:
        key_word = 'controller 2 '
    print(
        'As for the totol uniform and stability of the controller, ' + key_word + 'performs better, which mean this controller behaves better !')
    print('Uniform and Stability comparison of the controller analysis finished !')
    print('*' * 120)














if __name__ == '__main__':
    print('*' * 120)
    print('Safety analysis can comparison of controller Starts')
    main()
    print('Safety analysis can comparison of controller Finished')
    print('*' * 120)












