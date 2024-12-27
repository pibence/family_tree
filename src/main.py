from .create_tree import FamilyTree
from .tree_app import FamilyTreeApp
from .input_prompts import PROMPTS

import os


if __name__ == "__main__":
    source_path = os.path.join("data", "final_cleaned.csv")
    family_tree_factory = FamilyTree(source_path=source_path)
    app = FamilyTreeApp(prompts=PROMPTS, family_tree_factory=family_tree_factory)
    app.run()
