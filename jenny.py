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
    content=''
    title=''
    title_id=''
    subtitle=''
    date=''
    for line in file:
        stripped = line.lstrip()

        if stripped.startswith('@'):
            command,_,args = stripped.rstrip('\n').lstrip('@').partition(' ')
            args = args.strip()

            if command == 'date':
                date = args
            elif command == 'subtitle':
                subtitle = args
        elif stripped.startswith('\\'):
            content += stripped[2:]
        elif stripped.startswith('# '):
            title = stripped.rstrip('\n').lstrip('# ').lstrip(' ')
            title_id = title.replace(" ", "-").lower()
        elif stripped.startswith('##'):
            data = stripped.rstrip('\n').lstrip('##').lstrip(' ')
            id = data.replace(" ", "-").lower()
            content += "<h2 id=\"" + id + "\"> <a href=\"#" + id + "\">" + data + "</a></h2>"

        else:
            content += line
    return {"content": content, "title": title, "title_id": title_id, "date": date, "subtitle": subtitle}
# PREPROCES FILE END

def format_file(post, template):
    template = template.replace("{{content}}", post['content'])
    template = template.replace("{{title}}", post['title'])
    template = template.replace("{{subtitle}}", post['subtitle'])
    template = template.replace("{{title_id}}", post['title_id'])
    template = template.replace("{{date}}", post['date'])
    return template

posts = []
if not os.path.exists( 'public' ):
    os.mkdir( 'public' )

def process_posts():
    for f in glob.iglob( 'src/**/*.md', recursive=True):
        post = {}
        template = open('assets/template.html', 'r').read()
        with open( f, 'r' ) as file:
            post = preprocess_file(file)
            post['content'] = markdown.markdown( post["content"] )

        file_name = os.path.basename( f )
        destination = os.path.join( "public", os.path.splitext( file_name )[ 0 ] + ".html" )
        post["dest"] = destination

        with open( destination, 'w' ) as file:
            template = format_file(post, template)
            file.write(template)
        posts.append(post)

def process_index():
    index = open('assets/index_template.html', 'r').read()
    content = ''

    for post in reversed(posts):
        content += "<div class=\"post\">"
        content += "<span>" + post['date'] + "</span>"
        content += "<a href=\"" + post['dest'] + "#main\">"
        content += post['title']
        content += "</a></div>"

    with open ('index.html', 'w') as file:
        index = index.replace("{{title}}", posts[-1]['title'])
        index = index.replace("{{date}}", posts[-1]['date'])
        index = index.replace("{{subtitle}}", posts[-1]['subtitle'])
        index = index.replace("{{latest}}", posts[-1]['content'])
        index = index.replace("{{posts}}", content)
        file.write(index)

process_posts()
process_index()
