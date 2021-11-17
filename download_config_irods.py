# imports

'''
# iinit command


# ils command


# download directories


# clear cache function


# scroll through the directories to download
# CL to download:
# $      iget -PT /iplant/home/cyverse_username/target_file /local_destination (-r for downloadìng the whole directory)
# $      ipwd to see the directory current? other like ils and icd to see the different files
# -> find the CAN and GPS files, associate the and them download them
# (we can explore the fileshare through these commands)

# (launch bash from python to automate it)
# https://janakiev.com/blog/python-shell-commands/

# run iinit by hand???

import subprocess


# TODO; find the folders
# https://docs.google.com/presentation/d/1Jiw1kstiDrSe89g-dOOrbdUSg3H9DCkULGyzYSHy4gI/edit#slide=id.gea16c18cba_0_10
# https://docs.google.com/presentation/d/1_yIHI9mTJUPUW1Mf9ZnANhw5wghpqAUePTNwFRoeAHY/edit#slide=id.gfd87d47e3e_1_5

folders = ['/iplant/home/noecarras/analyses']
folder = folders[0]

subprocess.run(['icd', folder],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
# TODO: read folders from a list of it

process_files = subprocess.run(['ils'],
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
# 1st is useless, so we split
files = process_files.stdout.split()[1:]
print(files)


# TODO: find the CAN and GPS linked data inside of this
file_list = []
for file in files:
    if '_CAN_Messages.csv' in file:
        file_list.append({'can': file, 'gps': None})
print(file_list)

for i in range(len(file_list)):
    file_list[i]['gps'] = file_list[i]['can'][0:-17] + '_GPS_Messages.csv'

print(file_list)

'''




# find all files within a folder nested
# associate the CAN and GPS files
# put everything in an object at the end
import subprocess


def ils():
    process_files = subprocess.run(['ils'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
    files = process_files.stdout.split(sep='\n')[1:-1]
    return [f.strip() for f in files]


def icd(destination):
    return subprocess.run(['icd', destination],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)


def ipwd(destination):
    return subprocess.run(['ipwd', destination],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)


def findall_files(root):
    dir_queue = [root]
    files = []


    while len(dir_queue) != 0:
        print('---------')
        print('current queue dir: ', dir_queue)
        current_dir = dir_queue.pop()
        icd(current_dir)
        print('current directory is: ', current_dir)
        queue = ils()
        print('current file queue is: ', queue)

        for f in queue:
            print('current file tests on: ', f, ' and test gives f[0:2]: ', f[0:2], ' and f[-4:] is: ', f[-4:])
            if f[0:2] == 'C-':
                dir_queue.append(f[3:])
                print('appending dir queue; ', f)
            elif f[-4:] == '.csv':
                files.append(f)
                print('appending file; ', f)

        # dir_queue = dir_queue[1:]

    return files


root = '/iplant/home/sprinkjm/publishable-circles'
files = findall_files(root)
print(files)
