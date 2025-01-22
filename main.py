import os
from vne.core import VNEngine as Core

if __name__ == "__main__":
    core = Core()

    project_folder = os.path.join(os.path.dirname(__file__), 'test-game')
 
    core.run(project_folder)