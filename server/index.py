from flask import Flask

app = Flask(__name__)


# imports to remove later on when refactoring into RCS architecture
from utils import init_cache, ipwd, iget, icd, ils, findall_files, read_metadata_from_exploration_name
from flask import jsonify

############################ GLOBAL VARIABLES ############################

cyverse_path_file_explorations = '/iplant/home/noecarras/resources_server/file_exploration'
cyverse_path_server_resources = '/iplant/home/noecarras/resources_server'

local_temp_folder = '/server/temp_cache'




############################ DEFINING ROUTES ############################

# ------------------------ file exploration ------------------------
## OK ## - Create a new file exploration
### - Get the available file explorations
### - Get an iterator over the files -> file explorer for Jonathan -> returns ack, then 1st file, then continues after each next, then ack of the end of the exploration
### ((())) Set the file exploration to use ////// NO -> done in the other parts to specify which to use
### - delete a file exploration

@app.route("/file_exploration", methods=['GET'])
def get_available_exploration():
    files_available = findall_files(cyverse_path_file_explorations, verbose=False)
    files_data = [read_metadata_from_exploration_name(filename) for filename in files_available]
    return jsonify(files_data)

@app.route("/file_exploration/", methods=['POST'])
def create_exploration():

    return None

@app.route("/file_exploration/", methods=['DELETE'])
def delete_one_exploration():
    return None

@app.route("/file_exploration/get_file_iterator", methods=['GET'])
def get_file_iterator():
    return None




####### DEFINING ERROR HANDLERS #######





