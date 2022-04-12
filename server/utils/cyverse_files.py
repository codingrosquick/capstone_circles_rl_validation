import asyncio
import subprocess


async def async_command_shell(command, verbose: bool = False):
    """Run command in subprocess (shell).
    source: https://fredrikaverpil.github.io/2017/06/20/async-and-await-with-subprocesses/
    """
    # set new event loop
    #old_loop = asyncio.get_event_loop()
    #loop = asyncio.new_event_loop()
    #asyncio.set_event_loop(loop)
    # Create subprocess
    # process = await asyncio.create_subprocess_shell(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, loop=loop)
    print('\n\ncommand', command, '\n\n')

    # NOTE: switched to use subprocess_exec as it is only for 1 command. Creating a shell doesn't seem to be fully supported and is overkill for here
    process = await asyncio.create_subprocess_exec(command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
    

    # close the loop
    #loop.close()
    #asyncio.set_event_loop(old_loop)

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
        await async_command_shell(f'iget -T {file_adress} {destination}', verbose=verbose)
        local_address = destination + '/' + file_adress.split('/')[-1]
        return local_address
    except Exception as e:
        raise Exception(f'Error while downloading file at:'
                        f'\n\tremote: {file_adress}'
                        f'\n\tto local address: {destination}`'
                        f'\n\tFailing on {e}')


def get_remote_object_name(remote_folder_path, name):
    if (remote_folder_path[-1] == '/') or (remote_folder_path[-1] == '\\'):
        return remote_folder_path + name
    else: 
        return remote_folder_path + '/' + name


async def iput(remote_folder_path, local_file_path, is_folder=False, verbose: bool = False):
    '''
    wrapper for iRODS iput command
    async command using asyncio library
    :param local_file_path: local address of the file|folder to upload
    :param remote_folder_path: remote address on CyVerse of the folder in which to put the file
    :return: remote address of the uploaded file
    '''
    try:
        if is_folder:
            folder_add = ''
        else:
            folder_add = '-r '
        name = local_file_path.split('/')[-1]
        remote_object_name = get_remote_object_name(remote_folder_path, name)

        print('\n\n', folder_add, '\n\n')
        print('\n\n', local_file_path, '\n\n')
        print('\n\n', remote_object_name, '\n\n')

        await async_command_shell(f'iput {folder_add}{local_file_path} {remote_folder_path}', verbose=verbose)
        
        return remote_object_name
    except Exception as e:
        raise Exception(f'Error while uploading file at:'
                        f'\n\tremote folder: {remote_folder_path}'
                        f'\n\tfrom local address: {local_file_path}'
                        f'\n\tFailing on {e}')


def ils():
    '''
    wrapper for iRODS ils command
    :return: list of files and folder in the current folder
    '''
    process_files = subprocess.run(['ils'],
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True)
    files = process_files.stdout.split(sep='\n')[1:-1]
    return [f.strip() for f in files]


def icd(destination):
    '''
    wrapper for iRODS icd command
    :param destination: destination to which go to
    :return: subprocess output
    '''
    return subprocess.run(['icd', destination],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)


def ipwd():
    '''
    wrapper for iRODS ipwd command
    :return: current directory on CyVerse
    '''
    pwd = subprocess.run(['ipwd'],
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          universal_newlines=True)
    out = pwd.stdout.strip().strip('\n')
    print('pwd output is:', out)
    return out


async def findall_files(root, verbose: bool = False):
    '''
    finds all files within the root directory and recursively below
    :param root: str, root file from which to begin the search
    :param verbose: bool, set to True to see fuller logs
    :return: List<str>
    '''
    dir_queue = [root]
    files = []

    while len(dir_queue) != 0:

        current_dir = dir_queue.pop()
        icd(current_dir)
        queue = ils()

        if verbose:
            print('---------')
            print('current queue dir: ', dir_queue)
            print('current directory is: ', current_dir)
            print('current file queue is: ', queue)

        for f in queue:
            if verbose:
                print('current file tests on: ', f, ' and test gives f[0:2]: ', f[0:2], ' and f[-4:] is: ', f[-4:])
            # avoid dashcams and bafiles folders, only use the libpanda ones -> reduces the number of files to scan for
            if f[0:2] == 'C-' and 'bagfiles' not in f and 'dashcams' not in f:
                dir_queue.append(f[3:])
                if verbose:
                    print('appending dir queue; ', f)
            elif f[-4:] == '.csv':
                # We also conserve the current folder to get the entire path to the file
                current_folder = ipwd()
                files.append(f'{current_folder}/{f}')
                if verbose:
                    print('appending file; ', f)

        if verbose:
            print('found ', len(files), ' files')

    return files
