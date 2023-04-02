# jenny
small static site generator mostly for my personal use
i wrote a blog post about it [here](https://derpyzza.github.io/public/01_about-jenny.html)

# Usage
just run `jenny`, or `jenny build`.

# Build instructions
```go
go build
```

# Installation
```
git clone git@github.com:derpyzza/jenny.git
cd jenny
```

# Changelog

- v.0.0.1
	- Reimplements basic features of jenny.py, but in go.
		- reads data from markdown source directory
		- reads in templates from template directory
		- mashes them together
		- places the output `.html` file into an output directory
	- Has very very very basic commandline args support. ( flagless )
	- Uses built in template replacing, so it's *ahem* "opinionated" ( as in if it doesn't fit my workflow it doesn't work ). 
		This will be fixed in a later version.
