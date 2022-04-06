

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
