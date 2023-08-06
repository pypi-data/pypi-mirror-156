"""
loz main module.
"""
from click_aliases import ClickAliasedGroup
from getpass import getpass
from loz import loz
from loz.exceptions import *
from os import path
from prompt_toolkit import prompt
import click
import csv
import logging
import loz as app
import sys

logging.basicConfig()
logger = logging.getLogger("loz")
logger.setLevel(logging.WARNING)

loz_file = path.expanduser("~/.loz")
check_mode = False
yes_mode = False


class color:
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


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


def confirm_change(change):
    if check_mode or yes_mode:
        return True
    if not "-" in change[0]:
        # non-destructive change
        return True
    answer = input("Is this ok [Y/n]: ")
    if answer.lower() in ["", "y", "yes"]:
        print("Confirmed!")
        return True
    print("Abandoning changes.")
    return False


def print_change(change):
    col = color.GREEN
    if "+" in change[0]:
        col = color.YELLOW
    if "-" in change[0]:
        col = color.RED
    print(
        f"{col}{change[0]} {color.BOLD}{change[1]}/{change[2]}{color.END} {col}{change[3]}{color.END}"
    )


def save(storage, change):
    print_change(change)
    if not check_mode:
        if confirm_change(change):
            loz.save(storage, loz_file)
        return
    print("Check mode is on, so nothing is really changed.")


def enter_password(storage):
    while True:
        password = getpass("enter password:")
        if loz.validate_key(storage, password):
            return password


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
    "-c",
    "--check",
    is_flag=True,
    help="Enable check mode that shows changes but changes nothing.",
)
@click.option(
    "-y",
    "--yes",
    is_flag=True,
    help="Answer yes to all questions.",
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
    global check_mode
    global yes_mode
    if ctx.params.get("debug"):
        logger.setLevel(logging.DEBUG)
        logger.info("debug mode is on")
    check_mode = ctx.params.get("check")
    yes_mode = ctx.params.get("yes")
    loz_file = ctx.params.get("file")


@cli.command()
def init():
    "Initialize .loz file with master password."
    change = ["", "", "", "Initialize lozfile with password."]
    if path.isfile(loz_file):
        change = ["+-", "", "", "Overwrite lozfile and reinitialize."]
    password = None
    while password == None:
        password = getpass("enter password:")
        if password != getpass("repeat:"):
            print(f"passwords do not match")
            password = None
    storage = loz.init(password)
    save(storage, change)


@cli.command(aliases=["set"])
@click.argument("domain")
@click.argument("user")
def add(domain, user):
    "Set secret for 'domain user' pair."
    storage = load(loz_file)
    secret = prompt(
        "Write multiline secret. Alt+Return to save:\n", default="", multiline=True
    )
    change = loz.store(storage, domain, user, secret)
    save(storage, change)


@cli.command()
@click.argument("domain")
@click.argument("user")
def make(domain, user):
    "Make random secret for 'domain user' pair."
    storage = load(loz_file)
    change = loz.store(storage, domain, user)
    save(storage, change)


@cli.command()
@click.argument("domain")
@click.argument("user")
def get(domain, user):
    "Get secret for 'domain user' pair."
    storage = load(loz_file)
    if not loz.exists(storage, domain, user):
        print(f"user not found: {color.BOLD}{domain}/{user}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    secret = loz.get(storage, domain, user)
    print(secret)


@cli.command(aliases=["del"])
@click.argument("domain")
@click.argument("user", required=False, default=None)
def rm(domain, user):
    "Delete user from domain or whole domain."
    storage = load(loz_file)
    change = loz.rm(storage, domain, user)
    save(storage, change)


@cli.command()
@click.argument("domain")
def show(domain):
    "List all secrets in one domain."
    storage = load(loz_file)
    if not loz.exists(storage, domain):
        print(f"domain not found: {color.BOLD}{domain}{color.END}")
        sys.exit(1)
    password = enter_password(storage)
    for domain, user, secret in loz.show(storage, domain, password):
        print(f"\n{color.BOLD}{domain}/{user}{color.END}\n{secret}")


@cli.command()
@click.argument("domain", required=False, default=None)
def ls(domain):
    "List all storage or users under one domain."
    storage = load(loz_file)
    results = loz.ls(storage, domain)
    print("\n".join(results))


@cli.command(aliases=["search"])
@click.argument("word")
def find(word):
    "List storage and users that contain the search phrase."
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
    total_change = ["", "", "", "total change"]
    for change in loz.import_csv(storage, csv_file):
        print_change(change)
        total_change[0] += change[0]
    if not total_change[0]:
        print("\bNo changes detected.")
        return
    save(storage, total_change)


@cli.command("export")
@click.argument("csv_file", type=click.File("w"), required=False, default=sys.stdout)
def export_csv(csv_file):
    "Export plaintext storage and print to output or save to CSV file."
    storage = load(loz_file)
    password = enter_password(storage)
    loz.export_csv(storage, password, csv_file)


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
