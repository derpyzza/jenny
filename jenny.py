#!/bin/python3

import os
import glob
import markdown
import commonmark

# generate an index.html file if it does not exist yet
# read an index template, and 
posts = []

if not os.path.exists( 'public' ):
    os.mkdir( 'public' )


for f in glob.iglob( 'src/*.md' ):
    content = ''
    title = ''
    date = ''
    subtitle = ''
    template = open('assets/template.html', 'r').read()
    with open( f, 'r' ) as file:
        # preprocess the file for metadata. 
        # metadata in this implementation just starts with a "$" symbol, followed by a command name and command args
        # current commands are:
        #
        # title:    the document title, to be displayed at the top of the document and also on the main page to represent
        #           the corresponding blog page
        # subtitle: same as title, but smaller and longer. kind of a summary in a way.
        # date:     the date on which the post was published or written. to be displayed at the top of the document and also
        #           the main page
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
            else:
                content += line
        raw = file.read()
        html = markdown.markdown( content, extensions=[ 'extra', 'codehilite', 'toc', 'superscript'] )
        # print( "file: " + f + " content: \n" + content )

    file_name = os.path.basename( f )
    destination = os.path.join( "public", os.path.splitext( file_name )[ 0 ] + ".html" )
    # print( f + " title = " + title + " date = " + date + " subtitle = " + subtitle )
    # print(f + " : " + destination)

    with open( destination, 'w' ) as file:
        template = template.replace("{{content}}", html)
        template = template.replace("{{title}}", title)
        template = template.replace("{{date}}", date)
        template = template.replace("{{subtitle}}", subtitle)
        # print(f + "/" + destination + " : \n" + template)
        file.write(template)
    posts.append({  "post"      : destination,
                    "title"     : title,
                    "date"      : date,
                    "subtitle"  : subtitle })

index = open('assets/index_template.html', 'r').read()
content = ''

for post in posts:
    content += "<a href=\"" + post['post'] + "\" class=\"post\">"
    content += "<div class=\"content\">" + "<div class=\"post-title\">"
    content += "<h2>" + post['title'] + "</h2>"
    content += "<h4>" + post['date'] + "</h4>"
    content += "</div> <p>" + post['subtitle'] + "</p> </div> </a>"

# post = '''<a href="./public/00_test.html">
#     <div class="content">
#     <div class="post-title">
#         <h2>{{title}}</h2>
#         <h4>{{date}}</h4>
#     </div>
#     <p>{{subtitle}}</p>
#     </div>
#     </a>
# '''

with open ('index.html', 'w') as file:
    index = index.replace("{{posts}}", content)
    file.write(index)

print(posts)
