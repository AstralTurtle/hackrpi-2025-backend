from fastapi import APIRouter
from classes.lines import lines

router = APIRouter(prefix="/health", tags=["health"])

@router.get("/lines")
def check_lines_loaded():
    return lines
