import urllib2
import string
import re
from pprint import pprint
from HTMLParser import HTMLParser


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class BakaTsukiParser:
    def __init__(self, urlParse, wikiLocation="https://www.baka-tsuki.org/project/"):
        self.projectPageTitle = urlParse
        self.mainURL = "".join([wikiLocation.split("?")[0], "?action=raw&title=%s"])
        self.strangeProjecs = ["[[Tabi ni Deyou:Volume 1|Our Journey to the End of the Ceasing World]]",
                          "The \"HEAVY OBJECT\" Series",
                          "Rakuin no Monshou", "Iris on Rainy Days", "Gekkou", "Web Novel Translation",
                          "== ''Shakugan no Shana'' [http://en.wikipedia.org/wiki/Yashichiro_Takahashi Yashichiro Takahashi]=="]


    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    def wm2txt(self, var):
        try:
            var = var.strip("=")
            var = self.strip_tags(var)
            intWikiLinkReg = re.compile("\[\[(.+?)\|(.+?)\]\]")
            btSpecificLinks = re.compile("\(\s*\[.+?\]\s*?\)")
            for i in btSpecificLinks.findall(var):
                var = var.replace(i, "")
            try:
                if var.split(intWikiLinkReg.match(var).group())[0] is "":
                    var = intWikiLinkReg.match(var).groups()[1].strip("()").strip()
                else:
                    var = intWikiLinkReg.match(var).groups()[0]
            except:
                None
            return var.strip()
        except:
            return var.strip()

    def getChapters(self, ContentLines):
        chapters = []
        internalLinkIdent = ["[[", "]]"]
        for volumesMainContentLine in ContentLines:
            if all(linkIdent in volumesMainContentLine for linkIdent in internalLinkIdent) and "File:" not in volumesMainContentLine and "Image:" not in volumesMainContentLine:
                volumesMainContentLine = volumesMainContentLine.split("[[", 1)[-1].strip()
                volumesMainContentLine = volumesMainContentLine.split("]]", 1)[0].strip()
                try:
                    chapterLink, chapterName = volumesMainContentLine.split("|")
                    chapters.append(
                        (filter(lambda x: x in string.printable, self.strip_tags(chapterName)), chapterLink))
                except:
                    chapters.append((volumesMainContentLine))
            else:
                continue
        return chapters

    def getVolumes(self):
        #structureObjects = ["Synopsis", "Updates", "Staff" "History", "links"]
        projectPageContent = urllib2.urlopen(self.mainURL % self.projectPageTitle).read()
        projectPageContentSplit = [i.strip() for i in filter(None, projectPageContent.split('\n'))]
        projectPageHeaders = [line.strip() for line in projectPageContentSplit if line.startswith("==")]
        projectPageHeadersMain = [header for header in projectPageHeaders if "===" != header[:3] and "==" == header[:2]]
        volumesMain = [mainHeader for mainHeader in projectPageHeadersMain if " by " in mainHeader]
        if len(volumesMain) == 1:
            volumesMain = ''.join(volumesMain)
        elif len(volumesMain) == 0:
            for j in self.strangeProjecs:
                a = [mainHeader for mainHeader in projectPageHeadersMain if j in mainHeader]
                if len(a) == 1:
                    volumesMain = ''.join(a)
                    break
        else:
            volumesMain = volumesMain[0]
        volumesMainIndex = projectPageHeadersMain.index(volumesMain)
        if volumesMainIndex < (len(projectPageHeadersMain) - 1):
            volumesMainContent = projectPageContentSplit[projectPageContentSplit.index(volumesMain) + 1:projectPageContentSplit.index(projectPageHeadersMain[volumesMainIndex + 1])]
        else:
            volumesMainContent = projectPageContentSplit[projectPageContentSplit.index(volumesMain) + 1:]
        volumeIndexes = [volumesMainContent.index(line) for line in volumesMainContent if line.startswith("==")]
        volumeList = []
        if len(volumeIndexes) > 0:
            for volumeIndex in volumeIndexes:
                volumeName = self.wm2txt(filter(lambda x: x in string.printable, volumesMainContent[volumeIndex]))
                try:
                    nextIndex = volumeIndexes[volumeIndexes.index(volumeIndex) + 1]
                except IndexError:
                    nextIndex = None
                volumeList.append((volumeName, self.getChapters(volumesMainContent[volumeIndex + 1:nextIndex])))
        elif len(volumeIndexes) == 0:
            volumeName = self.wm2txt(filter(lambda x: x in string.printable, self.volumesMain))
            volumeList.append((volumeName, self.getChapters(volumesMainContent)))
        else:
            print("Failed to Parse: %s" % self.projectPageTitle)
        if len(volumeList) > 0: return volumeList
