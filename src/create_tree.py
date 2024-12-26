import pandas as pd
import webbrowser
from pathlib import Path
from pyvis.network import Network
import os

import logging

logger = logging.getLogger(__name__)


class FamilyTree:
    def __init__(self, source_path: str):
        self.source_df = pd.read_csv(source_path, sep=";", dtype="string")
        self.marriages_df = self.get_marriages_dataframe()
        self.plot_path = self.get_plot_path()

    def get_plot_path(self):
        """
        creating new folder for plots if it hasn't existed yet.
        """
        path = "plots"
        os.makedirs(path, exist_ok=True)

        return path

    def get_marriages_dataframe(self) -> pd.DataFrame:
        """
        Creates a new dataframe from the source dataframe. In the new version each marriage
        is represented as a row where the ids of the husband and wife
        """

        marriages = pd.DataFrame()

        for i in range(1, 7):
            # iterating through the partner id columns after filtering
            # for males and for existing partner id-s and appending
            # the filtered df to the new df.

            new = self.source_df[
                (self.source_df["sex"] == "male")
                & (pd.notna(self.source_df[f"partner_id{i}"]))
            ][["id", f"partner_id{i}"]]
            new.columns = ["husband_id", "wife_id"]
            marriages = pd.concat([marriages, new])

        return marriages

    def remove_partner_data_from_df(self) -> pd.DataFrame:
        return self.source_df[
            [
                "id",
                "first_name_1",
                "first_name_2",
                "last_name",
                "birth_date",
                "birth_place",
                "death_date",
                "death_place",
                "father_id",
                "mother_id",
                "sex",
            ]
        ]

    def lookup(self, firstname: str, lastname: str) -> pd.DataFrame:
        """This function returns a dataframe containing the people called
        as the given name. It also given information about the parents' name
        and birth date and id. The aim of this function is to help identify
        the desired person by other attributes and locate its id for further
        search purposes."""

        # Initializing dataframe

        # Transforming names into regex to find similar characters as well.

        # Creating dictionary of special characters and their pairs in english alphabet.
        # langs = 'ÁáČčĎďÉéĚěÍíŇňÓóŘřŠšŤťÚúŮůÝýŽž'
        langs_eng = "AaCcDdEeIiNnOoRrSsTtUuYyZz"
        lang_dic = {
            "A": "[A,Á]",
            "C": "[C,Č]",
            "D": "[D, Ď]",
            "E": "[E,É,Ě]",
            "I": "[I,Í]",
            "N": "[N,Ň]",
            "O": "[O,Ó]",
            "R": "[R,Ř]",
            "S": "[S,š]",
            "T": "[T,Ť]",
            "U": "[U,Ú,Ů]",
            "Y": "[Y,Ý]",
            "Z": "[Z,Ž]",
        }
        lang_dic.update({k.lower(): v.lower() for (k, v) in lang_dic.items()})

        # Creating regex compatible first and last names
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
        id_list = list(
            self.source_df[
                (
                    self.source_df["first_name_1"].str.contains(
                        firstname_reg, regex=True, na=False
                    )
                )
                & (
                    self.source_df["last_name"].str.contains(
                        lastname_reg, regex=True, na=False
                    )
                )
            ]["id"]
        )

        if len(id_list) == 0:
            raise ValueError("No person in the database with the given name.")
        else:
            d = {
                "id": [],
                "first_name_1": [],
                "first_name_2": [],
                "last_name": [],
                "birth_date": [],
                "father_name": [],
                "mother_name": [],
            }
            for i in id_list:
                # Iterating through the id-s and collect data about the person

                d["id"].append(i)
                d["first_name_1"].append(
                    self.source_df[(self.source_df["id"] == i)].iloc[0, 1]
                )
                d["first_name_2"].append(
                    self.source_df[(self.source_df["id"] == i)].iloc[0, 2]
                )
                d["last_name"].append(
                    self.source_df[(self.source_df["id"] == i)].iloc[0, 3]
                )
                d["birth_date"].append(
                    self.source_df[(self.source_df["id"] == i)].iloc[0, 4]
                )

                father_id = self.source_df[(self.source_df["id"] == i)].iloc[0, 8]
                if not pd.isnull(father_id):
                    d["father_name"].append(
                        self.source_df[self.source_df["id"] == father_id].iloc[0, 1]
                        + " "
                        + self.source_df[self.source_df["id"] == father_id].iloc[0, 3]
                    )
                else:
                    d["father_name"].append(None)

                mother_id = self.source_df[(self.source_df["id"] == i)].iloc[0, 9]
                if not pd.isnull(mother_id):
                    d["mother_name"].append(
                        self.source_df[self.source_df["id"] == mother_id].iloc[0, 1]
                        + " "
                        + self.source_df[self.source_df["id"] == mother_id].iloc[0, 3]
                    )
                else:
                    d["mother_name"].append(None)

                    # Appending dictionary to dataframe

            people = pd.DataFrame(d)

            # Returning df with a given order of columns
            return people[
                [
                    "id",
                    "first_name_1",
                    "first_name_2",
                    "last_name",
                    "birth_date",
                    "father_name",
                    "mother_name",
                ]
            ]

    def lookup_earliest(self, id: str) -> str:
        """This function returns the name and birth year of the earliest ancestor"""

        if len(self.source_df[self.source_df["id"] == id]) == 0:
            raise ValueError("Please add an existing id!")
        else:
            father_id = self.source_df[self.source_df["id"] == id].iloc[0, 8]

            if pd.isnull(father_id):
                return f"The eldest ancestor is: {self.source_df[self.source_df['id'] == id].iloc[0,1]} {self.source_df[self.source_df['id'] == id].iloc[0,3]}. He/She was born in {self.source_df[self.source_df['id'] == id].iloc[0, 4]}."
            else:
                return self.lookup_earliest(father_id)

    def earliest_id(self, id: str) -> str:
        "This function returns the id of the earliest ancestor."
        father_id = self.source_df[self.source_df["id"] == id].iloc[0, 8]

        if pd.isnull(father_id):
            return self.source_df[self.source_df["id"] == id]["id"].tolist()[0]
        else:
            return self.earliest_id(father_id)

    def mother_list(self, id: str, result=[]) -> list:
        """This function returns the list of mothers' id who are in
        the selected person's family tree. The goal of this function
        is to select the wives from every father's partners who belong
        to the selected tree. The logic is the same as in the earliest_id
        function."""

        father_id = self.source_df[self.source_df["id"] == id].iloc[0, 8]
        if not pd.isnull(self.source_df[self.source_df["id"] == id].iloc[0, 9]):
            result.append(self.source_df[self.source_df["id"] == id].iloc[0, 9])

        if pd.isnull(father_id):
            return result[::-1]
        else:
            return self.mother_list(father_id, result)

    def father_list(self, id: str, result=[]) -> list:
        """This function returns the list of fathers' id who are in
        the selected person's family tree. The logic is the same as
        in the earliest_id function."""

        father_id = self.source_df[self.source_df["id"] == id].iloc[0, 8]
        if not pd.isnull(father_id):
            result.append(father_id)

        if pd.isnull(father_id):
            return result[::-1]
        else:
            return self.father_list(father_id, result)

    def namestr(self, id_: str, sep=" ") -> str:
        """This function creates a string containing the name of the person.
        It selects the name attributes of a given id and pastes together in
        firstname1, firstname2 (if exists), last name order."""

        # Creating list from the names
        name_list = self.source_df[self.source_df["id"] == id_][
            ["first_name_1", "first_name_2", "last_name"]
        ].values.flatten()

        st = ""
        for n in name_list:
            if not pd.isna(n):
                st += n
                if n != name_list[-1]:
                    st += sep
        return st

    def get_wife_id(self, husband_id: str, orig_id: str) -> str:
        "This function returns the wife id to a husband id."
        # orig_id: the id of the person whose tree is being built.

        mothers = self.mother_list(orig_id)

        wives = self.marriages_df[self.marriages_df["husband_id"] == husband_id]
        if len(wives[wives["wife_id"].isin(mothers)]) == 0:
            return None
        else:
            return wives[wives["wife_id"].isin(mothers)]["wife_id"].tolist()[0]

    def get_birth_date(self, id: str) -> str:
        """This function returns the date of birth of a person by id.
        If there is no info, it returns an empthy string."""

        bd = self.source_df[self.source_df["id"] == id]["birth_date"].tolist()[0]

        if pd.isnull(bd):
            return ""
        else:
            return bd

    def get_death_date(self, id: str) -> str:
        """This function returns the date of death of a person by id.
        If there is no info, it returns an empthy string."""

        dd = self.source_df[self.source_df["id"] == id]["death_date"].tolist()[0]

        if pd.isnull(dd):
            return ""
        else:
            return dd

    def get_birth_place(self, id: str) -> str:
        """
        gets the birth place for a given id
        """

        birth_place = self.source_df[self.source_df["id"] == id][
            "birth_place"
        ].tolist()[0]

        if pd.isnull(birth_place):
            return ""
        else:
            return birth_place

    def get_death_place(self, id: str) -> str:
        """
        gets the birth place for a given id
        """

        death_place = self.source_df[self.source_df["id"] == id][
            "death_place"
        ].tolist()[0]

        if pd.isnull(death_place):
            return ""
        else:
            return death_place

    def nodecolor(self, act_id: str, orig_id: str) -> str:
        """This function returns a color based on the person's details.
        Pink, if female, blue, if male, and orange if the person is the same
        whose tree is being built for better visualization."""

        gender = self.source_df[self.source_df["id"] == act_id]["sex"].tolist()[0]
        if act_id == orig_id:
            return "orange"
        elif pd.isna(gender):
            return "grey"
        elif gender == "male":
            return "lightblue"
        else:
            return "pink"

    def generate_node_label(self, id: str):
        """
        Generates a node label for each id including the name, the birth and death date and the
        birth and death places.
        """
        birth_date = self.get_birth_date(id)
        death_date = self.get_death_date(id)
        birth_place = self.get_birth_place(id)
        death_place = self.get_death_place(id)

        label = f"{self.namestr(id)}\n{birth_date}"
        if birth_place:
            label += f"\n({birth_place})"
        label += f" -\n{death_date}"
        if death_place:
            label += f"\n({death_place})"

        return label

    def create_tree(self, id: str):
        """ "This function takes the id of a person and returns the whole family tree on
        father's side. The shown attributes of a person in the tree are the full name, birth
        date and date of death. The men's boxes are blue while the female's are pink."""

        # Creating list of fathers, mothers ids
        fathers = self.father_list(id)

        # ID of the earliest ancestor
        eid = self.earliest_id(id)

        # Initializing network object and adding earliest ancestor
        net = Network(layout="hieararchical", height=1000, width=2000)
        net.add_node(
            eid,
            label=self.generate_node_label(eid),
            level=1,
            shape="box",
            color="lightblue",
        )

        # Iterating through the fathers list and adding the wife, marriage nodes first.
        # Adding edges between them later and finally adding children as well for nodes
        # and edges for them The level of a node is also set based on the iteration number.
        for i, father in enumerate(fathers):
            # Adding earliest ancestor node.
            net.add_node(
                f"m{i+1}",
                label=" ",
                level=2 * i + 1,
                shape="dot",
                size=3,
                color="black",
            )

            # Adding wife node and edge only in case id is known.
            wife_id = self.get_wife_id(father, id)
            if not pd.isnull(wife_id):
                net.add_node(
                    wife_id,
                    label=self.generate_node_label(wife_id),
                    level=2 * i + 1,
                    shape="box",
                    color="pink",
                )
                net.add_edge(wife_id, f"m{i+1}", color="black", size=2)

            # Adding child collector node and edges between already added nodes.
            net.add_node(
                f"c{i+1}",
                label=" ",
                level=2 * i + 2,
                shape="dot",
                size=3,
                color="black",
            )
            net.add_edge(father, f"m{i+1}", color="black")
            net.add_edge(f"m{i+1}", f"c{i+1}")

            # Creating children list and omitting the one that will continue the tree in the
            # next level. Goal is to add him at the end so it will be placed on the left of
            # the children and adding wife in next iteration won't mess up the layout.
            # The creation has an if-else case to handle missing mother id-s.
            if not pd.isnull(wife_id):
                children = self.source_df[
                    (self.source_df["father_id"] == father)
                    & (self.source_df["mother_id"] == wife_id)
                ]
            else:
                children = self.source_df[(self.source_df["father_id"] == father)]

            # Adding all children's nodes except the next father. Edges to the previous child
            # collector node are also added.
            for child_id in children[~children["id"].isin(fathers)]["id"]:
                net.add_node(
                    child_id,
                    label=self.generate_node_label(child_id),
                    level=2 * i + 3,
                    shape="box",
                    color=self.nodecolor(child_id, id),
                )

                net.add_edge(child_id, f"c{i+1}", color="black")

            # Adding next iteration's father to the left of his siblings in case
            # the loop is not in the final iretarion. In the final iteration the
            # people have no children by definiton. Edge is also added to the
            # previous child collector node.
            if len(children[children["id"].isin(fathers)]) != 0:
                f = children[children["id"].isin(fathers)]["id"].tolist()[0]
                net.add_node(
                    f,
                    label=self.generate_node_label(f),
                    level=2 * i + 3,
                    shape="box",
                    color="lightblue",
                )
                net.add_edge(f, f"c{i+1}", color="black")

        name_to_file = self.namestr(id, sep="_")
        # Showing tree and saving it to plots folder.
        generated_html_path = os.path.join(
            self.plot_path, f"tree_{name_to_file}_{id}.html"
        )
        net.save_graph(generated_html_path)
