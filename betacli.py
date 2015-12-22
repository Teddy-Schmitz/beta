import click
import os
from beta import Beta
@click.group()
def cli():
    pass

@cli.command()
@click.argument('project_dir', default=os.getcwd())
@click.option('--single', is_flag=True, default=False)
def push(project_dir, single):
    beta = Beta()
    if single:
        beta.push_single(project_dir)
    else:
        beta.push_all(project_dir)

if __name__ == '__main__':
    cli()