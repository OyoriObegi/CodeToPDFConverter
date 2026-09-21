import os
import tempfile
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import nbformat
from nbconvert import HTMLExporter
from playwright.sync_api import sync_playwright

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
