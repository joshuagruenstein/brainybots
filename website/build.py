from jemdoc import *
import os, shutil, sys

CONF_FILE = 'mysite.conf'
OUT_DIR = '../docs'

def make_file(filename):    
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
    
def get_watch_files():
    if os.path.exists(OUT_DIR):
        shutil.rmtree(OUT_DIR) 

    os.makedirs(OUT_DIR)
    watch_files = []

    for (path, dirs, files) in os.walk('.'):
        # don't traverse hidden directories or files
        dirs[:] = [d for d in dirs if not
            (d[0] == '.' or d == 'build')
        ]

        watch_files += [
            os.path.join(path, f) for f in files
            if not f[0] == '.'
        ]
    
    return watch_files

FILES_TO_WATCH = ['.css', '.png', '.js']

def build(watch_files):
    for file in watch_files:
        if file.endswith('.jemdoc'):
            make_file(file[:-7])
        elif any(file.endswith(e) for e in FILES_TO_WATCH):
            shutil.copyfile(
                file, os.path.join(OUT_DIR,file)
            )

watch_files = {
    f: os.stat(f).st_mtime
    for f in get_watch_files()
}

build(watch_files.keys())

while sys.argv[-1] == '--watch':
    for file, time in watch_files.items():
        if os.stat(file).st_mtime > time:
            watch_files[file] = os.stat(file).st_mtime
            print('Detected change in', file, 'so rebuilding')
            build(watch_files.keys())
            break