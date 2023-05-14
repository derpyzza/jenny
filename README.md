# jenny
small static site generator mostly for my personal use

# Usage
you'll need python3 installed, along with the markdown package from pip:

```sh
$ pip install markdown
```

after that simply create your blog's root directory, along with three subdirectories:

```sh 
$ mkdir $YOUR_BLOG_NAME_HERE && cd $YOUR_BLOG_NAME_HERE
$ mkdir assets/ public/ src/
```

`assets/` is where you'll be placing all your html templates. jenny expects two: `assets/index_template.html` & `assets/template.html`. those names are hardcoded into the script for now :)
`src/` is where all your markdown files go.
`public/` is where all your outputted html files shall reside.

that is all. enjoy :)

## TODO

- [ ] Add some way to split posts apart based off of date e.g `0523 = [ post_1, post_2] # All posts of May 2023`
