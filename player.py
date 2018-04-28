"""
Created on: 25.01.2018

@author: Denis Semenov
"""
import os
from pygame import mixer
# from os._path import isfile


class Player:
    """
    This class can play mp3 tracks_information.
    """
    def __init__(self, file_path=None):
        """
        Initialize the class.

        :param file_path: _path to mp3 file
        """
        if isinstance(file_path, str):
            if not os.path.isfile(file_path):
                raise FileNotFoundError('this _path does not contain usr_input '
                                        'file')
            if not file_path.endswith('.mp3'):
                raise FileExistsError('this is not mp3 file')
            self._track_path = file_path
        else:
            if file_path is not None:
                raise ValueError('_path must be str')
        mixer.init()
        mixer.music.load(file_path)  # load track
        self._playing = False

    def play(self):
        """Start playing current file."""
        mixer.music.play()
        self._playing = True

    @staticmethod
    def pause():
        """Pause current playing track."""
        mixer.music.pause()

    @staticmethod
    def unpause():
        """Continue playing current track, after pause."""
        mixer.music.unpause()

    def stop(self):
        """Stop playing current track."""
        mixer.music.stop()
        self._playing = False


if __name__ == '__main__':
    # os.chdir('D:\\Music\\Music\\')
    s = Player('A Day to Remember - All I Want.mp3')
    s.play()
    while True:
        k = input('> ')
        if k == 'play':
            s.unpause()
        elif k == 'pause':
            s.pause()
        elif k == 'stop':
            s.stop()
            break
