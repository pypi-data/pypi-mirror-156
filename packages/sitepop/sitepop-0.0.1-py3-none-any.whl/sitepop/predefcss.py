'''
Here are some pre-defined styles to speed up common styling ops, like centering on a page
'''

from sitepop import *

# center in parent
centerOnPage = StyleGroup('.centerOnPage', 'centerOnPage')
centerOnPage.setProperty('margin', 'auto')
centerOnPage.setProperty('max-width', '100%')
centerOnPage.setProperty('max-height', '100%')

# center contents
flexCentered = StyleGroup('.flexCentered', 'flexCentered')
flexCentered.setProperty('display', 'flex')
flexCentered.setProperty('justify-content', 'center')
flexCentered.setProperty('align-items', 'center')

# max width and height, no margin
fillContainer = StyleGroup('.fillContainer', 'fillContainer')
fillContainer.setProperty('margin', '0px')
fillContainer.setProperty('height', '100%')
fillContainer.setProperty('width', '100%')

# generic rounded borders with 8px radius
roundBorders = StyleGroup('.roundBorders', 'roundBorders')
roundBorders.setProperty('border-radius', '8px')

# fully rounded borders
circleBorder = StyleGroup('.circleBorder', 'circleBorder')
circleBorder.setProperty('border-radius', '50%')

# semi-transparent background white
seeThruLite = StyleGroup('.seeThruLite', 'seeThruLite')
seeThruLite.setProperty('background-color', 'rgba(255, 255, 255, .5)')

# semi-transparent background black
seeThruDark = StyleGroup('.seeThruDark', 'seeThruDark')
seeThruDark.setProperty('background-color', 'rgba(0, 0, 0, .5)')

# common button appearance
basicButton = StyleGroup('.basicButton', 'basicButton')
basicButton.setProperty('width', '150px')
basicButton.setProperty('height', '30px')
basicButton.setProperty('font-size', '20px')
basicButtonHover = StyleGroup('.basicButton:Hover')
basicButtonHover.setProperty('color', 'white')
basicButtonActive = StyleGroup('.basicButton:Active')
basicButtonActive.setProperty('background-color', 'black')

# basic header
basicHeader = StyleGroup('.basicHeader', 'basicHeader')
basicHeader.setProperty('width', '100%')
basicHeader.setProperty('height', '100px')
basicHeader.setProperty('background-color', 'black')
basicHeader.setProperty('color', 'whitesmoke')
basicHeader.setProperty('display', 'flex')
basicHeader.setProperty('align-items', 'center')
basicHeader.setProperty('justify-content', 'space-evenly')
