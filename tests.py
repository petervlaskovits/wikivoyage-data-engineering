from scrapers import WikivoyageScraper, WikipediaScraper
import unittest

class WikivoyageScraperTestCase(unittest.TestCase):
    scraper = WikivoyageScraper()

    def testForNone(self):
        row = self.scraper.get_by_car_row("ABCDEF")
        text = row.section_text.values[0]
        self.assertEqual(text, None)

    def testForContent(self):
        row = self.scraper.get_by_car_row("Budapest")
        text = row.section_text.values[0]
        self.assertIsInstance(text, str)

if __name__ == "__main__":
    unittest.main()