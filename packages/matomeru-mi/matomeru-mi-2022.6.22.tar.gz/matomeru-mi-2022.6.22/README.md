# Markdown-like Markup Interpreter

## Project goal
Initially the idea was to use Markdown for making ODT files which will be
compilant with GOST 7.32-2017. But as things were going the goal expanded
to making an ODT from markup file and a template directory.

Possibly this project can be used as a library for a web-service, but there is no info about such use.

## Installation and use
### Via git
Clone the repository:
```
git clone https://gitlab.com/Fe-Ti/matomeru-mi.git
```
Run install.sh script (on *BSD, *Linux and others):
```
./install.sh
```
If everything was left as default then running a command below creates a zip
archive with ODT structure:
```
matomeru-mi -if <input file> -of <output file>
```
For example
```
matomeru-mi -if README.md -of README.odt
```

### Via pip
Run:
```
python3 -m pip install --upgrade matomeru-mi
```
Then the package will be downloaded. The execution is simple:
```
python3 -m matomerumi -if <input file> -of <output file>
```

## Syntax
Consult Syntax.md (or a page in project documentation).

## Implemented stuff
- [x] Paragraphs, headings and code blocks (paragraphs with monospace font);
- [x] Basic picture handling support;
- [x] Creation of multilevel numbered and bulleted lists;
- [x] Basic page break support;
- [x] Support for relative and absolute paths.

## Ideas
- [x] No temporal directory;
- [x] PIP package;
- [ ] Title page support;
- [ ] Styling Engine;
- [ ] Documentation;
- [ ] Escape characters support;
- [ ] CI;
- [ ] Spreadsheets in docs.

## Documentation
For syntax reference consult: [Syntax](https://fe-ti.gitlab.io/matomeru-mi/md_Syntax.html)

Documentation for library: [Main page](https://fe-ti.gitlab.io/matomeru-mi/index.html)

```
Copyright 2021 Fe-Ti
```
