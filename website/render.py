import marko, re
from marko import inline, ast_renderer
from marko.ext.gfm import GFMExtension

class LatexInline(inline.InlineElement):
    pattern = r'\$(.+?)\$'
    parse_children = False
    
    def __init__(self, match):
        self.math = match.group(1)

class LatexBlock(inline.InlineElement):
    pattern = r'\$\$([\S\s]+?)\$\$'
    parse_children = False
    
    def __init__(self, match):
        self.math = match.group(1)
        
class SolutionBlock(marko.block.BlockElement):
    pattern = re.compile(r'<solution>([\S\s]+?)<\/solution>')
    inline_children = True
    priority = 8
    
    def __init__(self, match):
        self.children = match.group(1)

    @classmethod
    def match(cls, source):
        return source.expect_re(cls.pattern)
    
    @classmethod
    def parse(cls, source):
        m = source.match
        source.consume()
        return m
        
class GenericBlock(SolutionBlock):
    pattern = re.compile(r'<block ?(.+?)?>([\S\s]+?)<\/block>')
    priority = 2
    
    def __init__(self, match):
        self.children = match.group(2)
        self.title = match.group(1)

class ShortCatsoopBlock(GenericBlock):
    pattern = re.compile(r'<catsoopq ?(.+?)?>([\S\s]+?)<\/catsoopq>')
    inline_children = False
        
class RawBlock(SolutionBlock):
    pattern = re.compile(r'<raw>([\S\s]+?)<\/raw>')
    inline_children = False
    
    def __init__(self, match):
        self.content = match.group(1)

class TopHeader(marko.block.Heading):
    pattern = re.compile(
        r"^(#)((?=\s)[^\n]*?|[^\n\S]*)(?:(?<=\s)(?<!\\)#+)?[^\n\S]*$\n?",
        flags=re.M,
    )
    
    priority = 10
    
        
class RenderMixin(marko.HTMLRenderer):
    def render_latex_inline(self, element):
        return f'\({element.math}\)'
    
    def render_latex_block(self, element):
        return f'\[{element.math}\]'
    
    def render_generic_block(self, element):
        text = self.render_children(element)
        
        content = '<div class="infoblock">'
        
        if element.title is not None:
            content += f'<div class="blocktitle">{element.title}</div>'
        
        content += f"""<div class="blockcontent">{text}</div></div>"""

        
        return content
    
    def render_solution_block(self, element):
        text = self.render_children(element)
        return """
<div class="infoblock solutionblock">
<div class="blocktitle">Solution<span class="solutionhelp"> (hover to show)</span>:</div><div class="blockcontent">""" + text + "</div></div>"
    
    def render_raw_block(self, element):
        return element.content

    def render_top_header(self, element):
        return f"<div id='toptitle'>{self.render_heading(element)}</div>"
    
    def render_short_catsoop_block(self, element):
        if element.title is None:
            element.title = ""
        
        return f"""<div class="infoblock catsoopblock">
<div class="blockcontent">
{element.title}
<br /><input type="text" />
<input type="button" value="Submit">
<div class="catsoopres"></div>
<div class="catsoopsol">
{element.children}
</div>
</div>
</div>"""



class BrainyRenderExtension:
    elements = [
        LatexInline,
        LatexBlock,
        SolutionBlock,
        GenericBlock,
        RawBlock,
        TopHeader,
        ShortCatsoopBlock
    ]
    renderer_mixins = [RenderMixin]

def get_title(raw):
    def get_heading(ast):
        if ast['element'] == 'heading':
            while isinstance(ast['children'], list):
                ast = ast['children'][0]
            return ast['children']
        
        if isinstance(ast['children'], list):
            for c in ast['children']:
                h = get_heading(c)
                if h:
                    return h
        
        return None
    
    return get_heading(marko.Markdown(
        renderer=ast_renderer.ASTRenderer
    ).convert(raw))

def render(raw):
    marko.block.HTMLBlock.priority = 0
    return marko.Markdown(
        extensions=[BrainyRenderExtension, 'codehilite', GFMExtension]
    ).convert(raw)