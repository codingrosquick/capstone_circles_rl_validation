const {spawn} = require('child_process');

exports.getTestData = function (query, opt1) {

    try {
        // var testData = `This is a test sample, ${opt1}`
        var dataToSend;
        // TODO change towards relative paths -> why relative not recognized??
        const python = spawn('python3', ['/Users/noecarras/Documents/03_Berkeley_EECS/cours/Capstone_RL_validation/capstone_circles_rl_validation/server/temp_server/python_scripts/test_python_script.py']);
        python.stderr.on('data', (data) => { console.log(`Error while fetching python script.\nFailed on: ${data}`) });
        python.stdout.on('data', (data) => {
            console.log('Pipe data from python script ...');
            dataToSend = data.toString();
        });
        python.on('close', (code) => {
            console.log(`child process close all stdio with code ${code}`);
            console.log(`data to send is ${dataToSend}`);
            // send data to the controller
            return dataToSend;
        });
    } catch (e) {
        // Log Errors
        throw Error('Error while fetching testData')
    }
}