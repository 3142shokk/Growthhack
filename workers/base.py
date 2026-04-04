from abc import ABC, abstractmethod

from models.post import Post


class BaseWorker(ABC):
    platform: str = ""

    @abstractmethod
    def scrape(self) -> list[Post]:
        """Run the scraper and return a list of normalized Post objects."""
        ...
