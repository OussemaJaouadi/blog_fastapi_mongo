from fastapi import FastAPI
from fastapi.openapi.models import SecurityScheme
from contextlib import asynccontextmanager
from db.connect import Database
from config.config import Settings
from routes import blog, user



# Define the custom OpenAPI function
def custom_openapi(app: FastAPI):
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = app.openapi()
    openapi_schema['components']['securitySchemes'] = {
        'BearerAuth': {
            'type': 'http',
            'scheme': 'bearer',
            'bearerFormat': 'JWT'
        }
    }
    openapi_schema['security'] = [
        {'BearerAuth': []}
    ]
    app.openapi_schema = openapi_schema
    return openapi_schema

settings = Settings()
database = Database()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting")
    try:
        yield
    finally:
        # Optionally close the database connection here
        print("Server Shutting")

app = FastAPI(
    title="Testing SQLModel",
    version="0.1.0",
    lifespan=lifespan,
    openapi=custom_openapi
)

# Include routes and pass the database instance
app.include_router(user.router)
app.include_router(blog.router)
