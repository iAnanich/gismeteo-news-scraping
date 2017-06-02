import sys
import requests as r


def extract_id_from_relative_url(relative_url: str) -> int:
    return int(relative_url.split('/')[3].split('-')[0])


def clear_description(description: str) -> str:
    return description.replace('\xa0', ' ')


def fetch_latest_id() -> int:
    content = str(r.get('https://app.scrapinghub.com/api/items.csv?project={project}&spider={spider}&include_headers=1&fields={fields}&apikey={key}'.format(
        project='200327',
        spider='news-list',
        fields='id',
        key=get_api_key(),
    )).content)  # looks like 'b\'"id"\\n\''
    if content == """b'{"status": "error", "message": "Authentication failed"}'""":
        raise RuntimeError('Wrong API_KEY provided.')
    ids = content.split('"\\n"')[1:]
    if len(ids) == 0:
        return 0
    else:
        return int(ids[0])


def get_api_key() -> str:
    for arg in sys.argv:
        if 'API_KEY=' in arg:
            return arg[arg.find('=')+1:]
    else:
        raise RuntimeError('No "API_KEY" argument found.')


def parse_news(selector, host) -> dict:
    path = selector.xpath('div[@class="item__title"]/a/@href').extract_first()
    id = extract_id_from_relative_url(path)
    header = selector.xpath('div[@class="item__title"]/a/text()').extract_first()
    description_unclear = selector.xpath('div[@class="item__descr"]/text()').extract_first()
    tag = selector.xpath('p[@class="item__date links-black"]/a/text()').extract_first()
    description = clear_description(description_unclear)
    url = 'https://{host}{path}'.format(host=host, path=path)
    return dict(
        url=url,
        id=id,
        header=header,
        description=description,
        tag=tag,
    )
