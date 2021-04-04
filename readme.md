# Family tree visualizer

@author: Bence Pipis, 2021

This repo contains my project that aims to enable users to visualize their family tree if their ancestors are in the database. The database contains people who were born in and near Tótkomlós, Hungary in the last three centuries, meaning roughly 70k individual. 
The app runs in command line. It can be started by clicking on the *run_family_tree* bat file or on the *Family_Tree* shortcut. Keep in mind that tha bat file works only if file is in the same folder as the .py file, while the shortcut can be copied and placed anywhere. For those with no python environment on the computer the *tree.exe* can be used from the working directory. Shortcut can be created if needed, although it is not advised to use exe when python environment is available, since the launch time is longer for exe.

## The structure of the project
1. All data were available in individual html files for each person so as a first step necessary information was parsed from them using BeautifulSoup. Function for parsing can be found in datacollection.py file. This function has been executed in data_collection.ipynb where data cleaning was also done. The output is the *final_cleaned.csv* that is used in the next step.
2. After creating a dataframe where each record contains details about people, a search algorhitm was written that identifies the earliest ancestor of a given person on father's side. Later this algorhitm is used to plot the family tree from the earliest ancestor. Currently available features are the following: look for earliest ancestor and print name and date of birth, and plotting the whole tree. These actions can be done by typing in the necessary commands when it is asked.

## Information on the visualization
The tree contains the parents of the searched person, the siblings of the father, the parents of the father, the siblings of the father, and so on, until the earliest ancestor. This was implemented due to visibility reasons as there are several people with more than 3 husbands/wives over their lives, which would make tree layout complicated. 
### Results of visualization
The code uses the pyvis package that returns the image as a html file saved on the computer and opens it in the default browswer. When a tree visualization happens for the first time, the code creates a *plots* folder in the working directory, where the results will be saved as *tree_{id}*. Later it just saves the new plots in the directory.

## Steps to take to plot someone's family tree
1. The user need to type in the first and last name of the desired person. It is important to use the letters of the English alphabet and use uppercase in the beginning of the names. The names in the database are in Slovakian, but regex method is used to handle special characters in Slovakian alphabet.
2. After typing in the name, the program returns a dataframe in a pretty format, containing all people in the database with the entered name. The user then needs to identify the person he/she is looking for by the data of birth (if available), and the name of the father and mother.
3. After identification the user is asked to copy the id of the person he/she has chosen and paste it to the field.
4. In the next step the user can chose from the avaiable features.
5. After plotting a person's tree the user can decide whether he/she'd like to continue with a new search or terminate the code.
In case inapropriate input is typed the code asks the user to enter it correctly until it happens. The code can be terminated at any time by the *ctrl + c* combination.

## Copyright information
The data collection was done by the local curch and published in the above mentioned html formats. My contribution is only the plot visualizer.
