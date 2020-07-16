import markdown
from markdown import Extension
from markdown.blockprocessors import BlockProcessor
from markdown.inlinepatterns import InlineProcessor
import xml.etree.ElementTree as etree
import re




class AdmonitionExtension(Extension):
    """ Admonition extension for Python-Markdown. """

    def extendMarkdown(self, md):
        """ Add Admonition to Markdown instance. """
        md.registerExtension(self)

        md.parser.blockprocessors.register(AdmonitionProcessor(md.parser), 'admonition', 105)

class AdmonitionProcessor(BlockProcessor):

    CLASSNAME = 'infoblock'
    CLASSNAME_TITLE = 'blocktitle'
    RE = re.compile(r'(?:^|\n)!!! ?([\w\-]+(?: +[\w\-]+)*)(?: +"(.*?)")? *(?:\n|$)')
    RE_SPACES = re.compile('  +')

    def test(self, parent, block):
        sibling = self.lastChild(parent)
        return self.RE.search(block) or \
            (block.startswith(' ' * self.tab_length) and sibling is not None and
             sibling.get('class', '').find(self.CLASSNAME) != -1)

    def run(self, parent, blocks):
        sibling = self.lastChild(self.lastChild(parent))
        block = blocks.pop(0)
        m = self.RE.search(block)

        if m:
            block = block[m.end():]  # removes the first line

        block, theRest = self.detab(block)

        if m:
            klass, title = self.get_class_and_title(m)
            div = etree.SubElement(parent, 'div')
            div.set('class', '{} {}'.format(self.CLASSNAME, klass))
            
            if title:
                p = etree.SubElement(div, 'div')
                if title != 'Solution':
                    p.text = title
                else:
                    p.text = 'Solution:'
                    hover = etree.SubElement(p, 'span')
                    hover.set('class', 'solutionhelp')
                    hover.text = ' (hover to show)'
                p.set('class', self.CLASSNAME_TITLE)
            
            div = etree.SubElement(div, 'div')
            div.set('class', 'blockcontent')

        else:
            div = sibling
        
        self.parser.parseChunk(div, block)

        if theRest:
            # This block contained unindented line(s) after the first indented
            # line. Insert these lines as the first block of the master blocks
            # list for future processing.
            blocks.insert(0, theRest)

    def get_class_and_title(self, match):
        klass, title = match.group(1).lower(), match.group(2)
        klass = self.RE_SPACES.sub(' ', klass)
        if title is None:
            # no title was provided, use the capitalized classname as title
            title = klass.split(' ', 1)[0].capitalize()
        elif title == '':
            # an explicit blank title should not be rendered
            # e.g.: `!!! warning ""` will *not* render `p` with a title
            title = None
        return klass, title

def get_title(raw):
    return raw.strip().split('\n')[0].split('#')[1].strip()

def render(raw):
    return markdown.markdown(
        raw, extensions=[AdmonitionExtension()]
    )