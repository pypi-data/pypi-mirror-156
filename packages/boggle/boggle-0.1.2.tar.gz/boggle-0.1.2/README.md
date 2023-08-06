# Boggle

This project generates boards for the game boggle.

[![codecov](https://codecov.io/gl/bmaximuml-os/boggle/branch/master/graph/badge.svg?token=NXDZKTANX1)](https://codecov.io/gl/bmaximuml-os/boggle)
[![Pipeline Status](https://gitlab.com/bmaximuml-os/boggle/badges/master/pipeline.svg)](https://gitlab.com/bmaximuml-os/boggle)

## Installation

This package can be installed using pip.

`pip install boggle`

## Usage

### CLI

This package exposes the `boggle` command in a shell.

```bash
$ boggle --help
Usage: boggle [OPTIONS]

Options:
  -s, --seed TEXT  A key to create a board from
  --help           Show this message and exit.
```

If a seed valaue is not provided, a random board will be returned:

```bash
$ boggle
╒═══╤═══╤═══╤═══╕
│ R │ S │ P │ L │
├───┼───┼───┼───┤
│ N │ H │ I │ L │
├───┼───┼───┼───┤
│ N │ T │ A │ W │
├───┼───┼───┼───┤
│ B │ U │ U │ T │
╘═══╧═══╧═══╧═══╛
$ boggle
╒═══╤═══╤═══╤═══╕
│ R │ F │ M │ B │
├───┼───┼───┼───┤
│ A │ N │ N │ R │
├───┼───┼───┼───┤
│ T │ E │ R │ S │
├───┼───┼───┼───┤
│ S │ D │ T │ T │
╘═══╧═══╧═══╧═══╛
```

If a seed value is provided, a board will be generated deterministically from the seed value:

```bash
$ boggle -s 'fish'
╒═══╤═══╤═══╤═══╕
│ T │ F │ R │ O │
├───┼───┼───┼───┤
│ E │ C │ E │ W │
├───┼───┼───┼───┤
│ H │ E │ J │ Y │
├───┼───┼───┼───┤
│ T │ N │ V │ W │
╘═══╧═══╧═══╧═══╛
$ boggle -s 'fish'
╒═══╤═══╤═══╤═══╕
│ T │ F │ R │ O │
├───┼───┼───┼───┤
│ E │ C │ E │ W │
├───┼───┼───┼───┤
│ H │ E │ J │ Y │
├───┼───┼───┼───┤
│ T │ N │ V │ W │
╘═══╧═══╧═══╧═══╛
$ boggle -s 'hamster'
╒═══╤═══╤═══╤═══╕
│ E │ O │ B │ T │
├───┼───┼───┼───┤
│ V │ T │ E │ H │
├───┼───┼───┼───┤
│ G │ E │ E │ H │
├───┼───┼───┼───┤
│ W │ U │ P │ F │
╘═══╧═══╧═══╧═══╛
$ boggle -s 'hamster'
╒═══╤═══╤═══╤═══╕
│ E │ O │ B │ T │
├───┼───┼───┼───┤
│ V │ T │ E │ H │
├───┼───┼───┼───┤
│ G │ E │ E │ H │
├───┼───┼───┼───┤
│ W │ U │ P │ F │
╘═══╧═══╧═══╧═══╛
```

### Python Package

Import the `boggle()` method from the `boggle` package:

`from boggle import boggle`

This method will return a list of 16 boggle characters (including *Qu*). These are intended to be arranged into a
square of four characters by four characters.

If a seed value is not provided, a random board will be returned:

```python
>>> from boggle import boggle
>>> boggle()
['B', 'A', 'S', 'T', 'H', 'U', 'M', 'H', 'R', 'P', 'E', 'R', 'O', 'T', 'O', 'N']
>>> boggle()
['A', 'E', 'T', 'L', 'E', 'E', 'W', 'D', 'E', 'D', 'J', 'T', 'Y', 'I', 'O', 'F']
>>> boggle()
['E', 'S', 'Y', 'F', 'V', 'X', 'N', 'Y', 'H', 'O', 'E', 'U', 'T', 'T', 'N', 'O']
```

If a seed value is provided, a board will be generated deterministically from the seed value:

```python
>>> from boggle import boggle
>>> boggle('fish')
['T', 'F', 'R', 'O', 'E', 'C', 'E', 'W', 'H', 'E', 'J', 'Y', 'T', 'N', 'V', 'W']
>>> boggle('fish')
['T', 'F', 'R', 'O', 'E', 'C', 'E', 'W', 'H', 'E', 'J', 'Y', 'T', 'N', 'V', 'W']
>>> boggle('hamster')
['E', 'O', 'B', 'T', 'V', 'T', 'E', 'H', 'G', 'E', 'E', 'H', 'W', 'U', 'P', 'F']
>>> boggle('hamster')
['E', 'O', 'B', 'T', 'V', 'T', 'E', 'H', 'G', 'E', 'E', 'H', 'W', 'U', 'P', 'F']
```

&copy; Max Levine 2022
