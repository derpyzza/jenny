package main

import (
	"bufio"
	"fmt"
	"os"
	"path/filepath"
	"sort"
	"strings"

	// third-party
	"github.com/charmbracelet/log"
	"github.com/gomarkdown/markdown"
	"github.com/gomarkdown/markdown/html"
	"github.com/gomarkdown/markdown/parser"
)

const SRCDIR string = "./src/"
const TEMPDIR string = "./templates/"
const PUBDIR string = "./public/"

func report(err error) bool {
	if err != nil {
		log.Error(err)
		return true
	}
	return false
}

func fatal(err error) bool {
	if err != nil {
		log.Fatal(err)
		return true
	}
	return false
}

type Post struct {
	title    string
	subtitle string
	date     string
	content  string
}

type indexData struct {
	// date string;
	slug     string
	title    string
	subtitle string
}

/*
Iterates through the source directory,
and checks every file to see if it's a markdown
file. If so, it stuffs the file's name into an array and returns
the array of file names.
*/
func GetSourceFiles() []string {
	files, err := os.ReadDir(SRCDIR)

	var srcFiles []string

	if err != nil {
		log.Error(err)
	}

	log.Info("Fetching Source Files")
	for _, file := range files {
		log.Info("Found", "file", file.Name())
		if filepath.Ext(file.Name()) == ".md" {
			fileName := strings.TrimRight(file.Name(), ".md")
			srcFiles = append(srcFiles, fileName)
		}
	}
	return srcFiles
}

/*
Loops over every line in a given file and
searches for the template metadata. template
metadata is defined inside a block with a
beginning and an end marker in order to be able
to quickly exit out of a file when all the
relevant data has been extracted from the file.

metadata begins with an "@" symbol, followed immediately
by the key name, followed by a "<-" marker, and then everything
after that until a newline is accepted as the value.

TODO: replace pathetic metadata parsing with yaml header
*/
func PreprocessFile(file string) Post {

	// messy, TODO: clean

	post := Post{}

	path := SRCDIR + file + ".md"
	rawFile, err := os.Open(path)
	if err != nil {
		log.Fatal(err)
	}

	scanner := bufio.NewScanner(rawFile)

	for scanner.Scan() {
		line := scanner.Text()
		str := strings.TrimRight(line, " ")

		if strings.HasPrefix(str, "@") {
			str = strings.TrimLeft(str, "@")
			str = strings.TrimRight(str, "\t")
			split := strings.Split(str, "<-")
			command := split[0]
			command = strings.TrimRight(command, "\t")
			command = strings.TrimRight(command, " ")

			if command == "title" {
				log.Debug("Command found; ", "cmd", command)
				post.title = string(split[1])
			} else if command == "subtitle" {
				log.Debug("Command found; ", "cmd", command)
				post.subtitle = string(split[1])
			} else if command == "date" {
				log.Debug("Command found; ", "cmd", command)
				post.date = string(split[1])
			} else {
				log.Debug("Unknown command; ", "cmd", command)
			}
		} else {
			post.content = post.content + "\n" + line
		}
	}

	if scanner.Err() != nil {
		log.Fatal(scanner.Err())
	}

	return post
}

func FormatContent(content string) string {

	log.Info("Converting to markdown")
	md := []byte(content)
	md = markdown.NormalizeNewlines(md)

	extensions := parser.CommonExtensions | parser.AutoHeadingIDs
	p := parser.NewWithExtensions(extensions)

	doc := p.Parse(md)

	// create HTML renderer
	htmlFlags := html.CommonFlags | html.HrefTargetBlank
	opts := html.RendererOptions{Flags: htmlFlags}
	renderer := html.NewRenderer(opts)

	html := markdown.Render(doc, renderer)

	return string(html[:])
}

func TemplateFile(post Post, template string) (string, error) {
	path := TEMPDIR + template + ".html"
	templateRaw, err := os.ReadFile(path)

	log.Info("Templating file")
	postFile := string(templateRaw[:])

	postFile = strings.Replace(postFile, "{{content}}", post.content, 1)
	postFile = strings.Replace(postFile, "{{title}}", post.title, 1)
	postFile = strings.Replace(postFile, "{{subtitle}}", post.subtitle, 1)
	postFile = strings.Replace(postFile, "{{date}}", post.date, 1)
	postFile = strings.TrimRight(postFile, "\n")

	return postFile, err
}

// meat and bones of the app;
func Jennyrate() {
	files := GetSourceFiles()

	posts := make(map[string]indexData)

	for _, f := range files {
		log.Info("Jennyrating ", "file", f)

		post := PreprocessFile(f)
		post.content = FormatContent(post.content)

		html, err := TemplateFile(post, "post")
		if report(err) {
			continue
		}

		htmlf := strings.ReplaceAll(f, " ", "-")
		path := PUBDIR + htmlf + ".html"
		file, ferr := os.Create(path)
		if report(ferr) {
			continue
		}

		defer file.Close()

		_, err = file.WriteString(html)
		if report(err) {
			continue
		}
		log.Info("Wrote", "file", path+"!")

		posts[post.date] = indexData{slug: PUBDIR + htmlf + ".html", title: post.title, subtitle: post.subtitle}
	}

	var indices []string

	dates := make([]string, 0, len(posts))

	for k := range posts {
		dates = append(dates, k)
	}

	sort.Strings(dates)	

	path := TEMPDIR + "post-card.html"
	templateRaw, err := os.ReadFile(path)

	for _, v := range dates {
		post := posts[v]
		str := string(templateRaw[:])
		str = strings.Replace(str, "{{slug}}", post.slug, 1)
		str = strings.Replace(str, "{{title}}", post.title, 1)
		str = strings.Replace(str, "{{subtitle}}", post.subtitle, 1)
		str = strings.Replace(str, "{{date}}", v, 1)
		// str := `
		// <div>
		// <a href="` + PUBDIR + post.slug + `">
		// ` + "<h1>" + post.title + "</h1>" + `
		// <h2>` + post.subtitle + "</h2>" + `
		// <h2>` + v + "</h2>" + "\n</a></div>"
		indices = append(indices, str)
	}

	fmt.Println(indices)

	// path := TEMPDIR + template + ".html"
	rawIndexTemplate, err := os.ReadFile(TEMPDIR + "index.html")
	indexTemplate := string(rawIndexTemplate[:])
	var str string

	for _, v := range indices {
		str = str + "\n" + v
	}

	indexTemplate = strings.Replace(indexTemplate, "{{posts}}", str, 1)

	file, ferr := os.Create("index.html")
	report(ferr)

	defer file.Close()

	_, err = file.WriteString(indexTemplate)
	report(err)
	// log.Info("Wrote", "file", path+"!")
}

const helpMessage = `
Welcome to jenny!
version: 0.0.1

this is help text :), use 'jenny build' to build your site!`;


func main() {
	for _, s := range os.Args[1:] {
		switch s {
			case "build":
				fmt.Println("Building...")
				Jennyrate()
			case "help":
				fmt.Println(helpMessage)

			default:
				fmt.Println("no commands found")
		}
	}
	// buildPtr := flag.Bool("v", false, "verbose");
	// flag.Parse();
	// fmt.Println("verbose: ", *buildPtr)
	// defer Jennyrate()
}
