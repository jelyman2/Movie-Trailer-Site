#!/usr/bin/env python

__author__ = 'jlyman'

# The core script to run this app.

import collections as col
import config as cfg
import json
import os
import re
import webbrowser as web

# Open the template parts and assign them for later usage, making sure to
# convert them from objects to strings.
template = open(cfg.TEMPLATE_FOLDER + cfg.TEMPLATE_HEADER)
main_page_head = template.read()
template = open(cfg.TEMPLATE_FOLDER + cfg.TEMPLATE_MAIN)
main_page_content = template.read()
template = open(cfg.TEMPLATE_FOLDER + cfg.TEMPLATE_CONTENT)
movie_tile_content = template.read()

# Pull in the trailer DBF file. This is where the data is stored.
trailer_dbo = open(cfg.DBF_LOCATION)

# Let's read that bad boy with our JSON interpreter.
trailer_json = json.dumps(trailer_dbo.read())

# Break down the natural dictionary into an object. This is the only time
# I've ever used lambda for ANYTHING. The "X" character for the named tuple
# is irrelevant but I needed to put something there. It was easier than building
# up a whole class and overwriting the natural dictionary-izing of loading up
# JSON data from the trailers.dbf file.


def parse_json(json_data):
    blob = json.loads(json_data, object_hook=lambda d:
                      col.namedtuple("X", d.keys())(*d.values()))
    return blob

trailer_data = parse_json(json.loads(trailer_json))

# Now we have attributes for every iteration of trailer_data. They are (as of
# version 0.1):
# - .title
# - .imdb.link
# - .poster
# - .yturl
# - .director
# - .release_date

# Code below came from fresh_tomatoes.py. It made more sense for me to include
# it in this script since it's not very complex.

# Let's build out each of the tiles.


def build_tiles(movies):
    # The HTML content for this section of the page
    content = ''
    for movie in movies:

        # Extract the youtube ID from the url
        youtube_match = re.search(r'(?<=v=)[^&#]+', movie.yturl)
        youtube_match = youtube_match or \
                        re.search(r'(?<=be/)[^&#]+', movie.yturl)
        trailer_youtube_id = youtube_match.group(0) if youtube_match else None

        # Append the tile for the movie with its content filled in
        content += movie_tile_content.format(
            movie_title=movie.title,
            poster_image_url=cfg.POSTER_IMAGE_FOLDER + movie.poster,
            trailer_youtube_id=trailer_youtube_id,
            imdb_link=movie.imdb_link,
            director=movie.director,
            release_date=movie.release_date

        )
    return content

# Now we need to assemble the whole HTML page.


def open_movies_page(movies):
    # Create or overwrite the output file
    output_file = open('trailers.html', 'w')

    # Replace the placeholder for the movie tiles with the actual
    # dynamically generated content

    render_content = ''

    render_content += main_page_content.format(
        movie_tiles=build_tiles(movies),
        app_title=cfg.APP_TITLE,
        app_desc=cfg.APP_DESCRIPTION,
        app_author=cfg.APP_AUTHOR
    )

    render_header_content = ''

    # Because I like debugging, let's barf our config.py file.

    config_barf = open('config.py', 'r')
    render_header_content += main_page_head.format(
        app_title=cfg.APP_TITLE,
        config_barf=config_barf.read()
    )

    # Output the file
    output_file.write(render_header_content + render_content)
    output_file.close()

    # open the output file in the browser
    url = os.path.abspath(output_file.name)
    web.open('file://' + url, new=2) # open in a new tab, if possible

# RELEASE THE KRAKEN!

open_movies_page(trailer_data)