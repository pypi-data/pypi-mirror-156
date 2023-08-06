#!/bin/python3

import click

from .api_methods import logger
from .cli_utils import CLI_Utils, PATH_UTILS


# To create args for each option, replace is_flag with 
# type=(<data_type1>, <data_type2>, ...) function in each option  
@click.group()
@click.pass_context
def main(ctx) -> int:
    try:
        ctx.obj = CLI_Utils()
    except Exception as err:
        logger.error(err)
    
    return 0

@main.command("init", help="Test and fmt .tf code.")
@click.pass_context
def init(ctx) -> None:
    ctx.obj.init()

@main.command("plan", help="Make plans to local repo.")
@click.pass_context
def plan(ctx) -> None:
    ctx.obj.plan()

@main.command("apply", help="Apply tf14 data to server.")
@click.pass_context
def apply(ctx) -> None:
    ctx.obj.apply()

@main.command("clean", help="Clean unnecessary tf14 files.")
@click.pass_context
def clean(ctx) -> None:
    ctx.obj.clean()

@main.command("edit", help="Edit the provided helper files.")
@click.option("-i", "--init", is_flag=True, multiple=False, help="Test and fmt .tf code.")
@click.option("-p", "--plan", is_flag=True, multiple=False, help="Make plans to local repo.")
@click.option("-a", "--apply", is_flag=True, multiple=False, help="apply tf14 data to server.")
@click.option("-c", "--clean", is_flag=True, multiple=False, help="Clean unnecessary tf14 files.")
@click.pass_context
def edit_cli(ctx, init, plan, apply, clean) -> None:

    if init:
        ctx.obj.edit(script_file=PATH_UTILS.SCRIPT_INIT.value)
    
    elif plan:
        ctx.obj.edit(script_file=PATH_UTILS.SCRIPT_PLAN.value)
    
    elif apply:
        ctx.obj.edit(script_file=PATH_UTILS.SCRIPT_APPLY.value)
    
    elif clean:
        ctx.obj.edit(script_file=PATH_UTILS.SCRIPT_CLEAN.value)
    

if __name__ == '__main__':
    main()
