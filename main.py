from lxml.html import fromstring
from pickle import dump, load
from requests import get


TG_HOST = 'https://api.telegram.org'
TG_TOKEN = 'place a real token here'
TG_GROUP = '-1001879088495'

STANDUP_URL = 'http://aristandupclub.tilda.ws/'
EVENTS_XPATH = (
    '//*[starts-with(@id,"rec")]'
    '/div[starts-with(@class,"t")]'
    '/div[starts-with(@class,"t")]'
    '/div[starts-with(@class,"t")]'
    '[count(div)=3]'
)


def get_text_list(branch):
    if not branch.itertext:
        return
    result = [
        _ for _ in branch.itertext()
        if not _.isspace()
    ]
    return result


def get_link_list(branch):
    if not branch.iterlinks:
        return
    result = [
        _[2] for _ in branch.iterlinks()
        if "http" in _[2]
    ]
    return result


def save_events(events_list):
    '''Saves events list into binary file'''
    with open('events.bin', 'wb') as file:
        dump(events_list, file)


def send_to_telegram(text: str):
    url = f"{TG_HOST}/bot{TG_TOKEN}/sendMessage?chat_id={TG_GROUP}&text={text}"
    print(url)
    _ = get(url)
    print(_)


print("begin")
response = get(STANDUP_URL)

if not response.status_code == 200:
    print("code is not 200")
    print(response)
    raise

tree = fromstring(response.text)
events = tree.xpath(EVENTS_XPATH)

if not len(events):
    print("no events to scrap - structure changed?")
    raise

print("events parsed:", len(events))
parsed_events = []

for event in events:
    combined_list = get_text_list(event) + get_link_list(event)
    message = " - ".join(combined_list)
    parsed_events.append(message)

try:
    with open('events.bin', 'rb') as file:
        stored_events = load(file)
    new_events = [_ for _ in parsed_events if _ not in stored_events]
    print("new events filtered")
except FileNotFoundError:
    save_events(parsed_events)
    stored_events = []
    new_events = parsed_events.copy()
    print("file not found, new events = copy of parsed")

if new_events:
    print("there are new events:", len(new_events))
    for new_event in new_events:
        send_to_telegram(new_event)
    total_events = stored_events + new_events
    # TODO: limit total events to 100 or so.
    save_events(total_events)

print("all done")
