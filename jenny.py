#!/usr/bin/python3

import os
import sys
import glob
import markdown
from datetime import date

src_dir = "src"
out_dir = "public"
res_dir = "assets"
list_template = "index_template.html"
post_template = "template.html"
list_files = ['archive']

if not list_template.endswith(".html"):
    list_template = list_template + ".html"
if not post_template.endswith(".html"):
    post_template = post_template + ".html"

if not os.path.exists(src_dir):
    print(f"creating input dir {src_dir}/...")
    os.mkdir( src_dir )
if not os.path.exists( out_dir ):
    print(f"creating output dir {out_dir}/...")
    os.mkdir( out_dir )


# extract any variables in a file.
def preprocess_file(file):
    vars = {
        "post_content": "",
        "file_name": file,
    }
    keep_scanning = True
    for line in file:
        stripped = line.lstrip()
 
        if stripped.startswith('@') and keep_scanning:
            command,_,args = stripped.rstrip('\n').lstrip('@').partition(' ')
            args = args.strip().split('+')

            # If only one item in list just convert it into a string
            if len(args) == 1:
                args = "".join(args)

            vars[command] = args
        elif stripped.startswith("---"):
            keep_scanning = False
            continue
        else: 
            vars['post_content'] += line;
    return vars

def format_file(post, template):

    # Necessary for every post
    # TODO error handling.
    try:
        template = template.replace("{{title}}", post['post_title'])
        template = template.replace("{{content}}", post['post_content'])
        template = template.replace("{{date}}", post['post_date'].replace('-', '.'))
    except:
        print(f"Error processing file {post["file_name"]}")
        exit()

    if "post_subtitle" in post:
        template = template.replace("{{subtitle}}", f"<h4><span>{post['post_subtitle']}</span></h4>")
    else:
        template = template.replace("{{subtitle}}", "")
    return template

posts = []

def process_posts():
    # Globbed files are unsorted >:[
    post_list = sorted(glob.glob(f"{src_dir}/**/*.md", recursive=True))
    for f in post_list:
        post = {}

        # Read and preprocess the source file.
        print(f"generating {f}...")
        template = open(f"{res_dir}/{post_template}", 'r').read()
        with open( f, 'r' ) as file:
            post = preprocess_file(file)
            post['post_content'] = markdown.markdown( post["post_content"] )

        file_name = os.path.basename( f )
        destination = os.path.join( out_dir , os.path.splitext( file_name )[ 0 ] + ".html" )
        post["dest"] = destination
        destination.rstrip(".md")

        # skip file if the current file is a list file rather than a post file.
        if f.lstrip(src_dir+"/").rstrip(".md") in list_files:
            continue

        print(f"creating file {destination}...")
        with open( destination, 'w' ) as file:
            template = format_file(post, template)
            file.write(template)
        posts.append(post)


def process_index(file: str):

    # list index template file.
    index = open(f'{res_dir}/{list_template}', 'r').read()
    content = open(f'{src_dir}/{file}.md', 'r').read()
    content = markdown.markdown(content)
    list = ''
    last_year = "0"
    file_name = f"{out_dir}/{file}.html"

    for post in reversed(posts):
        year = "".join(post['post_date']).split('.')[0]
        if not (year == last_year):
            # Nasty little hack, but i have a slight headache and i'm losing 
            # my will to keep working on this script anymore today.
            # ( he says as if he wouldn't put in nasty little hacks in his code otherwise )
            if last_year == "0":
                head = "<br><br>"
            else:
                head = "<br><hr><br>"
            last_year = year
            list += f"{head}<h3>{last_year}<h3>"
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
    today = date.today().strftime("%Y.%m.%d")
    
    if name:
        post = today.replace(".", "").removeprefix("20") + "-" + name + ".md"
    else:
        name = "[title]"
        post = today + ".md"
    file = f"{src_dir}/{post}"
    with open (file, 'w') as f:
        f.write(f"""@post_title {name}
@post_date {today}
@post_subtitle [post_subtitle]
@post_tags tag1 + tag2
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
            for f in list_files:
                print(f"processing {f}...")
                process_index(f)
        case "new-post":
            print("Input a name for your post:")
            name = input()
            create_new_post(name)
            pass
