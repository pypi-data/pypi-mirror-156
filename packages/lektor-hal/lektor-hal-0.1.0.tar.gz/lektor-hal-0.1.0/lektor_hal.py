from dataclasses import dataclass
from typing import Dict, List

import requests
from lektor.pluginsystem import Plugin


@dataclass
class Publication:
    raw: Dict[str, str]
    title: str
    hal_id: str
    authors: List[str]
    date: str

    @staticmethod
    def from_entry(publi_dict: Dict[str, str]):
        return Publication(
            raw=publi_dict,
            title=publi_dict["title_s"][0],
            hal_id=publi_dict["halId_s"],
            authors=publi_dict["authFullName_s"],
            date=publi_dict["producedDate_s"],
        )

    @property
    def link(self):
        return f"https://hal.archives-ouvertes.fr/{self.hal_id}"

    @property
    def where(self):
        return self.raw.get("journalTitle_s") or self.raw.get("conferenceTitle_s")


class HalPlugin(Plugin):
    name = "hal"
    description = "Fetches publications from HAL"

    def on_setup_env(self, **extra):
        req = get_request(self.get_config()["query"])
        request_url = req.url
        self.env.jinja_env.globals.update(
            hal_publications=get_publications(req), hal_request=req.url
        )


def get_request(query):
    return requests.get(
        url="https://api.archives-ouvertes.fr/search/",
        params={
            "q": query,
            "sort": "producedDate_tdate desc",
            "fl": "title_s,label_s,docid,authFullName_s,"
            "journalTitle_s,conferenceTitle_s,publisher_s,"
            "halId_s,producedDate_s",
        },
    )


def get_publications(req):
    return [Publication.from_entry(p) for p in req.json()["response"]["docs"]]
