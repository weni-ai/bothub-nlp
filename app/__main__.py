import click

from app.models.utils import create_schema
from app.server import start_server


@click.command()
@click.option('--service', type=click.Choice(['start_server', 'create_schema']))
@click.argument('arg', required=False)
def start_service(service, arg):
    if service == 'start_server':
        start_server(arg)
    elif service == 'create_schema':
        create_schema()


if __name__ == '__main__':
    start_service()
