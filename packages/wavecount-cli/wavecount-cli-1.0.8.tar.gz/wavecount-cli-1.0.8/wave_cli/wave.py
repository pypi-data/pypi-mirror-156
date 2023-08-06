# import os
# import sys

import click
import pyfiglet
import PyInquirer as inq
from examples import custom_style_1

from wave_cli import COMMAND_NAME, PACKAGE_NAME, VERSION
from wave_cli.commands.contract_commands import contract
from wave_cli.commands.delete_commands import delete
from wave_cli.commands.log_commands import log
from wave_cli.commands.new_commands import new
from wave_cli.commands.reboot_commands import reboot
from wave_cli.commands.reset_command import reset
from wave_cli.commands.show_commands import show
from wave_cli.commands.update_commands import update
from wave_cli.services.backend_services import Backend
from wave_cli.utils import read_config, save_config
from wave_cli.version_check import compare

# sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))



@click.group(name='main', help='Wavecount CLI for controlling and monitoring wavecount things!')
@click.pass_context
def main(ctx):
    compare()
    ctx.obj = read_config()
    if 'roles' not in ctx.obj:
        ctx.forward(login)
    pass


@click.command('sync', help='Synchronize cache.')
@click.option('-t', '--access-token', type=click.STRING, help='Your access token')
@click.pass_context
def sync(ctx, access_token, **kwarg):
    if not access_token:
        if 'access_token' not in ctx.obj:
            ctx.forward(login)
        else:
            access_token = ctx.obj['access_token']
    backend = Backend(context=ctx)
    result = backend.sync_cache()
    ctx.obj = {**ctx.obj, **result}
    save_config(ctx.obj)


@click.command('login', help='Authorize user.')
@click.option('-u', '--username', help='Your username', default=None)
@click.option('-p', '--password', help='Your password', default=None)
@click.pass_context
def login(ctx, username, password):
    try:
        if not username:
            username = inq.prompt(
                questions=[{'type': 'input', 'name': 'username', 'message': 'Enter username'}],
                style=custom_style_1
            )['username']
        if not password:
            password = inq.prompt(
                questions=[{'type': 'password', 'name': 'password', 'message': 'Enter password'}],
                style=custom_style_1
            )['password']
        backend = Backend(context=ctx)
        response = backend.login({'user': username, 'password': password})
        ctx.obj['name'] = response['name']
        ctx.obj['roles'] = response['roles']
        ctx.obj['access_token'] = response['accessToken']
        ctx.forward(sync)
        text_logo = 'wavecount cli'
        pyfiglet.print_figlet(text=text_logo, font='big', justify='center')
        click.secho()
        click.secho(bold=True, fg='blue', message='Welcome {}!'.format(response['name'].split(' ')[0]))
        click.secho()
        click.echo('Now run:' + click.style(text=' {} --help'.format(COMMAND_NAME), fg='blue'))
        click.secho()
    except Exception as e:
        exit()


@click.command('version', help='Show {0} version.'.format(PACKAGE_NAME))
@click.pass_context
def version(ctx):
    message = 'using version: {0}'.format(VERSION)
    click.secho(message, fg='bright_black')


main.add_command(sync)
main.add_command(login)
main.add_command(show)
main.add_command(new)
main.add_command(update)
main.add_command(reboot)
main.add_command(delete)
main.add_command(reset)
main.add_command(version)
main.add_command(log)
main.add_command(contract)

if __name__ == '__main__':
    main()
