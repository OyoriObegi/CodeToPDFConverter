import os
import tempfile
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_by_name
from pygments.formatters import HtmlFormatter
import nbformat
from nbconvert import HTMLExporter
from playwright.sync_api import sync_playwright
import mistune

def html_to_pdf(html_content: str, output_path: str, wait_for_mathjax: bool = False):
    """
    Renders HTML to a PDF using Playwright.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        page = browser.new_page()
        page.set_content(html_content, wait_until="networkidle")
        
        if wait_for_mathjax:
            # Jupyter notebooks use MathJax for equations. We need to wait for it to finish rendering.
            # MathJax 2 adds 'MathJax_Processed' or 'MathJax_SVG_Hidden' to elements, but a generic delay
            # or waiting for the network is usually sufficient. Let's add a small script to check if MathJax is done.
            try:
                page.wait_for_function('() => window.MathJax ? window.MathJax.isReady : true', timeout=5000)
                # Give it an extra moment to draw to the DOM
                page.wait_for_timeout(500)
            except Exception:
                pass # If it times out or MathJax isn't there, just proceed
        
        page.pdf(path=output_path, format="A4", print_background=True, margin={"top": "1in", "bottom": "1in", "left": "1in", "right": "1in"})
        browser.close()

def convert_py_to_pdf(python_code: str, output_path: str):
    """
    Converts Python source code to PDF.
    """
    # Generate HTML with Pygments
    formatter = HtmlFormatter(full=True, style='monokai', linenos=True)
    html_content = highlight(python_code, PythonLexer(), formatter)
    
    # Add some extra CSS to make it look like a nice document
    extra_style = '''
    <style>
        body { font-family: monospace; font-size: 14px; background-color: #272822; color: #f8f8f2; }
        pre { white-space: pre-wrap; word-wrap: break-word; margin: 0; padding: 15px; }
        .linenos { color: #75715e; margin-right: 10px; border-right: 1px solid #75715e; padding-right: 10px; }
    </style>
    '''
    html_content = html_content.replace('</head>', f'{extra_style}</head>')
    
    html_to_pdf(html_content, output_path)

def convert_ipynb_to_pdf(ipynb_content: str, output_path: str):
    """
    Converts Jupyter Notebook (.ipynb) content to PDF.
    """
    # Read notebook format
    notebook_node = nbformat.reads(ipynb_content, as_version=4)
    
    # Configure HTMLExporter
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic'
    
    # Export to HTML
    (body, resources) = html_exporter.from_notebook_node(notebook_node)
    
    # Optional: Hide the input prompts [1]: if desired
    extra_style = '''
    <style>
        .jp-InputArea-prompt { display: none !important; }
        .jp-OutputArea-prompt { display: none !important; }
    </style>
    '''
    body = body.replace('</head>', f'{extra_style}</head>')
    
    # Convert HTML to PDF using Playwright
    html_to_pdf(body, output_path, wait_for_mathjax=True)


class HighlightRenderer(mistune.HTMLRenderer):
    """Custom mistune renderer that syntax-highlights fenced code blocks with Pygments."""

    def block_code(self, code, info=None, **attrs):
        if info:
            lang = info.strip().split()[0]
            try:
                lexer = get_lexer_by_name(lang, stripall=True)
            except Exception:
                lexer = get_lexer_by_name('text', stripall=True)
        else:
            lexer = get_lexer_by_name('text', stripall=True)
        formatter = HtmlFormatter(style='monokai', nowrap=False, cssclass='highlight')
        return highlight(code, lexer, formatter)


def convert_md_to_pdf(md_content: str, output_path: str):
    """
    Converts Markdown (.md) content to PDF.
    """
    # Parse markdown with syntax-highlighted code blocks
    renderer = HighlightRenderer()
    markdown = mistune.create_markdown(renderer=renderer, plugins=['table', 'strikethrough', 'task_lists'])
    body_html = markdown(md_content)

    # Pygments CSS for code highlighting
    pygments_css = HtmlFormatter(style='monokai').get_style_defs('.highlight')

    html_content = f'''<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
        font-size: 15px;
        line-height: 1.7;
        color: #24292e;
        max-width: 800px;
        margin: 0 auto;
        padding: 2rem;
    }}
    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 0.5em; }}
    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; margin-top: 1.5em; margin-bottom: 0.5em; }}
    h3 {{ font-size: 1.25em; margin-top: 1.5em; margin-bottom: 0.5em; }}
    h4 {{ font-size: 1em; margin-top: 1.5em; margin-bottom: 0.5em; }}
    h5, h6 {{ font-size: 0.875em; margin-top: 1.5em; margin-bottom: 0.5em; }}
    p {{ margin-top: 0; margin-bottom: 1em; }}
    a {{ color: #0366d6; text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    img {{ max-width: 100%; height: auto; }}
    blockquote {{
        margin: 0 0 1em 0;
        padding: 0.5em 1em;
        border-left: 4px solid #dfe2e5;
        color: #6a737d;
        background: #f6f8fa;
    }}
    blockquote p {{ margin-bottom: 0; }}
    code {{
        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
        font-size: 0.9em;
        background: #f6f8fa;
        padding: 0.2em 0.4em;
        border-radius: 3px;
    }}
    pre {{
        background: #272822;
        border-radius: 6px;
        padding: 1em;
        overflow-x: auto;
        margin-bottom: 1em;
    }}
    pre code {{
        background: none;
        padding: 0;
        color: #f8f8f2;
        font-size: 0.85em;
    }}
    .highlight {{
        background: #272822;
        border-radius: 6px;
        padding: 1em;
        overflow-x: auto;
        margin-bottom: 1em;
    }}
    table {{
        border-collapse: collapse;
        width: 100%;
        margin-bottom: 1em;
    }}
    th, td {{
        border: 1px solid #dfe2e5;
        padding: 0.6em 1em;
        text-align: left;
    }}
    th {{
        background: #f6f8fa;
        font-weight: 600;
    }}
    tr:nth-child(even) {{ background: #f6f8fa; }}
    hr {{
        border: none;
        border-top: 2px solid #eaecef;
        margin: 2em 0;
    }}
    ul, ol {{
        margin-top: 0;
        margin-bottom: 1em;
        padding-left: 2em;
    }}
    li {{ margin-bottom: 0.25em; }}
    li > ul, li > ol {{ margin-top: 0.25em; margin-bottom: 0; }}
    {pygments_css}
</style>
</head>
<body>
{body_html}
</body>
</html>'''

    html_to_pdf(html_content, output_path)
