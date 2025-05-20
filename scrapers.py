import mechanicalsoup
import pandas as pd
import unicodedata
from datetime import datetime
from ordered_set import OrderedSet

class WikivoyageScraper():    
    # Extract
    def get_by_car_row(self, city):
        browser = mechanicalsoup.StatefulBrowser(
            user_agent="Wikivoyage-Scraper-Bot/1.0"
        )

        article_link = f"https://en.wikivoyage.org/wiki/{city}"

        browser.open(article_link)
        url = browser.url
        headers = browser.page.find_all("h3", string="By car")
        browser.close()
        headers_len = len(headers)

        text = ""
        status = ""
        has_get_around_by_car_section = None

        try: 
            status_table = browser.page.find("table", class_="article-status")
            status_id = status_table.attrs["id"]
        except:
            status = "unknown"
            status_id = "unknown"

        if headers_len == 2:
            get_by_header = headers[1]
            has_get_around_by_car_section = True
            get_by_children = get_by_header.parent.parent.children
            for child in get_by_children:                
                if child.name == "p":
                    text += child.text

                if child.name == "section":
                    for section in child.contents:
                        if section.name == "p":
                            text += section.text
                            
                        if section.name == "ul":
                            text += section.text
        elif headers_len == 1:
            get_by_header = headers[0]

            mw_heading_2 = get_by_header.parent.parent.parent.find("div", class_="mw-heading mw-heading2").find("h2").text

            if mw_heading_2 == "Get around":
                has_get_around_by_car_section = True
            else:
                has_get_around_by_car_section = False

            get_by_children = get_by_header.parent.parent.children
            for child in get_by_children:                
                if child.name == "p":
                    text += child.text

                if child.name == "section":
                    for section in child.contents:
                        if section.name == "p":
                            text += section.text
                            
                        if section.name == "ul":
                            text += section.text
        else:
            text = None
            has_get_around_by_car_section = False
            
        if status_id == "outline_city" or status_id == "outline_region" or status_id == "outline_country":
            status = "Outline"
        elif status_id == "usable_city" or status_id == "usable_region" or status_id == "usable_country":
            status = "Usable"
        elif status_id == "guide_city" or status_id == "guide_region" or status_id == "guide_country":
            status = "Guide"
        elif status_id == "star_city" or status_id == "star_region" or status_id == "star_country":
            status = "Star"
        else:
            status = "Unknown/Stub"

        if has_get_around_by_car_section == True:
            word_count = len(text)
            return pd.DataFrame({
                "city": [city],
                "wikivoyage_article": [url],
                "has_get_around_by_car_section": [has_get_around_by_car_section],
                "section_text": [text],
                "article_status": [status],
                "section_word_count": [word_count],
                "polarity": [0],
                "subjectivity": [0],
                "date_retrieved": [str(datetime.now())]
            })
        else:
            return pd.DataFrame({
                "city": [city],
                "wikivoyage_article": [url],
                "has_get_around_by_car_section": [has_get_around_by_car_section],
                "section_text": [text],
                "article_status": [status],
                "section_word_count": [0],
                "polarity": [0],
                "subjectivity": [0],
                "date_retrieved": [str(datetime.now())]
            })    
class WikipediaScraper():
    wikipedia_article = "https://en.wikipedia.org/wiki/Globalization_and_World_Cities_Research_Network"

    # scraping just so I can get a good data source on global cities based on how prominent they are
    # we need to get all of the <li> elements within the 2024 city classification list and retrieve the info as well
    # then we combine it somehow with the world cities dataset

    def get_div_cols(self):
        browser = mechanicalsoup.StatefulBrowser()
        browser.open(self.wikipedia_article)
        browser.close()

        div_cols = browser.page.find_all("div", class_='div-col')
        cols_list = []
        for div_col in div_cols:
            cols_list.append(div_col)
        
        return cols_list

    def grab_world_cities(self, div_cols):
        cities = []
        actual_cities = []

        for city in div_cols:
            for child in city.children:
                cities.append((child.text))

        for city in cities: 
            splitted = city.split("\n ")
            for split in splitted:
                actual_cities.append(split)

        unique_cities = (OrderedSet(actual_cities))
        unique_cities.remove("\n")
        actual_cities = list(unique_cities)

        cleaned_cities = []
        for city in actual_cities:
            city = city.strip().replace("[i]", "").replace(" (1)", "").replace(" (2)", "").replace(" (3)", "").replace(" (4)", "").replace(" (6)", "")
            ascii_city = ''.join(char for char in unicodedata.normalize('NFD', city) if unicodedata.category(char) != 'Mn')
            cleaned_cities.append(ascii_city)
            
        return cleaned_cities

    def grab_city_country(self, div_cols):
        countries = []

        for div_col in div_cols:
            imgs = div_col.find_all("img")
            for img in imgs:
                if img.attrs['alt'] != "Increase" and img.attrs['alt'] != "Decrease":
                    countries.append(img.attrs['alt'])

        return countries
    
    def get_wikipedia_articles(self, div_cols):
        articles = []

        for div_col in div_cols:
            links = div_col.find_all("a")
            for link in links:
                wiki_link = "https://en.wikipedia.org" + link.find_parent("li").contents[2]['href']
                articles.append(wiki_link)

        return list(OrderedSet(articles))
    
    def get_world_cities(self):
        div_cols = self.get_div_cols()

        cities = self.grab_world_cities(div_cols)
        countries = self.grab_city_country(div_cols)
        wiki_articles = self.get_wikipedia_articles(div_cols)
        
        return pd.DataFrame({
            "city": cities,
            "country": countries,
            "wiki_article": wiki_articles
        })