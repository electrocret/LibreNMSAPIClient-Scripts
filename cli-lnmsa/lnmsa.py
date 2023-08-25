#!/usr/bin/env python3
from Libs.LibreNMSAPIClient import LibreNMSAPIClient
import click
import pandas as pd
from pathlib import Path
import sys
from rich import box
from rich.console import Console
from rich.table import Table
from typing import Optional
import json
import re
libreapi=LibreNMSAPIClient()
console=Console()

def df_to_table( #From: https://gist.github.com/avi-perl/83e77d069d97edbdde188a4f41a015c4
    pandas_dataframe: pd.DataFrame,
    rich_table: Table,
    show_index: bool = False,
    index_name: Optional[str] = None,
) -> Table:
    """Convert a pandas.DataFrame obj into a rich.Table obj.
    Args:
        pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
        show_index (bool): Add a column with a row count to the table. Defaults to True.
        index_name (str, optional): The column name to give to the index column. Defaults to None, showing no value.
    Returns:
        Table: The rich Table instance passed, populated with the DataFrame values."""

    if show_index:
        index_name = str(index_name) if index_name else ""
        rich_table.add_column(index_name)

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column))

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(index)] if show_index else []
        row += [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table

def list_functions():
        funcs=pd.DataFrame.from_dict(libreapi.functions,orient='index')
        funcs.sort_index(inplace=True)
        console.print("[red]For help execute lnmsa --help[/red]")
        table = Table(show_header=True, header_style="bold magenta")
        table.row_styles = ["none", "dim"]
        table.box = box.ROUNDED
        table.add_column("Function")
        table.add_column("Route")
        table.add_column("Request Method")
        for index, row in funcs.iterrows():
            table.add_row(*[index,row['route'],row['request_method']])
        console.print(table)

#CLI Options
@click.command()
@click.argument('parameters', nargs=-1)
@click.option('--xlsx',help='Write output to xlsx at specified location')
@click.option('--csv',help='Write output to csv at specified location')
@click.option('-c','--columns',help='Comma List of Columns to show')
@click.option('-s','--search', type=(str, str),help='Search Column',multiple=True,metavar='<column> <regex>')
@click.option('-f','--filter', type=(str, str),help='Filter Column',multiple=True,metavar='<column> <regex>')
@click.option('-so', '--sort',help='Column to sort data by')
@click.option('-sa','--sort_ascending', help='Sort data in Ascending Order',is_flag=True,default=False)
@click.option('-h','--human_readable', help='Convert Columns into human readable - WIP',is_flag=True,default=False)
@click.option('-n','--rows',help='Number of rows to show. (or use paging)',default=20)
@click.option('-p','--paging', help='Page output. (Rows is ignored)',is_flag=True,default=False)
def main(parameters,xlsx,csv,sort,sort_ascending,human_readable,columns,rows,paging,search,filter):
    '''
    This Script makes the LibreNMS API endpoints accessible through commandline.
    The command structure for GET, and DELETE request methods is 'lnmsa <function> <parameters>'
    The command structure for POST,PATCH, and PUT request mothods is 'lnmsa <json of object> <function> <parameters>'
    Parameter order should be in the order they appear in the function route.
    For more information on what each API function does, please check LibreNMS Documentation.
    '''
    if not parameters:
        list_functions()
    else:
        first=True
        params=[]
        function=""
        req_method=""
        for param in parameters:
            if first:
                try:
                    function=libreapi.__getattr__(param)
                except:
                    pass
                first=False
                if param not in libreapi.functions:
                    sfunction_name=param.split('_',1) #Check for flags in function call
                    if len(sfunction_name) == 2 and sfunction_name[1] in libreapi.functions:
                        function_name=sfunction_name[1]
                    else:
                        console.print("[red]Invalid Function provided[/red]")
                        list_functions()
                        exit()
                else:
                    function_name=param
                req_method=libreapi.functions[function_name]['request_method']
            else:
                if req_method in 'POST,PATCH,PUT':
                    param=json.loads(param)
                    req_method=None
                params.append(param)
        console.print("[cyan]Requesting Data from Libre[/cyan]")
        try:
            response=function(*params)
        except Exception as err:
            print("An Error occurred")
            print(str(err))
            exit()
        data=pd.DataFrame(response if type(response) is list else [response])
        response_columns=data.columns
        for verify_column in [sort,*dict((x, y) for x, y in search).keys(),*dict((x, y) for x, y in filter).keys()]:
            if type(verify_column) == str and verify_column not in data:
                console.print("[red]Column '" + verify_column + "' not found in response[/red]")
                exit()
        if sort:
            data.sort_values(by=[sort], ascending=sort_ascending,inplace=True)
            data.reset_index(drop=True,inplace=True)
        if search:
            for scol,sreg in dict((x, y) for x, y in search).items():
                data=data[data[scol].apply(lambda x: True if re.search(sreg,x)else False)]
            data.reset_index(drop=True,inplace=True)
        if filter:
            for fcol,freg in dict((x, y) for x, y in filter).items():
                data=data[data[fcol].apply(lambda x: True if re.search(freg,x)else False)]
            data.reset_index(drop=True,inplace=True)
        #if human_readable:

        if columns:
            data=data.filter(items=columns.split(","))
        if xlsx == None and csv == None:
            try:
                table = Table(show_header=True, header_style="bold magenta")
                table.row_styles = ["none", "dim"]
                table.box = box.ROUNDED
                console.print("[blue]Data Shape:[/blue] " + str(data.shape) + " - [red]Only showing first " + str(rows) + " rows.(See help --rows)[/red]") if not paging and data.shape[0] != 1 and type(rows) is  int and rows < data.shape[0] else console.print("[blue]Data Shape:[/blue] " + str(data.shape))
                console.print("[blue]Columns:[/blue] " + ','.join(response_columns)+" [red](See help --columns)[/red]")if len(data.columns) > 5 else console.print("[blue]Columns:[/blue] " + ','.join(response_columns))
                console.print("\n[bold cyan]Data from Libre:[/bold cyan]")
                if data.shape[0] == 1:
                    table.add_column("Key")
                    table.add_column("Value")
                    for label, content in data.items():
                        table.add_row(*[label,str(content.values[0])])
                else:
                    if not paging and type(rows) is  int and rows < data.shape[0]:
                        data=data.truncate(after=rows)
                    table = df_to_table(data, table)
                if paging:
                    with console.pager():
                        console.print(table)
                else:
                    console.print(table)
            except (BrokenPipeError, IOError):
                pass
            sys.stderr.close()
        else:
            if xlsx:
                with pd.ExcelWriter(xlsx) as work_book:
                    data.to_excel(work_book, engine="xlsxwriter",index=False)
            if csv:
                filepath = Path(csv)  
                filepath.parent.mkdir(parents=True, exist_ok=True)  
                data.to_csv(filepath,index=False)
            console.print("[bold cyan]Data written to file[/bold cyan]")
                

if __name__ == '__main__':
    main()
