__all__ = [ 'Video' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

from pk_services.core import Tor
from pk_services.players import MediaPlayer
        
# --------------------------------------------------------------------
        
class Video(object) :

    def __init__(self, uri, titre=None) :
        self._player = None
        self._titre = titre or uri
        self._uri = uri

    @property
    def player(self) :
        if self._player is None :
            self.change_player()
        return self._player

    @player.setter
    def player(self, player) :
        self.change_player(player)
        
            

    def change_player(self, player=None) :
        if player is None :
            self._player = MediaPlayer.getPlayer()
        else :
            self._player = MediaPlayer.getPlayer(player)
        if Tor.isEnabled() :
            self._player.add_options('--ytdl-raw-options=proxy=socks5://127.0.0.1:9150')
        log.debug(f'change_player - {self._player.id_player}:options{self._player.options}')

    def play(self) :
        process = self.player.play(self._titre, self._uri)
        log.debug(f'play - {self._player.id_player}:console={self._player.console}')
        log.debug(f'play - {self._player.id_player}:options{self._player.options}')
        log.debug(f'play - process:{process.pid}')
        return process

# --------------------------------------------------------------------

