from tabulate import tabulate

from .create_tree import FamilyTree


class FamilyTreeApp:
    def __init__(self, prompts: dict, family_tree_factory: FamilyTree):
        self.lang = "en"
        self.active = True
        self.PROMPTS = prompts
        self.family_tree_factory = family_tree_factory

    def prompt_language(self):
        """Prompt the user to select a language."""
        print(self.PROMPTS["en"]["welcome"])
        while True:
            lang = input(self.PROMPTS["en"]["select_language"]).strip().lower()
            if lang in self.PROMPTS:
                self.lang = lang
                break
            print("Invalid language selection. Please choose en or hu.")

    def prompt_yes_no(self, prompt):
        """Prompt the user for a yes/no response."""
        yes = self.PROMPTS[self.lang]["yes"]
        no = self.PROMPTS[self.lang]["no"]
        while True:
            response = input(prompt).strip().lower()
            if response in {yes, no}:
                return response == yes
            print(self.PROMPTS[self.lang]["yes_or_no"])

    def prompt_name(self):
        """Prompt the user for a first and last name."""
        return (
            input(self.PROMPTS[self.lang]["enter_first_name"]).strip(),
            input(self.PROMPTS[self.lang]["enter_last_name"]).strip(),
        )

    def prompt_person_id(self):
        """Prompt the user for a valid person ID."""
        while True:
            person_id = input(self.PROMPTS[self.lang]["enter_person_id"]).strip()
            try:
                self.family_tree_factory.lookup_earliest(person_id)  # Validate the ID
                return person_id
            except ValueError:
                print(self.PROMPTS[self.lang]["invalid_id"])

    def lookup_person(self):
        """Handle the name lookup and display the results."""
        while True:
            firstname, lastname = self.prompt_name()
            try:
                result = self.family_tree_factory.lookup(firstname, lastname).fillna(
                    "-"
                )
                print(tabulate(result, headers="keys", tablefmt="fancy_grid"))
                return
            except ValueError:
                print(self.PROMPTS[self.lang]["invalid_name"])

    def run(self):
        """Run the main application loop."""
        self.prompt_language()
        while self.active:
            self.lookup_person()
            person_id = self.prompt_person_id()
            print(self.PROMPTS[self.lang]["plotting_tree"].format(person_id=person_id))
            self.family_tree_factory.create_tree(person_id)
            self.active = self.prompt_yes_no(self.PROMPTS[self.lang]["continue"])
