__all__ = [ 'Video' ]

# logging
import logging
log = logging.getLogger(__name__)
log.debug('MODULE {}'.format(__name__))

from subprocess import TimeoutExpired

from pk_services.core import Tor
from pk_services.players import MediaPlayer
        
# --------------------------------------------------------------------
        
class Video(object) :

    def __init__(self, uri, *, titre=None, filtre="hasvid") :
        self._uri = uri
        self._titre = titre or uri
        self._filtre = filtre
        self._player = None

    @property
    def player(self) :
        if self._player is None :
            self.change_player()
        return self._player

    @player.setter
    def player(self, player) :
        self.change_player(player)

    @property
    def filtre(self) :
        return self._filtre

    @filtre.setter
    def filtre(self, filtre) :
        self._filtre = filtre
        if self._player is not None :
            self._player.mpv_options.set_raw_options('format-sort', self._filtre)
        
    def change_player(self, player=None) :
        self._player = MediaPlayer(id=player or 'mpv')
        self.ytdl_raw_options()
        log.debug(f'change_player - {self.player.id_player}:options{self.player.mpv_options.options}')

    def ytdl_raw_options(self) :
        self.player.mpv_options.set_raw_options('format-sort', self.filtre)
        if Tor.isEnabled() :
            self.player.mpv_options.set_raw_options('proxy', 'socks5h://127.0.0.1:9150')
        else :
            self.player.mpv_options.clear_raw_options('proxy')
            
    def play(self) :
        self.ytdl_raw_options()
        process = self.player.play(self._titre, self._uri)
        try :
            # le process ne s'est-il pas terminé de façon prématurée ?
            process.wait(timeout=7)
            if process.poll() :
                log.warning(f"{process.args}")
                log.warning(f"pid={process.pid} returncode={process.returncode}")
                return
        except TimeoutExpired :
            pass
        log.debug(f'play - {self.player.id_player}:console={self.player.console}')
        log.debug(f'play - {self.player.id_player}:options{self.player.mpv_options.options}')
        log.debug(f'play - process:{process.pid}')

        return process

# --------------------------------------------------------------------

