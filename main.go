package main

import (
	// stdlib
	"bufio"
	// "fmt"
	"os"
	"path/filepath"
	"strings"

	// third-party
	"github.com/charmbracelet/log"
	"github.com/gomarkdown/markdown"
	"github.com/gomarkdown/markdown/html"
	"github.com/gomarkdown/markdown/parser"
)

// source directory, should contain markdown (.md) files :)
const SRCDIR string = "./src/";
const TEMPDIR string = "./templates/";
const PUBDIR string = "./public/";

type Post struct {
	title string;
	subtitle string;
	date string;
	tags string;
	content string;
}

/*
	Iterates through the source directory,
	and checks every file to see if it's a markdown
	file. If so, it stuffs the file's name into an array and returns
	the array of file names.
*/
func GetSourceFiles() []string {
	files, err := os.ReadDir(SRCDIR);

	var srcFiles []string;

	if err != nil {
		log.Error(err)
	}

	log.Info("Fetching Source Files");
	for _, file := range files {
		log.Info("Found", "file", file.Name());
		if filepath.Ext(file.Name()) == ".md" {
			// fmt.Println("Correct format!");
			fileName := strings.TrimRight(file.Name(), ".md");
			srcFiles = append(srcFiles, fileName);
		}
	}
	return srcFiles;
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
*/
func PreprocessFile(file string) Post {

// messy, TODO: clean

	post := Post{};

	path := SRCDIR + file + ".md"
	rawFile, err := os.Open(path);
	if err != nil {
		log.Fatal(err);
	}

	scanner := bufio.NewScanner(rawFile);

	for scanner.Scan() {
		line := scanner.Text();
		str := strings.TrimRight(line, " ");

		if strings.HasPrefix(str, "@") {
			str = strings.TrimLeft(str, "@");
			str = strings.TrimRight(str, "\t");
			split := strings.Split(str, "<-");
			command := split[0];
			command = strings.TrimRight(command, "\t");
			command = strings.TrimRight(command, " ");

			if command == "title" {
				log.Debug("Command found, 'TITLE'", "cmd", command );
				post.title = string(split[1])
			} else if command == "subtitle" {
				log.Debug("Command found, 'SUBTITLE'", "cmd", command );
				post.subtitle = string(split[1])
			} else if command == "date" {
				log.Debug("Command found, 'DATE'", "cmd", command );
				post.date = string(split[1])
			} else if command == "tags" {
				log.Debug("Command found, 'TAGS'", "cmd", command );
				post.tags = string(split[1])
			} else {
				log.Debug("Unknown command", "cmd", command );
			}
		} else {
			post.content = post.content + "\n" + line;
		}
	}

	if scanner.Err() != nil {
		log.Fatal(scanner.Err())
	}

	// log.Info("", "POST", post);
	return post;
}

/*
Takes in a file, 
*/
func FormatContent(content string) string {

	// path := SRCDIR + file + ".md"
	// rawFile, err := os.ReadFile(path);
	// if err != nil {
	// 	log.Fatal(err);
	// }
	log.Info("Converting to markdown")
	md := []byte(content)
	md = markdown.NormalizeNewlines(md);

	extensions := parser.CommonExtensions | parser.AutoHeadingIDs;
	p := parser.NewWithExtensions(extensions);

	doc := p.Parse(md);

	// create HTML renderer
	htmlFlags := html.CommonFlags | html.HrefTargetBlank
	opts := html.RendererOptions{Flags: htmlFlags}
	renderer := html.NewRenderer(opts)

	html := markdown.Render(doc, renderer)

	return string(html[:]);
}

func TemplateFile(post Post, template string) (string, error) {
	path := TEMPDIR + template + ".html"
	templateRaw, err := os.ReadFile(path);	

	log.Info("Templating file");
	postFile := string(templateRaw[:]);

	postFile = strings.Replace(postFile, "{{content}}", post.content, 1);
	postFile = strings.Replace(postFile, "{{title}}", post.title, 1);
	postFile = strings.Replace(postFile, "{{subtitle}}", post.subtitle, 1);
	postFile = strings.Replace(postFile, "{{date}}", post.date, 1);
	postFile = strings.Replace(postFile, "{{tags}}", post.tags, 1);
	postFile = strings.TrimRight(postFile, "\n");

	// fmt.Println(postFile)
	
	return postFile, err;
}

// meat and bones of the app;
func jennyrate() {
	files := GetSourceFiles();

	for _, f := range files {
		log.Info("Jennyrating ", "file", f);
		post := PreprocessFile(f);
		post.content = FormatContent(post.content);

		html, err := TemplateFile(post, "post");
		if err != nil {
			log.Error(err);
			continue;
		}

		path := PUBDIR + f + ".html";
		file, ferr := os.Create(path)
		if ferr != nil {
			log.Error(ferr);
			continue;
		}

		defer file.Close();

		_, err = file.WriteString(html);
		if err != nil {
			log.Error(err);
			continue;
		}
	}
}

func main() {
	log.Info("Initialized jenny");
	jennyrate();
	// post := Post {
	// 	title: "Post title",
	// 	subtitle: "Post subtitle",
	// 	date: "23-03-20",
	// 	tags: "#hello #there",
	// 	content: "this is post content :)",
	// }
	// TemplateFile(post, "post")
	//
	// PreprocessFile("other")

}
