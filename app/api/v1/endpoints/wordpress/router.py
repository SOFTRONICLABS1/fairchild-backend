from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from httpx import HTTPError, HTTPStatusError

from app.schemas.common import ApiResponse, ErrorDetail
from app.schemas.wordpress.auth import WordPressAuthorizeRequest, WordPressAuthorizeResponse
from app.schemas.wordpress.product import WooProductCreateRequest
from app.services.wordpress.service import WordPressService
from app.services.platform_auth_service import platform_auth_service

router = APIRouter(prefix='/wordpress', tags=['WordPress'])


@router.get('/health')
def wordpress_health() -> dict[str, str]:
    return {'platform': 'wordpress', 'status': 'ready'}


def _resolve_wordpress_credentials() -> dict[str, str]:
    credentials = platform_auth_service.get_credentials('wordpress')
    if credentials:
        return credentials
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=ErrorDetail(
            code='MISSING_AUTHORIZATION',
            message='Set WordPress credentials first via POST /api/v1/wordpress/authorize',
        ).model_dump(),
    )


@router.post('/authorize', response_model=ApiResponse[WordPressAuthorizeResponse])
def wordpress_authorize(body: WordPressAuthorizeRequest) -> ApiResponse[WordPressAuthorizeResponse]:
    platform_auth_service.set_credentials(
        'wordpress',
        {
            'domain': body.domain,
            'wc_consumer_key': body.wc_consumer_key,
            'wc_consumer_secret': body.wc_consumer_secret,
        },
    )
    return ApiResponse(
        data=WordPressAuthorizeResponse(
            platform='wordpress',
            domain=body.domain,
            authorized=True,
            message='WordPress credentials saved successfully',
        )
    )


@router.post('/media/upload', response_model=ApiResponse[Any])
async def wordpress_upload_media(
    file: UploadFile | None = File(default=None),
    image_url: str | None = Form(default=None, alias='image_url'),
) -> ApiResponse[Any]:
    credentials = _resolve_wordpress_credentials()
    if file is None and not (image_url and image_url.strip()):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=ErrorDetail(
                code='INVALID_MEDIA_INPUT',
                message='Provide either file or image_url',
            ).model_dump(),
        )

    try:
        if image_url and image_url.strip():
            payload = await WordPressService.upload_media_from_url(
                domain=credentials['domain'],
                wc_consumer_key=credentials['wc_consumer_key'],
                wc_consumer_secret=credentials['wc_consumer_secret'],
                image_url=image_url.strip(),
            )
        else:
            payload = await WordPressService.upload_media(
                domain=credentials['domain'],
                wc_consumer_key=credentials['wc_consumer_key'],
                wc_consumer_secret=credentials['wc_consumer_secret'],
                picture=file,
            )
        return ApiResponse(data=payload)
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=ErrorDetail(
                code='WORDPRESS_API_ERROR',
                message=f'WordPress API error: {exc.response.status_code}',
                details=exc.response.text,
            ).model_dump(),
        ) from exc
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorDetail(
                code='WORDPRESS_CONNECTIVITY_ERROR',
                message='Unable to reach WordPress API',
            ).model_dump(),
        ) from exc


@router.post('/products', response_model=ApiResponse[Any])
async def wordpress_create_product(
    body: WooProductCreateRequest,
) -> ApiResponse[Any]:
    credentials = _resolve_wordpress_credentials()

    try:
        payload = await WordPressService.create_product(
            domain=credentials['domain'],
            wc_consumer_key=credentials['wc_consumer_key'],
            wc_consumer_secret=credentials['wc_consumer_secret'],
            payload=body,
        )
        return ApiResponse(data=payload)
    except HTTPStatusError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=ErrorDetail(
                code='WORDPRESS_API_ERROR',
                message=f'WordPress API error: {exc.response.status_code}',
                details=exc.response.text,
            ).model_dump(),
        ) from exc
    except HTTPError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=ErrorDetail(
                code='WORDPRESS_CONNECTIVITY_ERROR',
                message='Unable to reach WordPress API',
            ).model_dump(),
        ) from exc
