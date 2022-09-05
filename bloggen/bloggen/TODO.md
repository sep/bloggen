# Bugs:

### It is possible for the user to execute bloggen.py from outside of the pypi/src dir. See below:

```
(bloggen) lee@porkbelly bloggen % python pypi-package/src/bloggen.py --generate wallet_notes
Traceback (most recent call last):
  File "/Users/lee/bloggen/pypi-package/src/bloggen.py", line 54, in <module>
    main()
  File "/Users/lee/bloggen/pypi-package/src/bloggen.py", line 9, in main
    config = Configure()
  File "/Users/lee/bloggen/pypi-package/src/config.py", line 10, in __init__
    self.active_config = self.get_active_config()
  File "/Users/lee/bloggen/pypi-package/src/config.py", line 33, in get_active_config
    with open('.bloggen/config.json') as f:
FileNotFoundError: [Errno 2] No such file or directory: '.bloggen/config.json'
```

### How do you publish a site?

I think you have to --publish [path_to_local_static_site]
Make this work without passing the path to a site.

# How

Make the class that changes links a class that references the provider defined in a central config file

# Next

The user provides a notes directory.
Bloggen should derive the structure of the user's blog from the notes dir.
Bloggen should interpret every folder as a new blog node.

## Strategy for generating site_info

### data

the contents of site_info.data might change.
create a modular function that composes itself of provided functions. For example:

```
def build_siteinfo_data(extract_subject, extract_content, extract_tags, generate_metadata, generate_id, notes):
	return [{"id": generate_id(note), "subject": extract_subject(note), "content": extract_content(note), "tags": extract_tags(note), "metadata": generate_metadata(note)} for note in notes]
```

### relationships

bfs or dfs using os.scandir()
Learn why it's better to use one over the other

## How?

When user runs --generate, bloggen creates a site.info file

Steps:

- create index
- create relationship graph
- populate data

_These steps can happen in parallel_

# Next next

Bloggen generates static site from code. At present, bloggen only populates a template.

## Why?

publishing the package with a template inside of it feels bad.

### Why?

I don't want to add weight to the package.

### What if you did?

The package would weigh 44k more. Also, it would contain an extra folder. I would feel like my perfect system is less clean.

### Potential pros of leaning in to it?

I could plop the template into the user's filesystem. Users could edit the template directly or make a copy of the template. Bloggen could import user-created templates, store them as `templates` in a json, and let the user add their template names to `"metadata":{template-style:"Kevin's Template"}`.

### What would I rather do?

Store the schema of the root template in json. Write a template-inflater to read the instructions of the json and generate the template when it is needed. Allow users to create their own templates with json.

### Why would I rather do it?

I want to write a dsl. I want to say that my app uses a dsl. I want to say that I have written a dsl.

## What implementation do both approaches share?

Bloggen imports template. bs4 imports html. bs4 imports and edits html according to defined user parameters.

##

```
Bloggen:

As notes:
-> phase 1:
	deployment tool
		-> support for multiple configurations
			eg buckets, platforms
			a local config file: a json that stores data for each configuration
				data is:

		-> users might want to create distinct clusters of notes
			- create an abstract structure for note-sets. Make this a structure nest-able
-> phase 2:
	associate notes with one another
		1. Tags, preceded by a specific symbol, in the footer of the file
		2. Explicit links, in the footer of the file —> use Andy M’s janitor tool to insert backlinks. format: [[ ]]
-> phase 3:
	enhance note-reading experience:
		load and render linked notes as pop-up boxes, like on Andy M’s site: https://notes.andymatuschak.org/About_these_notes
-> phase 4:
	enhance note-taking feature set


As blog:
-> phase 1:
	style presets for each note
		-> this makes blogger versatile:
			1. Posts for people to see, read, and follow
			2. Understand subject in a context of a the given note
				1. some notes will be graphs that show relationships of ideas
				2. Some notes with be short essays
				3. Some notes will compare images
				4. Some notes will associate images with text
				5. Some notes are todo lists
-> phase 2:
	IoC: let users associate js with their notes
	- maybe even with note structures?
```