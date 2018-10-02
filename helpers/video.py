# -*- encoding: utf-8 -*-

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
            self._player = MediaPlayer.getPlayer()
        return self._player

    @player.setter
    def player(self, player) :
        self._player = MediaPlayer.getPlayer(player)

    def play(self) :
        return self.player.play(self._titre, self._uri)


# --------------------------------------------------------------------

