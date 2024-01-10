import requests
from bs4 import BeautifulSoup
import re


def get_data(url):
    request_text = requests.get(url)

    soup = BeautifulSoup(request_text.text, "html.parser")

    main_body = soup.find("div", {"id":"legalDictionary"})
    
    return main_body, soup


def parse_word(main_body, soup) -> dict:
    json_info = {}

    json_info["title"] = main_body.find("p", {"class":"hword"}).text
    json_info['spelling'] = main_body.find("span", {"class": "word-syllables-entry"}).text.replace("\u200b", "")
    json_info['description'] = soup.find("meta", {"name": "description"})['content']
    json_info['definitions'] = []

    definition_items = main_body.find("div", {"class":"vg"}).find_all("div", {"class":"vg-sseq-entry-item"})

    for item in definition_items:

        list_entry = item.find_all("div", {'class': "sb-entry"})

        main_label_entry = item.find("div", {"class": "vg-sseq-entry-item-label"}).text

        definition = {}
        definition['title'] = main_label_entry
        definition['definitions'] = []
        definition['description'] = None

        for entry in list_entry:
            if not entry.find("span", {"class": "letter"}):
                definition['description'] = entry.find("span", {"class": "dtText"}).contents[1]
            else:
                sub_term = entry.find("span", {"class": "letter"}).text

                sub_term_definition = {
                    'title': sub_term,
                    'description': entry.find("span", {"class": "dtText"}).contents[1]
                }

                additional_item = entry.find("span", {"class":"dx-jump"})
                if additional_item:
                    title = additional_item.contents[2].strip()
                    sub_term_definition[title] = additional_item.text.replace(additional_item.contents[2], '').strip()
                    if additional_item.find('a', {"class": "mw_t_dxt"}):
                        sub_term_definition[f'{title} link'] = additional_item.find('a', {"class": "mw_t_dxt"}).get('href', None)

                note = entry.find("span", {"class":"note-txt text-uppercase"})
                if note:
                    sub_term_definition['note'] = entry.find("p", {"class":"snote"}).text

                definition['definitions'].append(sub_term_definition)

        json_info['definitions'].append(definition)

    return json_info


def parse_similar_words(main_body, soup) -> dict:
    json_info = {}

    json_info["title"] = main_body.find("p", {"class":"hword"}).text

    main_entry = main_body.find("div", {'class': "sb-entry"})

    json_info['description'] = main_entry.find("span", {"class": "dtText"}).contents[1]

    additional_item = main_entry.find("span", {"class":"dx-jump"})
    if additional_item:
        title = additional_item.contents[2].strip()
        json_info[title] = additional_item.text.replace(additional_item.contents[2], '').strip()
        if additional_item.find('a', {"class": "mw_t_dxt"}):
            json_info[f'{title} link'] = additional_item.find('a', {"class": "mw_t_dxt"}).get('href', None)

    json_info["definitions"] = []

    subs_div = main_entry.find("div", {"class": "subs"})
    if not subs_div:
        return json_info
    subs_list = subs_div.find_all("div", {"class":"sub"})

    for sub in subs_list:

        sub_title = sub.find("span", {"class": "shw"})

        if sub_title:

            sub_title = sub_title.text

            definition = {}

            definition['title'] = sub_title

            entry_list = sub.find_all("div", {"class":"sense"})
            definition['definitions'] = []

            for entry in entry_list:

                if not entry.find("span", {"class": "letter"}):
                    sub_definition = {
                        'title': sub_title,
                        'description': entry.find("span", {"class": "dtText"}).contents[1]
                    }
                    definition['definitions'].append(sub_definition)

                else:
                    sub_term = entry.find("span", {"class": "letter"}).text
                    sub_term_definition = {
                        'title': sub_term,
                        'description': entry.find("span", {"class": "dtText"}).contents[1]
                    }

                    additional_item = entry.find("span", {"class":"dx-jump"})
                    if additional_item:
                        title = additional_item.contents[2].strip()
                        sub_term_definition[title] = additional_item.text.replace(additional_item.contents[2], '').strip()
                        if additional_item.find('a', {"class": "mw_t_dxt"}):
                            sub_term_definition[f'{title} link'] = additional_item.find('a', {"class": "mw_t_dxt"}).get('href', None)

                    note = entry.find("span", {"class":"note-txt text-uppercase"})
                    if note:
                        sub_term_definition['note'] = entry.find("p", {"class":"snote"}).text

                    definition['definitions'].append(sub_term_definition)

            json_info["definitions"].append(definition)

    return json_info
