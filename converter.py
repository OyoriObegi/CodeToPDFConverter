import os
import tempfile
from weasyprint import HTML, CSS
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
import nbformat
from nbconvert import HTMLExporter

def convert_py_to_pdf(python_code: str, output_path: str):
    """
    Converts Python source code to PDF.
    """
    # 1. Generate HTML with Pygments
    formatter = HtmlFormatter(full=True, style='monokai', linenos=True)
    html_content = highlight(python_code, PythonLexer(), formatter)
    
    # 2. Add some extra CSS for WeasyPrint to make it look like a nice document
    extra_css = CSS(string='''
        @page { size: A4; margin: 1in; }
        body { font-family: monospace; }
        pre { white-space: pre-wrap; word-wrap: break-word; }
    ''')
    
    # 3. Convert HTML to PDF
    HTML(string=html_content).write_pdf(output_path, stylesheets=[extra_css])

def convert_ipynb_to_pdf(ipynb_content: str, output_path: str):
    """
    Converts Jupyter Notebook (.ipynb) content to PDF.
    """
    # 1. Read notebook format
    notebook_node = nbformat.reads(ipynb_content, as_version=4)
    
    # 2. Configure HTMLExporter
    html_exporter = HTMLExporter()
    html_exporter.template_name = 'classic' # Or lab, or basic
    
    # 3. Export to HTML
    (body, resources) = html_exporter.from_notebook_node(notebook_node)
    
    # 4. Convert HTML to PDF using WeasyPrint
    # Note: nbconvert HTML output can be complex, WeasyPrint might have some minor rendering quirks 
    # compared to a browser, but it's generally very good for standard notebooks.
    extra_css = CSS(string='''
        @page { size: A4; margin: 1in; }
        body { font-size: 12px; }
        .jp-Cell { margin-bottom: 15px; }
        .jp-InputArea-prompt { display: none; }
    ''')
    
    HTML(string=body).write_pdf(output_path, stylesheets=[extra_css])
