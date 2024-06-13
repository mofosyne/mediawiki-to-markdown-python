#!/usr/bin/env python3
import sys
import os
import re
import html
import argparse
from lxml import etree
import pypandoc

# This may cause issue if used with github pages repo
enable_permalink = False

def new_link(matches):
    if '|' not in matches[1]:
        link_text = matches[1]
        new_link = matches[1]
    else:
        link_text = matches[1].split('|')[1].strip()
        new_link = matches[1].split('|')[0].strip()
    new_link = new_link.replace(' ', '_')
    new_link = new_link.replace('?', '')

    if enable_permalink:
        return f"[[/{new_link}|{link_text}]]"

    return f"[[{new_link}|{link_text}]]"

def normalize_path(path):
    parts = []
    path = path.replace('\\', '/')
    path = re.sub(r'\/+', '/', path)
    segments = path.split('/')
    test = ''
    for segment in segments:
        if segment != '.':
            test = parts.pop() if parts else None
            if test is None:
                parts.append(segment)
            else:
                if segment == '..':
                    if test == '..':
                        parts.append(test)
                    if test == '..' or test == '':
                        parts.append(segment)
                else:
                    parts.append(test)
                    parts.append(segment)
    return '/'.join(parts)

def main():
    args = parse_arguments()

    if not args.filename:
        print("No input file specified. Use --filename=mediawiki.xml\n\n")
        exit(1)

    if args.output:
        output_path = args.output
        if not os.path.exists(output_path):
            print(f"Creating output directory {output_path}\n\n")
            os.makedirs(output_path)
    else:
        output_path = ''

    format = args.format
    add_meta = args.fm or (not args.fm and format == 'gfm')

    with open(args.filename, 'r', encoding='utf-8') as file:
        xml_string = file.read()

    format_ = args.format or 'gfm'
    add_meta = args.fm or (not args.fm and format_ == 'gfm')

    # Register the default namespace
    nsmap = {'mw': 'http://www.mediawiki.org/xml/export-0.11/'}

    xml = etree.fromstring(xml_string.encode('utf-8'))
    result = xml.xpath('//mw:page', namespaces=nsmap)
    count = 0
    directory_list = {}

    print(f"writing as {format_}")

    print(pypandoc.convert_text(" [[Hello Prez]] ", format='mediawiki', to=format_))

    sitewide_contributors = []

    for node in result:
        title = node.xpath('mw:title', namespaces=nsmap)[0].text
        url = title.replace(' ', '_')
        url = url.replace('?', '')
        slash = url.rfind('/')

        # Skip talk pages and file pages and other special pages
        if ':' in title:
            print(f"skipping {title}")
            continue

        if slash != -1:
            title = title.replace('/', ' ')
            directory = url[:slash]
            filename = url[slash+1:]
            directory_list[directory] = True
        else:
            directory = ''
            filename = url

        revision_elements = node.xpath('mw:revision', namespaces=nsmap)
        revision_elements.sort(key=lambda elem: elem.findtext('mw:timestamp', namespaces=nsmap))

        # Iterate all the revision, collecting all the useful metadata we want to preserve (especially the contributors)
        contributors = []
        for revision_element in revision_elements:
            contributor = revision_element.findtext('mw:contributor/mw:username', namespaces=nsmap)
            # Check if contributor is not None and not already in the list
            if contributor and contributor not in contributors:
                contributors.append(contributor)
            if contributor and contributor not in sitewide_contributors:
                sitewide_contributors.append(contributor)

        # Extract relevant information from the latest revision
        latest_revision = revision_elements[-1] # Get the last (highest) <revision> element
        latest_id = latest_revision.findtext('mw:id', namespaces=nsmap)
        latest_timestamp = latest_revision.findtext('mw:timestamp', namespaces=nsmap)
        latest_contributor = latest_revision.findtext('mw:contributor/mw:username', namespaces=nsmap)
        latest_content = latest_revision.findtext('mw:text', namespaces=nsmap)
        print(f"{title} ({latest_id} {latest_timestamp} {latest_contributor})")

        text = html.unescape(latest_content)
        text = text.replace('<br>', '\n\n')
        text = re.sub(r'\[\[(.+?)\]\]', new_link, text)

        if add_meta:
            frontmatter = "---\n"
            frontmatter += f"title: {title}\n"
            if enable_permalink:
                frontmatter += f"permalink: /{url}/\n"
            # Add contributors to the front matter
            if contributors:
                frontmatter += "contributors:\n"
                for contributor in contributors:
                    frontmatter += f"  - {contributor}\n"
            frontmatter += "---\n\n"

        text = pypandoc.convert_text(text, format='mediawiki', to=format_)

        # Add the .md extension to wikilinks if the --mdbook argument is passed
        # This is similar to running this sed function changing all instances of `[Text](Text "wikilink")` to `[Text](Text.md)`
        # ergo: `find . -name '*.md' -exec sed -i 's/\(\[.*\]\)(\(.*\)\s"wikilink")/\1(\2.md)/g' {} \;`
        if args.mdbook:
            text = re.sub(r'\[([^\]]+)\]\(([^ )]+)( "wikilink"\))', r'[\1](\2.md)', text)

        text = text.replace('\\_', '_')
        text = text.replace('\. ', '. ')

        if add_meta:
            text = frontmatter + text

        if not output_path.endswith('/'):
            output_path += '/'

        directory = output_path + directory

        if directory:
            if not os.path.exists(directory):
                os.makedirs(directory, 0o755, True)
            directory += '/'

        with open(normalize_path(directory + filename + '.md'), 'w') as file:
            file.write(text)

        count += 1

    if sitewide_contributors:
        print("sitewide_contributors:")
        for contributor in sitewide_contributors:
            print(f"  - {contributor}")

    if directory_list and args.indexes:
        directory_list = list(directory_list.keys())

        for directory_name in directory_list:
            if os.path.exists(output_path + directory_name + '.md'):
                os.rename(output_path + directory_name + '.md', output_path + directory_name + '/index.md')

    if count > 0:
        print(f"{count} files converted\n\n")

def parse_arguments():
    parser = argparse.ArgumentParser(description="Convert MediaWiki XML to Markdown")
    parser.add_argument('--filename', required=True, help="Input XML file")
    parser.add_argument('--output', help="Output directory")
    parser.add_argument('--format', default='gfm', help="Output format (default: gfm)")
    parser.add_argument('--fm', action='store_true', help="Add front matter")
    parser.add_argument('--indexes', action='store_true', help="Rename and move files with the same name as directories")
    parser.add_argument('--mdbook', action='store_true', help="Convert wikilinks to .md links for mdBook compatibility")
    return parser.parse_args()

if __name__ == "__main__":
    main()
