const {spawn} = require('child_process');
// NOTE: see this link for more info: https://nodejs.org/api/child_process.html#child_processspawncommand-args-options


const runPyScript = (py_script_name, args) => {
    try {
        // TODO: use global arguments for those ones! -> adaptable to other places?
        const base_path = '/Users/noecarras/Documents/03_Berkeley_EECS/cours/Capstone_RL_validation/capstone_circles_rl_validation/server/temp_server/python_scripts/';
        const path = base_path + py_script_name + '.py';

        const python = spawn('python3', [
            path,
            ...args,
        ]);

        python.stderr.on('data', (err) => {
            console.log(`Error while running python script.\nFailed on: ${err}`);
            throw Error(err);
        });
        python.stdout.on('data', (res) => {
            console.log(res);
        });
        python.on('close', (code) => {
            console.log(`python script process close all stdio with code ${code}`);
            return code;
        });

        return python;
    } catch (e) {
        // Log Errors
        throw Error(`Error while running python script.\nFailed on: ${e}`);
    }
};

const runJupyterNotebook = async (notebook_name, args) => {
    try {
        console.log('inside the ipynb handler')

        const base_path = '/Users/noecarras/Documents/03_Berkeley_EECS/cours/Capstone_RL_validation/capstone_circles_rl_validation/server/temp_server/python_scripts/';
        const path = base_path + notebook_name + '.ipynb';
        console.log('path called is: ', path)

        //COMMAND TO RUN: jupyter nbconvert --to notebook --execute fileshare_exploration_create_db.ipynb(IE NAME)
        let arguments = [];
        if (args) {
            arguments = ['nbconvert', '--to', 'notebook', '--execute', path, ...args];
        } else {
            arguments = ['nbconvert', '--to', 'notebook', '--execute', path];
        }
        const jupyter = spawn('jupyter',  arguments);

        jupyter.stdout.on('data', (res) => {
            console.log(res);
        });
        jupyter.stderr.on('error', (err) => {
            console.log(`Error while running jupyer notebook.\nFailed on: ${err}`);
            throw Error(err);
        });
        jupyter.on('close', (code) => {
            console.log(`jupyter notebook process close all stdio with code ${code}`);
            return code;
        });        
        jupyter.on('exit', (code) => {
            console.log(`child process exited with code ${code}`);
        });

        return jupyter;
    } catch (e) {
        // Log Errors
        console.error(`Error while running Jupyter Notebook.\nFailed on: ${e}`);

        throw Error(`Error while running Jupyter Notebook.\nFailed on: ${e}`);
    }
};

exports.runPyScript = runPyScript;
exports.runJupyterNotebook = runJupyterNotebook;
