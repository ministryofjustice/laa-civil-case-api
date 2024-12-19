from functools import wraps
from fastapi import FastAPI, APIRouter, Depends
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
            version_router = APIRouter(prefix=f"/{version}", tags=[f"{version}"])

            # Loop through each router and include the versioned endpoints
            for router in routers:
                for route in router.routes:
                    if route.endpoint in endpoints:
                        version_router.add_api_route(
                            route.path,
                            route.endpoint,
                            methods=route.methods,
                            response_model=route.response_model,
                            dependencies=route.dependencies + [Depends(oauth2_scheme)],
                            name=route.name,
                            summary=route.summary,
                            description=route.description,
                        )

            # Add the versioned router to the app
            self.include_router(version_router)

        # Include non-versioned routes directly to the app
        for router in routers:
            for route in router.routes:
                if not any(
                    route.endpoint in endpoints
                    for endpoints in versioned_endpoints.values()
                ):
                    # Add authentication for non-versioned routes
                    route.dependencies.append(Depends(oauth2_scheme))
                    self.router.routes.append(route)
