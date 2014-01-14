from bs4 import BeautifulSoup
import urllib2

url = "http://www.mangaupdates.com/groups.html?id=630"
soup = BeautifulSoup(urllib2.urlopen(url).read())
series = soup.find("td", text="Series").findParent("table").findAll("a", {"title": "Series Info"})

list = ()
list = [(ser.string.replace(" (Novel)",""),ser.attrs["href"]) for ser in series]