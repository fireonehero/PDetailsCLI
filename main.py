import click
from pypdf import PdfReader
from functools import wraps
import json, requests
from datetime import datetime

def clean_key(key):
    """Remove leading slash and convert to title case."""
    cleaned = key.lstrip('/').replace('_', ' ').title()
    return cleaned

def transform_value(key, value):
    """Transform specific metadata values."""
    if key in ['/creationdate', '/moddate']:
        try:
            cleaned_date = value.replace('D:', '').split('-')[0]
            parsed_date = datetime.strptime(cleaned_date, '%Y%m%d%H%M%S')
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return value
        
    if key == '/producer':
        return value.replace('Acrobat Distiller ', '')
    
    return value

def pdf_meta_wrap(func):
    @wraps(func)
    def meta_wrap(filename):
        reader = PdfReader(filename)
        return func(filename, reader)
    return meta_wrap

@click.group()
def metadata():
    """Tool for extracting PDF metadata."""
    pass

@metadata.command()
@click.argument('filename', type=click.Path(exists=True))
@pdf_meta_wrap
def get_all(filename, reader):
    """Gets all the metadata of any PDF you pass to it."""
    metadata = reader.metadata or {}
    
    formatted_metadata = "\n".join([
        f"{clean_key(key)}: {transform_value(key, value)}" 
        for key, value in metadata.items() 
        if value is not None
    ])
    
    click.echo(formatted_metadata if formatted_metadata else "No metadata found.")



@metadata.command()
@click.argument('filename', type=click.Path(exists=True))
@pdf_meta_wrap
def get_author(filename, reader):
    """Gets the author of the PDF you pass to it."""
    author = reader.metadata.get('author', 'No author found')
    click.echo(author)
   
if __name__ == '__main__':
    metadata()