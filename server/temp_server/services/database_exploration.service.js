const {runPyScript, runJupyterNotebook} = require('./run_py_script');


const callFileExploration = (query, opt1) => {
    try {
        /*
        // ADD THE FILE EXPLORATION SCRIPT OVER HERE:
        const scriptFileExploration = '';
        
        // KEEP PARAMETERS HERE AND BUBBLE UP THIS CALL WORKS:
        const parameters = {
        };
        */
        console.log('inside the service to call the notebook')

        //const resPy = runPyScript(scriptFileExploration, parameters);
        const jup = runJupyterNotebook('fileshare_exploration_create_db');
        // TODO: is there a need to delete this newly created jupyter notebook?
        return jup;
        
    } catch (e) {
        throw Error('Error while calling file exploration')
    }
};


const getTestData = (query, opt1) => {
    try {
        // var testData = `This is a test sample, ${opt1}`
        var dataToSendAndReceive = 'tinkie winkie';
        
        // TODO change towards relative paths -> why relative not recognized??
        const scriptName = 'test_python_script';
        const resPy = runPyScript(scriptName, dataToSendAndReceive);
        
    } catch (e) {
        // Log Errors
        throw Error('Error while calling python script from outside (TESTING PHASE)')
    }
};

exports.callFileExploration = callFileExploration;