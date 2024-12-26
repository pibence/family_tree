import pandas as pd
from pyvis.network import Network
import numpy as np
import re
from tabulate import tabulate
import os

# Reading csv containing data
df = pd.read_csv('final_cleaned.csv', sep = ';', dtype = "string")


# Creating new dataframe for marriages to reduce duplication

# Initializing dadaframe
marriages = pd.DataFrame()

for i in range(1,7):
    # iterating through the partner id columns after filtering
    # for males and for existing partner id-s and appending 
    # the filtered df to the new df.
    
    new = df[(df["sex"] == "male") & (pd.isna(df[f"partner_id{i}"]) == False)][["id", f"partner_id{i}"]]
    new.columns = ["husband_id", "wife_id"]
    marriages =  pd.concat([marriages, new])

# Creating new df without parnter data
df = df[['id', 'first_name_1', 'first_name_2', 'last_name', 'birth_date', 'birth_place', 'death_date', 
        'death_place', 'father_id' , 'mother_id', 'sex']]



def lookup(df:pd.DataFrame, firstname:str, lastname:str) -> pd.DataFrame:
    """This function returns a dataframe containing the people called 
    as the given name. It also given information about the parents' name
    and birth date and id. The aim of this function is to help identify
    the desired person by other attributes and locate its id for further
    search purposes."""
    
    # Initializing dataframe
    
    # Transforming names into regex to find similar characters as well.

    # Creating dictionary of special characters and their pairs in english alphabet.
    #langs = 'ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž'
    langs_eng = 'AaCcDdEeIiNnOoRrSsTtUuYyZz'
    lang_dic = {'A' : '[A,Á]', 'C' : '[C,Č]', 'D' : '[D, Ď]', 'E' : '[E,É,Ě]', 'I' : '[I,Í]', 'N' : '[N,Ň]', 'O': '[O,Ó]', 'R' : '[R,Ř]' ,'S' : '[S,š]', 'T': '[T,Ť]', 'U' : '[U,Ú,Ů]', 'Y': '[Y,Ý]', 'Z': '[Z,Ž]'}
    lang_dic.update({k.lower() : v.lower() for (k,v) in lang_dic.items()})

    #Creating regex compatible first and last names
    firstname_reg = str()
    lastname_reg = str()

    for i in firstname:
        if i in langs_eng:
            firstname_reg += lang_dic[i]
        else:
            firstname_reg += i

    for i in lastname:
        if i in langs_eng:
            lastname_reg += lang_dic[i]
        else:
            lastname_reg += i
                

    # Getting list of id-s with matching names based on regex similar chars
    id_list = list(df[(df["first_name_1"].str.contains(firstname_reg, regex = True, na = False)) & (df["last_name"].str.contains(lastname_reg, regex = True, na = False))]["id"])

    if len(id_list) == 0:
        raise ValueError("No person in the database with the given name.")
    else:
        d = {
            "id": [],
            "first_name_1": [],
            "first_name_2": [],
            "last_name": [],
            "birth_date":[],
            "father_name":[],
            "mother_name" :[],
        }
        for i in id_list:
            # Iterating through the id-s and collect data about the person
            
            
            d["id"].append(i)
            d["first_name_1"].append(df[(df["id"] == i)].iloc[0, 1])
            d["first_name_2"].append(df[(df["id"] == i)].iloc[0, 2])
            d["last_name"].append(df[(df["id"] == i)].iloc[0, 3])
            d["birth_date"].append(df[(df["id"] == i)].iloc[0, 4])
            
            father_id = df[(df["id"] == i)].iloc[0, 8]                     
            if not pd.isnull(father_id):
                d["father_name"].append(df[df["id"] == father_id].iloc[0,1]  + ' ' + df[df["id"] == father_id].iloc[0,3])
            else:
                d["father_name"].append(None)
            
            mother_id = df[(df["id"] == i)].iloc[0, 9]                     
            if not pd.isnull(mother_id):
                d["mother_name"].append(df[df["id"] == mother_id].iloc[0,1]  + ' ' + df[df["id"] == mother_id].iloc[0,3])
            else:
                d["mother_name"].append(None)
                
                # Appending dictionary to dataframe 

        people = pd.DataFrame(d)
            
        # Returning df with a given order of columns
        return people[["id", "first_name_1", "first_name_2", "last_name", "birth_date", "father_name", "mother_name"]]
   

def lookup_earliest(df:pd.DataFrame, id:str) -> str:
    """This function returns the name and birth year of the earliest ancestor"""

    if len(df[df["id"] == id]) == 0:
        raise ValueError("Please add an existing id!")
    else:
        father_id = df[df["id"] == id].iloc[0,8]
        
        if pd.isnull(father_id):
            return f"The eldest ancestor is: {df[df['id'] == id].iloc[0,1]} {df[df['id'] == id].iloc[0,3]}. He/She was born in {df[df['id'] == id].iloc[0, 4]}." 
        else:
            return lookup_earliest(df, father_id)    


def earliest_id(df:pd.DataFrame, id:str) -> str:
    "This function returns the id of the earliest ancestor."
    father_id = df[df["id"] == id].iloc[0,8]
    
    if pd.isnull(father_id):
        return df[df["id"] == id]["id"].tolist()[0]
    else:
        return earliest_id(df, father_id)


def mother_list(df:pd.DataFrame, id:str, result = None) -> list:
    """This function returns the list of mothers' id who are in 
    the selected person's family tree. The goal of this function 
    is to select the wives from every father's partners who belong
    to the selected tree. The logic is the same as in the earliest_id
    function."""

    if result == None:
        result = []
    
    father_id = df[df["id"] == id].iloc[0,8]
    if not pd.isnull(df[df["id"] == id].iloc[0,9]):
        result.append(df[df["id"] == id].iloc[0,9])
    
    if pd.isnull(father_id):
        return result[::-1]
    else:
        return mother_list(df, father_id, result)


def father_list(df:pd.DataFrame, id:str, result = None) -> list:
    """This function returns the list of fathers' id who are in 
    the selected person's family tree. The logic is the same as
    in the earliest_id function."""

    if result == None:
        result = []
    
    father_id = df[df["id"] == id].iloc[0,8]
    if not pd.isnull(father_id):
        result.append(father_id)
    
    if pd.isnull(father_id):
        return result[::-1]
    else:
        return father_list(df, father_id, result)


def namestr(df:pd.DataFrame, id_:str, sep=" ") -> str:
    """This function creates a string containing the name of the person.
    It selects the name attributes of a given id and pastes together in 
    firstname1, firstname2 (if exists), last name order."""
    
    # Creating list from the names
    name_list = df[df['id'] == id_][['first_name_1', 'first_name_2', 'last_name']].values.flatten()
     
    st = ""
    for n in name_list:
        if not pd.isna(n):
            st += n
            if n != name_list[-1]:
                st += sep
    return st


def get_wife_id(df:pd.DataFrame, husband_id:str, orig_id:str) -> str:
    "This function returns the wife id to a husband id."
    #orig_id: the id of the person whose tree is being built.
    
    mothers = mother_list(df, orig_id)

    wives = marriages[marriages["husband_id"] == husband_id]
    if len(wives[wives["wife_id"].isin(mothers)]) == 0:
        return None
    else:
        return wives[wives["wife_id"].isin(mothers)]["wife_id"].tolist()[0]


def get_birth_date(df:pd.DataFrame, id:str)->str:
    """This function returns the date of birth of a person by id.
    If there is no info, it returns an empthy string."""

    bd = df[df["id"] == id]["birth_date"].tolist()[0]
    
    if pd.isnull(bd):
        return ""
    else: 
        return bd


def get_death_date(df:pd.DataFrame, id:str) -> str:
    """This function returns the date of death of a person by id.
    If there is no info, it returns an empthy string."""
    
    dd = df[df["id"] == id]["death_date"].tolist()[0]

    if pd.isnull(dd):
        return "" 
    else:
        return dd 

def get_birth_place(df:pd.DataFrame, id:str) -> str:
    """
    gets the birth place for a given id
    """

    birth_place = df[df["id"] == id]["birth_place"].tolist()[0]

    if pd.isnull(birth_place):
        return "" 
    else:
        return birth_place 

def get_death_place(df:pd.DataFrame, id:str) -> str:
    """
    gets the birth place for a given id
    """

    death_place = df[df["id"] == id]["death_place"].tolist()[0]

    if pd.isnull(death_place):
        return "" 
    else:
        return death_place 


def nodecolor(df:pd.DataFrame, act_id:str, orig_id:str) -> str:
    """This function returns a color based on the person's details.
    Pink, if female, blue, if male, and orange if the person is the same
    whose tree is being built for better visualization."""

    gender = df[df['id'] == act_id]['sex'].tolist()[0]
    if act_id == orig_id:
        return 'orange'
    elif pd.isna(gender):
        return 'grey'
    elif gender == "male":
        return 'lightblue'
    else:
        return 'pink'
    
def generate_node_label(df:pd.DataFrame, id:str):
    """
    Generates a node label for each id including the name, the birth and death date and the 
    birth and death places.
    """
    birth_date = get_birth_date(df, id)
    death_date = get_death_date(df, id)
    birth_place = get_birth_place(df, id)
    death_place = get_death_place(df, id)

    label = f"{namestr(df, id)}\n{birth_date}"
    if birth_place:
        label += f"\n({birth_place})"
    label += f" -\n{death_date}"
    if death_place:
        label += f"\n({death_place})"
    
    return label

def tree_create(df:pd.DataFrame, id:str):
    """"This function takes the id of a person and returns the whole family tree on 
    father's side. The shown attributes of a person in the tree are the full name, birth
    date and date of death. The men's boxes are blue while the female's are pink."""
    
    # Creating list of fathers, mothers ids
    fathers = father_list(df, id)
    
    # ID of the earliest ancestor
    eid = earliest_id(df, id)

    # Initializing network object and adding earliest ancestor
    net = Network(layout = 'hieararchical', height = 1000, width = 2000)
    net.add_node(eid, label = generate_node_label(df, eid) , level = 1, shape ='box', color = "lightblue")

    # Iterating through the fathers list and adding the wife, marriage nodes first.
    # Adding edges between them later and finally adding children as well for nodes
    # and edges for them The level of a node is also set based on the iteration number. 
    for i, father in enumerate(fathers):
        # Adding earliest ancestor node.
        net.add_node(f"m{i+1}", label = " ", level = 2*i+1, shape = 'dot', size = 3, color = "black")
        
        # Adding wife node and edge only in case id is known.
        wife_id = get_wife_id(df,father, id)
        if not pd.isnull(wife_id):
            net.add_node(wife_id, label = generate_node_label(df, wife_id) , level = 2*i+1, shape ='box', color = "pink")
            net.add_edge(wife_id, f"m{i+1}", color = "black", size = 2)
        
        # Adding child collector node and edges between already added nodes. 
        net.add_node(f"c{i+1}", label = " ", level = 2*i+2, shape = 'dot', size = 3, color = "black")
        net.add_edge(father, f"m{i+1}", color = "black")
        net.add_edge(f"m{i+1}", f"c{i+1}")

        # Creating children list and omitting the one that will continue the tree in the 
        # next level. Goal is to add him at the end so it will be placed on the left of
        # the children and adding wife in next iteration won't mess up the layout. 
        # The creation has an if-else case to handle missing mother id-s. 
        if not pd.isnull(wife_id):
            children = df[(df["father_id"] == father) & (df["mother_id"] == wife_id)]
        else:
            children = df[(df["father_id"] == father)]

        # Adding all children's nodes except the next father. Edges to the previous child
        # collector node are also added.
        for child_id in children[~children["id"].isin(fathers)]["id"]:
            net.add_node(child_id, label = generate_node_label(df, child_id) , level = 2*i+3, shape ='box', color = nodecolor(df, child_id, id))

            net.add_edge(child_id, f"c{i+1}", color = "black")
        
        # Adding next iteration's father to the left of his siblings in case
        # the loop is not in the final iretarion. In the final iteration the
        # people have no children by definiton. Edge is also added to the
        # previous child collector node.
        if len(children[children["id"].isin(fathers)]) != 0:
            f = children[children["id"].isin(fathers)]["id"].tolist()[0]
            net.add_node(f, label = generate_node_label(df, f) , level = 2*i+3, shape ='box', color = "lightblue")
            net.add_edge(f, f"c{i+1}", color = "black")


    # Creating new folder for plots if it hasn't existed yet. 
    path = os.path.join(os.getcwd(), "plots")
    if not os.path.exists(path):
        os.mkdir(path)
    name_to_file = namestr(df, id, sep="_")
    # Showing tree and saving it to plots folder.
    return net.show(f"{path}/tree_{name_to_file}_{id}.html")

# Communicating with the user
# The idea is to ask questions as inputs and 1) check the inputs first
# 2a) execute the desired step 2b) ask for new input if the first was 
# not correct. 

active = True 
while active:

    nvalid = True
    while nvalid:
        firstname = input("\nPlease enter the first name of the person you are looking for! ")
        lastname = input("Please enter the last name of the person you are looking for! ")

        try:
            print(f"{tabulate(lookup(df, firstname, lastname).fillna('-'), headers = 'keys', tablefmt = 'fancy_grid')}\n")
            nvalid = False
        except ValueError:
            print("Please add a valid name!")
    
    person_id = input("Please enter the id of the person you are looking for! \nThe ids are in the table above, you need to copy and insert it! ")

    nvalid2 = True
    while nvalid2:

        try:
            lookup_earliest(df, person_id)
            nvalid2 = False
        except ValueError:
            person_id = input("Please add a valid id! ")        

    decision = input("\nwould you like to find the earliest ancestor or plot the whole tree? \nType tree ancestor for ancestor finding and tree for visualization! ")

    nvalid3 = True
    while nvalid3:
   
        if decision == "ancestor":
            print(lookup_earliest(df, person_id))
            nvalid3 = False
            
            decision2 = input("Would like to plot the family tree(yes/no)? ")

            nvalid4 = True
            while nvalid4:

                if decision2 == "yes":
                    tree_create(df, person_id)
                    nvalid4 = False

                    decision3 = input("Would like to continue with a new person(yes/no)? ")

                    nvalid5 = True
                    while nvalid5:

                        if decision3 == "yes":
                            nvalid5 = False
                            pass
                        elif decision3 == "no":
                            nvalid5 = False
                            active = False
                        else:
                            decision3 = input("Please enter yes or no! ")
            
                elif decision2 == "no":
                    nvalid4 = False
                    decision4 = input("Would like to continue with a new person(yes/no)? ")

                    nvalid6 = True
                    while nvalid6:
            
                        if decision4 == "yes":
                            nvalid6 = False
                            pass
                        elif decision4 == "no":
                            nvalid6 = False
                            active = False
                        else:
                            decision4 = input("Please enter yes or no! ")       
                
                else:
                    decision2 = input("Plese enter yes or no! ")
                    
        elif decision == "tree":
            tree_create(df, person_id)
            nvalid3 = False

            decision5 = input("Would like to continue with a new person(yes/no)? ")

            nvalid7 = True
            while nvalid7:

                if decision5 == "yes":
                    nvalid7 = False
                    pass
                elif decision5 == "no":
                    nvalid7 = False
                    active = False
                else:
                    decision5 = input("Please enter yes or no! ")
        else:
            decision = input("Please enter a valid option (ancestor/tree)! ")
            pass




