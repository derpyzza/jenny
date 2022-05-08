#!/bin/python3

import os
import glob
import markdown

if not os.path.exists( 'public' ):
    os.mkdir( 'public' )

template = open('template.html', 'r').read()
title = ''
content = ''

for f in glob.iglob( 'src/*.md' ):
    with open( f, 'r' ) as file:
        for line in file:
            stripped = line.lstrip()

            if stripped.startswith('$'):
                print("yes")
                command,_,args = stripped.rstrip('\n').lstrip('$').partition(' ')
                args = args.strip()
                print(command, args)

                if command == 'title':
                    title = args
                    print(title)
            else:
                content += line
        #print(content)
        raw = file.read()
        html = markdown.markdown( content )

    file_name = os.path.basename( f )
    destination = os.path.join( "public", os.path.splitext( file_name )[ 0 ] + ".html" )

    with open( destination, 'w' ) as file:
        template = template.replace("{{content}}", html)
        template = template.replace("{{title}}", title)
        file.write(template)
