#!/usr/bin/python3

import os
import sys
import glob
import markdown
import json
from datetime import date

config = {}
# for ease of access.
src_dir = ""
out_dir = ""
res_dir = ""

# checks for and creates a config file.
cfg_file = "config_jenny.json"
if not os.path.exists(cfg_file):
    print("No jenny project detected, create a new one? (Y/n)")
    x = input()
    if x == 'n' or x == 'N':
        exit()
    opts = {
        "src_dir": "src",
        "out_dir": "public",
        "res_dir": "assets",
        "list_template": "index_template.html",
        "post_template": "template.html",

        "list_files": [
            'archive'
        ], #trailing comma wooooo
    }

    print("creating config file...")
    f = open(cfg_file, "w")
    f.write(json.dumps(opts))
    f.close()
    config = opts

    print("done! enjoy your new blog!")
else:
    f = open(cfg_file, "r").read()
    config = json.loads(f)

if not config["list_template"].endswith(".html"):
    config["list_template"] = config["list_template"] + ".html"
if not config["post_template"].endswith(".html"):
    config["post_template"] = config["post_template"] + ".html"
src_dir = config["src_dir"]
out_dir = config["out_dir"]
res_dir = config["res_dir"]

if not os.path.exists(src_dir):
    print(f"creating input dir [{src_dir}]...")
    os.mkdir( src_dir )
if not os.path.exists( out_dir ):
    print(f"creating output dir [{out_dir}]...")
    os.mkdir( out_dir )


# extract any variables in a file.
def preprocess_file(file):
    vars = {
            "post_content": ""
            }
    keep_scanning = True
    for line in file:
        stripped = line.lstrip()
 
        if stripped.startswith('@') and keep_scanning:
            command,_,args = stripped.rstrip('\n').lstrip('@').partition(' ')
            args = args.strip().split(',')
            vars[command] = args
        elif stripped.startswith("---"):
            keep_scanning = False
            continue
        else: 
            vars['post_content'] += line;
    return vars

def format_file(post, template):
    template = template.replace("{{content}}", post['post_content'])
    template = template.replace("{{title}}", "".join(post['post_title']))
    template = template.replace("{{subtitle}}", "".join(post['post_subtitle']))
    template = template.replace("{{date}}", "".join(post['post_date']).replace('-', '.'))
    return template

posts = []

def process_posts():
    for f in glob.iglob( f"{src_dir}/**/*.md", recursive=True):
        post = {}

        # Read and preprocess the source file.
        print(f"generating {f}...")
        template = open(f"{res_dir}/{config["post_template"]}", 'r').read()
        with open( f, 'r' ) as file:
            post = preprocess_file(file)
            post['post_content'] = markdown.markdown( post["post_content"] )

        file_name = os.path.basename( f )
        destination = os.path.join( out_dir , os.path.splitext( file_name )[ 0 ] + ".html" )
        post["dest"] = destination
        destination.rstrip(".md")

        # skip file if the current file is a list file rather than a post file.
        if f.lstrip(src_dir+"/").rstrip(".md") in config["list_files"]:
            continue

        print(f"creating file {destination}...")
        with open( destination, 'w' ) as file:
            template = format_file(post, template)
            file.write(template)
        posts.append(post)


def process_index(file: str):

    # list index template file.
    index = open(f'{res_dir}/{config["list_template"]}', 'r').read()
    content = open(f'{src_dir}/{file}.md', 'r').read()
    content = markdown.markdown(content)
    list = ''
    year = "0"
    file_name = f"{out_dir}/{file}.html"

    for post in reversed(posts):
        if not ("".join(post['post_date']).split('-')[0] == year):
            year = "".join(post['post_date']).split('-')[0]
            list += "20" + year
        list += "<li>"
        list += "<a href=\"/" + post['dest'] + "#main\">"
        list += "".join(post['post_title'])
        list += "</a></li>"

    print(f"creating file {file}...")
    with open (file_name, 'w') as f:
        index = index.replace("{{posts}}", list)
        index = index.replace("{{content}}", content)
        index = index.replace("{{title}}", file.capitalize())
        f.write(index)


def create_new_post(name: str):
    today = date.today().strftime("%Y-%m-%d")
    
    if name:
        post = today + "-" + name + ".md"
    else:
        name = "[title]"
        post = today + ".md"
    file = f"{src_dir}/{post}"
    with open (file, 'w') as f:
        f.write(f"""@post_title {name}
@post_date {today}
@post_subtitle [post_subtitle]
@post_tags tag1, tag2
---

# {name.capitalize()}

Hello this is a new post wooooo
""")
        f.close()
        pass


# TODO implement match case cmdline arg handling...

if len(sys.argv) < 2:
    print("welcome to jenny!")
    exit()
else:
    match sys.argv[1]:
        case "build":
            process_posts()
            for f in config["list_files"]:
                print(f"processing {f}...")
                process_index(f)
        case "new-post":
            print("Input a name for your post:")
            name = input()
            create_new_post(name)
            pass
