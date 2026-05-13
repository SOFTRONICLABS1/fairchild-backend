from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.services.platform_auth_service import platform_auth_service

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    docs_url='/docs',
    redoc_url='/redoc',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_LOCAL_ORIGIN, settings.FRONTEND_PROD_ORIGIN],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.on_event('startup')
async def preload_platform_credentials() -> None:
    if settings.CJ_TOKEN:
        platform_auth_service.set_token('cj', settings.CJ_TOKEN)

    if settings.METRICOOL_TOKEN:
        platform_auth_service.set_token('metricool', settings.METRICOOL_TOKEN)

    if settings.RENDERFORM_API_KEY:
        platform_auth_service.set_token('renderform', settings.RENDERFORM_API_KEY)

    if settings.IMPACT_ACCOUNT_SID and settings.IMPACT_AUTH_TOKEN:
        platform_auth_service.set_credentials(
            'impact',
            {
                'account_sid': settings.IMPACT_ACCOUNT_SID,
                'auth_token': settings.IMPACT_AUTH_TOKEN,
            },
        )

    if settings.WORDPRESS_DOMAIN and settings.WORDPRESS_WC_CONSUMER_KEY and settings.WORDPRESS_WC_CONSUMER_SECRET:
        platform_auth_service.set_credentials(
            'wordpress',
            {
                'domain': settings.WORDPRESS_DOMAIN,
                'wc_consumer_key': settings.WORDPRESS_WC_CONSUMER_KEY,
                'wc_consumer_secret': settings.WORDPRESS_WC_CONSUMER_SECRET,
            },
        )


app.include_router(api_router, prefix=settings.API_V1_PREFIX)
