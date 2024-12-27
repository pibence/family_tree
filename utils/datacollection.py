from bs4 import BeautifulSoup
import html5lib
import pandas as pd
from glob import glob
from datetime import datetime
from tqdm import tqdm


def html_to_df(path):
    ''' This function was created to perform data collection from html files 
    that contain personal data about people. The function iterates through all
    html files in the given folder and concatenates the necessary data from 
    the files in a dataframe. The searched data are the following: first name,
    last name, id of the person, place and date of birth, place and date of
    death, partners's id. It uses BeautifulSoup to create and navigate in the
    html files and obtain the desired data. The variable is a path indicating
    the folder where the files are stored.'''

    
    # Initializing dataframe
    df = pd.DataFrame()

    
    # Iterating through the html files
    for src in tqdm(glob(path + '/*.html'), desc = f"Creating dataframe from htmls in {path.split('/')[-1]} folder"):    
        
        # Creating the soup object from the html and creating help objects
        soup = BeautifulSoup(open(src, encoding = "utf8"), "html5lib")
        table = soup.find('table')
        help_table = table.caption.find_all('span')
        help_table2 = table.tbody.find_all('span', attrs = {'class' : 'gpn'})
        
        # Inintializing loop variables
        d = {}
        n_birthdate = int()
        n_deathdate = int()
        n_father = int()
        n_mother = int()

        # Locating birth and death data
        for i, element in enumerate(help_table):
            if element.text.replace(u'\xa0', u'') == '*' and not n_birthdate:
                n_birthdate = i + 1 
            if element.text.replace(u'\xa0', u'') == '†'and not n_deathdate:
                n_deathdate = i + 1    

        # Locating father and mother data 
        for i, element in enumerate(help_table2):        
            if element.text == 'Otec:': # Otec(sk) = father
                n_father = i+1
            if element.text == 'Matka:': # Matka (sk) = mother
                n_mother = i+1

        # Locating and copying personal data (name, id)
        d['id'] = table.find('span', attrs = {'class' : 'id'}).text.replace(u'\xa0', u' ').split(' ')[0]
        frist_name_list = table.find('span', attrs = {'class' : 'vnh'}).text.replace(u'\xa0', u'').split(' ')
        d['first_name_1'] = frist_name_list[0]
        if len(frist_name_list) > 1:
            d['first_name_2'] = frist_name_list[1]
        else:
            d['first_name_2'] = ''
        d['last_name'] = table.find('span', attrs = {'class' : 'nnh'}).text.replace(u'\xa0', u'').split(' ')[0]

        # Birth year and place collection if exists. Also converting 
        # dates into datetime date format and handling wrong inputs.
        
        if help_table[n_birthdate].text == '':
            d['birth_date'] = ''
            d['birth_place'] = ''
        else:
            if len(help_table[n_birthdate].text.split(' ')[0]) < 2:
                d['birth_date'] = ''
            else:
                d['birth_date'] = datetime.strptime(help_table[n_birthdate].text.split(' ')[0], '%Y.%m.%d').date()
            if len(help_table[n_birthdate].text.split(' ')[1]) < 2:
                d['birth_place'] = ''   
            else:    
                d['birth_place'] = help_table[n_birthdate].text.split(' ')[1]

        # Death year and place collection if exists. Also converting 
        # dates into datetime date format and handling wrong inputs
        
        if help_table[n_deathdate].text == '':
            d['death_date'] = ''
            d['death_place'] = ''
        else:
            if len(help_table[n_deathdate].text.split(' ')[0]) < 2:
                d['death_date'] = ''
            else:
                d['death_date'] = datetime.strptime(help_table[n_deathdate].text.split(' ')[0], '%Y.%m.%d').date()
            if len(help_table[n_deathdate].text.split(' ')[1]) < 2:
                d['death_place'] = ''   
            else:    
                d['death_place'] = help_table[n_deathdate].text.split(' ')[1]

        # Parent id collection if exists
        if n_father:
            d['father_id'] = help_table2[n_father].a.text
        else:
            d['father_id'] = ''

        if n_mother:    
            d['mother_id'] = help_table2[n_mother].a.text
        else:
            d['mother_id'] = ''

        # Partner id collection. Containers have no id so the method is the
        # following: locating container with 'Házastárs' (hun, = Partner) text
        # in it and check how many partners they had by selecting the following 
        # containers with partner info. The max no of partners is 5 in the files
        # so that is the maximum. 
        
        for i, element in enumerate(table.tbody.find_all('td')):
            if element.text.strip() =='Házastárs':
                for j in range(6):
                    if len(table.tbody.find_all('td')) >= i+2+5*j:
                        if table.tbody.find_all('td')[i+1+5*j].text == f'{j+1}:':
                            d[f'partner_id{j+1}'] = table.tbody.find_all('td')[i+2+j*5].a.text
                        else:
                            d[f'partner_id{j+1}'] = ''
                    else:
                        d[f'partner_id{j+1}'] = ''
        #  Appending one person's data to the dataframe
        df = df.append(d, ignore_index = True)
        
        column_list = ['id', 'first_name_1', 'first_name_2', 'last_name', 'birth_date', 'birth_place', 'death_date', 
        'death_place', 'father_id', 'mother_id', 'partner_id1', 'partner_id2', 'partner_id3', 'partner_id4',
        'partner_id5', 'partner_id6']
    return df[column_list]