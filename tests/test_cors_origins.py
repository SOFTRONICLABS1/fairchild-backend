from app.core.config import Settings, get_cors_origins


def test_cors_origins_use_explicit_list_when_present() -> None:
    settings = Settings(
        FRONTEND_LOCAL_ORIGIN='http://localhost:3000',
        FRONTEND_PROD_ORIGIN='https://app.domain.com',
        FRONTEND_ORIGINS='http://localhost:3000, https://app.domain.com, https://preview.domain.com,',
    )

    assert get_cors_origins(settings) == [
        'http://localhost:3000',
        'https://app.domain.com',
        'https://preview.domain.com',
    ]


def test_cors_origins_fallback_to_legacy_fields() -> None:
    settings = Settings(
        FRONTEND_LOCAL_ORIGIN='http://localhost:3000',
        FRONTEND_PROD_ORIGIN='https://app.domain.com',
        FRONTEND_ORIGINS='',
    )

    assert get_cors_origins(settings) == [
        'http://localhost:3000',
        'https://app.domain.com',
    ]


def test_cors_origins_ignore_empty_entries_and_duplicates() -> None:
    settings = Settings(
        FRONTEND_LOCAL_ORIGIN='http://localhost:3000',
        FRONTEND_PROD_ORIGIN='http://localhost:3000',
        FRONTEND_ORIGINS='https://one.example.com, , https://one.example.com, https://two.example.com',
    )

    assert get_cors_origins(settings) == [
        'https://one.example.com',
        'https://two.example.com',
    ]
