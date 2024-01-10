import json
from concurrent.futures import ThreadPoolExecutor

import click
import requests

import mw_parser
import findlaw_parser


MAX_THREADS = 4


@click.group()
def cli():
    pass


def read_config(filename: str) -> dict:
    with open(filename) as file:
        conf = json.loads(file.read())

    if conf.get('url', False):
        return conf['url']
    raise ValueError('Config doesn\'t contain urls')


def parse_mw_page(word: str) -> dict:
    url = f"https://www.merriam-webster.com/dictionary/{word}#legalDictionary"
    main_body, soup = mw_parser.get_data(url)
    json_info = {}

    if main_body:
        if main_body.find("div", {"class": "vg-sseq-entry-item-label"}):
            json_info = mw_parser.parse_word(main_body, soup)

        else:
            json_info = mw_parser.parse_similar_words(main_body, soup)

    json_info['url'] = url

    return json_info


def parse_findlaw_page(url: str) -> dict:
    main_body = findlaw_parser.get_data(url=url)

    json_info = findlaw_parser.parse(main_body)

    json_info['url'] = url

    return json_info


@cli.command()
def parse_mw_pages():
    """Parse pages from Merriam-Webster's Dictionary website"""
    urls = read_config('./mw.json')

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(parse_mw_page, urls)

    results_file = './mw_results.json'

    results = list(results)

    with open(results_file, 'w') as file:
        file.write(json.dumps(results, indent=4))

    print(f'Parsed {len(results)} pages. Result saved to {results_file}')


@cli.command()
def parse_findlaw_pages():
    """Parse pages from FindLaw Legal Dictionary website"""
    urls = read_config('./findlaw.json')

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        results = executor.map(parse_findlaw_page, urls)

    results_file = './findlaw_results.json'

    results = list(results)

    with open(results_file, 'w') as file:
        file.write(json.dumps(results, indent=4))

    print(f'Parsed {len(results)} pages. Result saved to {results_file}')


if __name__ == '__main__':
    cli()
