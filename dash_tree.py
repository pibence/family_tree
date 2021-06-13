from typing import List
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import dash_daq as daq
import visdcc
import pandas as pd
import sys
import random
from flask import request

# Initializing classes
class Node():
    """This class is created for containing information on the people.
    id(str): unique id of the person in the database.
    name(str): full name of the person.
    sex(str)
    .
    .
    ."""
    def __init__(self, id:int, name:str, birth:str, death:str, sex:str, hidden:bool, level:int, partner:"Node" = None, is_outsider = False, mainb = False):
        self.id = id
        self.name = name
        self.birth = birth
        self.death = death
        self.sex = sex
        self.hidden = hidden
        self.level = level
        self.is_outsider = is_outsider
        self.children = []
        self.partner = partner
        self.partner_list = []
        self.mainb = mainb

    def update_partner_list(self, person:"Node"):
        if not self.is_outsider:
            self.partner_list.append(person)
        return self.partner_list

    def update_children_list(self, children:List["Node"]):
        self.children.extend(children)
        return self.children

    def modify_node_status(self):
        if self.is_outsider:
            if self.level != self.partner.level + 1:
                self.level -= 1

                # Displaying children
                if len(self.children) > 0:
                    for child in self.children:
                        child.hidden = False
                
                # Hiding other partners
                if len(self.partner.partner_list) >0:
                    for partner in self.partner.partner_list:
                        if partner != self:
                            partner.hidden = True

                return self.level, self.children, self.partner

            if self.level == self.partner.level + 1:
                self.level += 1

                # Hiding children
                if len(self.children) > 0:
                    for child in self.children:
                        child.hidden = True

                # Displaying other partners
                if len(self.partner.partner_list) >0:
                    for partner in self.partner.partner_list:
                        if partner != self:
                            partner.hidden = False

                return self.level, self.children, self.partner
    
    def node_update(self):
        if self.partner != None:
            if self.partner.hidden == False:
                other = False
                for partner in self.partner.partner_list:
                    if self.partner.level + 1 == partner.level:
                        other = True
                        break
                if not other:
                    self.hidden = False

            if self.partner.hidden == True:
                self.hidden = True
                if len(self.children) > 0:
                    for child in self.children:
                        child.hidden = True
                if self.level == self.partner.level + 1:
                    self.level += 1

        return self.hidden, self.level

class Edge():
    def __init__(self, from_:object, to_:object):
        self.id = f"{from_.id}-{to_.id}"
        self.from_n = from_
        self.fr = self.from_n.id
        self.to_n = to_ 
        self.to = self.to_n.id

        if self.from_n.hidden == True or self.to_n.hidden == True:
            self.hidden = True
        else:
            self.hidden = False
    
    def edge_update(self):
        if self.from_n.hidden == False and self.to_n.hidden == False:
            self.hidden = False
        return self.hidden

class Tree():
    def __init__(self, nodes: List[Node], edges: List[Edge]):
        self.nodes = nodes
        self.edges = edges

    def print_node_name(self):
        ret = []
        for node in self.nodes:
            ret.append(node.name)
        return ret
    
    def print_edge_status(self):
        ret = {}
        for edge in self.edges:
            ret[edge.id] = edge.hidden
        return ret
    
    def modify_selected_node_status(self, node_id):
        n = [node for node in self.nodes if node.id == node_id][0]
        return n.modify_node_status()
    
    def modify_rest_tree(self, level):
        [node.node_update() if node.level >= level else node for node in self.nodes]
        [edge.edge_update() for edge in self.edges]
        return self.edges, self.nodes

    def find_node(self, node_id):
        n = [node for node in self.nodes if node.id == node_id][0]
        return n


# Reading data from csv
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
    marriages = marriages.append(new)

# Creating new df without parnter data
df = df[['id', 'first_name_1', 'first_name_2', 'last_name', 'birth_date', 'birth_place', 'death_date', 
        'death_place', 'father_id' , 'mother_id', 'sex']]


def earliest_id(df:pd.DataFrame, id:str) -> str:
    "This function returns the id of the earliest ancestor."
    father_id = df[df["id"] == id].iloc[0,8]
    
    if pd.isnull(father_id):
        return df[df["id"] == id]["id"].tolist()[0]
    else:
        return earliest_id(df, father_id)

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

def namestr(df:pd.DataFrame, id_:str) -> str:
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
                st += " "
    return st


def birthdate(df:pd.DataFrame, id:str)->str:
    """This function returns the date of birth of a person by id.
    If there is no info, it returns an empthy string."""

    bd = df[df["id"] == id]["birth_date"].tolist()[0]
    
    if pd.isnull(bd):
        return ""
    else: 
        return bd


def deathdate(df:pd.DataFrame, id:str) -> str:
    """This function returns the date of death of a person by id.
    If there is no info, it returns an empthy string."""
    
    dd = df[df["id"] == id]["death_date"].tolist()[0]

    if pd.isnull(dd):
        return "" 
    else:
        return dd

def sex(df:pd.DataFrame, id:str) -> str:
    "This function returns the sex of a person by id."
    s = df[df["id"] == id]["sex"].tolist()[0]
    if pd.isnull(s):
        return ''
    else:
        return s

def nodecolor(node:Node):
    if node.id == target:
        return 'orange'
    else:
        if node.sex == 'female':
            return 'pink'
        elif node.sex == 'male':
            return 'lightblue'
        else:
            return 'grey'

# creating list of mothers and first node

target = 'I930675KOM'
mothers = mother_list(df, target)
earliest = earliest_id(df, target)
depth = len(father_list(df, target))

n_list = []
n_list.append(Node(id = earliest, name = namestr(df, earliest), birth = birthdate(df, earliest), death = deathdate(df, earliest), sex = sex(df, earliest), hidden = False, level = 0))


def node_creation(df, n:Node, n_list:list, depth:int, e_list:list = None, n_id_list = None):

    # exit condition
    if n.level == depth * 2:
        return None


    if e_list == None:
        e_list = []
    if n_id_list == None:
        n_id_list = []

    if n.sex == 'male':
        wife_ids = marriages[marriages['husband_id'] == n.id]['wife_id'].tolist()
        
        for wife in wife_ids:
            i = 0

            # If wife is in main branch, she is displayed next to the husband, children visible.
            # If not, wife(s) are displayed below the husband, can be placed next to him by selecting the node.     
            if wife in mothers:
                w_level = n.level + 1
                child_hidden = False
            else:
                w_level = n.level + 2
                child_hidden = True


            if wife in n_id_list:
                # Adding a random number to id if it occurs for the second time. The only goal is to be able to create nodes with dash, the id will be the same when searching.
                wife += str(random.random())

            # Adding partner as node
            n_list.append(Node(id = wife, name = namestr(df, wife[:10]), birth = birthdate(df, wife[:10]), death = deathdate(df, wife[:10]), sex = sex(df, wife[:10]), hidden = n.hidden, level = w_level, partner = n, is_outsider = True))
            # Adding node id to list to ensure there are no duplicates 
            n_id_list.append(n_list[-1].id)
            # Updating husband's partner list with the wife
            n.update_partner_list(n_list[-1])
            # Adding edge between husband and wife.
            e_list.append(Edge(from_= n, to_=n_list[-1]))

            # listing children from current wife and husband
            children_id = df[(df["father_id"] == n.id[:10]) & (df["mother_id"] == n_list[-1].id[:10])]['id'].tolist()
            
            if len(children_id) > 0:
                children_list = []
                for child in children_id:

                    i += 1
                    # Adding node for child
                    if child in n_id_list:
                    # Adding a random number to id if it occurs for the second time. The only goal is to be able to create nodes with dash, the id will be the same when searching.
                        child += str(random.random())
                    
                    n_list.append(Node(id = child, name = namestr(df, child[:10]), birth = birthdate(df, child[:10]), death = deathdate(df, child[:10]), sex = sex(df, child[:10]), hidden = child_hidden, level = n.level + 2))
                    # Adding node id to list to ensure there are no duplicates
                    n_id_list.append(n_list[-1].id)
                    # Adding child to list
                    children_list.append(n_list[-1])
                    # Adding edge between mother and child
                    e_list.append(Edge(from_=n_list[-i-1], to_=n_list[-1]))
                
                # Updating wife's children list with child
                n_list[-i-1].update_children_list(children_list)

                # Iterating through the children, calling the same function to build the tree
                for child in children_list:
                    node_creation(df, child, n_list, depth, e_list, n_id_list)
                

    if n.sex == 'female':
        husband_ids = marriages[marriages['wife_id'] == n.id]['husband_id'].tolist()

        for husband in husband_ids:
            i = 0

            if husband in n_id_list:
                # Adding a random number to id if it occurs for the second time. The only goal is to be able to create nodes with dash, the id will be the same when searching.
                husband += str(random.random())

            # Adding partner as node, edge between husband and wife
            n_list.append(Node(id = husband, name = namestr(df, husband[:10]), birth = birthdate(df, husband[:10]), death = deathdate(df, husband[:10]), sex = sex(df, husband[:10]), hidden = n.hidden, level = n.level + 2, partner = n, is_outsider = True))
            # Adding node id to list to ensure there are no duplicates
            n_id_list.append(n_list[-1].id)
            # Updating wife's partner list with husband
            n.update_partner_list(n_list[-1])
            # Adding edge between husband and wife.
            e_list.append(Edge(from_= n, to_=n_list[-1]))

            # listing children from current husband and wife
            children_id = df[(df["mother_id"] == n.id[:10]) & (df["father_id"] == n_list[-1].id[:10])]['id'].tolist()
            
            if len(children_id) > 0:
                children_list = []
                for child in children_id:

                    i += 1
                    # Adding node for child
                    if child in n_id_list:
                    # Adding a random number to id if it occurs for the second time. The only goal is to be able to create nodes with dash, the id will be the same when searching.
                        child += str(random.random())

                    n_list.append(Node(id = child, name = namestr(df, child[:10]), birth = birthdate(df, child[:10]), death = deathdate(df, child[:10]), sex = sex(df, child[:10]), hidden = True, level = n.level + 2))
                    # Adding node id to list to ensure there are no duplicates
                    n_id_list.append(n_list[-1].id)
                    # Adding child to list
                    children_list.append(n_list[-1])
                    # Adding edge between father and child
                    e_list.append(Edge(from_=n_list[-i-1], to_=n_list[-1]))
                
                # Updating husband's children list with child
                n_list[-i-1].update_children_list(children_list)

                # Iterating through the children, calling the same function to build the tree  
                for child in children_list:
                    node_creation(df, child, n_list, depth, e_list, n_id_list)


    return [n_list, e_list]


treedata = node_creation(df, n_list[0], n_list, depth)
tree = Tree(nodes = treedata[0], edges = treedata[1])


#creating dash
app = dash.Dash()
app.layout = html.Div([
    daq.StopButton(
        id='my-stop-button',
        n_clicks=0
    ),
    html.Div(id='stop-button-output'),
    visdcc.Network(
        id = 'net',       
        options = dict(
            height= '1000px',
            width= '100%',
            layout={
                'hierarchical': {
                    'enable': True,
                    'levelSeparation': 100,
                    'nodeSpacing' : 250,
                    'edgeMinimization': True},
                    'blockShifting': True,
                    'parentCentralization' : True,
                    'sortMethod' : 'directed'},
            physics= {'enabled': False}),
            
        data = {'nodes' : [{'id': node.id, 'label': f"{node.name}\n{node.birth} - {node.death}", 'shape' : 'box', 'level': str(node.level), 'color' : nodecolor(node), 'hidden' : node.hidden} for node in tree.nodes if node.hidden == False],
         'edges' :[{'id': edge.id, 'from': edge.fr, 'to': edge.to, 'hidden': edge.hidden} for edge in tree.edges if edge.hidden == False]}
    )
])


@app.callback(
    Output('net', 'data'),
    Input('net', 'selection'),
    State('net', 'data'))
def my_fun(x, net):
    data = net
    if x:
        n = tree.find_node(x['nodes'][0])

        if len(x['nodes']) > 0 and n.is_outsider:
            n.modify_node_status()
            #tree.modify_selected_node_status(x['nodes'][0])
            tree.modify_rest_tree(n.level)
            data = {'nodes' : [{'id': node.id, 'label': f"{node.name}\n{node.birth} - {node.death}", 'shape' : 'box', 'level': str(node.level), 'color' : nodecolor(node), 'hidden' : node.hidden} for node in tree.nodes],
            'edges' :[{'id': edge.id, 'from': edge.fr, 'to': edge.to, 'hidden': edge.hidden} for edge in tree.edges]}
    
    return data

@app.callback(
    dash.dependencies.Output('stop-button-output', 'children'),
    [dash.dependencies.Input('my-stop-button', 'n_clicks')])
def update_output(n_clicks):
    return 'The stop button has been clicked {} times.'.format(n_clicks)


       


if __name__ == '__main__':
    app.run_server(debug=True)
