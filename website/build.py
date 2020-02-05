from jemdoc import *
import os, shutil

CONF_FILE = 'mysite.conf'
OUT_DIR = './build'

def make_file(filename):
    #os.makedirs(OUT_DIR)
    
    outfile = os.path.join(
        OUT_DIR, filename+'.html'
    )
        
    try:
        os.makedirs(os.path.dirname(outfile))
    except FileExistsError:
        pass
 
    

    f = controlstruct(
        io.open(filename+'.jemdoc', 'rb'),
        io.open(outfile, 'w'), parseconf([CONF_FILE]), filename
    )
    
    procfile(f)

if os.path.exists(OUT_DIR):
    shutil.rmtree(OUT_DIR) 

os.makedirs(OUT_DIR)


for (path, dirs, files) in os.walk('.'):
    # don't traverse hidden directories or files
    dirs[:] = [d for d in dirs if not
        (d[0] == '.' or d == 'build')
    ]
    
    files = [f for f in files if not f[0] == '.']
 
    for f in files:
        file = os.path.join(path, f)
        if file.endswith('.jemdoc'):
            make_file(file[:-7])
        elif file.endswith('.css'):
            shutil.copyfile(file, os.path.join(OUT_DIR,file))
 
