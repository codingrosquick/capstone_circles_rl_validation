
import subprocess


# TODO expand on these functionalities
# have a way to just say temp or long cache (temp is for files 1 by 1, long is for files to keep for next steps)
# also, needs to be able to remove file specifically 1 by 1

# NOTE: probably will need to use something in the JWT cookies to identify a session? Or by users? probably something to not erase everything





def init_cache(local_folder: str, kind: str):
    '''
    clears the cache if exists and initialise it
    :param local_folder: root folder for the analysis
    :param kind: subfolder to reach
    :return: temporary cache address
    
    note:   here, the local folder is /server/temp_cache/               (here only the temp folders are used)
            the kind folder is fileshare_exploration for instance       (if you are working with this)
    '''
    if local_folder != '':
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
    if kind in files:
        subprocess.run(['rm', '-r', '-f', kind],
                   stdout=subprocess.PIPE,
                   stderr=subprocess.PIPE,
                   universal_newlines=True)
    subprocess.run(['mkdir', 'temp_cache'],
               stdout=subprocess.PIPE,
               stderr=subprocess.PIPE,
               universal_newlines=True)
    temp_cache_address = f'{local_folder_absolute}/temp_cache'
    return temp_cache_address
