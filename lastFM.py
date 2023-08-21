# Logging
import logging
import argparse

# Configuration
import __main__ as locator
from pk_config import config

# Services
from services.lastfm import LastFmUrl, Playlist
from services.web import WebService, GrabService
from services.youtube import YoutubeService
from services.players import MediaPlayer

import yt_dlp
from yt_dlp.utils import DownloadError, ExtractorError

def parse_args() :
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter
    )

    parser.add_argument(
        '-L', '--loglevel',
        default='WARNING',
        help='log level'
    )

    parser_group = parser.add_mutually_exclusive_group(required=True)
    parser_group.add_argument(
        '-A', '--artist',
    )
    parser_group.add_argument(
        '-T', '--tag',
    )
    parser_group.add_argument(
        '-U', '--url',
    )

    parser.add_argument(
        '-S', '--song',
    )

    args = parser.parse_args()
    return args

if __name__ == '__main__' :

    # Command line arguments
    args = parse_args()

    # Logging
    logging.basicConfig(level=args.loglevel)
    logging.info('start logging')
    logging.info('args=%r', args)

    # Configuration
    prj_database = config.project_database(locator)
    conf = config.Configuration(prj_database)
    logging.info(conf.database)
    assert conf.checklist(['User-Agent'])

    # Build url
    lastUrl = LastFmUrl(**vars(args))
    logging.info(f"url={lastUrl.url}")

    # Build playlist
    pl = Playlist(lastUrl.url)

    # Play auto
    pl.play_auto(height=720)


    
