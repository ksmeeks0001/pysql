"""
Jinja filters to help with writing SQL queries
"""

def quote_wrap(value, quotes='single'):
    """
    return value wrapped in quotes
    if quotes contained within the value then escape
    """
    if quotes == 'single':
        wrap = "'"
    elif quotes == 'double':
        wrap = '"'
    else:
        raise Exception("Invalid value for quotes ('single', 'double')")

    return wrap + value.replace(wrap, f'\\{wrap}') + wrap

def sql_escape(value):
    """
    wrap value in backticks 
    """
    return f"`{value}`"

def columns(value):
    """
    return a string of escaped column names from a list
    """
    return ','.join([sql_escape(x) for x in value])

def where(value, operator='='):
    """
    wrap values in a SQL where clause with quotes if the value is a string
    use 'IS (NOT) NULL' for None type 
    """
    if value is None and operator == '=':
        return 'IS NULL'
    if value is None and operator == '!=':
        return 'IS NOT NULL'

    if value is None:
        value = 'NULL'
        
    if isinstance(value, int) or isinstance(value, float):
        return operator + ' ' + str(value)
    
    return operator + ' ' + quote_wrap(value)

def copy_table(original_table, new_table, database=None, new_database=None):
    """
    generate SQL for creating a table with the same 
    structure as another and inserting all the data.
    """
    copy_sql = f"create table {sql_escape(new_database)+'.' if new_database is not None else ''}{sql_escape(new_table)} like {sql_escape(database)+'.' if database is not None else ''}{sql_escape(original_table)};"
    copy_sql += f"\ninsert into {sql_escape(new_database)+'.' if new_database is not None else ''}{sql_escape(new_table)} select * from {sql_escape(database)+'.' if database is not None else ''}{sql_escape(original_table)};"

    return copy_sql