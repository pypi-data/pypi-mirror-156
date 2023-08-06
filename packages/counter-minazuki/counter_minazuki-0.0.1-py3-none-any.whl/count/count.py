from collections import Counter
from functools import lru_cache

import click


@lru_cache()
def count(string):
    word = Counter(string)
    last_list = 0
    for value in word.values():
        if value == 1:
            last_list += 1
    return last_list


def counter(string):
    if not isinstance(string, str):
        raise TypeError("Must be sting")
    return count(string)


def counter_file(path):
    try:
        with open(path, 'r', encoding='utf-8') as file:
            return counter(file.read())
    except Exception as e:
        print(str(e))


@click.command()
@click.option('--string', type=str, help="Returns the number of unique single characters in string")
@click.option('--file', help="Returns the number of unique single characters in file")
def cli(string, file):
    if file:
        return click.echo(counter_file(file))
    elif string:
        click.echo(counter(string))


if __name__ == '__main__':
    cli()