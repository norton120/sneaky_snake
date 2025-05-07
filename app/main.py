from fastapi import FastAPI, Depends, BackgroundTasks
from random import randint
from typing import Optional
import time
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from datetime import datetime
from contextlib import asynccontextmanager
from app.database import get_db, ScrapeResult
from app.models import ScrapeRequest, ScrapeResponse, ScrapeResult as ScrapeResultSchema, ResponseUrl
from app.playwright_scraper import Scraper
from app.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """set up the scraper cache"""
    logger.info("Initializing PlaywrightScraper with fresh profile")
    _ = Scraper(reset_profile=True)
    logger.info("Startup complete")
    yield
    logger.info("Shutting down")

app = FastAPI(title="Sneaky Snake API",
              lifespan=lifespan,
              description="Scrape URLs simply, using your own browser profile")

@app.get("/health")
async def health_check():
    """check if the API is running"""
    logger.debug("Health check requested")
    return JSONResponse(
        content={"status": "healthy"},
        status_code=200
    )

@app.post("/scrape")
async def scrape(
    scrape_request: ScrapeRequest,
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
) -> ScrapeResponse:
    """scrape url(s) and return scrape request IDs that can be used to retrieve the results"""
    logger.info(f"Received scrape request for {len(scrape_request.urls)} URLs")
    with db as session:
        cached_request_ids = []
        new_request_ids = []
        for url in scrape_request.urls:
            # check for cache
            logger.debug(f"Checking cache for URL: {url.url}")
            result = session.query(ScrapeResult).filter(ScrapeResult.url == url.url and ScrapeResult.selector == url.selector).first()
            if result and url.use_cache:
                logger.info(f"Cache hit for URL: {url.url}")
                cached_request_ids.append(result.request_id)
                continue
            if result:
                logger.info(f"Deleting cached result for URL: {url.url}")
                session.delete(result)
            logger.info(f"Creating new scrape request for URL: {url.url} with selector: {url.selector}")
            new_result = ScrapeResult(url=url.url, content=None, processed=False, selector=url.selector)
            session.add(new_result)
            session.commit()
            session.refresh(new_result)
            new_request_ids.append(new_result.request_id)

        for request_id in new_request_ids:
            logger.debug(f"Adding background task for request_id: {request_id}")
            background_tasks.add_task(background_scrape,
                                      stealth=scrape_request.stealth,
                                      request_id=request_id,
                                      delay=randint(0,4),
                                      db=db)

    logger.info(f"Returning {len(cached_request_ids)} cached and {len(new_request_ids)} new request IDs")
    return ScrapeResponse(request_ids=cached_request_ids + new_request_ids)

@app.get("/result/{result_id}")
async def get_result(
    result_id: str,
    db: Session = Depends(get_db)
) -> ScrapeResultSchema:
    """get the result of a scrape by request ID"""
    logger.info(f"Fetching result for request_id: {result_id}")
    result = db.query(ScrapeResult).filter(ScrapeResult.request_id == result_id).first()
    if not result:
        logger.warning(f"Result not found for request_id: {result_id}")
        return JSONResponse(
            content={"error": "Result not found"},
            status_code=404
        )
    logger.debug(f"Found result for request_id: {result_id}, processed: {result.processed}")
    return ScrapeResultSchema(
        request_id=result_id,
        url=ResponseUrl(url=result.url),
        processed_at=result.processed_at,
        content=result.content,
        errors=result.errors,
        processed=result.processed,
        selector=result.selector
    )


def background_scrape(request_id: str,
                      stealth: bool,
                      delay: Optional[int] = 0,
                      db: Session = None):
    logger.info(f"Delaying background scrape for {delay} seconds")
    time.sleep(delay)
    logger.info(f"Starting background scrape for request_id: {request_id}")
    with db as session:
        try:
            result = session.query(ScrapeResult).filter(ScrapeResult.request_id == request_id).first()
            if not result:
                logger.error(f"Could not find result for request_id: {request_id}")
                return
            scraper = Scraper(stealth=stealth)
            logger.debug(f"Attempting to scrape URL: {result.url} with selector: {result.selector}")
            result.content = scraper.raw_scrape(result.url, selector=result.selector, timeout=result.timeout)
            if not result.content:
                logger.error(f"Failed to scrape URL: {result.url}")
            else:
                logger.info(f"Successfully scraped URL: {result.url} with content length: {len(result.content)}")
        except Exception as e:
            logger.error(f"Error scraping URL {result.url}: {str(e)}", exc_info=True)
            result.errors = str(e)
        result.processed_at = datetime.now()
        result.processed = True
        session.commit()
    logger.info(f"Completed background scrape for request_id: {request_id}")