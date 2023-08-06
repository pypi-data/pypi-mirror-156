"""
loz main module.
"""
from click_aliases import ClickAliasedGroup
from getpass import getpass
from loz import loz
from loz import tools
from loz.exceptions import *
from loz.tools import color
from os import path
import click
import csv
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
    except LozFileDoesNotExist as e:
        logger.debug(e)
        if warn:
            print(f"First time use. Run init command.")
        sys.exit(1)
    except LozIncompatibleFileVersion as e:
        logger.debug(e)
        if warn:
            print(f"Update loz. {e}")
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
@click.argument("domain")
@click.argument("username")
def add(domain, username):
    "Set secret for 'domain username' pair."
    storage = load(loz_file)
    password = enter_password(storage)
    secret = tools.multiline_input(
        f"{color.BOLD}Write multiline secret. Enter on empty line to save:{color.END}"
    )
    change = loz.store(storage, domain, username, secret, password)
    loz.save(storage, loz_file)
    if change:
        print(f"{color.YELLOW}{color.BOLD}{str(change)}{color.END}")


@cli.command()
@click.argument("domain")
@click.argument("username")
@click.argument("length", required=False, default=16)
def make(domain, username, length):
    "Make random secret for 'domain username' pair."
    storage = load(loz_file)
    password = enter_password(storage)
    secret = tools.make_password(length)
    change = loz.store(storage, domain, username, secret, password)
    loz.save(storage, loz_file)
    if change:
        print(f"{color.YELLOW}{color.BOLD}{str(change)}{color.END}")
    print(secret)


@cli.command()
@click.argument("domain")
@click.argument("username")
def get(domain, username):
    "Get secret for 'domain username' pair."
    storage = load(loz_file)
    if not loz.exists(storage, domain, username):
        print(f"user not found: {color.BOLD}{domain}/{username}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    secret = loz.get(storage, domain, username, password)
    print(secret)


@cli.command(aliases=["del"])
@click.argument("domain")
@click.argument("username", required=False, default=None)
def rm(domain, username):
    "Delete username from domain or whole domain."
    storage = load(loz_file)
    change = loz.rm(storage, domain, username)
    loz.save(storage, loz_file)
    if change:
        print(f"{color.RED}{color.BOLD}{str(change)}{color.END}")


@cli.command()
@click.argument("domain")
def show(domain):
    "List all secrets in one domain."
    storage = load(loz_file)
    if not loz.exists(storage, domain):
        print(f"{color.RED}domain not found: {color.BOLD}{domain}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    results = loz.show(storage, domain, password)
    for domain, username, secret in results:
        print(f"\n{color.BOLD}{domain}/{username}{color.END}\n{secret}")


@cli.command()
@click.argument("domain", required=False, default=None)
def ls(domain):
    "List all storage or usernames under one domain."
    storage = load(loz_file)
    results = loz.ls(storage, domain)
    print("\n".join(results))


@cli.command(aliases=["search"])
@click.argument("word")
def find(word):
    "List storage and usernames that contain the search phrase."
    storage = load(loz_file)
    results = loz.find(storage, word)
    for res in results:
        bold = f"{color.BOLD}{res[-1]}{color.END}"
        res[-1] = bold
        print("/".join(res))


@cli.command("import")
@click.argument("csv_file", type=click.File("r"))
def import_csv(csv_file):
    "Import CSV file and merge with existing lozfile."
    storage = load(loz_file)
    password = enter_password(storage)
    rows = csv.reader(csv_file, delimiter=" ", quotechar="|")
    something_changed = False
    for row in rows:
        domain = row[0]
        username = row[1]
        secret = row[2]
        change = loz.store(storage, domain, username, secret, password)
        if change:
            something_changed = True
            print(f"{color.YELLOW}{color.BOLD}{str(change)}{color.END}")
    if something_changed:
        loz.save(storage, loz_file)


@cli.command("export")
@click.argument("csv_file", type=click.File("w"), required=False, default=sys.stdout)
def export_csv(csv_file):
    "Export plaintext storage and print to output or save to CSV file."
    storage = load(loz_file)
    password = enter_password(storage)
    writer = csv.writer(
        csv_file, delimiter=" ", quotechar="|", quoting=csv.QUOTE_MINIMAL
    )
    for row in loz.get_all(storage, password):
        writer.writerow(row)


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
