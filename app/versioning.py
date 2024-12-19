from functools import wraps
from fastapi import FastAPI, APIRouter
from typing import Callable, List, Dict
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

versioned_endpoints: Dict[str, List[Callable]] = {}


def version(*versions: str):
    """
    Decorator to mark an endpoint with specific API versions.
    :param versions: The versions of the API (e.g., "v1", "v2").
    """

    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)

        for version in versions:
            if version not in versioned_endpoints:
                versioned_endpoints[version] = []
            versioned_endpoints[version].append(func)

        # Preserves the original FastAPI function
        return func

    return decorator


class VersionedFastAPI(FastAPI):
    def add_versioned_routes(self, routers: List[APIRouter]):
        """
        Dynamically add versioned routes for decorated endpoints.

        :param routers: List of APIRouters containing endpoints.
        """
        for version, endpoints in versioned_endpoints.items():
            version_router = APIRouter(
                prefix=f"/v{version}", tags=[f"Version {version}"]
            )

            # Loop through each router and include the versioned endpoints
            for router in routers:
                for route in router.routes:
                    if route.endpoint in endpoints:
                        version_router.add_api_route(
                            route.path,
                            route.endpoint,
                            methods=route.methods,
                            response_model=route.response_model,
                            dependencies=route.dependencies,
                            name=route.name,
                            summary=route.summary,
                            description=route.description,
                        )

            # Add the versioned router to the app
            self.include_router(version_router)

        # Adds the security router as default
        for router in routers:
            if router.tags == ["security"]:
                for route in router.routes:
                    self.router.routes.append(route)
