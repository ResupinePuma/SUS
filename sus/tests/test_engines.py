from sus.engines import telegram, reddit, rss
import vcr
import unittest


class EngineTests(unittest.TestCase):
    @vcr.use_cassette('./sus/tests/cassettes/telegram.yaml')
    def test_telegram(self):
        self.assertEqual(len(telegram.scrab(
            {"url": "https://t.me/s/durov", "time_limit_hours": 24*31*6})), 19)

    @vcr.use_cassette('./sus/tests/cassettes/reddit.yaml')
    def test_reddit(self):
        self.assertEqual(len(reddit.scrab(
            {"url": "https://www.reddit.com/r/announcements/", "time_limit_hours": 24*31})), 1)

    @vcr.use_cassette('./sus/tests/cassettes/rss.yaml')
    def test_rss(self):
        self.assertEqual(len(rss.scrab(
            {"url": "https://feeds.bbci.co.uk/news/world/europe/rss.xml"})), 9)


            
