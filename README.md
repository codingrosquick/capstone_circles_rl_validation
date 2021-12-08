# capstone_circles_rl_validation

## Useful links
Trello board: https://trello.com/b/SAKirZem/todolist-capstone-rl-validation

Miro drawing board: https://miro.com/app/board/o9J_lpOkcqc=/

Github codebase: https://github.com/codingrosquick/capstone_circles_rl_validation

## Code structure

The code is split between different logical parts. For now, only the database exploration and analysis is available here. Soon, there will be a new subjects like metrics, agregation, or ROS playback added to this repository.

## How to use this code

This section is temporary as this will change when the conteneurisationthrough docker will be completed.

### Launch a database analysis

This is done with the content of the notebook *database_exploration/analyse_and_create_db.ipynb*.

To perform the analysis, create a JSON configuration file, as described in the function *explore_and_analyse_bdd*

Then, pass this configuration file as an argument of the *config_path_full* variable at the bottom of the notebook.

Finally, perform the analysis by launching the notebook.

**NOTE:** The folder *database_exploration/results_permanent* has some file exploration CSVs ready, like the full exploration of CIRCLES' database.

### Serve preprocessed files for events

Use, in *database_exploration/events_api.ipynb* the class **FileServer()** to serve files using the **next()** method.

You will have to define the base CSV for the analysis used (check the name for informations about the different parameters used), as well as the preprocessing behavior of the File Server (namely, select the time before and after the event that you wish to keep).

