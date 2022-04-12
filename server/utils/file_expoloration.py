from asyncio import subprocess
from datetime import datetime
from threading import local
from typing import List
from utils.cyverse_files import findall_files, iput
import pandas as pd


def read_metadata_from_exploration_name(filename: str):
    '''
    :param filename: name of the file onto which extract metadata
    :return: Dict object with those fields:
    {
        filename: <>,
        name: <>,
        created_on: <>,
        root: <>, 
    }
    NOTE: the root file has _ instead of /
    '''
    splitted_filename = filename.split('&')
    return {'filename': filename, 'name': splitted_filename[1], 'created_on': splitted_filename[2].split('=')[1], 'root': splitted_filename[3].split('=')[1]}


def can_gps_coupling(files: List[any]):
    '''
    links the CAN and GPS from same acquisitions
    :param files: array of file adresses
    :return: List<{'can': str, 'gps': str || None}>
    '''
    file_list = []
    for file in files:
        if '_CAN_Messages.csv' in file:
            file_list.append({'can': file, 'gps': None})

    for i in range(len(file_list)):
        file_gps = file_list[i]['can'][0:-17] + '_GPS_Messages.csv'
        if file_gps in files:
            file_list[i]['gps'] = file_gps

    return file_list


def coupled_files_file_namer(name: str, root: str):
    root_mod = root.replace("/", "_").replace("'", "")
    if root_mod[-4:] == '.csv':
        root_mod = root_mod[:-4]
    name_mod = name.replace("'", "")

    return f'file_exploration&{name_mod}&create_on={str(datetime.now()).replace(" ", "_")}&root={root_mod}.csv'


async def create_fileshare_exploration(root: str, exploration_name: str, remote_exploration_folder: str, local_upload_folder_address: str, verbose: bool = False):
    '''
    :param root: root of the exploration to consider (on CyVerse)
    :param exploration_name: name to give to the exploration
    :param remote_exploration_folder: remote address of the folder holding the files for explorations
    :param local_upload_folder_address: local folder address for holding the exploration to upload
    :param verbose: set to True to have more extensive logs
    :return: the address of the newly created file on CyVerse
    '''
    # explores the folders to find CSV pairs of CAN & GPS files
    all_files = await findall_files(root, verbose)

    coupled_files = can_gps_coupling(all_files)

    # save the csv file
    output_filename = coupled_files_file_namer(exploration_name, root)
    local_file_path = f'{local_upload_folder_address}/{output_filename}'
    print(local_file_path)

    # subprocess.run(['touch', local_file_path],
    #                 stdout=subprocess.PIPE,
    #                 stderr=subprocess.PIPE,
    #                 universal_newlines=True)

    df = pd.DataFrame(data={'Files': coupled_files})
    df.to_csv(path_or_buf=local_file_path)
    if verbose:
        print('exploration logged as: ', output_filename)
    
    # uploads to CyVerse, to remote_exploration_address
    remote_name = await iput(remote_folder_path=remote_exploration_folder, local_file_path=local_file_path)

    # init the local cache
    # TODO

    # returns the address on CyVerse, returns remote_exploration_address (or name?)
    return remote_name
