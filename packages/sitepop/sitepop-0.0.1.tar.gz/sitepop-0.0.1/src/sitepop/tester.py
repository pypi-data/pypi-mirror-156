import webbrowser
from sitepop import *
import predefcss
import predefcomponents


class Tester:
    def __init__(self):
        pass

    def viewDocument(self, doc):
        ''' opens document in browswer '''
        doc.writeToFile(file_name='test.html')
        i = 0
        for ss in doc.stylesheets:
            ss[0].writeToFile()
            
        webbrowser.open_new_tab(doc.getOutputLocation() + 'test.html')
        

## some basic test/example code
tester = Tester()
d = Document()
s = Stylesheet()

a = predefcomponents.RoundCornerButton(text='Test Button')
header = predefcomponents.BasicHeader()
p = Tag('p', text='Title Here', styles='font-size: 30px')

header.addChild(p)
d.body.addChild(header)
d.body.addChild(a)


# last stuff to call
d.linkStylesheet(s)
d.collectStyleGroups()
d.syncStyleGroupsAndStylesheet(s)
tester.viewDocument(d)
