#!/usr/bin/python3

import os
import re
import sys
import glob
import argparse
import markdown
from datetime import date
from bs4 import BeautifulSoup as Soup

# TODO: add standard.site support i think
# TODO: perhaps move to some sort of a class based approach so that there's a
#       more solid structure to my data

opt = {}
opt['src'] = "src"
opt['out'] = "public"
opt['force'] = False
opt['res'] = "assets"
opt['list_template'] = "index_template.html"
opt['post_template'] = "template.html"
opt['list_files'] = ['archive']

def dirty(src, dest):
    if not os.path.exists(dest):
        return True
    
    src_mtime  = os.path.getmtime(src)
    dest_mtime = os.path.getmtime(dest)
    
    return src_mtime > dest_mtime

# this seems kinda silly, genuinely don't remember why i put this here...
if not opt['list_template'].endswith(".html"):
    opt['list_template'] = opt['list_template'] + ".html"
if not opt['post_template'].endswith(".html"):
    opt['post_template'] = opt['post_template'] + ".html"

if not os.path.exists(opt['src']):
    print(f"creating input dir {opt['src']}/...")
    os.mkdir( opt['src'] )
if not os.path.exists( opt['out'] ):
    print(f"creating output dir {opt['out']}/...")
    os.mkdir( opt['out'] )


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
    except Exception as err:
        print(f"Error: could not process file {post["file_name"]}, err: {err}")
        exit()

    if "post_subtitle" in post:
        template = template.replace("{{subtitle}}", f"<h4>{post['post_subtitle']}</h4>")
    else:
        template = template.replace("{{subtitle}}", "")
    return template

posts = []

def process_notes(post):
    soup = Soup(post, 'html.parser')
    # Link subscript counter
    i = 1
    links = []
    has_links = False
    for a in soup.find_all('a'):
        href = a['href']
        if href.startswith("#"):
            continue
        has_links = True
        text = a.string
        if href == "_":
            aside = soup.new_tag('span')
            aside["class"] = "aside"

            sm = soup.new_tag('small')
            sm.string = f"{i}."

            aside.append(sm)
            aside.append(" ")
            aside.append(text)

            sup = soup.new_tag('sup')
            _a = soup.new_tag('a', href=f"#note-{i}")
            _a["id"] = f"link-{i}"
            _a.string = f"[{i}]"
            sup.append(_a)

            a.replace_with(sup)
            sup.insert_after(aside)
            links.append({"body": text})            
        else:
            # Is a proper link
            link = soup.new_tag('a')
            link["href"] = href
            link.string = text
            link.append(" ")

            sup = soup.new_tag('sup')
            _a = soup.new_tag('a', href=f"#note-{i}")
            _a["id"] = f"link-{i}"
            _a.string = f"[{i}]"
            sup.append(_a)

            a.replace_with(link)
            link.insert_after(sup)
            links.append({"body": href})
        i += 1
    return (has_links, links, str(soup))

def build_footnotes(post, links):
    soup = Soup(post, 'html.parser')
    sec = soup.new_tag('section')
    title = soup.new_tag('h2')
    title.string = "Footnotes + Links"
    sec.append(title)
    ls = soup.new_tag('ul')
    j = 1
    for link in links:
        li = soup.new_tag('li')
        li['id'] = f"note-{j}"

        a = soup.new_tag('a', href=f"#link-{j}")
        a.string = f"[{j}]"

        li.append(a)
        li.append(" ")
        li.append(link["body"])

        ls.append(li)
        j += 1
    sec.append(ls)
    soup.append(sec)
    return str(soup)
    

def process_posts():
    # Globbed files are unsorted >:[
    post_list = sorted(glob.glob(f"{opt['src']}/**/*.md", recursive=True))
    for f in post_list:
        post = {}
        file_name = os.path.basename( f )
        destination = os.path.join( opt['out'] , os.path.splitext( file_name )[ 0 ] + ".html" )
        destination.rstrip(".md")

        if not opt['force'] and not dirty(f, destination):
            continue

        # Read and preprocess the source file.
        print(f"generating {f}...")
        template = open(f"{opt['res']}/{opt['post_template']}", 'r').read()
        with open( f, 'r' ) as file:
            post = preprocess_file(file)
            post['post_content'] = markdown.markdown( post["post_content"] )
            if not (file.name == "src/archive.md"):
                (ok, links, post['post_content']) = process_notes(post['post_content'])
                if ok:
                    post['post_content'] = build_footnotes(post['post_content'], links)
        post["dest"] = destination

        # skip file if the current file is a list file rather than a post file.
        if f.lstrip(opt['src']+"/").rstrip(".md") in opt['list_files']:
            continue

        print(f"creating file {destination}...")
        with open( destination, 'w', encoding="utf-8" ) as file:
            template = format_file(post, template)
            file.write(template)
        posts.append(post)


def process_index(file: str):

    # list index template file.
    index = open(f'{opt['res']}/{opt['list_template']}', 'r').read()
    content = open(f'{opt['src']}/{file}.md', 'r').read()
    content = markdown.markdown(content)
    list = ''
    last_year = "0"
    file_name = f"{opt['out']}/{file}.html"

    for post in reversed(posts):
        year = "".join(post['post_date']).split('.')[0]
        if not (year == last_year):
            # Nasty little hack, but i have a slight headache and i'm losing 
            # my will to keep working on this script anymore today.
            # ( he says as if he wouldn't put in nasty little hacks in his code otherwise )
            last_year = year
            list += f"<h3>{last_year}</h3>"
        list += "<li>"
        list += "<a href=\"/" + post['dest'] + "\">"
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
    file = f"{opt['src']}/{post}"
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

def build_parser():
    common = argparse.ArgumentParser(add_help=False, description="Jenny — small static site generator :)")
    common.add_argument("--src", default=opt['src'], help="input files directory")
    common.add_argument("--out", default=opt['out'], help="output files directory")
    common.add_argument("--assets", default=opt['res'], help="template / assets directory")
    common.add_argument("--list-template", default=opt['list_template'], help="template used for list pages")
    common.add_argument("--post-template", default=opt['post_template'], help="template used for posts")
    common.add_argument("--list-files", nargs="*", default=opt['list_files'], help="source names that are list pages")
     
    parser = argparse.ArgumentParser(prog="jenny", parents=[common])
    sub = parser.add_subparsers(dest="command")
 
    build = sub.add_parser("build", help="build the site, only regenerating stale files", add_help=True)
    build.add_argument("--force", action="store_true", help="regenerate everything")
 
    new = sub.add_parser("new-post", help="create a new post")
    new.add_argument("--title", help="post title, prompted for if omitted")

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return

    opt['src'] = args.src
    opt['out'] = args.out
    opt['res'] = args.assets
    opt['list_template'] = args.list_template
    opt['post_template'] = args.post_template
    opt['list_files'] = args.list_files
    opt['force'] = getattr(args, "force", False)

    # print(f"src is {opt['src']}")
    # print(f"out is {opt['out']}")
    # print(f"res is {opt['res']}")
    # print(f"list_template is {opt['list_template']}")
    # print(f"post_template is {opt['post_template']}")
    # print(f"list_files is {opt['list_files']}")
        
    if args.command == "build":
        process_posts()
        for f in opt['list_files']:
            print(f"processing {f}...")
            process_index(f)
    elif args.command == "new-post":
        print("Input a name for your post:")
        name = input()
        create_new_post(name)

if __name__ == "__main__":
    main()
