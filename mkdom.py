#!/usr/bin/env python
from __future__ import unicode_literals, print_function
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
DBORDER = 5
DPIPRADIUS = 7

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

SIZING={}

_SIZING = {
    'height': '60.0mm',
    'width': '30.0mm',
    'x': '0.0mm',
    'y': '0.0mm',
    'version': '1.1',
    'viewBox': 'new 0.0 0.0 96.0 192.0'
}

RECTSTYLE = (
     'stroke: rgb({fg}); fill: rgb({bg}); stroke-width: 2px; stroke-linejoin: round; stroke-linecap: round; '
    )
LINESTYLE= 'stroke: rgb({fg}); stroke-width: 1px; '
PIPSTYLE = 'stroke: rgb({fg}); fill: rgb({fg}); '

PIPCLASS = 'pip'
LINECLASS = 'line'
RECTCLASS = 'rect'

def styles(css_styles, cls, explicitstyle, *args, **kwargs):
    if css_styles:
        return {'class': cls}
    else:
        return {'style': explicitstyle.format(*args,**kwargs)}

def css_def(*args,**kwargs):
    linestyle=LINESTYLE.format(*args, **kwargs)
    rectstyle=RECTSTYLE.format(*args, **kwargs)
    pipstyle=PIPSTYLE.format(*args, **kwargs)

    return ('.{rect} {{ {rectstyle} }}\n'
            '.{line} {{ {linestyle} }}\n'
            '.{pip}  {{ {pipstyle} }}\n').format(
                line=LINECLASS, rect=RECTCLASS, pip=PIPCLASS,
                linestyle=linestyle, pipstyle=pipstyle, rectstyle=rectstyle )

class DominoSVG(object):
    def __init__(self, num1, num2, fg='0,0,0', bg='255,255,255', matrix='', css_styles=False):
        assert num1 in range(7) and num2 in range(7)
        # always order tuples lower, higher
        self.dtuple = (num1,num2) if num1 < num2 else (num2,num1)
        self.init_svg(fg, bg, matrix, css_styles)

    def init_svg(self, fg, bg, matrix, css_styles):
        self.svg = ET.Element('svg',
                              attrib=SIZING,
                              xmlns='http://www.w3.org/2000/svg')
        self.svg.text = '\n'

        attrib = {'transform':'matrix({0})'.format(matrix)} if matrix else {}
        outer_grp = ET.SubElement(self.svg, GROUP, attrib=attrib)

        styleattrib = styles(css_styles, RECTCLASS, RECTSTYLE, fg=fg, bg=bg)
        ET.SubElement(outer_grp, RECT, x='5', y='5',
                      width=str(DWIDTH), height=str(DHEIGHT),
                      attrib=styleattrib)

        styleattrib = styles(css_styles, LINECLASS, LINESTYLE, fg=fg)
        ET.SubElement(outer_grp, LINE, x1='11', y1='101', x2='95', y2='101',
                      attrib=styleattrib)

        styleattrib = styles(css_styles, PIPCLASS, PIPSTYLE, fg=fg)
        self.tile_grp(outer_grp, TOP, self.dtuple[0], attrib=styleattrib)
        self.tile_grp(outer_grp, BOTTOM, self.dtuple[1], attrib=styleattrib)

    def tile_grp(self, grp, transform, number, attrib):
        pips = PIP_LAYOUT[number]
        if pips:
            tilegrp = ET.SubElement(grp, GROUP, transform=transform)
            for pip in pips:
                ET.SubElement(tilegrp, CIRCLE, r=str(DPIPRADIUS),
                              cx=str(pip[0]), cy=str(pip[1]), attrib=attrib)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--python', action='store_true',
                    help='Generate as a dict in a python module, ignore foreground, background')
    ap.add_argument('--dir', action='store', default='.')
    ap.add_argument('--foreground', '-f', action='store', default='0,0,0')
    ap.add_argument('--background', '-b', action='store', default='255,255,255')
    ap.add_argument('--matrix', '-m', action='store', default='',
                    help='Elements of a 2d transformation, e.g "1,0,0,1,0,0"')
    args = ap.parse_args()

    fg = '{fg}' if args.python else args.foreground
    bg = '{bg}' if args.python else args.background
    matrix = '{matrix}' if args.python else args.matrix
    dominoes = [DominoSVG(i, j, fg=fg, bg=bg, matrix=matrix, css_styles=True)
                 for i in range(7) for j in range(i, 7)]

    if not os.path.exists(args.dir):
        os.makedirs(args.dir)

    if args.python:
        mkpython(dominoes, css_styles=True, outdir=args.dir)
    else:
        with open(os.path.join(args.dir,'dominoes.css'), 'w') as f:
            f.write(css_def(fg=fg, bg=bg))
        mkfiles(dominoes, outdir=args.dir)


def mkfiles(dominoes, outdir='.'):
    '''Write the dominoes as individual SVG files'''

    for d in dominoes:
        ofile = os.path.join(outdir, '{}_{}.svg'.format(*d.dtuple))
        with open(ofile, 'w') as f:
            t = ET.ElementTree(element=indent(d.svg))
            t.write(f, encoding='utf-8', xml_declaration=True)


def mkpython(dominoes, module='dominoes', outdir='.', css_styles=True):
    '''Write the dominoes as constants in a module named dominoes'''
    ofile = os.path.join(outdir, '{}.py'.format(module))
    with open(ofile, 'w') as f:
        f.write("DWIDTH = {}\n".format(DWIDTH))
        f.write("DHEIGHT = {}\n".format(DHEIGHT))
        # write some rotation matrixes
        f.write("M2d_IDENTITY = '1, 0, 0, 1, 0, 0'\n")
        f.write("M2d_ROTLEFT = '0, -1, 1, 0, 0, {}'\n".format(DWIDTH+2*DBORDER))
        f.write("M2d_ROTRIGHT = '0, 1, -1, 0, 0, {}'\n".format(DHEIGHT+2*DBORDER ))
        f.write("SVG_DICT = dict( (\n")
        for d in dominoes:
            f.write("    ({}, '''{}'''),\n".format(
                d.dtuple, ET.tostring(d.svg).decode('utf-8')))
        f.write("    )\n")
        if css_styles:
            f.write("DOMINO_CSS = '''{}'''\n".format(
                css_def(fg='0,0,0',bg='255,255,255')))


if __name__ == '__main__':
    main()
