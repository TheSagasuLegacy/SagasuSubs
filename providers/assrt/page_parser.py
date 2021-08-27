import os
from cgi import parse_header
from pathlib import Path
from typing import Any, Dict
from urllib.parse import unquote

from httpx import URL, Client
from lxml import etree


class AssrtDetailPage:
    def __init__(self, headers: Dict[str, Any] = None):
        self.client = Client(
            http2=True, headers=headers, base_url="https://assrt.net/xml/sub/"
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
        description_text = ""
        for description in element_tree.cssselect("#detail-tbl-main div div span"):
            if description.text:
                description_text += description.text.replace("\n", "") + "\t"
        download_btn, *_ = element_tree.cssselect("#btn_download")
        download_path = download_btn.get("href")
        download_link = self.client.base_url.copy_with(path=download_path)
        return description_text, download_link

    def download(self, link: URL, path: Path):
        size = 0
        with self.client.stream("GET", link, timeout=None) as stream:
            stream.raise_for_status()
            _, disposition = parse_header(stream.headers["content-disposition"])
            filename = unquote(
                disposition.get("filename") or os.path.basename(link.path)
            )
            with (file := path / filename).open("wb") as f:
                for content in stream.iter_bytes():
                    size += f.write(content)
        return size, file

    def get_page(self, url: URL):
        response = self.client.get(url)
        response.raise_for_status()
        return response.content.decode("utf-8", errors="ignore")


if __name__ == "__main__":
    instance = AssrtDetailPage()
    page = instance.get_page(URL("https://assrt.net/xml/sub/643/643553.xml"))
    description, link = instance.parse_page(page)
    instance.download(link, Path("."))
