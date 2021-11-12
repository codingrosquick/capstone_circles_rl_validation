# capstone_circles_rl_validation


## Data exploration

### TODO
1. File crawler from CyVerse
   1. -> seems complex to do with IRODS
   2. find all the files !!! autiomate dumb with a list to look at for IRODS simple
   -> (check with the informations given to know all the places manually and handle them properly)
2. File reader -> strym -> way to extract useful CAN data + timing 
   1. -> find on the slides the different streams of data available from CAN, GPS and Bagfiles
   2. Mathematical relation to implement
   3. -> find a way to check this over large acquisitions really fast
3. Create DB SQL to store the indexes 
   1. -> where should I do this? In CyVerse??? --> check if this exists because potentially!
   2. proto thing: create a CSV file and populate it // if there is no SQL abilities // check before on CyVerse

### Pb des SQL DB?
Having the SQL DB if possible -> if not, use a CSV -> no SQL on CyVerse
SQL tables on CyVerse check if there is an application for this ?

(aussi, voir avec Jessica pour utiliser le git)

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
   1. find all the places where there is useful acquisitions (cf links given)
      -> gros fichier/dico avec ça? faire à la main?
   2. gestion load delete d'un cache
   3. DL depuis IRODS
5. API d'acces depuis le CSV
6. tests de l'API avec un CSV généré propre et petit? (checker quelle lib de test?)


### code cleaning
- passer tous les thresholds dans un crossing_analysis_parameter
- corriger orthographe threshold
- modularize
- make it launchable--- commit on Git
- document everything
- type useful things
