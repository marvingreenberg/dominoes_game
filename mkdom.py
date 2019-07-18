import xml.etree.ElementTree as ET
import sys

GROUP='g'
CIRCLE='circle'
STYLE='style'
LINE='line'
RECT='rect'

ZERO = []
ONE = [ (48,48) ]
TWO = [ (78,16), (16,78) ]
THREE = [ (78,16), (48,48), (16,78) ]
FOUR = [ (78,16), (78,78), (16,16), (16,78) ]
FIVE = [ (78,16), (78,78), (48,48), (16,16), (16,78) ]
SIX = [ (78,16), (78,47), (78,78), (16,16), (16,47), (16,78) ]

PIP_LAYOUT = [ZERO,ONE,TWO,THREE,FOUR,FIVE,SIX]
TOP = 'matrix(1, 0, 0, 1, 5, 5)'
BOTTOM = 'matrix(1, 0, 0, 1, 5, 101)'

def indent(elem, level=0):
    i = "\n" + level*"  "
    begin = True
    for subelem in elem:
        if begin:
            begin = False
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        indent(subelem, level+1)
    if begin:  # No subelements, subelem unset
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i
    else: # indent after last subelem
        if not subelem.tail or not subelem.tail.strip():
            subelem.tail = i

    return elem

class DominoSVG(object):
    def __init__(self,topnum, bottomnum):
        assert topnum in range(7) and bottomnum in range(7)
        self.topnum = topnum
        self.bottomnum = bottomnum
        self.init_svg()

    def init_svg(self):
        self.svg = ET.Element('svg',
            viewBox='0 0 106 202',
            xmlns='http://www.w3.org/2000/svg')
        self.svg.text = '\n'
        ET.SubElement(self.svg,
                      RECT, x='5', y='5', width='96', height='192',
                      style=
                      'stroke: rgb(0, 0, 0); '
                      'fill: rgb(255, 255, 255); '
                      'stroke-linejoin: round; stroke-linecap: round; '
                      'stroke-width: 2px;')
        ET.SubElement(self.svg,
                      LINE,  x1='11', y1='101', x2='95', y2='101',
                      style='stroke: rgb(0, 0, 0); stroke-width: 1px;' )
        self.tile_grp(TOP, self.topnum)
        self.tile_grp(BOTTOM, self.bottomnum)

    def tile_grp(self, transform, number):
        pips = PIP_LAYOUT[number]
        if pips:
            grp = ET.SubElement(self.svg, GROUP, transform=transform)
            for pip in pips:
               ET.SubElement(grp, CIRCLE, r='7', cx=str(pip[0]), cy=str(pip[1]),
                          style='stroke: rgb(0, 0, 0); fill: rbg(0,0,20)')

def main():
    html = False
    if len(sys.argv) > 1:
        if len(sys.argv) == 2 and '--html' == sys.argv[0]:
            html = True
        else:
            print('Usage: {} [--html]'.format(sys.argv[0]))
            sys.exit(1)

    dominoes = [DominoSVG(i,j)
                for i in range(7) for j in range(i,7) ]
    if html:
        mkhtml(dominoes)
    else:
        mkfiles(dominoes)

def mkfiles(dominoes):
    for d in dominoes:
        with open('{}_{}.svg'.format(d.topnum, d.bottomnum),'w') as f:
            t = ET.ElementTree(element=indent(d.svg))
            t.write(f, encoding='utf-8', xml_declaration=True)

def mkhtml(dominoes):
    html = ET.Element('html', lang='en')
    body = ET.SubElement(html, 'body')
    for n in 7,6,5,4,3,2,1:
        ul = ET.SubElement(body, 'ul', attrib={'class':'table'})
        row = dominoes[:n]
        del dominoes[:n]

        li = ET.SubElement(ul, 'li', attrib={'class':'row'})
        li.text = '\n'+ '\n'.join(d.svg for d in row)


if __name__ == '__main__':
    main()
