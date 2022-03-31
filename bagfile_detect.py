#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
# This is the first part and second part of my work, the events detection and evaluation
# of the driving behaviors. It includes four bagfile analysis function (which records some
# basic strategies to process the bagfile using bagpy) and 10 events detection metrics, of
# which 4 of them are defined referred to existed literature, and 6 of them are original
# defined by my self. I have written all the intsructions and input, output, comment below,
# hopefully, very clear. For more information, please refer to my work report.
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************

#***************************************************************************************
#***************************************************************************************
#Experiment configuration:
# python 3.8, bagpy 0.4.8, matplotlib, numpy, pandas
#***************************************************************************************
#***************************************************************************************



import bagpy
from bagpy import bagreader
import pandas as pd
import seaborn as sea
import matplotlib.pyplot as plt
import numpy as np
import os
from mpl_toolkits.axisartist.parasite_axes import HostAxes, ParasiteAxes

def read_bagfiles_and_topics(file_path):
    ##############################################################################################
    #This function use bagreader to decode the bagfile, and return some topics and readerble data
    ##############################################################################################
    #input:
    #file_path: string
    ##############################################################################################
    #output:
    #topics_num[int], topics_name[list], bag
    ##############################################################################################
    bag = bagreader(file_path)
    # print the topics of the bagfile
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
    ##Read the data in pandas DataFrame
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


#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
# This following functions are the events detection functions
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************
#***************************************************************************************


def lead_vehicle_dectect(data, thresh = 250):
    ##############################################################################################
    # This function detect if there is a lead vehicle (a lead vehicle is defined as the car leads
    # the current car and the distance of them is within a threshold), the distance threshold we use
    # there is 250 meter, and it can be adjusted by the user. it will output the information of the
    # lead vehicles, total lead time and etc.
    ##############################################################################################
    # input:
    # data [array]: dimension: time * 2
    # thresh [int]: the threshold we use to define whether the car is the lead car, default: 250
    ##############################################################################################
    # output:
    # The x_th lead vehicle INFO:
    # Start time is: T1
    # Stop time is: T2
    # Total lead time is: T3 seconds
    # Result is saved in 'path (the user defines)'
    ##############################################################################################
    print('*' * 120)
    print('Lead Vehicle detection starts')
    lead_dist = data
    t = np.where(lead_dist[:, 1] <= thresh)[0]
    if t == []:
        print('Lead Vehicle: No lead vehicles detected!')
    else:
        print('Lead Vehicle: Detected!')
        total_time = lead_dist[-1, 0] - lead_dist[0, 0]
        total_interval, _ = lead_dist.shape

        # clip the lead interval
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            # if i == len(t) - 1:
            #     break
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]
        for i in range(len(clips)):
            time_start_c = lead_dist[clips[i][0]][0]
            time_stop_c = lead_dist[clips[i][1]][0]
            print('The ' + str(i) + ' lead vehicle INFO:')
            print('Start time is:', time_start_c)
            print('Stop time is:', time_stop_c)
            print('Total lead time is:' + str(time_period[i]) + ' seconds')

        # plot
        name = 'Lead Vehicle Detection'
        fig, ax = plt.subplots(figsize=[15, 4])
        ax.plot(lead_dist[:, 0], lead_dist[:, 1], label='Lead_distance', color='red', linewidth=1)
        ax.plot(lead_dist[:, 0], np.ones(total_interval) * 250, label='Threshold', color='blue', linewidth=1)
        ax.set_xlabel('Time')
        ax.set_ylabel('Lead_distance')
        ax.set_title(name)
        ax.legend()
        # plt.show()
        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Lead Vehicle detection stops')
        print('*' * 120)


def lead_vehicle_with_cruise_dectect(lead_dis, allowed_control):
    ##############################################################################################
    # This function detect if there is a lead vehicle with a cruise control (a lead vehicle is
    # defined as the car leads the current car and the distance of them is within a threshold),
    # the distance threshold we use there is 250 meter, and it can be adjusted by the user. Another
    # input is allowed_control, which is a bool type array, signify whether the control system is
    # activated at the specific moment. It will output the information of the lead vehicles with
    # allowed control and the total lead time and etc.
    ##############################################################################################
    # input:
    # lead_dis [array]: dimension: T1  * 2; allowed_control [array]: dimension: T2 * 2
    # thresh [int]: the threshold we use to define whether the car is the lead car, default: 250
    ##############################################################################################
    # output:
    # The x_th lead vehicle with cruise control INFO:
    # Start time is: T1
    # Stop time is: T2
    # Total lead time with cruise control is: T3 seconds
    # Result is saved in 'path (the user defines)'
    ##############################################################################################
    print('*' * 120)
    print('Lead Vehicle with Cruise detection starts')

    t = np.where(lead_dis[:, 1] <= 250)[0]
    t_c = np.where(allowed_control[:, 1] == 1)[0]
    if t == [] or t_c == []:
        print('Lead Vehicle with crusie: No lead vehicles with cruise detected!')
    else:
        ### clip the lead distance
        total_time = lead_dis[-1, 0] - lead_dis[0, 0]
        total_interval, _ = lead_dis.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### clip the cruise control
        total_time_c = allowed_control[-1, 0] - allowed_control[0, 0]
        total_interval_c, _ = allowed_control.shape
        clips_c = []
        time_period_c = []
        start_curr_c = t_c[0]
        for i in np.arange(0, len(t_c) - 1, 1):
            if t_c[i + 1] - t_c[i] == 1 and i != len(t_c) - 2:
                continue
            else:
                stop_curr_c = t_c[i]
                time_period_c_ = (stop_curr_c - start_curr_c) / total_interval_c * total_time_c
                time_period_c.append(time_period_c_)
                clips_c.append([start_curr_c, stop_curr_c])
                start_curr_c = t_c[i + 1]

        for i in range(len(clips_c)):
            time_start_c = allowed_control[clips_c[i][0]][0]
            time_stop_c = allowed_control[clips_c[i][1]][0]
            for j in range(len(clips)):
                time_start = lead_dis[clips[j][0]][0]
                time_stop = lead_dis[clips[j][1]][0]
                if time_start_c >= time_start and time_start_c <= time_stop:
                    stop_time = np.array([time_stop, time_stop_c]).max()
                    print('#' * 60)
                    print('Lead Vehicle with cruise control detected!')
                    print('Start time is:', time_start_c)
                    print('Stop time is:', stop_time)
                    print('Total lead vehicle with control time is:' + str(stop_time - time_start_c) + ' seconds')
                    print('#' * 60)
                    break
        ### plot
        for i in range(len(allowed_control)):
            if allowed_control[i][1] == True:
                allowed_control[i][1] = 1
            else:
                allowed_control[i][1] = 0

        allowed_control = transfer_length(allowed_control, lead_dis)

        fig, ax1 = plt.subplots(figsize=[15, 4])
        ax2 = ax1.twinx()

        ax1.plot(lead_dis[:, 0], lead_dis[:, 1], label='Lead_distance', color='blue', linewidth=1)
        ax2.plot(lead_dis[:, 0], allowed_control[:, 1], label='Allowed_cruise_control', color='red', linewidth=1)

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Lead_distance')
        ax2.set_ylabel('Allowed_Cruise_Control')

        ax1.legend(loc='upper right')
        ax2.legend(loc = 'upper left')
        name = 'Lead Vehicle With Cruise Control'

        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Lead Vehicle with cruise control detection stops')
        print('*' * 120)


def short_lead_vehicle_dectect(lead_dis, theta):
    ##############################################################################################
    # This To identify clips where a lead vehicle was present for ﬁve seconds or less, the ﬁrst
    # step was to ﬁlter the lead distance by removing bad values and ﬁlling in gaps with radar traces.
    # Next, the lead distance data was divided into chunks where each chunk represented a distinct
    # vehicle. Only chunks with lengths less than or equal to ﬁve seconds and greater than one second
    # were kept. Within these chunks, the steering angle was checked. If the time interval for the chunk
    # had a steering angle greater than ﬁfteen degrees, this signiﬁed that the car was likely turning
    # left or right. Any lead data collected on this turn was likely to be a parked car or other
    # cars that were not lead vehicles. Therefore, time intervals with these large steering angles were
    # thrown out.
    ##############################################################################################
    # input:
    # lead_dis [array]: dimension: T1  * 2;
    # theta [array]: dimension: T2 * 2
    ##############################################################################################
    # output:
    # Short lead vehicle detected!
    # Start time is: T1
    # Stop time is: T2
    # Total short vehicle time is: T3 seconds
    ##############################################################################################
    print('*' * 120)
    print('Short Lead Vehicle detection starts')

    t = np.where(lead_dis[:, 1] <= 250)[0]
    t_t = np.where(theta[:, 1] <= 15)[0]
    if t == [] or t_t == []:
        print('Short Lead Vehicle: No Short Lead Vehicle detected!')
    else:
        ### clip the lead distance
        total_time = lead_dis[-1, 0] - lead_dis[0, 0]
        total_interval, _ = lead_dis.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### filter the lead_distance clips
        clips_filter = []
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = abs(point2 - point1) / total_interval * total_time
            if difference > 1 and difference <= 5:
                clips_filter.append(list)
        if clips_filter == []:
            print('Short Lead Vehicle: No Short Lead Vehicle detected!')
        else:


            clips = clips_filter

            ### clip the steering angle
            total_time_t = theta[-1, 0] - theta[0, 0]
            total_interval_t, _ = theta.shape
            clips_t = []
            time_period_t = []
            start_curr_t = t_t[0]
            for i in np.arange(0, len(t_t) - 1, 1):
                if t_t[i + 1] - t_t[i] == 1 and i != len(t_t) - 2:
                    continue
                else:
                    stop_curr_t = t_t[i]
                    time_period_t_ = (stop_curr_t - start_curr_t) / total_interval_t * total_time_t
                    time_period_t.append(time_period_t_)
                    clips_t.append([start_curr_t, stop_curr_t])
                    start_curr_t = t_t[i + 1]

            for i in range(len(clips_t)):
                time_start_t = theta[clips_t[i][0]][0]
                time_stop_t = theta[clips_t[i][1]][0]
                for j in range(len(clips)):
                    time_start = lead_dis[clips[j][0]][0]
                    time_stop = lead_dis[clips[j][1]][0]
                    if time_start_t >= time_start and time_start_t <= time_stop:
                        stop_time = np.array([time_stop, time_stop_t]).max()
                        print('#' * 60)
                        print('Short lead vehicle detected!')
                        print('Start time is:', time_start_t)
                        print('Stop time is:', stop_time)
                        print('Total short lead vehicle time is:' + str(stop_time - time_start_t) + ' seconds')
                        print('#' * 60)
                        break


        theta = transfer_length(theta, lead_dis)

        ### plot
        fig, ax1 = plt.subplots(figsize=[15, 4])
        ax2 = ax1.twinx()

        ax1.plot(lead_dis[:, 0], lead_dis[:, 1], color='blue', label = 'Lead_distance', linewidth=1)
        ax2.plot(lead_dis[:, 0], theta[:, 1], color='orange', label = 'steering angle', linewidth=1, linestyle = '--')

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Lead_distance')
        ax2.set_ylabel('Steering angle')

        ax1.legend(loc = 'upper left')
        ax2.legend(loc = 'upper right')
        name = 'Short Lead Vehicle'

        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Short Lead Vehicle detection stops')
        print('*' * 120)


def Long_lead_vehicle_dectect(lead_dis, theta):
    ##############################################################################################
    # A long period of time where a lead vehicle is present is deﬁned as having a length of at
    # least thirty seconds. The signal used to identify these events was the lead distance.
    # Each continuous section of lead distance represented following a lead vehicle for a period of time.
    # Only the chunks that were thirty seconds or more were kept. Some of the dash camera footage con-
    # tains instances where the vehicle is parked with something in front of it for longer than thirty
    # seconds. This was incorrectly being labeled as following a lead vehicle. To resolve this issue,
    # only instances with a lead distance of greater than one meter were considered. When following a
    # car while driving, a safe following distance should be greater than one meter. Anything with one
    # meter or less lead distance can therefore be removed.
    ##############################################################################################
    # input:
    # lead_dis [array]: dimension: T1  * 2;
    # theta [array]: dimension: T2 * 2
    ##############################################################################################
    # output:
    # Long lead vehicle detected!
    # Start time is: T1
    # Stop time is: T2
    # Total long vehicle time is: T3 seconds
    ##############################################################################################
    print('*' * 120)
    print('Long Lead Vehicle detection starts')

    t1 = np.where(lead_dis[:, 1] <= 250)[0]
    t2 = np.where(lead_dis[:, 1] > 1)[0]
    t = np.array(np.intersect1d(t1, t2))

    t_t = np.where(theta[:, 1] <= 15)[0]
    if t == [] or t_t == []:
        print('Long Lead Vehicle: No Short Long Vehicle detected!')
    else:
        ### clip the lead distance
        total_time = lead_dis[-1, 0] - lead_dis[0, 0]
        total_interval, _ = lead_dis.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### filter the lead_distance clips
        clips_filter = []
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = point2 - point1
            difference = difference / total_interval * total_time
            if difference > 30:
                clips_filter.append(list)
        if clips_filter == []:
            print('Long Lead Vehicle: No Long Lead Vehicle detected!')
        else:


            clips = clips_filter

            ### clip the steering angle
            total_time_t = theta[-1, 0] - theta[0, 0]
            total_interval_t, _ = theta.shape
            clips_t = []
            time_period_t = []
            start_curr_t = t_t[0]
            for i in np.arange(0, len(t_t) - 1, 1):
                if t_t[i + 1] - t_t[i] == 1 and i != len(t_t) - 2:
                    continue
                else:
                    stop_curr_t = t_t[i]
                    time_period_t_ = (stop_curr_t - start_curr_t) / total_interval_t * total_time_t
                    time_period_t.append(time_period_t_)
                    clips_t.append([start_curr_t, stop_curr_t])
                    start_curr_t = t_t[i + 1]

            for i in range(len(clips_t)):
                time_start_t = theta[clips_t[i][0]][0]
                time_stop_t = theta[clips_t[i][1]][0]
                for j in range(len(clips)):
                    time_start = lead_dis[clips[j][0]][0]
                    time_stop = lead_dis[clips[j][1]][0]
                    if time_start_t >= time_start and time_start_t <= time_stop:
                        stop_time = np.array([time_stop, time_stop_t]).max()
                        print('#' * 60)
                        print('Long lead vehicle detected!')
                        print('Start time is:', time_start_t)
                        print('Stop time is:', stop_time)
                        print('Total long lead vehicle time is:' + str(stop_time - time_start_t) + ' seconds')
                        print('#' * 60)
                        break
            ### plot

        theta = transfer_length(theta, lead_dis)

        fig, ax1 = plt.subplots(figsize=[15, 4])  # 定义figure，（1）中的1是什么
        ax2 = ax1.twinx()

        ax1.plot(lead_dis[:, 0], lead_dis[:, 1], color='blue', label = 'Lead_distance', linewidth=1)
        ax2.plot(lead_dis[:, 0], theta[:, 1], color='blueviolet', label = 'steering angle', linewidth=1, linestyle = '--')

        ax1.set_xlabel('Time')  # 设置x轴标题
        ax1.set_ylabel('Lead distance')  # 设置Y1轴标题
        ax2.set_ylabel('Steering angle')  # 设置Y2轴标题

        ax1.legend(loc = 'upper left')
        ax2.legend(loc = 'upper right')
        name = 'Long Lead Vehicle'

        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Long Lead Vehicle detection stops')
        print('*' * 120)


def turn_dectect(theta):
    ##############################################################################################
    # This function align the data of two different topics with different sample rate：
    # This method use l1-norm to find the position of one value should be located in which entry
    # of a whole one dimention array, for-loop is not a great choice because it is not efficient
    # and need lot of computing and time. Here I use vector substraction and then find the index of
    # the minimal entry of the difference.
    ##############################################################################################
    # input:
    # theta [array]: steering angle, dimension: T1 * 2
    ##############################################################################################
    # output:
    # Turn detected!
    # Start time is: T1
    # Stop time is: T2
    # Total turn time is:T3 seconds
    # Average turn angle is: alpha degree
    ##############################################################################################
    # Lead Vehicle
    print('*' * 120)
    print('Turn detection starts')

    t_t = np.where(np.abs(theta[:, 1]) >= 100)[0]
    if t_t == []:
        print('Turn: No Turn detected!')
    else:
        ### clip the steering angle
        total_time_t = theta[-1, 0] - theta[0, 0]
        total_interval_t, _ = theta.shape
        clips_t = []
        time_period_t = []
        start_curr_t = t_t[0]
        for i in np.arange(0, len(t_t) - 1, 1):
            if t_t[i + 1] - t_t[i] == 1 and i != len(t_t) - 2:
                continue
            else:
                stop_curr_t = t_t[i]
                time_period_t_ = (stop_curr_t - start_curr_t) / total_interval_t * total_time_t
                time_period_t.append(time_period_t_)
                clips_t.append([start_curr_t, stop_curr_t])
                start_curr_t = t_t[i + 1]

        for i in range(len(clips_t)):
            time_start_t = theta[clips_t[i][0]][0]
            time_stop_t = theta[clips_t[i][1]][0]

            averge_angle = np.mean(theta[clips_t[i][0] : clips_t[i][1], 1])
            print('#' * 60)
            print('Turn detected!')
            print('Start time is:', time_start_t)
            print('Stop time is:', time_stop_t)
            print('Total turn time is:' + str(time_stop_t - time_start_t) + ' seconds')
            print('Average turn angle is:'+ str(averge_angle) + ' degree')
            print('#' * 60)
        ### plot


        fig, ax1 = plt.subplots(figsize=[15, 4])  # 定义figure，（1）中的1是什么

        ax1.plot(theta[:, 0], theta[:, 1], color='darkorchid', label='Steering angle', linewidth=1, linestyle='dotted')

        ax1.set_xlabel('Time (s)')  # 设置x轴标题
        ax1.set_ylabel('Steering angle (degree)')  # 设置Y1轴标题

        ax1.legend(loc='upper right')
        name = 'Turns'

        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Long Lead Vehicle detection stops')
        print('*' * 120)


def accel_intensity(data):
    ##############################################################################################
    # This function calculate the acceleration intensity of driving. The acceleration intensity weighs
    # the average acceleration rate among the driving. This is a new metric and the details of its \
    # defination should refer to my reports.
    ##############################################################################################
    # input:
    # data [array]: this is numpyarray that reflect the acceleration data, dimension: T1 * 2
    ##############################################################################################
    # output:
    # The x-th acceleration INFO:
    # Start time is: T1
    # Stop time is: T2
    # Total accelaration time is:T3 seconds
    # Acceleration intensity is X (times/min)
    # Result is saved in ./Result/Acceleration intensity.png
    ##############################################################################################
    print('*' * 120)
    print('Aacceleration intensntity detection begins')
    accel = np.array(data)
    t = np.where(accel[:, 1] > 2)[0]
    if t == []:
        print('No acceleration more than 2 m/(s^2) was detected!')
    else:
        print('Acceleration more than 2 m/(s^2) was detected!')
        total_time = accel[-1, 0] - accel[0, 0]
        total_interval, _ = accel.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            # if i == len(t) - 1:
            #     break
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### filter the clips
        clips_filter = []
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = (point2 - point1) / total_interval * total_time
            if difference > 1:
                clips_filter.append(list)
        if clips_filter == []:
            print('Acceleration intensity: No obvious accleration detected!')
        else:
            clips = clips_filter
            mark = np.zeros(accel.shape)
            for i in range(len(clips)):
                print('#' * 120)
                time_start_c = accel[clips[i][0]][0]
                time_stop_c = accel[clips[i][1]][0]
                mark[clips[i][0] : clips[i][1]][1] = 1
                print('The ' + str(i) + ' acceleration INFO:')
                print('Start time is:', time_start_c)
                print('Stop time is:', time_stop_c)
                p = difference = (clips[i][1] - clips[i][0]) / total_interval * total_time
                print('Total accelaration time is:' + str(p) + ' seconds')

                print('#' * 120)

        name = 'Acceleration intensity'
        fig, ax = plt.subplots(figsize=[15, 4])  # 定义figure，（1）中的1是什么
        ax2 = ax.twinx()

        ax.plot(accel[:, 0], accel[:, 1], color='cyan', label='Accel', linewidth=1, linestyle='--')
        ax2.plot(accel[:, 0], mark[:, 1], color='red', label='Obvious acceleration', linewidth=1, linestyle='dotted')
        ax2.set_ylabel('Obvious acceleration')  # 设置Y2轴标题
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')


        ax.set_xlabel('Time (s)')  # 设置x轴标题
        ax.set_ylabel('Acceleration')  # 设置Y1轴标题

        name = 'Acceleration intensity'
        num_accel = i + 1
        intensity = num_accel / total_time * 60
        print('Acceleration intensity is ' + str(intensity) + '(times/min)' )
        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)

        print('Acceleration intensity detection stops')
        print('*' * 120)


def de_accel_intensity(data):
    ##############################################################################################
    # This function calculate the de-acceleration intensity of driving. The de-acceleration intensity
    # weighs the average de-acceleration rate among the driving. This is a new metric and the details
    # of its defination should refer to my reports.
    ##############################################################################################
    # input:
    # data [array]: this is numpyarray that reflect the acceleration data, dimension: T1 * 2
    ##############################################################################################
    # output:
    # The x-th acceleration INFO:
    # Start time is: T1
    # Stop time is: T2
    # Total de- accelaration time is:T3 seconds
    # De-acceleration intensity is X (times/min)
    # Result is saved in ./Result/Acceleration intensity.png
    ##############################################################################################
    print('*' * 120)
    print('De-Aacceleration intensntity detection begins')
    accel = np.array(data)
    t = np.where(accel[:, 1] < -2)[0]
    if t == []:
        print('No acceleration less than -2 m/(s^2) was detected!')
    else:
        print('De-Acceleration less than -2 m/(s^2) was detected!')
        total_time = accel[-1, 0] - accel[0, 0]
        total_interval, _ = accel.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            # if i == len(t) - 1:
            #     break
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### filter the clips
        clips_filter = []
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = (point2 - point1) / total_interval * total_time
            if difference > 1:
                clips_filter.append(list)
        if clips_filter == []:
            print('De-Acceleration intensity: No obvious de-accleration detected!')
        else:
            clips = clips_filter
            mark = np.zeros(accel.shape)
            for i in range(len(clips)):
                print('#' * 120)
                time_start_c = accel[clips[i][0]][0]
                time_stop_c = accel[clips[i][1]][0]
                mark[clips[i][0] : clips[i][1]][1] = 1
                print('The ' + str(i) + ' de-acceleration INFO:')
                print('Start time is:', time_start_c)
                print('Stop time is:', time_stop_c)
                p = difference = (clips[i][1] - clips[i][0]) / total_interval * total_time
                print('Total de-accelaration time is:' + str(p) + ' seconds')

                print('#' * 120)

        name = 'De-Acceleration intensity'
        fig, ax = plt.subplots(figsize=[15, 4])  # 定义figure，（1）中的1是什么
        ax2 = ax.twinx()

        ax.plot(accel[:, 0], accel[:, 1], color='cyan', label='De-Accel', linewidth=1, linestyle='--')
        ax2.plot(accel[:, 0], mark[:, 1], color='darkred', label='Obvious de-acceleration', linewidth=1, linestyle='dotted')
        ax2.set_ylabel('Obvious de-acceleration')  # 设置Y2轴标题
        ax.legend(loc='upper left')
        ax2.legend(loc='upper right')


        ax.set_xlabel('Time (s)')  # 设置x轴标题
        ax.set_ylabel('De-Acceleration')  # 设置Y1轴标题

        name = 'De-Acceleration intensity'
        num_accel = i + 1
        intensity = num_accel / total_time * 60
        print('De-Acceleration intensity is ' + str(intensity) + '(times/min)' )
        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)

        print('De-Acceleration intensity detection stops')
        print('*' * 120)

def average_accel(data):
    ##############################################################################################
    # This function calculate the average acceleration of driving. This is a new metric and the details
    # of its defination should refer to my reports.
    ##############################################################################################
    # input:
    # data [array]: this is numpyarray that reflect the acceleration data, dimension: T1 * 2
    ##############################################################################################
    # output:
    # TAverage acceleration rate detection begins
    # Average Acceleration is x (m/s)
    # Result is saved in ./Result/Average Acceleration rate.png
    ##############################################################################################
    print('*' * 120)
    print('Average acceleration rate detection begins')
    accel = np.array(data)
    total_time = accel[-1, 0] - accel[0, 0]
    total_interval, _ = accel.shape
    average = np.zeros(accel.shape)
    average[:, 1] = np.mean(accel[:, 1])

    fig, ax = plt.subplots(figsize=[15, 4])
    ax2 = ax.twinx()

    ax.plot(accel[:, 0], accel[:, 1], color='deepskyblue', label='Acceleration', linewidth=1, linestyle='-')
    ax2.plot(accel[:, 0], average[:, 1], color='crimson', label='Average Acceleration', linewidth=1, linestyle='dotted')
    ax2.set_ylabel('Average Acceleration')
    ax.legend(loc='upper left')
    ax2.legend(loc='upper right')


    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Acceleration')

    name = 'Average Acceleration rate'
    print('Average Acceleration is ' + str(np.mean(accel[:, 1])) + '(m/s)' )
    path = './Result/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    print('Result is saved in ' + path)

    print('Average Acceleration detection stops')
    print('*' * 120)


def urgent_deac(vel, accel):
    ##############################################################################################
    # This function is to detect if there exists an urgent brake and de-acceleration, This is a new metric
    # and the details of its defination should refer to my reports.
    ##############################################################################################
    # input:
    # vel [array]: this is numpyarray that reflect the acceleration data, dimension: T1 * 2
    # accel [array]: this is numpyarray that reflect the velocity data, dimension: T2 * 2
    ##############################################################################################
    # output:
    # Urgent de-acceleration detected!
    # Start time is: T1
    # Stop time is: T2
    # Total urgent de-acceleration time is:T3 seconds
    # The end velocity is: v seconds
    ##############################################################################################
    print('*' * 120)
    print('Urgent de-acceleration detection starts')

    t = np.where(accel[:, 1] <= -1.5)[0]
    if t == []:
        print('Urgent de-acceleration: No Urgent de-celleration detected!')
    else:
        ### clip the lead distance
        total_time = vel[-1, 0] - vel[0, 0]
        total_interval, _ = vel.shape
        clips = []
        time_period = []
        start_curr = t[0]
        for i in np.arange(0, len(t) - 1, 1):
            if t[i + 1] - t[i] == 1 and i != len(t) - 2:
                continue
            else:
                stop_curr = t[i]
                time_period_ = (stop_curr - start_curr) / total_interval * total_time
                time_period.append(time_period_)
                clips.append([start_curr, stop_curr])
                start_curr = t[i + 1]

        ### filter the clips
        clips_filter = []
        for list in clips:
            point1 = list[0]
            point2 = list[1]
            difference = point2 - point1
            difference = difference / total_interval * total_time
            if difference > 2:
                clips_filter.append(list)
        if clips_filter == []:
            print('Urgent de-acceleration: No Urgent de-celleration detected!')
        else:
            clips = clips_filter
            for i in range(len(clips)):
                time_start_t = accel[clips[i][0]][0]
                time_stop_t = accel[clips[i][1]][0]

                p1 = time_start_t * np.ones(vel.shape)
                idx_start = np.argmin(np.abs(p1[:, 0] - vel[:, 0]))
                p2 = time_stop_t * np.ones(vel.shape)
                idx_stop = np.argmin(np.abs(p2[:, 0] - vel[:, 0]))

                vel_stop = vel[idx_stop, 1]

                if vel_stop < 10:
                    print('#' * 60)
                    print('Urgent de-acceleration detected!')
                    print('Start time is:', vel[idx_start, 0])
                    print('Stop time is:', vel[idx_stop, 0])
                    print('Total urgent de-acceleration time is:' + str(vel[idx_stop, 0] - vel[idx_start, 0]) + ' seconds')
                    print('The end velocity is:' + str(
                        vel[idx_start, 1] - vel[idx_stop, 1]) + ' m/s')
                    print('#' * 60)
            ### plot

        accel = transfer_length(accel, vel)

        fig, ax1 = plt.subplots(figsize=[15, 4])
        ax2 = ax1.twinx()

        ax1.plot(vel[:, 0], vel[:, 1], color='blue', label='Velocity', linewidth=1)
        ax2.plot(vel[:, 0], accel[:, 1], color='blueviolet', label='Acceleration', linewidth=1, linestyle='dashdot')

        ax1.set_xlabel('Time')
        ax1.set_ylabel('Velocity')
        ax2.set_ylabel('Acceleration')

        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')
        name = 'Urgent de-acceleration detection'

        path = './Result/' + name + '.png'
        plt.savefig(path)
        # plt.close()
        print('Result is saved in ' + path)
        print('Urgent de-acceleration detection stops')
        print('*' * 120)


def command_vel_comp(cmd_vel):
    ##############################################################################################
    # This function is to show the command velocity from the followerstopper controller
    ##############################################################################################
    # input:
    # cmd_vel [array]: this is numpyarray that reflect the cmd_velocity data, dimension: T1 * 2
    ##############################################################################################
    # output:
    # an plot of the command velocity of the driving
    ##############################################################################################
    print('*' * 120)
    print('The command velocity from the followerstopper')

    total_time_cmd = cmd_vel[-1, 0] - cmd_vel[0, 0]
    total_interval_cmd, _ = cmd_vel.shape


    fig, ax = plt.subplots(figsize=[15, 4])
    ax2 = ax.twinx()

    ax.plot(cmd_vel[:, 0], cmd_vel[:, 1], color='greenyellow', label='Cammand Velocity', linewidth=1, linestyle='-')

    ax.legend(loc='upper left')


    ax.set_xlabel('Time (s)')
    ax.set_ylabel('Command_velocity')

    name = 'The command velocity from the follwerstopper'

    path = './Result/' + name + '.png'
    plt.savefig(path)
    # plt.close()
    print('Result is saved in ' + path)

    print('The command velocity visualization stops')
    print('*' * 120)





def main():
    ## read the bagfile
    ## This is the only input of this analysis
    bagfile_path = './0802/2021_08_02_03_25_57_2T3H1RFV8LC057037following_real_vehicle_rl0719_enable_true.bag'

    print('Read bagfile from: ' + bagfile_path)


    ## call this function to read bagfiles
    topics_num, topics_name, bag = read_bagfiles_and_topics(bagfile_path)

    ## will print the basic topics and the information, e.g.:
    #
    #     # 0                                /accel  ...    205.281128
    #     # 1        /car/hud/cruise_cancel_request  ...      0.023581
    #     # 2              /car/hud/mini_car_enable  ...     68.678019
    #     # 3        /car/libpanda/controls_allowed  ...      0.855918
    #     # 4           /car/panda/controls_allowed  ...      0.854910
    #     # 5   /car/panda/gas_interceptor_detected  ...      0.854993
    #     # 6                 /car/panda/gps_active  ...      1.000035
    #     # 7                            /cmd_accel  ...    263.875684
    #     # 8                              /cmd_vel  ...     19.972876
    #     # 9                             /commands  ...    100.026328
    #     # 10                           /highbeams  ...      0.999613
    #     # 11                           /lead_dist  ...     25.561386
    #     # 12                       /lead_dist_869  ...     78.112038
    #     # 13                             /msg_467  ...    162.708666
    #     # 14                             /msg_921  ...    133.008943
    #     # 15                              /region  ...     19.974446
    #     # 16                             /rel_vel  ...     25.600156
    #     # 17                              /rosout  ...    249.727844
    #     # 18                          /rosout_agg  ...  24385.488372
    #     # 19                      /steering_angle  ...    101.994115
    #     # 20                         /timheadway1  ...     19.971735
    #     # 21                            /track_a0  ...     20.010992
    #     # 22                            /track_a1  ...     20.023220
    #     # 23                           /track_a10  ...     20.064264
    #     # 24                           /track_a11  ...     20.065560
    #     # 25                           /track_a12  ...     20.050069
    #     # 26                           /track_a13  ...     20.061481
    #     # 27                           /track_a14  ...     20.060282
    #     # 28                           /track_a15  ...     20.067288
    #     # 29                            /track_a2  ...     20.030296
    #     # 30                            /track_a3  ...     20.025132
    #     # 31                            /track_a4  ...     20.042644
    #     # 32                            /track_a5  ...     20.032449
    #     # 33                            /track_a6  ...     20.044655
    #     # 34                            /track_a7  ...     20.052465
    #     # 35                            /track_a8  ...     20.056157
    #     # 36                            /track_a9  ...     20.060282
    #     # 37                               /v_ref  ...     19.997444
    #     # 38                                 /vel  ...     50.207735

    ## transform the data to csv files
    data = transfer_format(bag, topics_name, topics_num)


    ##########Recognition of events#########
    ## 1. Detection of lead vehicle
    # find the target data from the data pool
    index_lead_dist = find_topic('lead_dist', topics_name)
    lead_dist = np.array(data[index_lead_dist[0]])

    # call the corresponding events detection function
    lead_vehicle_dectect(lead_dist)


    ## 2. Lead Vehicle with Cruise Control
    # find the target data from the data pool
    index_controls_allowed = find_topic('car/panda/controls_allowed', topics_name)
    controls_allowed = np.array(data[index_controls_allowed[0]])

    # call the corresponding events detection function
    lead_vehicle_with_cruise_dectect(lead_dist, controls_allowed)

    ## 3. Short Lead Vehicle
    # find the target data from the data pool
    index_theta = find_topic('steering_angle', topics_name)
    theta = np.array(data[index_theta[0]])

    # call the corresponding events detection function
    short_lead_vehicle_dectect(lead_dist, theta)

    ## 4. Long Lead Vehicle
    # call the corresponding events detection function
    Long_lead_vehicle_dectect(lead_dist, theta)

    ## 5. Turns
    # call the corresponding events detection function
    turn_dectect(theta)

    #### 6. acceleration intensity
    # find the target data from the data pool
    index_accel = find_topic('accel', topics_name)
    accel = np.array(data[index_accel[0]])

    # call the corresponding events detection function
    accel_intensity(accel)

    #### 7. de - acceleration intensity
    # call the corresponding events detection function
    de_accel_intensity(accel)

    #### 8. average acceleration rate
    # call the corresponding events detection function
    average_accel(accel)

    #### 9. urgent brake or de-acceleration
    # find the target data from the data pool
    index_vel = find_topic('vel', topics_name)
    vel = np.array(data[index_vel[0]])

    # call the corresponding events detection function
    urgent_deac(vel, accel)

    #### 10. Command velocity of the followerstopper
    # find the target data from the data pool
    index_cmd_vel = find_topic('cmd_vel', topics_name)
    cmd_vel = np.array(data[index_cmd_vel[0]])

    # call the corresponding events detection function
    command_vel_comp(cmd_vel)





if __name__ == '__main__':
    print('*' * 120)
    print('Execute the events detection of the bagfile')
    main()
    print('Analysis End')
    print('*' * 120)






