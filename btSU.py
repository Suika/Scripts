import mwclient
import gspread
import urllib2
import urllib
from xml.dom import minidom

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def check(tags):
    pageid=[]
    missing=[]
    invalid=[]
    for j in tags:
        try:
            for page in minidom.parse(urllib2.urlopen("https://www.baka-tsuki.org/project/api.php?action=query&titles=%s&format=xml" % "|".join([urllib.quote(unicode(i).encode('UTF8')) for i in j]))).getElementsByTagName('page'):
                if page.attributes.has_key('pageid'):
                    pageid.append(page.getAttribute('title'))
                elif page.attributes.has_key('missing'):
                    missing.append(page.getAttribute('title'))
                elif page.attributes.has_key('invalid'):
                    invalid.append(page.getAttribute('title'))
                else:
                    print 'I haz problemz:', page.getAttribute('title')
        except urllib2.URLError, e:
            print(e)
    return pageid, missing, invalid

c = gspread.Client(auth=('user', 'pass'))
c.login()
sht = c.open_by_key('0AheiUhJFmWFIdFhENFduU25GOGU3ZnpPMkVrZnByZkE')
worksheet = sht.get_worksheet(0)

list = dict([(worksheet.acell( 'A' + str( i ) ).value, worksheet.acell( 'H' + str( i ) ).value) for i in range(2,worksheet.row_count) if (worksheet.acell( 'H' + str( i ) ).value != '')])

p,m,i = check(split_list(list.keys(),10))

site = mwclient.Site('baka-tsuki.org', path='/project/')
site.login("User", "Password")
page = site.Pages['']
text = page.edit()
page.save(text + u'\nstrange stuff', summary = 'Bot Test')
