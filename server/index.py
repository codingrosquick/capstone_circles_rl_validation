from asyncio.log import logger
from flask import Flask, request

app = Flask(__name__)


# imports to remove later on when refactoring into RCS architecture
from utils import init_cache, ipwd, iget, icd, ils, findall_files, read_metadata_from_exploration_name, create_fileshare_exploration
from flask import jsonify


############################ GLOBAL VARIABLES ############################

cyverse_path_file_explorations = '/iplant/home/noecarras/resources_server/file_exploration'
cyverse_path_server_resources = '/iplant/home/noecarras/resources_server'

local_temp_folder = '/Users/noecarras/Documents/03_Berkeley_EECS/cours/Capstone_RL_validation/capstone_circles_rl_validation/server/temp_cache'
# TODO: change to work within Docker
local_long_cache_address = '/Users/noecarras/Documents/03_Berkeley_EECS/cours/Capstone_RL_validation/capstone_circles_rl_validation/server/long_cache'


############################ DEFINING ROUTES ############################

# ------------------------ file exploration ------------------------
## OK ## - Create a new file exploration
### - Get the available file explorations
### - delete a file exploration --> be very careful and try it on personal workspace -> only allow to remove files and not folders (test for spotting such flags?)
### - get the current running explorations --> find a way for this one to make it work

@app.route("/file_exploration", methods=['GET'])
def get_available_exploration():
    '''
    :return: List of filenames for past file explorations + associated metadata, in a JSON object
    '''
    try:
        files_available = findall_files(cyverse_path_file_explorations, verbose=False)
        files_data = [read_metadata_from_exploration_name(filename) for filename in files_available]
        return jsonify(files_data)
    except Exception as e:
        raise Exception(f'Error while getting fileshare exploration list'
                f'\n\tFailing on {e}')

@app.route("/file_exploration/", methods=['POST'])
async def create_exploration():
    '''
    request arguments:
        query params:
            - 'name': name to give to the file exploration
            - 'root': root folder on CyVerse
    '''
    try: 
        #legacy to remove, test for arguments to pass       
        #exploration_name = 'test-small-exploration'
        #root = '/iplant/home/sprinkjm/publishable-circles/2T3W1RFVXKW033343/libpanda/2021_08_02'

        arguments = request.args.to_dict()

        logger.info(arguments)

        uploaded_file = await create_fileshare_exploration(
            arguments['root'],
            arguments['name'],
            remote_exploration_folder=cyverse_path_file_explorations,
            local_upload_folder_address=local_long_cache_address,
            verbose=True)

        return jsonify({'remote_filename': uploaded_file})

    except Exception as e:
        raise Exception(f'Error while creating a new fileshare exploration'
                        f'\n\tFailing on {e}')

@app.route("/file_exploration/", methods=['DELETE'])
def delete_one_exploration():

    return None

@app.route("/file_exploration/get_file_iterator", methods=['GET'])
def get_file_iterator():

    return None




####### DEFINING ERROR HANDLERS #######





