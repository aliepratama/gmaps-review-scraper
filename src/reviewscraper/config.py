import os
from pydantic import BaseModel, AnyUrl
from typing import List, Optional

class Settings(BaseModel):
    place_url: str  # Change AnyUrl to str
    sort_direction: str = "desc"  # 'asc' for oldest first, 'desc' for newest first
    scroll_iterations: int = 15   # Number of times to scroll to load more reviews
    output_path: str = "out.json"
    headless: bool = True

    # If you still want URL validation but need a string output, you can use a validator:
    # from pydantic import validator
    # @validator('place_url')
    # def validate_url(cls, v):
    #     # You could run it through AnyUrl validation first
    #     # AnyUrl(v)
    #     return str(v)  # Return as string

    @classmethod
    def from_env(cls):
        return cls(
            place_url=os.getenv("PLACE_URL"),
            sort_direction=os.getenv("SORT_DIRECTION", "desc"),
            output_path=os.getenv("OUTPUT_PATH", "reviews.json"),
            headless=os.getenv("HEADLESS", "true").lower() == "true"
        )
