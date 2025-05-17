import os
from pydantic import BaseModel, AnyUrl, conint

class Settings(BaseModel):
    place_url:   AnyUrl
    star_filter: list[conint(ge=1, le=5)] | None = None
    output_path: str = "reviews.json"
    headless:    bool = True
    scroll_pause: float = 1.5
    max_scrolls: int = 30

    @classmethod
    def from_env(cls):
        return cls(
            place_url=os.getenv("PLACE_URL"),
            star_filter=([int(s) for s in os.getenv("STAR_FILTER", "").split(",")] 
                          if os.getenv("STAR_FILTER") else None),
            output_path=os.getenv("OUTPUT_PATH", "reviews.json"),
            headless=os.getenv("HEADLESS", "true").lower() == "true"
        )
