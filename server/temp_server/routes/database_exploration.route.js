var express = require('express');
var router = express.Router();

var DatabaseExplorationController = require('../controllers/database_exploration.controller')

router.get('/', DatabaseExplorationController.getTestData)

module.exports = router;