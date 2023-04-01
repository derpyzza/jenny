## Static site generator

	[ ] Migrate python script to Go

	[X] Initialize project ;)

	[X] Read markdown files in source folder.

	[X] Preprocess source files and extract metadata from them.

	[X] Convert markdown to html files.

	[X] Feed html data into templates and generate final html file with templates.

	[X] Place final html file into Public folder.

	[X] Update Index page with the latest html file.

	[ ] Add command line arguements and such
	--> [ ] 	Init: Initialize a new site
	--> [X] 	Build: Build a site
				| 		Flags:
				| 		[ ] -v, verbose
				| 		[ ] -o, --output, output directory
				| 		[ ] -s, --source, source directory
				| 		[ ] -t, --template, template directory
	--> [ ] Help: Help command

	[ ] Add support for config files.
	--> [ ] 	Replace manual variable replacement with automatic
				| 	letting the user choose and define their own site layout. so
				| 	instead of this being constrained to blog posts it can 
				| 	be used for whatever the user wants it to do.
