from fastapi import APIRouter
from . import case_information, security

router = APIRouter(prefix="/v1")
router.include_router(case_information.router)
router.include_router(security.router)
