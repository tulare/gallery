# Logging
import logging
import argparse

# Configuration
import __main__ as locator
from pk_config import config

# Services
from services.lastfm import LastFmPage, LastFmUrl, Playlist
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

    parser_group.add_argument(
        '-M', '--m3u',
    )
        
    parser.add_argument(
        '-S', '--song',
    )

    parser.add_argument(
        '-B', '--album'
    )

    parser.add_argument(
        '-a', '--play-auto',
        action='store_true'
    )

    parser.add_argument(
        '-c', '--play-cache',
        action='store_true'
    )

    parser.add_argument(
        '-s', '--save-m3u',
    )

    parser.add_argument(
        '-b', '--batch',
        type=int,
        default=50,
    )

    parser.add_argument(
        '-H', '--height',
        type=int,
        default=1080
    )

    parser.add_argument(
        '-R', '--shuffle',
        action='store_true'
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

    # Build Album
    album = None
    if args.album :
        album = LastFmPage(url=lastUrl.url, user_agent=conf.get('User-Agent'))

    # Build playlist
    pl = Playlist(url=lastUrl.url, batch=args.batch, album=album)

    # Save playlist ?
    if args.save_m3u :
        pl.save_m3u(args.save_m3u)

    # Play auto
    if args.play_auto :
        pl.play_auto(height=args.height, shuffle=args.shuffle)

    # Play cache
    if args.play_cache :
        pl.play_cache(height=args.height, shuffle=args.shuffle)

    # Play m3u
    if args.m3u :
        pl.play_m3u(args.m3u, height=args.height, shuffle=args.shuffle)

    
