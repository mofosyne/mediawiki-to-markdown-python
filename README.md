MediaWiki to Markdown (Python)
=====================

Ported version of mediawiki-to-markdown to reduce dependencies and fix various issues with it (plus easier for everyone to maintain/contribute because of wider mindshare of python coders)

Convert MediaWiki pages to GitHub flavored Markdown (or other formats supported by Pandoc). The conversion uses an XML export from MediaWiki and converts each wiki page to an individual markdown file. Directory structures will be preserved. The generated export can also include frontmatter for Github pages.

* [Original PHP source](https://github.com/realrubberduckdev/mediawiki-to-markdown)
    - forked version of this codebase available at https://github.com/philipashlock/mediawiki-to-markdown
    - forked version of this codebase available at https://github.com/outofcontrol/mediawiki-to-gfm

## Motivation for porting/forking

The original PHP approach had some issue with dealing with wikipages with multiple revisions, seems to only read the first revision. So I've ported it to python so I can fix this issue. It's now fixed.

## Export MediaWiki Pages

Your first step is to export all your pages as a single XML file following these steps: http://en.wikipedia.org/wiki/Help:Export

### Sitewide dumping

If you are doing a full (text only) sitewide migration then follow these steps to get your `mediawiki_dump.xml`

1. Log into your mediawiki server
2. Enter your mediawiki instance. Your directory may look like this

    ```
    /var/mediawiki/html# ls
    api.php       CODE_OF_CONDUCT.md          COPYING  extensions  images        index.php    languages          maintenance         opensearch_desc.php  resources  skins              thumb.php
    autoload.php  composer.json               CREDITS  FAQ         img_auth.php  INSTALL      load.php           mediawiki_dump.xml  README.md            rest.php   tests              UPGRADE
    cache         composer.local.json-sample  docs     HISTORY     includes      jsduck.json  LocalSettings.php  mw-config           RELEASE-NOTES-1.35   SECURITY   thumb_handler.php  vendor
    ```

    you are interested in `maintenance/dumpBackup.php` and `LocalSettings.php`. Note that in the above example I already generated `mediawiki_dump.xml`. This is your goal.

3. run `php maintenance/dumpBackup.php --conf LocalSettings.php --full > mediawiki_dump.xml`
4. download `mediawiki_dump.xml` to your computer and move it to the folder containing this repo and `convert.py`
5. You are ready, so we can proceed to do the conversion steps below

## Running Without Docker

```bash
./convert.py --filename=mediawiki_dump.xml --output=output
```

### Requirements
* pandoc
* python3
* pip3 install lxml
* pip3 install pypandoc

## Running With Docker

**at the moment have issue with output being written as root. If you can fix that, that would be appreciated**

You can run `./convert` which will run this script below

```bash
docker build -t wiki2md .
sudo rm -rf output/
docker run -v .:/src/ -v ./output/:/src/output wiki2md --filename=mediawiki_dump.xml --output=/src/output
```

### Requirements
* Docker

----

### Further granular run parameters

To tailor the conversion process to your needs, you can utilize additional command-line arguments when running the `convert.py` script. Here are the available options:

#### --filename
The `filename` parameter is mandatory and specifies the XML file exported from MediaWiki, e.g.:

```bash
python3 convert.py --filename=mediawiki.xml
```

#### --output
Use `output` to define a custom output directory. Each wiki page from the XML file will be converted into a separate markdown file within this directory:

```bash
python3 convert.py --filename=mediawiki.xml --output=export
```

#### --indexes
Set `indexes` to `true` if you wish for pages with the same name as a directory to be renamed to `index.md` and placed within that directory:

```bash
python3 convert.py --filename=mediawiki.xml --output=export --indexes=true
```

#### --frontmatter
Determine whether to include frontmatter. It defaults to `true` when the output format is `markdown_github`:

```bash
python3 convert.py --filename=mediawiki.xml --output=export --format=markdown_phpextra --frontmatter=true
```

#### --format
Choose the output format with `format`. The default is `markdown_github`. Supported pandoc formats include:

```bash
python3 convert.py --filename=mediawiki.xml --output=export --format=markdown_phpextra
```

<details>
<summary>Supported pandoc formats are:</summary>

* asciidoc
* beamer
* context
* docbook
* docx
* dokuwiki
* dzslides
* epub
* epub3
* fb2
* haddock
* html
* html5
* icml
* json
* latex
* man
* markdown
* markdown_github
* markdown_mmd
* markdown_phpextra
* markdown_strict
* mediawiki
* native
* odt
* opendocument
* opml
* org
* plain
* revealjs
* rst
* rtf
* s5
* slideous
* slidy
* texinfo
* textile

</details>

#### --mdbook
The `--mdbook` argument will modify wikilinks to add the `.md` file extension, supporting compatibility with mdBook. When enabled, it will convert `[Text](Link "wikilink")` to `[Text](Link.md)`:

```bash
python3 convert.py --filename=mediawiki.xml --output=export --mdbook
```


