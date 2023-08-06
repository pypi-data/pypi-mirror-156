import typer
import random

from .alphabets import alphanumeric as an
from .alphabets import anyprintable as ap
from .alphabets import emoji as em

app = typer.Typer()


def print_alphabet(alphabet, length):
    typer.echo("".join(random.choice(alphabet) for _ in range(length)))


@app.command()
def alphanumeric(
    length: int = 16,
    case: an.Case = typer.Option(an.Case.MIXED, case_sensitive=False),
    punctuation: bool = False,
) -> None:
    print_alphabet(an.get_alphabet(case, punctuation), length)


@app.command()
def anyprintable(length: int = 16):
    print_alphabet(ap.get_alphabet(), length)


@app.command()
def emoji(
    length: int = 16,
    category: em.EmojiCategory = typer.Option(em.EmojiCategory.ANY, case_sensitive=False),
):
    print_alphabet(em.get_alphabet(category), length)
