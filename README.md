# jenny

A tiny minimalistic static site generator, geared towards generating a simple blog site.

# Usage

You'll need python3 installed, along with the markdown package from pip:

```sh
$ pip install markdown
```

After that simply run the jenny script which will generate project files for you

```sh 
$ python3 jenny.py
```

or make the script into an executable and run it directly:

```sh
$ sudo chmod +x jenny.py
$ ./jenny.py
```
Jenny then creates three folders:
`assets/` is where you'll be placing all your html templates. 
Jenny by default expects two: `assets/index_template.html` & `assets/template.html`. 
`src/` is where all your markdown files go.
`public/` is where all your outputted html files are placed.

After generating the needed folders, you can either create a new post by using the `new-post` command or compile any existing `.md` files into html by using the `build` command:

```sh
$ ./jenny.py build

$ ./jenny.py new-post
```

Each post expects two metadata variables at the top: `post_title` and `post_date`, with a third optional `post_subtitle` variable.

Variables are defined at the top of the source `.md` file, and are defined using the following syntax:

```
@variable_name variable value
@list_variable item_one + item2 + item three + item, four
---
```

The variables section requires a stop marker of three hyphens `---` at the end so that the interpreter knows to stop looking for more variables.
Everything after the stop marker is treated as post content.

Jenny expects four variables to be present in the template files by default: `{{title}}`, `{{date}}`, `{{subtitle}}` and `{{content}}`. 
Since jenny is a very minimalist script, the user is expected to edit the source to add any extra variables that they may need.

These template variables are then replaced with their corresponding values from the source file, with the exception of `{{content}}`, which is built in to jenny itself, and represents the post content.

That is all. enjoy :)