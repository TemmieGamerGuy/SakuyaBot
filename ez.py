import os, pickle
from char_list import *

char_dir = "E://Bot files//touhoushit"
new = "E://Bot files//touhoushit//new"

def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
	
x = {}
		
save_obj(x,"achievements")