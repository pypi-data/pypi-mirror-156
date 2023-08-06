"""
loz main module.
"""
from click_aliases import ClickAliasedGroup
from getpass import getpass
from loz import loz, LozException
from loz import tools
from loz.tools import color
from os import path
import click
import logging
import loz as app
import sys

logging.basicConfig()
logger = logging.getLogger("loz")
logger.setLevel(logging.WARNING)

loz_file = path.expanduser("~/.loz")


def load(warn=True):
    storage = None
    try:
        storage = loz.load(loz_file)
    except LozException as e:
        logger.debug(e)
        if warn:
            print(f"{color.RED}First time use. Run init command.{color.END}")
        sys.exit(1)
    return storage


def enter_password(storage):
    while True:
        password = getpass("enter password:")
        if loz.is_valid_password(storage, password):
            return password
        print(f"{color.RED}bad password{color.END}")


@click.group(cls=ClickAliasedGroup)
@click.version_option(
    version=app.__version__, message=f"%(prog)s %(version)s - {app.__copyright__}"
)
@click.option(
    "-d",
    "--debug",
    is_flag=True,
    help="Enable debug mode with output of each action in the log.",
)
@click.option(
    "-f",
    "--file",
    type=str,
    default=loz_file,
    help=f"Specify custom loz file. Defaults to: {loz_file}",
)
@click.pass_context
def cli(ctx, **kwargs):
    global loz_file
    loz_file = ctx.params.get("file")
    if ctx.params.get("debug"):
        logger.setLevel(logging.DEBUG)
        logger.info("debug mode is on")


@cli.command()
def init():
    "Initialize .loz file with master password."
    if path.isfile(loz_file):
        logger.error(f"{loz_file} already exists")
        sys.exit(1)
    password = None
    while password == None:
        password = getpass("enter password:")
        if password != getpass("repeat:"):
            print(f"{color.RED}passwords do not match{color.END}")
            password = None
    storage = loz.init(password)
    loz.save(storage, loz_file)
    print(
        f"{color.YELLOW}{color.BOLD}{loz_file}{color.END} {color.YELLOW}initialized with password{color.END}"
    )


@cli.command(aliases=["set"])
@click.argument("entity")
@click.argument("username")
def add(entity, username):
    "Set secret for 'entity username' pair."
    storage = loz.load(loz_file)
    password = enter_password(storage)
    secret = tools.multiline_input(
        f"{color.BOLD}Write multiline secret. Enter on empty line to save:{color.END}"
    )
    added = loz.add(storage, entity, username, secret, password)
    loz.save(storage, loz_file)
    print(f"{color.YELLOW}added: {color.BOLD}{str(added)}{color.END}")


@cli.command()
@click.argument("entity")
@click.argument("username")
@click.argument("length", required=False, default=16)
def make(entity, username, length):
    "Make random secret for 'entity username' pair."
    storage = loz.load(loz_file)
    password = enter_password(storage)
    secret = tools.make_password(length)
    added = loz.add(storage, entity, username, secret, password)
    loz.save(storage, loz_file)
    print(f"{color.YELLOW}added: {color.BOLD}{str(added)}{color.END}")


@cli.command()
@click.argument("entity")
@click.argument("username")
def get(entity, username):
    "Get secret for 'entity username' pair."
    storage = loz.load(loz_file)
    if not loz.exists(storage, entity, username):
        print(f"{color.RED}user not found: {color.BOLD}{entity}/{username}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    secret = loz.get(storage, entity, username, password)
    print(secret)


@cli.command(aliases=["del"])
@click.argument("entity")
@click.argument("username", required=False, default=None)
def rm(entity, username):
    "Delete username from entity or whole entity."
    storage = loz.load(loz_file)
    removed = loz.rm(storage, entity, username)
    if not removed:
        print(f"{color.GREEN}nothing to do{color.END}")
        return
    loz.save(storage, loz_file)
    print(f"{color.YELLOW}removed: {color.BOLD}{str(removed)}{color.END}")


@cli.command()
@click.argument("entity")
def show(entity):
    "List all secrets in one entity."
    storage = loz.load(loz_file)
    if not loz.exists(storage, entity):
        print(f"{color.RED}entity not found: {color.BOLD}{entity}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    results = loz.show(storage, entity, password)
    for entity, username, secret in results:
        print(f"\n{color.BOLD}{entity}/{username}{color.END}\n{secret}")


@cli.command()
@click.argument("entity", required=False, default=None)
def ls(entity):
    "List all storage or usernames under one entity."
    storage = loz.load(loz_file)
    results = loz.ls(storage, entity)
    print("\n".join(results))


@cli.command(aliases=["search"])
@click.argument("word")
def find(word):
    "List storage and usernames that contain the search phrase."
    storage = loz.load(loz_file)
    results = loz.find(storage, word)
    for res in results:
        bold = f"{color.BOLD}{res[-1]}{color.END}"
        res[-1] = bold
        print("/".join(res))


@cli.command()
def bash_completion():
    "Generate bash completion file contents."
    completion = (
        f"_loz()\n"
        f"{{\n"
        f"    local cur prev\n"
        f"    COMPREPLY=()\n"
        f'    cur="${{COMP_WORDS[COMP_CWORD]}}"\n'
        f'    prev="${{COMP_WORDS[COMP_CWORD - 1]}}"\n'
        f"    words=\n"
        f"\n"
        f'    if [ "$COMP_CWORD" == "1" ]; then\n'
        f'        words="{" ".join([n for n, v in cli.commands.items()])}"\n'
        f"    fi\n"
        f"\n"
        f'    cmd="${{COMP_WORDS[1]}}"\n'
        f'    case "$cmd" in\n'
        f"        get|set|add|make|rm|del)\n"
        f'            case "$COMP_CWORD" in\n'
        f"                2)\n"
        f'                    words="$(loz ls)"\n'
        f"                    ;;\n"
        f"                3)\n"
        f'                    words="$(loz ls $prev)"\n'
        f"                    ;;\n"
        f"            esac\n"
        f"            ;;\n"
        f"        show|ls)\n"
        f'            if [ "$COMP_CWORD" == "2" ]; then\n'
        f'                words="$(loz ls)"\n'
        f"            fi\n"
        f"            ;;\n"
        f"    esac\n"
        f'    COMPREPLY=( $(compgen -W "${{words}}" -- ${{cur}}) )\n'
        f"}}\n"
        f"complete -F _loz loz\n"
    )
    print(completion)


if __name__ == "__main__":
    cli()
