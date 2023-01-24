import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import unittest
from silenceDetection import SilenceFilter
import json


class TestSilenceDetection (unittest.TestCase):

    def setUp(self):
        return 

    # 
    def test_process(self):
        return

    def test_check_silence_first_bar(self):
        return

    def test_check_silence_segment(self):
        return
    
    def test_bar_hop(self):
        return

    def test_four_bar_hop(self):
        return

    def test_detect_silence(self):
        return

    def test_envelope(self):
        return
    
    def test_med_filt(self):
        return
    
    def test_fill_holes(self):
        return

    


if __name__=='__main__':
    unittest.main()
