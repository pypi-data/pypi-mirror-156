#!/usr/bin/env python3

import click
import random

from tabulate import tabulate


def board(seed=None):
    dice = [
        ['C', 'A', 'P', 'S', 'H', 'O'],
        ['W', 'O', 'O', 'T', 'A', 'T'],
        ['S', 'I', 'U', 'N', 'E', 'E'],
        ['I', 'D', 'E', 'X', 'L', 'R'],
        ['L', 'R', 'D', 'Y', 'V', 'E'],
        ['Y', 'T', 'E', 'T', 'R', 'L'],
        ['V', 'T', 'W', 'E', 'R', 'H'],
        ['T', 'I', 'Y', 'S', 'D', 'T'],
        ['M', 'I', 'C', 'O', 'U', 'T'],
        ['U', 'Qu', 'I', 'M', 'N', 'H'],
        ['G', 'H', 'N', 'E', 'E', 'W'],
        ['H', 'Z', 'N', 'N', 'R', 'L'],
        ['J', 'O', 'B', 'B', 'A', 'O'],
        ['G', 'A', 'N', 'E', 'A', 'E'],
        ['S', 'E', 'S', 'O', 'T', 'I'],
        ['K', 'F', 'A', 'P', 'S', 'F']
    ]
    random.seed(seed) if seed is not None else random.seed()
    chosen = [random.choice(die) for die in dice]
    random.shuffle(chosen)
    return chosen


@click.command()
@click.option("--seed", "-s", help="A key to create a board from", default=None)
def board_cli(seed):
    chosen = board(seed)
    table = [chosen[:4], chosen[4:8], chosen[8:12], chosen[12:]]
    click.echo(tabulate(table, tablefmt="fancy_grid"))


if __name__ == "__main__":
    board_cli()
