import asyncio
import traceback

from fastapi import APIRouter, HTTPException
from services.tidal import tidal_service

router = APIRouter()


@router.post("/library/sync")
async def sync_library():
    try:
        result = await asyncio.to_thread(tidal_service.sync)
        return result
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
