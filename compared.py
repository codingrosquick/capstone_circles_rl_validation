# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# ***************************************************************************************
# This is the third part of my work. For this part, we should change
# the parameters of the ROS simulation, then get the command velocity from simulation
# results and make comparisons with the two. By checking the difference, we may further
# define new metrics to evaluate the performance of the controllers.
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



def main():
    ## read the bagfile
    # the original bagfile from the real-world driving
    real_bagfile_path = './0802/2021_08_02_03_25_57_2T3H1RFV8LC057037following_real_vehicle_rl0719_enable_true.bag'
    # the simulation bagfile from the ROS
    simulation_bagfile_path = '2022_03_16_04_41_45_following_real_vehicle_rl0719_enable_true.bag'

    print('Read real bagfile from: ' + real_bagfile_path)
    print('Read imulation bagfile from: ' + simulation_bagfile_path)
    topics_num_r, topics_name_r, bag_r = read_bagfiles_and_topics(real_bagfile_path)
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

    data_r = transfer_format(bag_r, topics_name_r, topics_num_r)
    data_s = transfer_format(bag_s, topics_name_s, topics_num_s)

    index_v_ref_r = find_topic('v_ref', topics_name_r)
    index_v_ref_s = find_topic('v_ref_new', topics_name_s)
    index_vel_r = find_topic('cmd_vel', topics_name_r)
    index_vel_s = find_topic('cmd_vel_new', topics_name_s)

    vel_r = np.array(data_r[index_vel_r[0]])
    vel_s = np.array(data_s[index_vel_s[0]])
    v_ref_r = np.array(data_r[index_v_ref_r[0]])
    v_ref_s = np.array(data_s[index_v_ref_s[0]])


    #align their length
    vel_length = min(vel_r.shape[0], vel_s.shape[0])
    v_ref_length = min(v_ref_r.shape[0], v_ref_s.shape[0])

    # plot the two figure in the same plot
    plot_compared(data1 = vel_r, data2 = vel_s, file_name='Comparison_cmd_vel', length = vel_length, x_lable='Time', y_label= 'Cmd_vel')
    plot_compared(data1 = v_ref_r, data2=v_ref_s, file_name='Comparison_v_ref', length=v_ref_length, x_lable='Time', y_label='V_ref')
    # plot(accel_r, accel_s, accel_length, file_name='Comparison_accel', x_lable='Time', y_label='Accel')

    difference_vel = np.array([vel_r[0 : vel_length, 0], np.abs(vel_r[0 : vel_length, 1] - vel_s[0 : vel_length, 1])])
    plot(difference_vel, vel_length, file_name='Difference_cmd_vel', x_lable='Time', y_label='abs(difference)')
    difference_v_ref = np.array([v_ref_r[0: v_ref_length, 0], np.abs(v_ref_r[0: v_ref_length, 1] - v_ref_s[0: v_ref_length, 1])])
    plot(difference_v_ref, v_ref_length, file_name='Difference_v_ref', x_lable='Time', y_label='abs(difference)')








if __name__ == '__main__':
    print('*' * 120)
    print('Analysis Start')
    main()
    print('Analysis End')
    print('*' * 120)












