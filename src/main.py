from .create_tree import FamilyTree
from tabulate import tabulate
import os


if __name__ == "__main__":
    # Communicating with the user
    # The idea is to ask questions as inputs and 1) check the inputs first
    # 2a) execute the desired step 2b) ask for new input if the first was
    # not correct.

    source_path = os.path.join("data", "final_cleaned.csv")
    family_tree_factory = FamilyTree(source_path=source_path)

    active = True
    while active:
        nvalid = True
        while nvalid:
            firstname = input(
                "\nPlease enter the first name of the person you are looking for! "
            )
            lastname = input(
                "Please enter the last name of the person you are looking for! "
            )

            try:
                print(
                    f"{tabulate(family_tree_factory.lookup(firstname, lastname).fillna('-'), headers = 'keys', tablefmt = 'fancy_grid')}\n"
                )
                nvalid = False
            except ValueError:
                print("Please add a valid name!")

        person_id = input(
            "Please enter the id of the person you are looking for! \nThe ids are in the table above, you need to copy and insert it! "
        )

        nvalid2 = True
        while nvalid2:
            try:
                family_tree_factory.lookup_earliest(person_id)
                nvalid2 = False
            except ValueError:
                person_id = input("Please add a valid id! ")

        decision = input(
            "\nwould you like to find the earliest ancestor or plot the whole tree? \nType tree ancestor for ancestor finding and tree for visualization! "
        )

        nvalid3 = True
        while nvalid3:
            if decision == "ancestor":
                print(family_tree_factory.lookup_earliest(person_id))
                nvalid3 = False

                decision2 = input("Would like to plot the family tree(yes/no)? ")

                nvalid4 = True
                while nvalid4:
                    if decision2 == "yes":
                        family_tree_factory.create_tree(person_id)
                        nvalid4 = False

                        decision3 = input(
                            "Would like to continue with a new person(yes/no)? "
                        )

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
                        decision4 = input(
                            "Would like to continue with a new person(yes/no)? "
                        )

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
                family_tree_factory.create_tree(person_id)
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
