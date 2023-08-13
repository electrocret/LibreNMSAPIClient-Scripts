#!/usr/bin/env python3
from Libs.LibreNMSAPIClient import LibreNMSAPIClient
import click
import pandas as pd
from pathlib import Path
import sys
from rich import box
from rich.console import Console
from rich.table import Table
libreapi=LibreNMSAPIClient()
console=Console()

def df_to_table(
    pandas_dataframe: pd.DataFrame,
    rich_table: Table
) -> Table:
    """Convert a pandas.DataFrame obj into a rich.Table obj.
    Args:
        pandas_dataframe (DataFrame): A Pandas DataFrame to be converted to a rich Table.
        rich_table (Table): A rich Table that should be populated by the DataFrame values.
    Returns:
        Table: The rich Table instance passed, populated with the DataFrame values."""

    for column in pandas_dataframe.columns:
        rich_table.add_column(str(column))

    for index, value_list in enumerate(pandas_dataframe.values.tolist()):
        row = [str(x) for x in value_list]
        rich_table.add_row(*row)

    return rich_table

#CLI Options
@click.command()
@click.argument('parameters', nargs=-1)
@click.option('--xlsx',help='Write output to xlsx at specified location')
@click.option('--csv',help='Write output to csv at specified location')
@click.option('-c','--columns',help='Comma List of Columns to show')
@click.option('-s', '--sort',help='Column to sort data by')
@click.option('-sa','--sort_ascending', help='Sort data in Ascending Order',is_flag=True,default=False)
@click.option('-h','--human_readable', help='Convert Columns into human readable values - WIP',is_flag=True,default=False)
@click.option('-n','--rows',help='Number of rows to show. (or use paging)',default=20)
@click.option('-p','--paging', help='Page output. (Rows is ignored)',is_flag=True,default=False)
def main(parameters,xlsx,csv,sort,sort_ascending,human_readable,columns,rows,paging):
    '''
    This Script makes the LibreNMS API endpoints accessible through commandline.
    The command structure for GET, and DELETE request methods is 'lnmsa <function> <parameters>'
    The command structure for POST,PATCH, and PUT request mothods is 'lnmsa <json of object> <function> <parameters>'
    Parameter order should be in the order they appear in the function route.
    For more information on what each API function does, please check LibreNMS Documentation.
    '''
    if not parameters:
        funcs=pd.DataFrame.from_dict(libreapi.functions,orient='index')
        funcs.drop(columns=['response_key','cache','flags'],inplace=True)
        funcs.sort_index(inplace=True)
        funcs.rename_axis("Available Functions",axis=1,inplace=True)
        print("For help execute lnmsa --help")
        print(funcs.to_string())
    else:
        first=True
        params=[]
        function=""
        for param in parameters:
            if first:
                function=libreapi.__getattr__(param)
                first=False
            else:
                params.append(param)
        console.print("[cyan]Requesting Data from Libre[/cyan]")
        try:
            response=function(*params)
        except Exception as err:
            print("An Error occurred")
            print(str(err))
            exit()
        data=pd.DataFrame(response if type(response) is list else [response])
        if sort:
            if sort in data:
                data.sort_values(by=[sort], ascending=sort_ascending,inplace=True)
                data.reset_index(drop=True,inplace=True)
            else:
                console.print("[red]Sort Column not found[/red]")
                exit()
        if columns:
            data=data.filter(items=columns.split(","))
        #if human_readable:
            
        if xlsx == None and csv == None:
            try:
                table = Table(show_header=True, header_style="bold magenta")
                table.row_styles = ["none", "dim"]
                table.box = box.ROUNDED
                console.print("[blue]Data Shape:[/blue] " + str(data.shape) + " - [red]Only showing first " + str(rows) + " rows.(See help --rows)[/red]") if not paging and data.shape[0] != 1 and type(rows) is  int and rows < data.shape[0] else console.print("[blue]Data Shape:[/blue] " + str(data.shape))
                console.print("[blue]Columns:[/blue] " + ','.join(data.columns)+" [red](See help --columns)[/red]")if len(data.columns) > 5 else console.print("[blue]Columns:[/blue] " + ','.join(data.columns))
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
