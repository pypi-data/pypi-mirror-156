"""Offline data-related tests"""
import unittest
from pathlib import Path


from metaindexmanager import utils


class TestOfflineIcon(unittest.TestCase):
    def test_offline_icon(self):
        path = Path("/probably/does/not/exist/video.mp4")
        icon = utils.get_ls_icon(path)

        self.assertFalse(path.exists())
        self.assertEqual(icon, "")
