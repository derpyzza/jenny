#!/bin/python3

import os
import glob
import markdown
import commonmark

# TODO read config files
    # what kinda configs?? idk
# DONE read in markdown files
# DONE read in template file
# DONE convert markdown to html
# DONE write html out using the template
# DOING generate an index using all the title ids

def preprocess_file(file):
        # preprocess the file for metadata. 
        # metadata in this implementation just starts with a "$" symbol, followed by a command name and command args
        # current commands are:
        #
        # title:    the document title, to be displayed at the top of the document and also on the main page to represent
        #           the corresponding blog page
        # subtitle: same as title, but smaller and longer. kind of a summary in a way.
        # date:     the date on which the post was published or written. to be displayed at the top of the document and also
        #           the main page
    content=''
    title=''
    subtitle=''
    date=''
    for line in file:
        stripped = line.lstrip()

        if stripped.startswith('$'):
            command,_,args = stripped.rstrip('\n').lstrip('$').partition(' ')
            args = args.strip()

            if command == 'title':
                title = args
            elif command == 'date':
                date = args
            elif command == 'subtitle':
                subtitle = args
        elif stripped.startswith('\\'):
            content += stripped[2:]
        elif stripped.startswith('##'):
            data = stripped.rstrip('\n').lstrip('##').lstrip(' ')
            id = data.replace(" ", "-").lower()
            content += "<h2 id=\"" + id + "\">" + data + "</h2>"
            ids.append({"id": id, "data": data})

        else:
            content += line
    return {"content": content, "title": title, "subtitle": subtitle, "date": date}
# PREPROCES FILE END

def format_file(post, template):
    template = template.replace("{{content}}", post['content'])
    template = template.replace("{{title}}", post['title'])
    template = template.replace("{{subtitle}}", post['subtitle'])
    template = template.replace("{{date}}", post['date'])
    return template

def generate_index(post, ids):
    if ids == []:
        return
    index = "<div class=\"index\">\n<h3>Index</h3>\n<ul>"
    for id in ids:
        print(id["id"])
        index += "<li><a href=\"#" + id["id"] + "\">" + id["data"] + "</a></li>\n"
    index += "</ul></div>"
    post["content"] = index + post["content"]
    return post

posts = []
if not os.path.exists( 'public' ):
    os.mkdir( 'public' )

for f in glob.iglob( 'src/*.md' ):
    post = {}
    ids = []
    template = open('assets/template.html', 'r').read()
    with open( f, 'r' ) as file:
        post = preprocess_file(file)
        post = generate_index(post, ids)
        post['content'] = markdown.markdown( post["content"], extensions=[ 'extra', 'codehilite', 'toc', 'superscript'] )

    file_name = os.path.basename( f )
    destination = os.path.join( "public", os.path.splitext( file_name )[ 0 ] + ".html" )
    post["dest"] = destination

    with open( destination, 'w' ) as file:
        template = format_file(post, template)
        file.write(template)
    posts.append(post)

index = open('assets/index_template.html', 'r').read()
content = ''

for post in posts:
    content += "<a href=\"" + post['dest'] + "\" class=\"post\">"
    content += "<div class=\"content\">" + "<div class=\"post-title\">"
    content += "<h2>" + post['title'] + "</h2>"
    content += "<h4>" + post['date'] + "</h4>"
    content += "</div> <p>" + post['subtitle'] + "</p> </div> </a>"

with open ('index.html', 'w') as file:
    index = index.replace("{{posts}}", content)
    file.write(index)
