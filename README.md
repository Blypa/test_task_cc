# This repository contains code for parsing legal definitions from FindLaw Legal Dictionary and Merriam-Webster's Dictionary website.

Code is developed using Python 3.11, for use install required libraries from requirements.txt. To change parsed urls use either [findlaw.json](./findlaw.json) or [mw.json](./mw.json)

Please note that you need to install packages listed in requirements.txt.

Moreover you need to install Firefox in you system to parse data from FindLaw Legal Dictionary.

```bash
Usage: main.py [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  parse-findlaw-pages  Parse pages from FindLaw Legal Dictionary website
  parse-mw-pages       Parse pages from Merriam-Webster`s Dictionary website
```