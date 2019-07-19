#!/usr/bin/env python
import argparse
import os
import sys
import xml.etree.ElementTree as ET

GROUP = 'g'
CIRCLE = 'circle'
STYLE = 'style'
LINE = 'line'
RECT = 'rect'

DWIDTH = 96
DHEIGHT = 192
ZERO = []
ONE = [(48, 48)]
TWO = [(78, 16), (16, 78)]
THREE = [(78, 16), (48, 48), (16, 78)]
FOUR = [(78, 16), (78, 78), (16, 16), (16, 78)]
FIVE = [(78, 16), (78, 78), (48, 48), (16, 16), (16, 78)]
SIX = [(78, 16), (78, 47), (78, 78), (16, 16), (16, 47), (16, 78)]

PIP_LAYOUT = [ZERO, ONE, TWO, THREE, FOUR, FIVE, SIX]
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
    else:  # indent after last subelem
        if not subelem.tail or not subelem.tail.strip():
            subelem.tail = i

    return elem


SIZING = {
    'enable-background': 'new 0.0 0.0 30.0 60.0',
    'height': '60.0mm',
    'width': '30.0mm',
    'x': '0.0mm',
    'y': '0.0mm',
    'version': '1.1',
    'viewBox': 'new 0.0 0.0 96.0 192.0'
}


class DominoSVG(object):
    def __init__(self, topnum, bottomnum, fg='0,0,0', bg='255,255,255'):
        assert topnum in range(7) and bottomnum in range(7)
        self.topnum = topnum
        self.bottomnum = bottomnum
        self.init_svg(fg, bg)

    def init_svg(self, fg, bg):
        self.svg = ET.Element('svg',
                              attrib=SIZING,
                              xmlns='http://www.w3.org/2000/svg')
        self.svg.text = '\n'
        style = 'stroke: rgb({fg}); fill: rgb({bg}); '.format(fg=fg, bg=bg)
        style += 'stroke-width: 2px; '
        style += 'stroke-linejoin: round; stroke-linecap: round; '
        ET.SubElement(self.svg, RECT, x='5', y='5',
                      width=str(DWIDTH), height=str(DHEIGHT),
                      style=style)
        style = 'stroke: rgb({fg}); stroke-width: 1px;'.format(fg=fg)
        ET.SubElement(self.svg, LINE, x1='11', y1='101', x2='95', y2='101',
                      style=style)
        self.tile_grp(TOP, self.topnum, fg, bg)
        self.tile_grp(BOTTOM, self.bottomnum, fg, bg)

    def tile_grp(self, transform, number, fg='0,0,0', bg='255,255,255'):
        pips = PIP_LAYOUT[number]
        if pips:
            grp = ET.SubElement(self.svg, GROUP, transform=transform)
            style = 'stroke: rgb({fg}); fill: rgb({fg})'.format(fg=fg)
            for pip in pips:
                ET.SubElement(grp, CIRCLE, r='7', cx=str(pip[0]), cy=str(pip[1]),
                              style=style)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--html', action='store_true')
    ap.add_argument('--dir', action='store', default=None)
    ap.add_argument('--foreground', '-f', action='store', default='(0,0,0)')
    ap.add_argument('--background', '-b', action='store',
                    default='(255,255,255)')
    args = ap.parse_args()

    dominoes = [DominoSVG(i, j, fg=args.foreground, bg=args.background)
                for i in range(7) for j in range(i, 7)]
    if args.dir and not os.path.exists(args.dir):
        os.makedirs(args.dir)
    if args.html:
        mkhtml(dominoes, outdir=args.dir)
    else:
        mkfiles(dominoes, outdir=args.dir)


def mkfiles(dominoes, outdir=None):
    for d in dominoes:
        ofile = os.path.join(outdir if outdir else '.',
                             '{}_{}.svg'.format(d.topnum, d.bottomnum))
        with open(ofile, 'w') as f:
            t = ET.ElementTree(element=indent(d.svg))
            t.write(f, encoding='utf-8', xml_declaration=True)


def mkhtml(dominoes, outdir=None):
    ofile = os.path.join(outdir if outdir else '.',
                         'dominos.html')

    html = ET.Element('html', lang='en')
    body = ET.SubElement(html, 'body')
    for n in 7, 6, 5, 4, 3, 2, 1:
        ul = ET.SubElement(body, 'ul', attrib={'class': 'table'})
        row = dominoes[:n]
        del dominoes[:n]

        li = ET.SubElement(ul, 'li', attrib={'class': 'row'})
        li.extend([d.svg for d in row])

    with open(ofile, 'w') as f:
        t = ET.ElementTree(element=indent(html))
        t.write(f, encoding='utf-8', xml_declaration=True)


if __name__ == '__main__':
    main()
