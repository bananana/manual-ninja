from app import app
from app.config import SITE_TITLE, DEFAULT_MANPATH, MANPATH
from app.search import search
from flask import render_template, request, redirect, url_for, flash
from bs4 import BeautifulSoup, Tag
from glob import glob
import os
import subprocess
import re


@app.route('/')
@app.route('/index', methods=['POST', 'GET'])
def index():
    '''The main page of the app that has a search box. Upon submission, if 
    there is only one result, the user is redirected to man page result.
    If there are several results (in multiple man sections) they will be
    displayed under the search box. If there are no results found, an error 
    message is displayed under the search box.
    '''
    if request.method == 'POST':
        search_request = request.form['search-field'] 
        search_results = search(search_request) 

        if len(search_results) == 1:
            # Only one result, display it immediately
            man = search_results.keys()[0]
            sec = search_results[search_request]['section']
            path = search_results[search_request]['path_index']
            return redirect(url_for('manpage', 
                                    manpage=man,
                                    section=sec,
                                    path_index=path))
        elif len(search_results) > 1:
            # More than 1 result, display them as a list under search bar
            return render_template('index.html',
                                   title='manny',
                                   query=search_request,
                                   results=search_results)
        else:
            # No results found, display an error message
            flash('No manual entry for <strong>' + \
                  request.form['search-field'] + \
                  '</strong>')
            return render_template('index.html',
                                   title='manny',
                                   query=search_request,
                                   results=None)
    else:
        # Display the default search page
        return render_template('index.html', 
                               title='manny', 
                               query=None,
                               results=None)


@app.route('/<manpage>/<section>/', 
           defaults={'path_index':MANPATH.index(DEFAULT_MANPATH)})
@app.route('/<manpage>/<section>/<int:path_index>/')
def manpage(manpage, section, path_index):
    #: Get manpath based on index passed to the page
    manpath = MANPATH[path_index]

    # Extract html from manpage archive 
    archive = glob(manpath + '/man' + \
                   section + '/' + \
                   manpage + '.' + \
                   section + '*')
    
    if archive[0].endswith('.gz'): 
        expand = subprocess.Popen(['zcat', archive[0]], 
                                  stdout=subprocess.PIPE)
        manpage = subprocess.check_output(['groff', '-t','-mandoc','-Thtml'], 
                                          stdin=expand.stdout)
    else:
        manpage = subprocess.check_output(['groff', '-t','-mandoc','-Thtml',
                                           archive[0]])

    soup = BeautifulSoup(manpage, 'html.parser')

    # Create table of contents links and anchors to sections
    table_of_contents = soup.body.find_all(href=re.compile('#*'))
    for sect in table_of_contents:
        # Section link in table of contents at the top of the page
        sect['class'] = 'section-link'

        # Anchors for individual sections
        anchor = soup.body.find('a', {'name':sect.string})
        anchor['class'] = 'anchor'

        # Anchor links
        anchor_link = soup.new_tag('a', href='#' + sect.string)
        anchor_link['class'] = 'anchor-link'
        anchor_link['title'] = 'Permalink to this section'
        anchor.insert_after(anchor_link)
         
    # Replace inline style declarations with classes
    styles_to_replace = [
        ('margin-left:22%;','description'),
        ('margin-left:11%;','command'),
        ('margin-left:11%; margin-top: 1em','standalone-paragraph')
    ]
    for style, replacement in styles_to_replace:
        for tag in soup.body.find_all(style=style):
            tag['class'] = replacement 
            del tag['style']

    # Some commands are displayed as tables, for some reason
    table_command = soup.body.find_all(frame='void')
    for cmd in table_command:
        cmd['class'] = 'table-command'

    #: Extract title string 
    title = soup.title.string + '(' + section + ')'

    #: Cast body into unicode for further processing
    body = unicode(soup.body)

    # Replace useless tags
    tags_to_replace = [
        # Remove body tag, it should be inserted in the template
        (u'<body>', u''),
        (u'</body>', u''),
        # Obsolete tags
        (u'b>', u'strong>'),
        (u'i>', u'em>'),
        (u'</br>', u'<br>'),
        (u'</hr>', u'<hr>'),
        # Unnecessary breaks in some strong tags
        (u'<br></strong>', u'</strong>'),
        # Unnecessary breaks in some em tags
        (u'<em><br>', u'<em>'),
        (u'<br></em>', u'</em>'),
        # Unnecessary quadruple breaks
        (u'<br><br><br><br>', u''),
        # Use correct ellipsis character
        (u'...', u'&hellip;')
    ]
    for tag, replacement in tags_to_replace:
        body = body.replace(tag, replacement)

    # Add links to plain text URLs
    urls = re.findall(r'(&lt;http:\/\/.*&gt;)', body)
    clean_urls = [u[4:-4] for u in urls]
    for index, url in enumerate(urls):
        body = body.replace(url, '<a href=\"' + clean_urls[index] + \
                                 '\">' + clean_urls[index] + '</a>')

    # Find references to other man pages and link them
    related = re.findall(r'[a-zA-Z0-9.]+\([1-8]\)', body)
    for item in related:
        section = item[-2]
        manpage = item[:-3]
        body = body.replace(item, 
                            '<strong><a href=\"/' + manpage + \
                            '/' + section + '\">' + item + \
                            '</a></strong>')

    # Sometimes references to other man pages are inside strong tags
    related_strong = re.findall(r'<strong>[a-zA-Z0-9]+</strong>\([1-8]\)', body)
    for item in related_strong:
        section = item[-2]
        manpage = item[8:-12]
        body = body.replace(item, '<strong><a href=\"/' + section + \
                                  '/' + manpage + '\">' + manpage + \
                                  '(' + section + ')' + '</a></strong>')

    # Use em instead of quotations for emphasis
    single_quotes = re.findall(ur'(?!\u2019s )\u2019(.+?)\u2019', body)
    for quote in single_quotes:
        body = body.replace(u'\u2019' + quote + u'\u2019', 
                            '<em>' + quote + '</em>')
    double_quotes = re.findall(ur' \"(.+?)\"', body)
    for quote in double_quotes:
        body = body.replace(u'\"' + quote + '\"',
                            '<em class=\"slanted\">' + quote + '</em>')

    return render_template('manpage.html', 
                           title=title,
                           body=body) 
