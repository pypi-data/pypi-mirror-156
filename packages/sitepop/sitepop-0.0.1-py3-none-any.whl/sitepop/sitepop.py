import re

class Doc:
    ''' base class inherited by Document and Stylesheet '''
    def __init__(self, name='', output_location=''):
        self.name = ''
        self.output_location = ''
    
    def fullPath(self):
        return self.output_location + self.name
    
    def getOutputLocation(self):
        path = self.output_location
        if len(path) > 0:
            path += '/'
        return path

    def setOutputLocation(self, path):
        self.output_location = path

    
    def writeToFile(self, file_name=''):
        if file_name == '':
            file_name = self.name
        path = self.getOutputLocation() + file_name
        f = open(path, 'w')
        print(self, file=f)
        f.close()
        
        #################################
        ####### END OF Doc CLASS  #######
        #################################  


class StyleGroup:
    ''' defines a bunch of styles to be applied to a selector '''
    def __init__(self, selector, className=''):
        self.selector = selector
        self.className = className
        self.properties = dict()

    def removeProperty(self, prop):
        if prop in self.properties:
            self.properties.pop(prop)

    def setProperty(self, prop, val):
        if prop not in self.properties:
            self.properties[prop] = val    

        #################################
        #### END OF StyleGroup CLASS ####
        #################################           


class Tag:

    class Classes:
        def __init__(self, *args):
            self.classes = list()
            if len(args) > 0:
                for arg in args:
                    self.add(arg)

        def __len__(self):
            return len(self.classes)

        def __str__(self):
            if len(self.classes) == 0:
                return ""
            else:
                return ' '.join(self.classes)

        def add(self, *args):
            starting_length = len(self.classes)
            # TODO: DRY this out
            for a in args:
                if type(a) != str:
                    raise Exception("Classes must be added as strings, not %s" % str(type(a)))
                if a.count(' ') > 0:
                    # can pass in muliple classes as a string separated by spaces
                    a = a.split()
                    for name in a:
                        if self.isValidClassName(self, name):
                            self.classes.append(name)
                        else:
                            raise Exception("Class name %s is not in the correct format" % name)
                else:
                    if self.isValidClassName(self, a):
                        self.classes.append(a)

            if len(self.classes) > starting_length:
                self.classes.sort()

        def remove(self, *args):
            # TODO: DRY this out
            for a in args:
                if type(a) != str:
                    raise Exception("Classes must be added as strings, not %s" % str(type(a)))
                if a.count(' ') > 0:
                    # can pass in muliple classes as a string separated by spaces
                    a = a.split()
                    for name in a:
                        if self.isValidClassName(self, name) and name in self.classes:
                            self.classes.remove(name)
                        else:
                            raise Exception("Class name %s is not in the correct format" % name)
                else:
                    if self.isValidClassName(self, a) and name in self.classes:
                        self.classes.add(a)

        def removeAll(self):
            self.classes = list()

        def toHtml(self):
            output = ''
            if len(self.classes) > 0:
                output = 'class="%s"' % ' '.join(self.classes)
            return output
            
            
        @staticmethod
        def isValidClassName(self, c):
            ''' returns True if c is a valid CSS class name '''
            return re.search('^[_a-zA-Z]+[_a-zA-Z0-9-]*', c)

        #################################
        ######END OF ClassList CLASS#####
        #################################


    class Styles:
        def __init__(self, styles=''):
            self.styles = dict()
            
            if len(styles) > 0:
                if styles.count(':') in (0, 1):
                    tup = self.parseStyle(self, styles)
                    self.set(tup[0], tup[1])
                elif styles.count(':') > 1:
                    try:
                        styles = styles.split(';')
                        for s in styles:
                            tup = self.parseStyle(s)
                            self.set(tup[0], tup[1])
                    except:
                        raise Exception('Multiple styles must be passed in with format "styleName:styleValue; styleName:styleValue"')
            

        @staticmethod
        def parseStyle(self, s):
            ''' tries to get key val from string formatted like "key: val" '''
            try:                
                key = s[:s.index(':')].strip()
                val = s[s.index(':')+1:].strip()
                return key, val
            except:
                raise Exception('Style not in expected format. Format expected to be "styleName:styleValue"')

        def remove(self, name):
            if name in self.styles:
                self.styles.pop(name)

        def set(self, name, value=''):
            self.styles[name] = value

        def toHtml(self):
            output = ''
            if len(self.styles) > 0:
                output = 'style="%s"' % ' '.join([name + ': ' + self.styles[name] + ';' for name in self.styles])
            return output

        #################################
        ######  END OF Styles CLASS #####
        #################################


    class Attributes:
        def __init__(self, attributes=''):
            self.attributes = dict()
            if len(attributes) > 0:
                if attributes.count('=') in (0, 1):
                    k,v = self.parseValue(attributes, '=')
                    self.set(k,v)
                elif attributes.count('=') > 1:
                    try:
                        if attributes.count(';') > 0:
                            attributes = attributes.split(';')
                        else:
                            attributes = attributes.split(' ')
                        for s in attributes:
                            k,v = self.parseValue(s, '=')
                            self.set(k,v)
                    except:
                        raise Exception('Multiple attributes must be passed in with format "attName=attValue; attName=attValue"')                

        @staticmethod
        # TODO: add base class and abstract this logic out 
        def parseValue(s, sep):
            ''' tries to get key val from string formatted like "key[sep]val" '''
            try:
                key = s[:s.index(sep)].strip()
                val = s[s.index(sep)+1:].strip()
                return key, val
            except:
                raise Exception('Style or Attribute not in expected format. Format expected to be "styleName%sstyleValue"' % sep)
            
        def set(self, name, value=''):
            self.attributes[name] = value
            
        def toHtml(self):
            output = ''
            if len(self.attributes) > 0:
                output = ' '.join([name + '="' + self.attributes[name] + '"' for name in self.attributes])
            return output            
        
        #################################
        #### END OF Attributes CLASS ####
        #################################
    
    def __init__(
        self, 
        tag_name, 
        text='', 
        children=list(), 
        classes='', 
        tag_id='', 
        styles='',
        attributes='',
        autoclose=True
    ):
        self.tag_name = tag_name
        self.text = text

        self.children = list()
        if type(children) == list:
            for child in children:
                self.addChild(child)
        else:
            self.addChild(children)
            
        if classes == '':
            self.classes = self.Classes()
        else:
            self.classes = self.Classes(classes)
        
        self.tag_id = tag_id

        if styles == '':
            self.styles = self.Styles()
        else:
            self.styles = self.Styles(styles)

        if attributes == '':
            self.attributes = self.Attributes()
        else:
            self.attributes = self.Attributes(attributes)
        
        self.outer_tabs = 0
        self.inner_tabs = 1
        self.autoclose = autoclose
        
    def addChild(self, child):
        child.indent(self.outer_tabs)
        self.children.append(child)

    def addScript(self, src=''):
        script = Tag('script', attributes='src=%s'%src)
        self.addChild(script)
        
    def dedent(self):
        if self.outer_tabs > 0:
            self.outer_tabs -= 1
            self.inner_tabs -= 1
            for child in self.children:
                child.dedent()
        
    def getId(self):
        output = ""
        if self.tag_id != output:
            output = 'id="%s"' % self.tag_id
        return output
    
    def getIndentedText(self):
        if self.text == '':
            return ''
        return (self.inner_tabs * "\t") + self.text + '\n'    

    def getPrintedChildren(self):
        return '\n'.join([str(c) for c in self.children])

    def getTagExtras(self):
        extras = {
            'classes': self.classes,
            'styles': self.styles,
            'attributes': self.attributes
        }
        return extras

    def indent(self, parent_tabs=0):
        if parent_tabs==0:
            self.outer_tabs += 1
        else:
            self.outer_tabs = parent_tabs + 1

        self.inner_tabs = self.outer_tabs + 1
        for child in self.children:
            child.indent(self.outer_tabs)         
    
    def removeAllChildren(self):
        for i in reversed(range(len(self.children))):
            del self.children[i]
        
    def removeChildByIndex(self, index):
        ''' remove child based on index '''
        self.removeChild(self.children[index])
        
    def removeChild(self, obj):
        self.children.remove(obj)
        
    def tagExtrasToHtml(self):
        extras = self.getTagExtras()
        return ' '.join([extras[key].toHtml() for key in extras if len(extras[key].toHtml()) > 0])
        
    def __str__(self):
        if len(self.children) == 0:
            if self.autoclose:
                # example would be <p>sometext</p> or <script...></script>
                return "%s<%s %s>%s</%s>" % (
                    "\t" * self.outer_tabs, 
                    self.tag_name, 
                    self.tagExtrasToHtml(), 
                    self.text,
                    self.tag_name
                )
            else:
                # an example is <link rel="stylesheet"...> or <br>
                return "%s<%s %s>" % (
                    '\t' * self.outer_tabs,
                    self.tag_name,
                    self.tagExtrasToHtml()
                )
        else:
            return "%s<%s %s>\n%s\n%s</%s>" % (
                    "\t" * self.outer_tabs, 
                    self.tag_name, 
                    self.tagExtrasToHtml(), 
                    #'\t' * self.inner_tabs + self.text, 
                    self.getPrintedChildren(), 
                    "\t" * self.outer_tabs, 
                    self.tag_name
                )

    ##################################
    #####   END OF Tag CLASS    ######
    ##################################


class Document(Doc):            
    
    def __init__(self, lang='en', name='', output_location=''):
        super(Document, self).__init__(name=name, output_location=output_location)
        self.doctype = ''
        if self.name == '':
            self.name = 'index.html'

        self.content = Tag('html')
        
        self.stylesheets = list()
        self.head = Tag('head')
        self.head.addChild(Tag('title', text='Test'))
        
        self.body = Tag('body')
        self.styleGroups = list()
        self.content.addChild(self.head)
        self.content.addChild(self.body)

    def __str__(self):
        return str(self.content)

    def collectStyleGroups(self):
        ''' BFS search for component stylegroups '''
        q = list()
        if len(self.body.children) > 0:
            for c in self.body.children:
                q.append(c)
            while len(q) > 0:
                current = q[0]
                q = q[1:]
                if issubclass(type(current), Component):
                    if len(current.styleGroups) > 0:
                        for sg in current.styleGroups:
                            if sg not in self.styleGroups:
                                self.styleGroups.append(sg)
                        for c in current.children:
                            if c not in q:
                                q.append(c)                    

    def linkStylesheet(self, stylesheet):
        if type(stylesheet) != Stylesheet:
            raise Exception('parameter for Document.linkStylesheet() must be of type Stylesheet')
        if stylesheet not in self.stylesheets:
            ss = Tag(
                'link',
                attributes="rel=stylesheet href=" + stylesheet.fullPath() + " type=text/css",
                autoclose=False
            )
            self.head.addChild(ss)
            self.stylesheets.append([stylesheet, ss])

    def removeStylesheet(self, stylesheet):
        if type(stylesheet) != Stylesheet:
            raise Exception('parameter for Document.linkStylesheet() must be of type Stylesheet')
        for ss in self.stylesheets:
            if ss[0] == stylesheet:
                self.head.removeChild(ss[1])
                self.stylesheets.remove(ss)
                break

    def syncStyleGroupsAndStylesheet(self, stylesheet):
        if type(stylesheet) != Stylesheet:
            raise Exception('parameter for Document.linkStylesheet() must be of type Stylesheet')
        for sg in self.styleGroups:
            stylesheet.addStyleGroup(sg)
            
       
###########################
## END OF Document CLASS ##
###########################

        
class Stylesheet(Doc):
    def __init__(self, name=''):
        super(Stylesheet, self).__init__(name=name)
        if self.name=='':
            self.name = 'style.css'
        self.output_location = ''
        self.styles = dict() #[property][value] = [class names]

    def __str__(self):
        groups = dict()
        for pn in self.styles:
            for pv in self.styles[pn]:
                namesAsKey = tuple(sorted(self.styles[pn][pv]))
                if namesAsKey not in groups:
                    groups[namesAsKey] = list()
                groups[namesAsKey].append('%s: %s;' % (pn, pv))

        # TODO: perform smart consolidation here
        
        output = ''
        for group in groups:
            c = ',\n'.join(group)
            c += ' {\n\t'
            c += '\n\t'.join(groups[group])
            c += '\n}'
            output += c + '\n\n'
        return output

    def addStyleGroup(self, sg):
        if type(sg) != StyleGroup:
            raise Exception('parameter for Stylesheet.addStyleGroup() must be of type StyleGroup')
        for prop in sg.properties:
            self.setProperty(sg.selector, prop, sg.properties[prop])

    def cleanSelectorFromProperty(self, selector, propertyName):
        if propertyName in self.styles:
            for val in self.styles[propertyName]:
                if selector in self.styles[propertyName][val]:
                    self.styles[propertyName][val].remove(selector)

    def setProperty(self, selector, propertyName, propertyValue):
        if propertyName not in self.styles:
            self.styles[propertyName] = dict()
        if propertyValue not in self.styles[propertyName]:
            self.styles[propertyName][propertyValue] = list()

        # search through values for this property and remove class name
        self.cleanSelectorFromProperty(selector, propertyName)

        # set property
        self.styles[propertyName][propertyValue].append(selector)

    def removeProperty(self, selector, propertyName):
        cleanSelectorFromProperty(selector, propertyName)

    def removeStyleGroup(self, sg):
        if type(sg) != StyleGroup:
            raise Exception('parameter for Stylesheet.removeStyleGroup() must be of type StyleGroup')
        for prop in sg.properties:
            self.removeProperty(sg.selector, prop)

###########################
# END OF Stylesheet CLASS #
###########################

class Component(Tag):

    # component is a tag with style groups attached

    def __init__(self, *args, **kwargs):
        super(Component, self).__init__(*args, **kwargs)
        self.styleGroups = list()
        # ^ styles doesn't apply any styling directly
        # rather, it makes sure that the styles
        # get included in the stylesheet

    def addStyleGroup(self, sg):
        if type(sg) != StyleGroup:
            raise Exception('parameter for Stylesheet.addStyleGroup() must be of type StyleGroup')
        if sg not in self.styleGroups:
            self.styleGroups.append(sg)

    def applyStyleGroupClassNames(self):
        for sg in self.styleGroups:
            self.classes.add(sg.className)

    def removeStyleGroup(self, sg):
        if type(sg) != StyleGroup:
            raise Exception('parameter for Stylesheet.removeStyleGroup() must be of type StyleGroup')
        if sg in self.styleGroups:
            self.styleGroups.remove(sg)

###########################
# END OF Component CLASS  #
###########################
