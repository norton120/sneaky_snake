from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class URL(BaseModel):
    url: str

class RequestUrl(URL):
    use_cache: Optional[bool] = True

class ResponseUrl(URL):
    pass

class ScrapeRequest(BaseModel):
    urls: List[RequestUrl]

class ScrapeResult(BaseModel):
    url: ResponseUrl
    processed_at: Optional[datetime] = None
    content: Optional[str] = None
    errors: Optional[str] = None
    processed: bool = False

class ScrapeResponse(BaseModel):
    request_ids: List[str]