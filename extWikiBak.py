import urllib2
import urllib
import cgi
import os
from xml.dom import minidom

path='/some/path'

os.chdir(path)
os.setuid(33)
os.setgid(33)

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

titles = []
ns=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 1198, 1199]

for j in ns:
    finished = False
    apcontinueB = False
    apcontinue = None
    while not finished:
        if not apcontinueB:
            a = minidom.parse(urllib2.urlopen("http://some.wiki.com/api.php?action=query&list=allpages&aplimit=500&apnamespace=%d&format=xml" % j)).getElementsByTagName('allpages')
            if len(a) == 2:
                apcontinue = a[0].getAttribute('apcontinue')
                apcontinueB = True
                [titles.append(i.getAttribute('title')) for i in a[1].childNodes]
            else:
                [titles.append(i.getAttribute('title')) for i in a[0].childNodes]
                finished = True
        elif apcontinueB:
            a = minidom.parse(urllib2.urlopen("http://some.wiki.com/api.php?action=query&list=allpages&aplimit=500&apcontinue=%s&apnamespace=%d&format=xml" % (urllib.quote(unicode(apcontinue).encode('UTF8')),j))).getElementsByTagName('allpages')
            if len(a) == 2:
                apcontinue = a[0].getAttribute('apcontinue')
                [titles.append(i.getAttribute('title')) for i in a[1].childNodes]
            else:
                [titles.append(i.getAttribute('title')) for i in a[0].childNodes]
                finished = True

len(list(chunks(titles, 2000)))

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:28.0) Gecko/20100101 Firefox/28.0'}

for k in list(chunks(titles, 2000)):
    print('array')
    print(len(k))
    params = urllib.urlencode([('title', 'Special:Export'), ('action', 'submit'), ('pages', "\n".join([unicode(l).encode('UTF8') for l in k])), ('curonly', 1), ('templates',1), ('wpDownload',0) ])
    req = urllib2.Request(url='http://some.wiki.com/index.php',data=params, headers=headers)
    response = urllib2.urlopen(req)
    _, params = cgi.parse_header(response.headers.get('Content-Disposition', ''))
    a =  open('.'+str(params['filename']), 'wb')
    a.write(response.read())
    a.close()

#os.system('GZIP=-9 tar --remove-files -cvzf Some-wiki-$(date +"%Y%m%d").tar.gz .Some-wiki-*.xml')

os.system('tar --remove-files -cvf - .Some-wiki-*.xml | pxz -9 > Some-wiki-$(date +"%Y%m%d").tar.xz')
