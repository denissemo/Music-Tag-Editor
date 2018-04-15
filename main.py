import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QApplication, QFileDialog, \
    QProgressBar, QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QFile, QIODevice
import resource_rc
from tag_extractor import TagExtractor
from player import Player
from mp3_tagger import MP3File, VERSION_1, VERSION_2, VERSION_BOTH

import psutil

def lsof(path = None):
    users = []
    for p in psutil.process_iter():
        files = []
        try:
            files = p.open_files()
        except:
            pass

        if path:
            users.extend(
                [(f.path, p.name(), p.pid, p.username()) for f in files if
                 f.path in path])
        else:
            users.extend(
                [(f.path, p.name(), p.pid, p.username()) for f in files])
    return users


class Tag(QMainWindow):
    bool_ = True  # for player (play/unpause)

    def __init__(self):
        super().__init__()
        self.ui = uic.loadUi('tag_editor.ui')
        self.ui.setWindowTitle('Music Tag Editor')
        self.ui.setWindowIcon(QIcon('window_icon.png'))
        self.statusBar = self.ui.statusBar()
        self.tracksTable = self.ui.tableWidgetItems
        self.tagsTable = self.ui.tableWidget
        self.progressBar = QProgressBar()
        # -- all imported files
        self.files = []
        self.current_file_index = 0
        self.tags_str_keys = ['artist', 'title', 'album', 'genre',
                              'tracknumber', 'date']

        self.initUI()

    def initUI(self):
        # -- resize column
        self.tracksTable.resizeColumnToContents(1)
        # -- activate cell
        self.tracksTable.cellClicked.connect(self.cell_clicked)  # coord
        self.tagsTable.cellDoubleClicked.connect(self.cell_double_clicked)

        # -- actions
        # add folder action
        add_folder_action = self.ui.actionAdd_Folder
        add_folder_action.triggered.connect(self.show_folder_dialog)
        # add file action
        add_file_action = self.ui.actionAdd_File
        add_file_action.triggered.connect(self.show_file_dialog)

        # close app action
        exit_action = self.ui.actionExit
        exit_action.triggered.connect(self.show_quit_message)

        self.ui.show()

    def cell_clicked(self, r, c):
        """Slot.
        :param r: row
        :param c: count
        """
        item = self.tracksTable.item(r, 2)  # title
        for file in self.files:
            if item.text() == file.track_info['title']:
                self.statusBar.showMessage('Quality: {} kbps, {} Hz\nTrack siz'
                                           'e: {} mb File path: {}'.format(
                    file.track_info['bitrate'], file.track_info['sample_rate'],
                    file.track_info['track_size'], file.file_path))
                self.current_file_index = self.files.index(file)
                self.update_tag_table(file)

                # -- player actions
                # play action
                play_action = self.ui.actionPlay
                # create instance of Player object
                self.player = Player(file.file_path)
                Tag.bool_ = True
                play_action.triggered.connect(self.play)

                # pause action
                pause_action = self.ui.actionPause
                pause_action.triggered.connect(self.pause)

                # stop action
                stop_action = self.ui.actionStop
                stop_action.triggered.connect(self.stop)

    # -- slots for player
    def play(self):
        # use for start playing
        if Tag.bool_:
            self.player.play()
            Tag.bool_ = False
        self.player.unpause()

    def pause(self):
        # use for pause playing
        self.player.pause()

    def stop(self):
        # stop playing
        self.player.stop()
        Tag.bool_ = True

    def cell_double_clicked(self, r, c):
        self.tagsTable.cellChanged.connect(self.cell_changed)

    def cell_changed(self, r, c):
        current_file = self.files[self.current_file_index]
        new_tag = self.tagsTable.item(r, c)
        orig_tag = self.tagsTable.item(r, 1)
        n_t = str(new_tag.text())
        o_t = str(orig_tag.text())
        if n_t != o_t:
            ask = self.show_change_tag_message(new_tag)
            if ask:
                # tag = current_file.edit_tag(self.tags_str_keys[r],
                #                             str(new_tag.text()))
                # path = current_file.path
                # tag = TagExtractor(os.path.join(path[0], path[1])).edit_tag(self.tags_str_keys[r], str(new_tag.text()))
                # test ----
                # path = os.path.join(current_file.path[0], current_file.path[1])
                # path = current_file.path[0] + '/' + current_file.path[1]
                # file = open('D:\\Music\\Music\\A Day to Remember - All I Want.mp3', 'r+b')
                # print(lsof('D:\\Music\\Music\\A Day to Remember - All I Want.mp3'))
                # print(file)
                mp3 = MP3File('D:\\Music\\Music\\A Day to Remember - All I Want.mp3')
                mp3.artist = n_t
                mp3.save()
                # self.files[self.current_file_index] = TagExtractor(path)
                self.update_tag_table(self.files[self.current_file_index])
                self.update_tracks_table()
                self.statusBar.showMessage('Change saved')

    def show_change_tag_message(self, cur_item):
        reply = QMessageBox.question(self, 'Save tag',
                                     'Are you want set the "{}" tag?'.
                                     format(str(cur_item.text())),
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)

        if reply == QMessageBox.Yes:
            return True
        else:
            return False

    def show_quit_message(self):
        reply = QMessageBox.question(self, 'Quit message', 'Are you sure you w'
                                                           'ant to exit Music T'
                                                           'ag Editor?',
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.ui.close()

    def show_file_dialog(self):
        self.files.clear()
        file_name = QFileDialog.getOpenFileName(self, 'Open file', '/home',
                                                '*.mp3')[0]
        print(file_name)
        if file_name:
            self.files.append(TagExtractor(file_name))
        # update trackTable widget
        self.update_tracks_table()

    def show_folder_dialog(self):
        self.files.clear()
        folder_items = QFileDialog \
            .getExistingDirectory(self, 'Open folder', '/home',
                                  QFileDialog.ShowDirsOnly
                                  | QFileDialog.DontResolveSymlinks)

        completed = 0
        self.progressBar.setMaximumSize(180, 20)
        self.statusBar.addPermanentWidget(self.progressBar)
        self.statusBar.showMessage('Load songs...')
        if folder_items:
            for item in os.listdir(folder_items):
                path = folder_items + '/' + item
                if os.path.isfile(path):
                    if path.endswith('.mp3'):
                        self.files.append(
                            TagExtractor(folder_items + '/' + item))
                else:
                    continue
                self.progressBar.setValue(completed)
                completed += 100 / len(os.listdir(folder_items)) + 0.1
        self.progressBar.close()
        self.statusBar.showMessage('Added ' + str(len(self.files)) + ' files')
        # -- update trackTable widget
        self.update_tracks_table()

    def update_tag_table(self, file):
        for count in range(1, 3):
            for row, tag in enumerate(self.tags_str_keys):
                new_item = QTableWidgetItem(file.track_info[tag])
                self.tagsTable.setItem(row, count, new_item)
                if count < 2:
                    t_item = self.tagsTable.item(row, count)
                    t_item.setFlags(
                        Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable
                        | Qt.ItemIsEnabled)

    def update_tracks_table(self):
        self.tracksTable.setRowCount(len(self.files))
        keys = ['artist', 'length', 'title']
        for r, item in enumerate(self.files):
            for c, key in enumerate(keys):
                new_item = QTableWidgetItem(item.track_info[key])
                self.tracksTable.setItem(r, c, new_item)
                t_item = self.tracksTable.item(r, c)  # get item
                t_item.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable
                                | Qt.ItemIsEnabled)
                item_for_icon = self.tracksTable.item(r, 0)
                item_for_icon.setIcon(QIcon('song_icon.png'))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Tag()
    sys.exit(app.exec_())
