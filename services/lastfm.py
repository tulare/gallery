__all__ = [ 'Playlist' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug(f'MODULE {__name__}')

import argparse
import yt_dlp as youtube_dl
from yt_dlp.utils import DownloadError, ExtractorError

from .players import MediaPlayer

# ------------------------------------------------------------------------------

class LastFmUrl :

    def __init__(self, **kwargs) :
        self.kwargs = {
            'url' : kwargs.get('url'),
            'tag' : kwargs.get('tag'),
            'artist' : kwargs.get('artist'),
            'song' : kwargs.get('song')
        }
        self.kwargs.update(kwargs)

    def __str__(self) :
        return self.url

    def __repr__(self) :
        return f"LastFmUrl(url='{self.url}')"
    
    @property
    def url(self) :
        # Build url
        url = None
        args = argparse.Namespace(**self.kwargs)
        if args.artist :
            url = f"https://www.last.fm/music/{args.artist}/+tracks?date_preset=LAST_7_DAYS"
            if args.song :
                url = f"https://www.last.fm/music/{args.artist}/_/{args.song}"
        if args.tag :
            url = f"https://www.last.fm/tag/{args.tag}/tracks"
        if args.url :
            url = f"{args.url}"
        self._url = url
        return self._url

# ------------------------------------------------------------------------------

class Playlist :

    def __init__(self, url=None) :
        # Instance
        self._infos = None
        self._cache = []
        self._url = url

        # YoutubeDL (yt_dlp)
        self._ytdl = youtube_dl.YoutubeDL()
        self._ytdl.params['verbose'] = True

        # Mpv Player
        self._mpv = MediaPlayer(id='mpv')

        # pre Load
        if url is not None :
            self._update(url)
            self.extract_info()

    @property
    def url(self) :
        return self._url

    @url.setter
    def url(self, url) :
        self._update(url)
        self.extract_info()

    @property
    def cache_size(self) :
        return len(self._cache)

    @cache_size.setter
    def cache_size(self, size) :
        resize = min(size, len(self._cache))
        self._cache[:] = self._cache[:resize:]

    def _update(self, url) :
        self._url = url
        self._infos = self._ytdl.extract_info(url, process=False)
        #self._cache = []
    
    def extract_info(self, batch=50) :
        if self._infos['_type'] == 'url' :
            self._cache = []
            self._cache.append(self._infos)
        else :
            bunch = list(x for _,x in zip(range(batch), self._infos['entries']))
            self._cache.extend(bunch)
        self._sinfos = iter(self._cache)

    def restart(self) :
        self._sinfos = iter(self._cache)

    def next_entry(self) :
        try :
            ie_result = next(self._sinfos)
            log.info("ie_result=%r", ie_result)
            return ie_result
        except StopIteration :
            return {}

    def info(self, ie_result) :
        try :
            info_dict = self._ytdl.process_ie_result(ie_result, download=False)
            log.info("info_dict: title=%s url=%s", info_dict['title'], info_dict['webpage_url'])
            return info_dict
        except ExtractorError as err :
            log.error("ExtractorError: %s", err)
        except DownloadError as err :
            log.error("DownloadError: %s", err)
        return {}

    def info_next(self) :
        try :
            ie_result = self.next_entry()
            return self.info(ie_result)
        except :
            pass


    def download(self, ie_result) :
        try :
            info_dict = self.info(ie_result)
            self._ytdl.process_info(info_dict)
        except :
            pass

    def play(self, ie_result, height=1080) :
        self._mpv.options.clear()
        self._mpv.add_options(f'--ytdl-format=bestvideo[height<={height}]+bestaudio/best[height<={height}]')        
        try :
            info_dict = self.info(ie_result)
            p = self._mpv.play(info_dict['title'], info_dict['webpage_url'])
            p.wait()
        except :
            pass

    def play_next(self, height=1080) :
        try :
            ie_result = self.next_entry()
            self.play(ie_result, height)
        except :
            pass

    def save_m3u(self, name='playlist') :
        with open(f'{name}.m3u', 'w', encoding='utf8') as fd :
            fd.write(f"#EXTM3U\n")
            for ie_result in self._cache :
                try :
                    url = ie_result.get('url')
                    title = ie_result.get('title')
                    if title is None :
                        info_dict = self.info(ie_result)
                        title = info_dict['title']
                    log.debug(f"Title: {title} - Url: {url}")
                    fd.write(f"#EXTINF:-1,{title}\n")
                    fd.write(f"{url}\n")
                except :
                    pass

    def play_m3u(self, name='playlist', height=1080) :
        self._mpv.options.clear()
        self._mpv.add_options(f'--ytdl-format=bestvideo[height<={height}]+bestaudio/best[height<={height}]')
        p = self._mpv.play('', f'{name}.m3u')
        p.wait()

    def play_cache(self, height=1080) :
        self.save_m3u('cache_playlist')
        self.play_m3u('cache_playlist', height)
            
    def play_auto(self, start=0, end=100, height=1080) :
        self._mpv.options.clear()
        self._mpv.add_options(f'--ytdl-raw-options=playlist-items={start}:{end}')
        self._mpv.add_options(f'--ytdl-format=bestvideo[height<={height}]+bestaudio/best[height<={height}]')
        p = self._mpv.play('', self.url)
        p.wait()
