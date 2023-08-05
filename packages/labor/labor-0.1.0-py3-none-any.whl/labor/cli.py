import click
from rich import print
from datetime import datetime

import api
import config
from sensitive_data import email, password
from beautify import printTasks, print_reports

@click.group()
def cli():
    ...


@cli.command(help="Login to Labor")
def sign_in():
    email = click.prompt('Enter your email', type=str)
    password = click.prompt('Enter your password', type=str, hide_input=True)
    data, status, headers = api.sign_in(email, password)

    saved_headers = {
        'access-token': headers['access-token'],
        'client': headers['client'],
        'expiry': headers['expiry'],
        'uid': headers['uid'],
        'token-type': headers['token-type']
    }

    config_json = {
        'saved_headers': saved_headers,
        'data': data,
    }

    if status == 200: 
        config.write(config_json)
        print("User logged in successfully")
    else: print("Error logging in")

@cli.command(help="Logout from Labor")
def sign_out():
    logged_user = config.load()
    headers = logged_user['saved_headers']
    status = api.sign_out(headers)
    if status == 200:
        config.write({})
    else: 
        print('Error while signing out')


@cli.command(help="Default is current month, use month and year in numbers")
@click.argument("month", required=False)
@click.argument("year", required=False)
def tasks(month, year):
    try:
        if not year:
            year = datetime.now().year
        if not month: 
            month = datetime.now().month
        logged_user = config.load()
        data, status, projects = api.tasks(logged_user, month, year)
        if status == 200: 
            print(printTasks(dict.items(data), projects))
        else: 
            print(f"Error while retrieving data: {status}")
    except: 
        print("You need to login first")

@cli.command(help="Get reports")
@click.argument("year", required=False)
def reports(year):
    try: 
        if not year:
            year = datetime.now().year
        logged_user = config.load()
        data, status = api.reports(logged_user, year)
        if status == 200:
            print(print_reports(data))
    except:
        print("You need to login first")

if __name__ == "__main__":
    cli()
