//var DatabaseExplorationService = require('../services/database_exploration.service')
const {callFileExploration} = require('../services/database_exploration.service')


const getTestData = async (req, res, next) => {
    // Validate request parameters, queries using express-validator
    var opt1 = req.params.opt1 ? req.params.opt1 : 1;
    try {
        var testData = await callFileExploration({}, opt1)
        return res.status(200).json({ status: 200, data: testData, message: "Succesfully testData Retrieved" });
    } catch (e) {
        return res.status(400).json({ status: 400, message: e.message });
    }
}

exports.getTestData = getTestData;