import os
import argparse

import json
from jinja2 import Environment, FileSystemLoader
from jinja2 import nodes

from PythonExtension import PythonExtension
from SQLExtension import SQLExtension
import filters


def get_options():
    """
    Parse arguments provided
    """
    parser = argparse.ArgumentParser(description="PySQL: Python + SQL Parser using Jinja2")

    parser.add_argument(
        "infile",
        help="pysql source file"
    )

    parser.add_argument(
        '-o',
        '--outfile',
        type=str,
        help="File to write generated SQL to",
        required=False
    )
    
    parser.add_argument(
        '-c',
        '--configs',
        type=str,
        help="Path to configuration file",
        required=False
    )

    options = vars(parser.parse_args())

    return options


def jinja_convert_type(value):
    """
    convert all types to something that jinja can work with in templates
    """
    if type(value) == list:
        for i in range(len(value)):
            value[i] = jinja_convert_type(value[i])
    
    elif type(value) in (tuple, set):
        dtype = type(value)
        tmp_list = list(value)
        for i in range(len(tmp_list)):
            tmp_list[i] = jinja_convert_type(tmp_list[i])
        value = dtype(tmp_list)

    elif type(value) == dict:
        tmp_dict = dict()
        for key, val in value.items():
            key = jinja_convert_type(key)
            tmp_dict[key] = jinja_convert_type(val)
        value = tmp_dict

    elif type(value) not in (int, float, str, bytes, type(None)):
        value = str(value)

    return value


def get_pysql_env():
    """
    return environment configured for PySQL
    """
    env = Environment(loader=FileSystemLoader(os.environ.get('PYSQL_TEMPLATE_DIR', '.')))
    env.trim_blocks = True
    env.lstrip_blocks = True

    # set python execution context on environment
    env.python_execution_context = dict()

    # add convert type function 
    env.jinja_convert_type = jinja_convert_type

    # register the custom tags
    env.add_extension(PythonExtension)
    env.add_extension(SQLExtension)

    # add custom variable filters
    env.filters['quote'] = filters.quote_wrap
    env.filters['where'] = filters.where
    env.filters['sql_escape'] = filters.sql_escape
    env.filters['columns'] = filters.columns
    env.filters['copy_table'] = filters.copy_table

    return env

def convert(pysql):
    """
       Convert PySQL to SQL
    """
    # Create a Jinja2 environment
    env = get_pysql_env()

    # Compile the Jinja2 template
    jinja_template = env.from_string(pysql)

    # Render the template and return the result as a string
    return jinja_template.render()
    
    
if __name__ == '__main__':
        
    # read command line options
    options = get_options()
    
    if options['configs']:
        # read config file
        try:
            with open(options['configs'], 'r') as config_file:
                configs = json.load(config_file)
        except FileNotFoundError as e:
            print("Config file not found")
            exit()
        except json.decoder.JSONDecodeError as e:
            print("Config file improperly formatted")
            exit()
        
        # set environment variables from config file 
        if configs.get('PYSQL_DB_CONN_STRING', False):
            os.environ['PYSQL_DB_CONN_STRING'] = configs['PYSQL_DB_CONN_STRING']
        
        if configs.get('PYSQL_TEMPLATE_DIR', False):
            os.environ['PYSQL_TEMPLATE_DIR'] = configs['PYSQL_TEMPLATE_DIR']
    
    # read input file to get source
    with open(options['infile'], 'r') as pysql_file:
        pysql = pysql_file.read()
    
    sql = convert(pysql)
    
    if options['outfile']:
        with open(options['outfile'], 'w') as outfile:
            outfile.write(sql)

    else:
        print(sql)
