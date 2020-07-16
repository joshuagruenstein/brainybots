import argparse, os, time, shutil, re
import render

MEDIA_EXT = ['css', 'js', 'png']

def frame_html(root_link, title, menu, body):
    return """
<!DOCTYPE html>
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html;charset=utf-8" />
    <link rel="stylesheet" href="{0}jemdoc.css" type="text/css" />
    <script src="{0}index.js"></script>
    <title>{1}</title>
    <script src='https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.5/latest.js?config=TeX-MML-AM_CHTML' async>
    </script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/numeric/1.2.6/numeric.min.js" integrity="sha256-t7CAuaRhODo/cv00lxyONppujwTFFwUWGkrhD/UB1qM=" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/roughjs@4.0.4/bundled/rough.min.js"></script>
    <script type="text/x-mathjax-config">
    MathJax.Hub.Config({{
    tex2jax: {{
          inlineMath: [['$','$']],
          displayMath: [['$$','$$']],
          processEscapes: true
        }},
     
    }});
    </script>
</head>
<body>
    <table summary="Table for page layout." id="tlayout">
    <tr valign="top">
        <td id="layout-menu">{2}</td>
        <td id="layout-content">{3}</td>
    </tr>
    </table>
</body>
</html>
    """.format(root_link, title, menu, body)

def dir_path_type(string):
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)

def traverse_tree(directory):
    watch_files = []

    for (path, dirs, files) in os.walk(directory):
        # don't traverse hidden directories or files
        dirs[:] = [d for d in dirs if not d[0] == '.']

        watch_files += [
            os.path.join(path, f) for f in files
            if not f[0] == '.'
        ]
    
    return watch_files

def make_menu(menu_path, root_link, out_path):
    with open(menu_path) as f:
        menu = f.read()
    
    menu = [
        m.strip() for m in menu.split('\n')
        if m.strip() != '' and m.strip()[0] != '#'
    ]
    
    menu_buffer = ""
    for m in menu:
        if '[' in m:
            name = m.split('[')[0].strip()
            url  = m.split('[')[1].split(']')[0].strip()
            selected = 'class="current"' if out_path.endswith(url) else ''
            if not 'http' in url:
                url = root_link + url
               
            menu_buffer += f'<div class="menu-item"><a href="{url}" {selected}>{name}</a></div>\n'
            
        else:
            menu_buffer += f'<div class="menu-category">{m}</div>\n'
    
    return menu_buffer
    
def body_html(path):
    with open(path) as f:
        raw = f.read()
        
    title = render.get_title(raw)
    body = render.render(raw)
        
    return title, body

def make_page(menu_path, page_path, out_path):
    root_link = ''.join('../' for _ in range(len(page_path.split('/'))-2))
    
    menu = make_menu(menu_path, root_link, out_path)

    title, body = body_html(page_path)
    
    page_html = frame_html(root_link, title, menu, body)
    with open(ensure_path(out_path), mode='w+') as f:
        f.write(page_html)

def ensure_path(path):
    if not os.path.exists(os.path.dirname(path)):
        os.makedirs(os.path.dirname(path))
       
    return path

def build_tree(tree, menu, out_dir):
    for f in os.listdir(out_dir):
        p = os.path.join(out_dir, f)
        try:
            shutil.rmtree(p)
        except OSError:
            os.remove(p)

    menu_path = os.path.join(tree[0].split('/')[0], menu)
    if not menu_path in tree:
        raise Exception(f'Menu file {menu_path} not found, exiting.')
    
    outputify = lambda p: os.path.join(*[out_dir]+p.split('/')[1:])
    for page_path in [p for p in tree if p.endswith('.md')]:
        make_page(menu_path, page_path, outputify(page_path)[:-2]+'html')
    
    for file_path in [p for p in tree if p.split('.')[-1] in MEDIA_EXT]:
        shutil.copyfile(file_path, ensure_path(outputify(file_path)))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Build BrainyBots website.')
    parser.add_argument('dir', type=dir_path_type, default='.', nargs='?',
                        help='directory to build')
    parser.add_argument('-o', dest='out', type=dir_path_type, default='../docs',
                        help='directory to build into')
    parser.add_argument('-m', dest='menu', type=str, default='MENU',
                        help='menu file name in directory')
    parser.add_argument('--watch', dest='watch', action='store_true',
                        help='automatically rebuild directory')
    args = parser.parse_args()
        
    tree = traverse_tree(args.dir)
    if args.out == args.dir:
        raise Exception('Cannot build to source directory.')
    
    build_tree(tree, args.menu, args.out)
    
    watch_files = { f: os.stat(f).st_mtime for f in tree }
        
    try:
        while args.watch:
            for file, t in watch_files.items():
                t_new = os.stat(file).st_mtime
                if t_new > t:
                    watch_files[file] = t_new
                    print('Detected change in', file, 'so rebuilding')
                    build_tree(tree, args.menu, args.out)
            
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print('Ending build gracefully.')