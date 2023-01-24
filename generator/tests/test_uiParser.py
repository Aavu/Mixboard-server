import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest
from uiParser import UiParser
import json


class TestUiParser(unittest.TestCase):

    def setUp(self):
        with open("test_json/testData.json") as f:
            self.test_data = json.load(f)
        self.ui_data = UiParser(self.test_data)

    def test_get_stem_dict(self):
        for i, stem_type in enumerate(UiParser.StemType):
            self.assertEqual(self.ui_data.get_stem(stem_type), self.test_data[str(i)])

    def test_get_songs_in_track(self):
        song_ids = ["0VjIjW4GlUZAMYd2vXMi3b", "7ul0wYKeeINO2JBlhA5PtN", "2Fxmhks0bxGSBdJ92vM42m"]
        self.assertEqual(self.ui_data.get_songs_in_track(UiParser.StemType.Vocals), song_ids)

    def test_get_num_of_blocks(self):
        self.assertEqual(self.ui_data.get_num_of_blocks(UiParser.StemType.Drums), 3)

    def test_get_start_bars(self):
        start_bars = [0, 4, 9]
        self.assertEqual(self.ui_data.get_start_bars(UiParser.StemType.Other).tolist(), start_bars)

    def test_get_bar_lengths(self):
        bar_lengths = [4, 7, 5]
        self.assertEqual(self.ui_data.get_bar_lengths(UiParser.StemType.Vocals).tolist(), bar_lengths)

    def test_get_selected_songs(self):
        selected_songs = ["0VjIjW4GlUZAMYd2vXMi3b", "5OsdVCiWEsi01xRpMObaIg", "2Fxmhks0bxGSBdJ92vM42m", "7ul0wYKeeINO2JBlhA5PtN"]
        self.assertTrue(all(elem in self.ui_data.selected_songs for elem in selected_songs))

    def test_get_song_duration(self):
        song_duration = 16
        self.assertEqual(self.ui_data.song_duration, song_duration)


if __name__=='__main__':
    unittest.main()
