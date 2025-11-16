from fastapi import APIRouter

from classes.line import lines_data

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/lines")
def check_lines_loaded():
    return lines_data
