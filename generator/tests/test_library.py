import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest
import json
from library import SongLibrary
import pathlib


class TestLibrary (unittest.TestCase):
    

    def setUp(self):
        self._audio_path = "test_audio/"
        self.song_library = SongLibrary(self._audio_path)    
        return 

    # 
    def test_load_song_ids(self):
        song_list = ['01BC4Xj5tfsfV8DLDrma7q', '1ULa3GfdMKs0MfRpm6xVlu', '3swc6WTsr7rl9DqQKQA55C', '4pdgV8qr9Oytcv6thCdiIZ']
        self.assertEqual(self.song_library._song_ids, song_list)
        return


    def test_get_song_metadata(self):
        song_id = "01BC4Xj5tfsfV8DLDrma7q"
        with open("test_audio/01BC4Xj5tfsfV8DLDrma7q/metadata.json") as f:
            data = json.load(f)
        self.assertEqual(data, self.song_library._get_song_metadata(song_id))
        pass

    # def test_load_metadata(self):
    #     pass
    
    # def test_get_metadata(self):
    #     pass

    # def test_set_selected_songlist(self, songlist_from_ui):
    #     pass

    # def test_get_song(self,song_id):
    #     pass

    # def test_get_avg_tempo(self):
    #     pass

    # def test_get_optimal_tempo(self):
    #     pass

    # def test_get_optimal_pitch_class(self):
    #     pass


    


if __name__=='__main__':
    unittest.main()
