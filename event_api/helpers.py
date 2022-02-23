import ast
import asyncio
import json
import subprocess

import numpy as np
import pandas as pd


async def async_command_shell(command, verbose: bool = False):
    """Run command in subprocess (shell).
    source: https://fredrikaverpil.github.io/2017/06/20/async-and-await-with-subprocesses/
    """
    # Create subprocess
    process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    # Status
    if verbose:
        print("Started:", command, "(pid = " + str(process.pid) + ")", flush=True)
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Output
    if process.returncode == 0:
        if verbose:
            print("Done:", command, "(pid = " + str(process.pid) + ")", flush=True)
        return stdout.decode().strip()
    else:
        if verbose:
            print("Failed:", command, "(pid = " + str(process.pid) + ")", flush=True)
        raise Exception(stderr.decode().strip())


async def iget(file_adress, destination, verbose: bool = False):
    '''
    wrapper for iRODS iget command
    async command using asyncio library
    :param file_adress: address on CyVerse fileshare
    :param destination: address to download to on the local computer
    :return: local address of the file
    '''
    try:
        print(f'Beginning the download of {file_adress}')
        await async_command_shell(f'iget -T {file_adress} {destination}', verbose=verbose)
        local_address = destination + '/' + file_adress.split('/')[-1]
        print(f'Download was successful')
        return local_address
    except Exception as e:
        raise Exception(f'Error while downloading file at:'
                        f'\n\tremote: {file_adress}'
                        f'\n\tto local address: {destination}`'
                        f'\n\tFailing on {e}')


def init_cache(local_folder):
    '''
    clears the cache if exists and initialise it
    :param local_folder: root folder for the analysis
    :return: temporary cache address
    '''
    subprocess.run(['cd', local_folder],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
    local_folder_absolute = subprocess.run(['pwd'],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True).stdout.strip()
    files = subprocess.run(['ls'],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
    files = files.stdout.split(sep='\n')
    if 'temp_cache' in files:
        subprocess.run(['rm', '-r', '-f', 'temp_cache'],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
    subprocess.run(['mkdir', 'temp_cache'],
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               universal_newlines=True)
    temp_cache_address = f'{local_folder_absolute}/temp_cache'
    print('Cache cleared')
    return temp_cache_address


def find_ts_time_close(ts_time, event_time):
    """
    Finds the available time point of a time series closest to a given point in time
    :param ts_time: Time Series time list
    :param event_time: Time at which we want the value
    :return: the time point available for the time series
    """
    min_index = np.argmin([np.abs(time - event_time) for time in ts_time])
    return ts_time[min_index]

def perform_cut(local_address, previous_cut_time, next_cut_time, event_time):
    """
    cuts a CAN/GPS time series before and after the event
    :param local_address: local address of the file to cut
    :param previous_cut_time: float, seconds before the event to keep
    :param next_cut_time: float, seconds after the event to keep
    :param event_time: float
    :return: Path of the cutted file
    """
    df_can = pd.read_csv(local_address)
    filename = local_address.split('/')[-1]
    folders = local_address.split('/')[:-1]
    foldername = ''
    for folder in folders:
        foldername += folder
    new_filename = 'cutted__' + filename

    time_beginning_cut = find_ts_time_close(df_can['Time'], event_time - previous_cut_time)
    time_ending_cut = find_ts_time_close(df_can['Time'], event_time + next_cut_time)
    cutted_df = df_can.loc[(df_can['Time'] >= time_beginning_cut) & (df_can['Time'] <= time_ending_cut)]
    cutted_df.to_csv(path_or_buf=f'results/{new_filename}')
    new_path = foldername + '/' + new_filename
    return new_path


class FileServer:
    """
    Class handling file download and caching, csv filtering and time cuts to be sent to CAN -> ROS playback
    """
    # attributes
    data = None
    current_remote_adresses = None
    current_event = None
    can_local_address = None
    gps_local_address = None
    index = 0
    max_index = None
    previous_cut_time = None
    next_cut_time = None
    local_root_folder = None

    # methods
    def __init__(self, analysis_path, local_root_folder):
        """
        Reads from a CSV analysis file
        :param analysis_path: string of the path of the CSV taken from the analysis
        :param local_root_folder: Local root for the download folder
        """
        self.local_root_folder = local_root_folder
        self.data = pd.read_csv(analysis_path)
        self.max_index = len(self.data)

    def filter(self, cc_state: [int] = None, speed: {str: int} = None, vin: [str] = None, date: {str: str} = None, event_type: [str] = None):
        """
        filter the rows based on those criteria
        :param cc_state: list of acceptable controller state values
        :param speed: {min: int min_speed in km/h, max: int max_speed in km/h}
        :param vin: list of acceptable vehicle identification numbers
        :param date: {beg: date, end: date}, with date as strings, formatted as YYYY-MM-DD-HH-MM-SS
        :param event_type: list of acceptable event types. possible event types are:
            - car_crossing
            - <more to come in the future>
        :return: updates self.data to only keep the desirable instances
        """
        if event_type is not None:
            self.data = self.data.loc[self.data['event_type'] in event_type]
        if vin is not None:
            self.data = self.data.loc[self.data['vin'] in vin]
        if cc_state is not None:
            self.data = self.data.loc[self.data['event_cc_state'] in cc_state]
        if speed is not None:
            self.data = self.data.loc[(self.data['event_speeds'] >= speed['min'])
                                  & (self.data['event_speeds'] >= speed['min'])]
        if date is not None:
            self.data = self.data.loc[(self.data['date'] >= date['min'])
                                  & (self.data['date'] >= date['min'])]
        self.max_index = len(self.data)

    def __str__(self):
        if self.max_index is None:
            return f'FileServer filtering is not finished'
        else:
            return f'file server with {self.max_index} files ready to be served, current index is: {self.index}'

    async def next(self, ignore_gps_file: bool = False):
        """
        clears cache & downloads the next couple of files
        :param: ignore_gps_file: set to True to avoid downloading the GPS file
        :return: - object with paths to the downloaded CAN and GPS file
        {'can': str, 'gps': str, 'remote_addresses': {'can': str, 'gps': str}}
                 - if the maximum index is reached, returns an exception as:
        Exception('max_index')
        """
        try:
            print(f'serving and preprocessing file, number {self.index} out of {self.max_index}')
            if self.index < self.max_index:
                cache = init_cache(self.local_root_folder)
                self.current_event = self.data.iloc[self.index]
                self.current_remote_adresses = ast.literal_eval(self.current_event['remote_addresses'])

                self.can_local_address = await iget(self.current_remote_adresses['can'], cache)
                if ignore_gps_file:
                    self.gps_local_address = None
                else:
                    self.gps_local_address = await iget(self.current_remote_adresses['gps'], cache)

                self.index += 1

                local_addresses = self.cut_can_file()
                print(f'Download and preprocessing of {local_addresses} was successful')
                return local_addresses
            else:
                raise Exception('max_index')

        except Exception as e:
            raise Exception(f'Downloading next file failed on {e}')

    def set_cut(self, previous, next):
        """
        sets the values of the parameters of the cut for the csv CAN/GPS files
        :param previous: number of seconds kept before the event
        :param next: number of seconds kept after the event
        :return: void. updates the attributes of the file server
        """
        self.previous_cut_time = previous
        self.next_cut_time = next

    def cut_can_file(self):
        """
        cut the current file according to the cutting parameters defined
        """
        event_time = self.current_event['event_time']
        can_new_path = perform_cut(self.can_local_address, self.previous_cut_time, self.next_cut_time, event_time)
        gps_new_path = None
        if self.gps_local_address is not None:
            gps_new_path = perform_cut(self.can_local_address, self.previous_cut_time, self.next_cut_time, event_time)
        return {
            'can': can_new_path,
            'gps': gps_new_path,
        }

    def clear(self):
        init_cache(self.local_root_folder)
        print('Cache cleared')

