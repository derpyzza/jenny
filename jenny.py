#!/bin/python3

import os
import glob
import markdown

if not os.path.exists( 'public' ):
    os.mkdir( 'public' )

template = open('template.html', 'r').read()

for f in glob.iglob( 'src/*.md' ):
    with open( f, 'r' ) as file:
        raw = file.read()
        html = markdown.markdown( raw )

    file_name = os.path.basename( f )
    destination = os.path.join( "public", os.path.splitext( file_name )[ 0 ] + ".html" )

    with open( destination, 'w' ) as file:
        template = template.replace("{{content}}", html)
        file.write(template)
