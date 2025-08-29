from decimal import Decimal, ROUND_HALF_UP

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_API_KEY


def _to_cents(amount: Decimal) -> int:
    """
    Преобразует Decimal в целое количество «копеек» (центов).

    Stripe принимает цены только в минимальных денежных единицах (например, копейках или центах).
    """
    return int((amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP) * 100).to_integral_value())


def create_product(name: str, description: str = "") -> str:
    """
    Создаёт продукт в Stripe.

    Args:
        name (str): Название продукта.
        description (str): Описание продукта.

    Returns:
        str: ID созданного продукта.
    """
    prod = stripe.Product.create(name=name, description=description or "")
    return prod["id"]


def create_price(product_id: str, amount: Decimal, currency: str) -> str:
    """
    Создаёт цену для продукта в Stripe.

    Args:
        product_id (str): ID продукта.
        amount (Decimal): Сумма (в валюте).
        currency (str): Валюта (например, "usd", "rub").

    Returns:
        str: ID созданной цены.
    """
    price = stripe.Price.create(
        product=product_id,
        unit_amount=_to_cents(amount),
        currency=currency,
    )
    return price["id"]


def create_checkout_session(price_id: str, success_url: str, cancel_url: str) -> tuple[str, str]:
    """
    Создаёт checkout-сессию в Stripe.

    Args:
        price_id (str): ID цены.
        success_url (str): URL успешной оплаты.
        cancel_url (str): URL отмены.

    Returns:
        tuple[str, str]: ID сессии и ссылка на оплату.
    """
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=success_url + "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url=cancel_url,
    )
    return session["id"], session["url"]


def retrieve_session(session_id: str) -> dict:
    """
    Получает данные о checkout-сессии по её ID.

    Args:
        session_id (str): ID сессии.

    Returns:
        dict: Данные о сессии из Stripe.
    """
    return stripe.checkout.Session.retrieve(session_id)
