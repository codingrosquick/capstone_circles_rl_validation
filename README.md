# capstone_circles_rl_validation


## Data exploration

### TODO

1. finir l'analyse fichiers (trouver bons params, tester sur plein de fichiers, pbs de l'échantillonage, utiliser des):
   1. --- résoudre pb des samplings ---
   2. --- graphical see the test effects ---
   3. --- tester sur bcp de fichiers ---
   4. --- cleaner code ---
   5. --- modularize, verbose activation? ---
2. messages slack: questions et assumptions, pousser le github, et prévenir pour demain, diapo update (assumptions, results and visuals)
   1. --- questions --- 
   2. slides
3. regarder pour avoir du CSV: création fichier (tables) + remplissage + lecture, des entrées analysées
   1. --- test -> OK ---
   2. --- intégrer au code ---
   3. --- travail sur les metadata à utiliser et storer depuis le filename ---
4. File crawler avec toutes les locations des acquisitions
   1. --- find all the places where there is useful acquisitions (cf links given) ---
   2. --- gestion load delete d'un cache --- 
      -> tester si fonctionne proprement:
      1. DL depuis IRODS
         1. TODO? iinit pour initialiser: 2 cas (non prep, déjà prep) faire python qui réagit au bash
         2. ils pour vérifier l'état du login
         3. ligne de DL depuis un repertoire d'adresse
         -> mettre dans le même fichier de configuration python
5. Ajout au CSV
   1. vérifier que fonctionne tout bien
   2. --- ajout des metadata? ---
6. API d'acces depuis le CSV
   1. load the CSV
   2. retrieve: which parameters?
   3. ajouter les fonctions pour print, et faire avec plotly et non matplotlib
7. tests de l'API avec un CSV généré propre et petit? (checker quelle lib de test?)
8. Define the entry points for the different algorithms to use (Dockerise & make the entrypoints functions)
   1. Find and define all the needed entrypoints, parameters etc
   2. Make them
   3. Dockerise that
9. Nouveaux visuels Miro pour documenter le fonctionnement de tout ça proprement, avec les différents niveaux des BDD et fichiers générés


### code cleaning
- passer tous les thresholds dans un objet crossing_analysis_parameter
- corriger orthographe threshold
- modularize -> non pas vraiment possible avec streymread TODO: ask Rahul if that's possible?
- document everything
- clean comments and verbose logging
- checker pour utiliser un formattage de documentation à la Google
