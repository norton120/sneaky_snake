from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class URL(BaseModel):
    url: str = Field(description="The URL to scrape")

class RequestUrl(URL):
    use_cache: Optional[bool] = Field(default=True, description="If True, will use a previously scraped URL/selector result if it exists")
    selector: Optional[str] = Field(default=None, description="The CSS selector (if any) to wait for before scraping the page")

class ResponseUrl(URL):
    selector: Optional[str] = Field(default=None, description="The CSS selector (if any) waited for before scraping the page")

class ScrapeRequest(BaseModel):
    urls: List[RequestUrl] = Field(description="The URLs to scrape")
    stealth: Optional[bool] = Field(default=False, description="If True, will attempt to use a more stealthy browser")
    timeout: Optional[int] = Field(default=10000, description="The timeout for the scrape in milliseconds")

class ScrapeResult(BaseModel):
    url: ResponseUrl = Field(description="The URL that was scraped")
    processed_at: Optional[datetime] = Field(default=None, description="The date and time the URL was scraped")
    content: Optional[str] = Field(default=None, description="The raw HTML content scraped from the URL")
    errors: Optional[str] = Field(default=None, description="Any errors that occurred during the scraping process")
    processed: bool = Field(default=False, description="True if the scraping process was completed (successful or not)")
    selector: Optional[str] = Field(default=None, description="The CSS selector (if any) waited for before scraping the page")

class ScrapeResponse(BaseModel):
    request_ids: List[str] = Field(description="The identifiers that can be used to retrieve the results of the scraping process")