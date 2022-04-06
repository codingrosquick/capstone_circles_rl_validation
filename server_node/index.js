const createError = require('http-errors');
const path = require('path');
const logger = require('morgan');
const express = require('express');
const {spawn} = require('child_process');

// Defining the routers
const DatabaseExplorationRouter = require('./temp_server/routes/database_exploration.route')

// Defining express application
const app = express();
const port = 8000;

// Middlewares
app.use(logger('dev'));
app.use(express.json());
app.use(express.urlencoded({ extended: false }));
app.use(express.static(path.join(__dirname, 'public')));

// use the routers here
app.use('/db_exploration', DatabaseExplorationRouter);

app.listen(port, () => {            //server starts listening for any attempts from a client to connect at port: {port}
    console.log(`Now listening on port ${port}`); 
});
