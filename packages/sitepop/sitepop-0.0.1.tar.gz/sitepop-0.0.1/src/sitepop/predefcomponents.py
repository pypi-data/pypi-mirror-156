from sitepop import Tag, StyleGroup, Component
import predefcss


class Subcontainer(Component):
    def __init__(self):
        super(Subcontainer, self).__init__(tag_name='div')
        self.addStyleGroup(predefcss.centerOnPage)
        self.addStyleGroup(predefcss.seeThruLite)
        self.applyStyleGroupClassNames()


class RoundCornerButton(Component):
    def __init__(self, text=''):
        super(RoundCornerButton, self).__init__(tag_name='button')
        self.text=text
        self.addStyleGroup(predefcss.roundBorders)
        self.addStyleGroup(predefcss.basicButton)
        self.addStyleGroup(predefcss.basicButtonHover)
        self.addStyleGroup(predefcss.basicButtonActive)
        self.addStyleGroup(predefcss.seeThruDark)
        self.applyStyleGroupClassNames()
        

class BasicHeader(Component):
    def __init__(self):
        super(BasicHeader, self).__init__(tag_name='div')
        self.addStyleGroup(predefcss.basicHeader)
        self.applyStyleGroupClassNames()
