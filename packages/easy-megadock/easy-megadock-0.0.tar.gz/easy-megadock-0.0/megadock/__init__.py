import os
from .dock import Docktools

dirname = os.path.dirname(__file__)
tag_file = os.path.join(dirname, 'tag.txt')
lib_dir = os.path.join(dirname, '../needlib')
if not os.path.exists(tag_file):
    os.system('touch ' + tag_file)
    inner_cmd = "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{}".format(lib_dir)
    cmd = 'echo {} >> ~/.bashrc'.format(inner_cmd)
    os.system(cmd)
    # cmd = 'source ~/.bashrc'
    # os.system(cmd)