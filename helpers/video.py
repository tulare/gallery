__all__ = [ 'Video' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

from pk_services.core import Tor
from pk_services.players import MediaPlayer
        
# --------------------------------------------------------------------

class YtdlRawOptions :

    def __init__(self, initial=dict()) :
        self._options = initial

    def set(self, name, value) :
        self._options[name] = value

    def clear(self, name) :
        self._options.pop(name,'')

    def __str__(self) :
        options = ','.join(f"{key}=[{value}]" for key, value in self._options.items())
        return f'--ytdl-raw-options={options}'
        

# --------------------------------------------------------------------
        
class Video(object) :

    def __init__(self, uri, *, titre=None, filtre="hasvid") :
        self._uri = uri
        self._titre = titre or uri
        self._filtre = filtre
        self._player = None
        self._ytdl_raw_options = YtdlRawOptions({'format-sort' : filtre})

    @property
    def player(self) :
        if self._player is None :
            self.change_player()
        return self._player

    @player.setter
    def player(self, player) :
        self.change_player(player)
        
    def change_player(self, player=None) :
        self._player = MediaPlayer(id=player or 'mpv')
        self.ytdl_raw_options()
        log.debug(f'change_player - {self._player.id_player}:options{self._player.options}')

    def ytdl_raw_options(self) :
        if Tor.isEnabled() :
            self._ytdl_raw_options.set("proxy", "socks5://127.0.0.1:9150")
        else :
            self._ytdl_raw_options.clear("proxy")
        for index, option in enumerate(self._player.options) :
            if option.startswith('--ytdl-raw-options') :
                self._player.options[index] = f"{self._ytdl_raw_options}"
            
    def play(self) :
        self.ytdl_raw_options()
        process = self.player.play(self._titre, self._uri)
        log.debug(f'play - {self._player.id_player}:console={self._player.console}')
        log.debug(f'play - {self._player.id_player}:options{self._player.options}')
        log.debug(f'play - process:{process.pid}')
        return process

# --------------------------------------------------------------------

