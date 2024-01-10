import re

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC


def get_data(url):

    options = webdriver.FirefoxOptions()
    options.add_argument('--headless')

    browser = webdriver.Firefox(
        service=FirefoxService(GeckoDriverManager().install()),
        options=options
    )

    browser.get(url)
    request_text = browser.page_source
    browser.quit()

    html = BeautifulSoup(request_text, "html.parser")

    return html

def parse_description(text) -> dict:
    result = {}

    # Check for notes
    note_pattern = r'NOTE:\s(?P<note>.*?)\s(</i>.*?)'
    note = re.findall(
        note_pattern,
        text
    )

    if len(note) == 1:
        result['note'] = note[0][0]

    elif len(note) > 1:
        result['note'] = []
        for title, __ in note:
            result['note'].append(title)

    text = re.sub(
        note_pattern,
        '',
        text
    )

    # check for compare
    compare_pattern = r'compare\s*<a\s+href=\"(?P<link>.+?)\">(?P<text>.*?)<\/a>'
    compare = re.findall(
        compare_pattern,
        text
    )
    
    if len(compare) == 1:
        result['compare link'] = compare[0][0]
        result['compare'] = compare[0][1]

    elif len(compare) > 1:
        result['compare'] = []
        result['compare link'] = []
        for link, title in compare:
            result['compare'].append(title)
            result['compare link'].append(link)

    text = re.sub(
        compare_pattern,
        '',
        text
    )

    # check for see also
    see_also_pattern = r'see also\s*<a\s+href=\"(?P<link>.+?)\">(?P<text>.*?)<\/a>'
    see_also = re.findall(
        see_also_pattern,
        text
    )

    if len(see_also) == 1:
        result['see_also link'] = see_also[0][0]
        result['see_also'] = see_also[0][1]

    elif len(see_also) > 1:
        result['see_also'] = []
        result['see_also link'] = []
        for link, title in see_also:
            result['see_also'].append(title)
            result['see_also link'].append(link)

    text = re.sub(
        see_also_pattern,
        '',
        text
    )

    result['description'] = text

    return result

def parse(html) -> dict:
    json_info = {}
    json_info['title'] = html.find("h1").text.strip()

    information = html.find("dd").text.strip()

    # json_info['description'] = re.search(
    #     r":\s(.*?)(\s\s)",
    #     information
    # )[1]

    origin = re.search(
        r"\[.*\]",
        information
    )
    json_info['origin'] = None if not origin else origin[0]

    groups = re.findall(
        r'<b>(?P<title>.*?)<\/b>(.+?)(?=<br\/> *<br\/>|$)',
        str(html.find("dd")).replace('\n', '')
    )

    json_info['definitions'] = []

    if len(groups) > 1:
        for title, text in groups:
            if title.strip() == ':':
                json_info.update(parse_description(text))
                continue
            sub_groups = re.findall(
                r'<b>(?P<title>.*?)<\/b>(.+?)(?=<br\/>|$)',
                text
            )
            definition = {
                'title': title
            }
            if sub_groups[0][0].strip() == ':':
                definition.update(parse_description(sub_groups[0][1]))

            definition['definitions'] = []

            for sub_title, sub_text in sub_groups[1:]:
                sub_definition = {
                    'title': sub_title
                }
                sub_definition.update(parse_description(sub_text))
                definition['definitions'].append(sub_definition)

            json_info['definitions'].append(definition)

    elif len(groups) == 1:
        sub_groups = re.findall(
            r'<b>(?P<title>.*?)<\/b>(.+?)(?=<br\/>|$)',
            str(html.find("dd")).replace('\n', '')
        )
        for sub_title, sub_text in sub_groups:
            sub_definition = {
                'title': sub_title
            }
            sub_definition.update(parse_description(sub_text))
            json_info['definitions'].append(sub_definition)

    return json_info
