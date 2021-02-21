import requests
from bs4 import BeautifulSoup
import csv

class RightmoveScraper:

    results = []

    def fetch(self, url):
        print('HTTP GET request to URL: {}'.format(url), end='')
        response = requests.get(url)
        print(' | Status code: {}'.format(response.status_code))
        return response

    def parse(self, html):
        content = BeautifulSoup(html, 'lxml')

        titles = [title.text.strip() for title in content.findAll('h2', {'class': 'propertyCard-title'})]
        for index in range(0, len(titles)):
            if not titles[index].split()[0].isdigit():
                titles[index] = "? bedroom" + titles[index]
        bedrooms = [title.split()[0] for title in titles]
        property_type = [title.split("for sale")[0].split("bedroom")[1].strip().lower() for title in titles]
        addresses = [' '.join(address['content'].splitlines()) for address in content.findAll('meta', {'itemprop': 'streetAddress'})]
        descriptions = [description.text for description in content.findAll('span', {'data-test': 'property-description'})]
        prices = [price.text.strip() for price in content.findAll('div', {'class': 'propertyCard-priceValue'})]
        dates = [date.text for date in content.findAll('span', {'class': 'propertyCard-branchSummary-addedOrReduced'})]
        agents = [agent.text[4:] for agent in content.findAll('span', {'class': 'propertyCard-branchSummary-branchName'})]
        images = [image['src'] for image in content.findAll('img', {'itemprop': 'image'})]
        urls = ["https://www.rightmove.co.uk"+anchor['href'] for anchor in content.findAll('a', {'data-test': 'property-details'})]
        ids = [url.split("/")[-1] for url in urls]
        
        for index in range(0,len(titles)):
            self.results.append({
                'Bedrooms': bedrooms[index],
                'Property Type': property_type[index],
                'Address': addresses[index],
                'Description': descriptions[index],
                'Price': prices[index],
                'Date': dates[index],
                'Agent': agents[index],
                'Image': images[index],
                'URL': urls[index],
                'id': ids[index],
            })


    def to_csv(self):
        with open('rightmove.csv', 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.results[0].keys())
            writer.writeheader()

            for row in self.results:
                writer.writerow(row)

            print('Stored results to csv file')
            
    def run(self):
        
        for page in range(0, 1):
            index = page * 24
            url = "https://www.rightmove.co.uk/property-for-sale/find.html?locationIdentifier=REGION%5E1244&index={}&propertyTypes=&includeSSTC=false&mustHave=&dontShow=&furnishTypes=&keywords=".format(index)
            response = self.fetch(url)

            self.parse(response.text)    

        self.to_csv()

if __name__ == '__main__':
    scraper = RightmoveScraper()
    scraper.run()