# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# In this part, we implement the five metrics to evaluate the controller with respect to
# its stability and uniform rate
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

def Var_lead(lead_dis, allowed_control):
    print('*' * 120)
    print('Variance of lead distance evaluation begins !')
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

    path = './Result/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    print('#' * 100)
    print('Analysis results:')
    print('Var_{lead} = ', var_control)
    print('Var_{lead}^{\prime} = ', var_total)
    print('U = ', U_lead)
    print('#' * 100)
    print('Figure is saved in ' + path)
    print('Variance of lead distance evaluation finished !')
    print('*' * 120)
    return var_control, var_total, U_lead


def S_SG(vel, allowed_control,
         sg_velocity_thresh, sg_time_thresh_min, sg_time_thresh_max):
    print('*' * 120)
    print('The evaluation on average stop and goes within control begins!')
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

    path = './Result/' + name + '.png'
    plt.savefig(path)

    print('#' * 100)
    print('Analysis results:')
    print('SG = ', SG)
    print('SG^{\prime} = ', SG_p)
    print('S_{SG} = ', S_SG)
    print('#' * 100)
    print('Figure is saved in ' + path)
    print('The evaluation on average stop and goes within control finished !')
    print('*' * 120)
    return SG, SG_p, S_SG

def Var_vel(vel, allowed_control):
    print('*' * 120)
    print('Velocity stability within the control assessment begins !')
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

    path = './Result/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    print('#' * 100)
    print('Analysis results:')
    print('Var_{vel} = ', var_control)
    print('Var_{vel}^{\prime} = ', var_total)
    print('S_{vel} = ', S_vel)
    print('#' * 100)
    print('Figure is saved in ' + path)
    print('Velocity stability within the control assessment finished !')
    print('*' * 120)
    return var_control, var_total, S_vel

def Var_accel(accel, allowed_control):
    print('*' * 120)
    print('Acceleration stability within the control assessment begins !')
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

    path = './Result/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    print('#' * 100)
    print('Analysis results:')
    print('Var_{accel} = ', var_control)
    print('Var_{accel}^{\prime} = ', var_total)
    print('S_{accel} = ', S_accel)
    print('#' * 100)
    print('Figure is saved in ' + path)
    print('Acceleration stability within the control assessment finished !')
    print('*' * 120)
    return var_control, var_total, S_accel

def US_controller(U_lead, s_sg, S_vel, S_accel,
                  lmd1 = 1/3,
                  lmd2 = 1/3,
                  lmd3 = 1/3,
                  alpha = 1/2):
    print('*' * 120)
    print('Uniform score and the stability score of the controller assessment begins !')


    U_score = 1/U_lead

    S_score = lmd1 * 1/ (s_sg + 0.001) + lmd2 * 1/ (S_vel + 0.001) + lmd3 * 1/ (S_accel + 0.001)

    Score = alpha * U_score + (1 - alpha) * S_score

    print('#' * 100)
    print('Analysis results:')
    print('U_score = ', U_score)
    print('S_score = ', S_score)
    print('Score of the controller = ', Score)
    print('#' * 100)

    print('Uniform score and the stability score of the controller assessment finished !')
    print('*' * 120)


def main():
    ## read the bagfile
    # the original bagfile from the real-world driving
    # the simulation bagfile from the ROS
    simulation_bagfile_path = '../bagfile/0802/2021_08_02_16_39_50_2T3H1RFV8LC057037following_real_vehicle_rl0719_enable_true.bag'
    print('Read simulation bagfile from: ' + simulation_bagfile_path)
    topics_num_s,topics_name_s, bag_s = read_bagfiles_and_topics(simulation_bagfile_path)

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

    data_s = transfer_format(bag_s, topics_name_s, topics_num_s)

    #### parameter and threshold assignment

    lmd1 = 1/3
    lmd2 = 1/3
    lmd3 = 1/3

    alpha = 1/2

    sg_velocity_thresh = 10
    sg_time_thresh_min = 3
    sg_time_thresh_max = 120



    #### 2.1 Variance of lead distance within control

    index_allowed_control = find_topic('car/panda/controls_allowed', topics_name_s)
    allowed_control = np.array(data_s[index_allowed_control[0]])

    index_lead_dis = find_topic('lead_dist', topics_name_s)
    lead_dis = np.array(data_s[index_lead_dis[0]])

    var_control, var_total, U_lead = Var_lead(lead_dis, allowed_control)

    #### 2.2 The average stop and goes within control

    index_vel = find_topic('vel', topics_name_s)
    vel = np.array(data_s[index_vel[0]])

    sg, sg_p, s_sg = S_SG(vel, allowed_control, sg_velocity_thresh, sg_time_thresh_min, sg_time_thresh_max)

    #### 2.3 Velocity stability within the control analysis
    var_vel, var_vel_, S_vel = Var_vel(vel, allowed_control)

    #### 2.4 Acceleration stability within the control analysis
    index_accel = find_topic('accel', topics_name_s)
    accel = np.array(data_s[index_accel[0]])
    var_accel, var_accel_, S_accel = Var_accel(accel, allowed_control)

    #### 2.5 Uniform score and the stability score of the controller
    US_controller(U_lead, s_sg, S_vel, S_accel)








if __name__ == '__main__':
    print('*' * 120)
    print('Evaluation of the controller analysis Starts')
    main()
    print('Evaluation of the controller analysis Ends')
    print('*' * 120)












