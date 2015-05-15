import mwclient, gspread, urllib2, urllib, re, sys
from xml.dom import minidom


def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [alist[i * length // wanted_parts: (i + 1) * length // wanted_parts]
            for i in range(wanted_parts)]


def check(tags):
    pageid = []
    missing = []
    invalid = []
    for j in tags:
        try:
            for page in minidom.parse(urllib2.urlopen(
                            "https://www.baka-tsuki.org/project/api.php?action=query&titles=%s&format=xml" % "|".join(
                            [urllib.quote(unicode(i).encode('UTF8')) for i in j]))).getElementsByTagName('page'):
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


c = gspread.Client(auth=('Google User', 'Password'))
c.login()

print("Logging into Google")

sht = c.open_by_key('0AheiUhJFmWFIdFhENFduU25GOGU3ZnpPMkVrZnByZkE')
worksheet = sht.get_worksheet(0)

print("Getting Worksheet")

list = dict([(worksheet.acell('A' + str(i)).value.replace("_", " "), worksheet.acell('H' + str(i)).value) for i in
             range(2, worksheet.row_count) if (worksheet.acell('H' + str(i)).value != '')])

if not list:
    sys.exit(1)

print("Got data from worksheet")

p, m, i = check(split_list(list.keys(), 10))

print("Checked if page exists")

if not p:
    sys.exit(1)

site = mwclient.Site('baka-tsuki.org', path='/project/')
site.login("B-T User", "Password")

print("Logged into Baka-Tsuki")

regex = re.compile('(\{\{Status\|(Idle|Inactive|Stalled)\}\})', re.IGNORECASE)

for t in p:
    print("Processing %s" % t)
    page = site.Pages[t]
    text = page.edit()
    found_in_text = regex.findall(text)

    try:
        if found_in_text:
            if len(found_in_text) == 1:
                if found_in_text[0][1] == list[t]:
                    continue
                else:
                    changed_text = re.sub(found_in_text[0][0], "{{Status|%s}}" % list[t], text)
            else:
                for j in sorted(set([b[0] for b in found_in_text])):
                    text.replace(j, "")
                changed_text = "{{Status|%s}}\n\n" % list[t] + text
            page.save(changed_text, summary='Status Cleanup')
        else:
            changed_text = "{{Status|%s}}\n\n" % list[t] + text
            page.save(changed_text, summary='Status Cleanup')
    except:
        print("Failed to process %s" % t)
