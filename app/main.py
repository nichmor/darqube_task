from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException


from app.api.errors.errors import http_error_handler
from app.api.errors.errors import http_validation_error_handler
from app.api.routes.api import router as api_router
from app.core.config import API_PREFIX, DEBUG, PROJECT_NAME, VERSION
from app.core.events import create_start_app_handler, create_stop_app_handler


def get_application() -> FastAPI:
    application = FastAPI(title=PROJECT_NAME, debug=DEBUG, version=VERSION)

    application.add_event_handler(
        "startup",
        create_start_app_handler(application)
    )
    application.add_event_handler(
        "shutdown",
        create_stop_app_handler(application)
    )

    application.include_router(api_router, prefix=API_PREFIX)

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http_validation_error_handler)

    return application


app = get_application()
