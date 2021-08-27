from typing import Any, Dict

from httpx import Client
from lxml import etree


def inner_text(node) -> str:
    return node.text + "".join(etree.tostring(e).decode() for e in node)


class AssrtSearchPage:
    def __init__(self, keyword: str, page: int = 1, headers: Dict[str, Any] = None):
        self.keyword, self.page = keyword, page
        self.client = Client(
            http2=True, base_url="https://assrt.net/sub/", headers=headers
        )

    def parse_page(self, content: str):
        element_tree = etree.fromstring(
            content,
            parser=etree.HTMLParser(
                encoding="utf-8",
                remove_blank_text=True,
                remove_comments=True,
                recover=True,
            ),
        )
        for title in element_tree.cssselect(".sublist_box_title_l a"):
            title_text: str = title.get("title")
            title_link: str = title.get("href")
            yield title_text, self.client.base_url.copy_with(path=title_link)
        for paginator in element_tree.cssselect(".pagelinkcard a"):
            current, _, total = inner_text(paginator).partition("/")
            if total.isdigit():
                return current, total
            continue
        return

    def spider(self):
        for page in range(1, int(self.page) + 1):
            response = self.client.get(
                url="", params={"searchword": self.keyword, "page": page}
            )
            response.raise_for_status()
            yield response.text


if __name__ == "__main__":
    for text in (instance := AssrtSearchPage("某科学的超电磁炮", 20)).spider():
        iterator = instance.parse_page(text)
        for title, link in iterator:
            print(f"{title}: {link}")
