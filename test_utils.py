from unittest import TestCase

import utils


class TestParseCommString(TestCase):
    def test_ParseCommString_singleline(self):
        self.assertEqual(utils.ParseCommString("x=2.;ID=4;name=Snert"),
                         [dict(x='2.', ID='4', name='Snert')])

    def test_ParseCommString_singlelineWithLeader(self):
        self.assertEqual(utils.ParseCommString("PLANET|x=2.;ID=3;name=Snert"),
                     [dict(x='2.', ID='3', name='Snert')])

    def test_ParseCommString_TwoLines(self):
        self.assertEqual(utils.ParseCommString("PLANET|x=2.;ID=3;name=Snert|x=1"),
                     [dict(x='2.', ID='3', name='Snert'), dict(x='1')])


    def test_ParseCommString_Invalid(self):
        self.assertEqual(utils.ParseCommString("PLANET|x=2.;ID=3;name=Snert|x=1;Skip!"),
                     [dict(x='2.', ID='3', name='Snert'), dict(x='1')])
