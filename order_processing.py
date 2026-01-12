DEFAULT_CURRENCY = "USD"
TAX_RATE = 0.21
MIN_PRICE = 0
MIN_QTY = 0

SAVE10_RATE = 0.10
SAVE20_RATE_HIGH = 0.20
SAVE20_RATE_LOW = 0.05
SAVE20_THRESHOLD = 200
VIP_DISCOUNT_LARGE = 50
VIP_DISCOUNT_SMALL = 10
VIP_THRESHOLD = 100


def parse_checkout_request(request):
    user_id = request.get("user_id")
    items = request.get("items", [])
    coupon = request.get("coupon")
    currency = request.get("currency", DEFAULT_CURRENCY)
    return user_id, items, coupon, currency


def validate_user_id(user_id):
    if user_id is None:
        raise ValueError("user_id is required")


def validate_items_structure(items):
    if not isinstance(items, list):
        raise ValueError("items must be a list")
    if len(items) == 0:
        raise ValueError("items must not be empty")


def validate_item_fields(item):
    if "price" not in item or "qty" not in item:
        raise ValueError("item must have price and qty")
    if item["price"] <= MIN_PRICE:
        raise ValueError("price must be positive")
    if item["qty"] <= MIN_QTY:
        raise ValueError("qty must be positive")


def compute_subtotal(items):
    return sum(item["price"] * item["qty"] for item in items)


def calculate_save10_discount(subtotal):
    return int(subtotal * SAVE10_RATE)


def calculate_save20_discount(subtotal):
    if subtotal >= SAVE20_THRESHOLD:
        return int(subtotal * SAVE20_RATE_HIGH)
    return int(subtotal * SAVE20_RATE_LOW)


def calculate_vip_discount(subtotal):
    if subtotal >= VIP_THRESHOLD:
        return VIP_DISCOUNT_LARGE
    return VIP_DISCOUNT_SMALL


def calculate_coupon_discount(subtotal, coupon):
    if coupon == "SAVE10":
        return calculate_save10_discount(subtotal)
    elif coupon == "SAVE20":
        return calculate_save20_discount(subtotal)
    elif coupon == "VIP":
        return calculate_vip_discount(subtotal)
    elif coupon:
        raise ValueError("unknown coupon")
    return 0


def compute_discount_amount(subtotal, coupon):
    if not coupon:
        return 0
    return calculate_coupon_discount(subtotal, coupon)


def calculate_tax_amount(total_after_discount):
    return int(total_after_discount * TAX_RATE)


def build_order_result(user_id, items, currency, subtotal, discount, tax, total):
    return {
        "order_id": f"{user_id}-{len(items)}-X",
        "user_id": user_id,
        "currency": currency,
        "subtotal": subtotal,
        "discount": discount,
        "tax": tax,
        "total": total,
        "items_count": len(items),
    }


def process_checkout(request):
    user_id, items, coupon, currency = parse_checkout_request(request)
    
    validate_user_id(user_id)
    validate_items_structure(items)
    
    for item in items:
        validate_item_fields(item)
    
    subtotal = compute_subtotal(items)
    discount = compute_discount_amount(subtotal, coupon)
    
    total_after_discount = max(subtotal - discount, 0)
    tax = calculate_tax_amount(total_after_discount)
    total = total_after_discount + tax
    
    return build_order_result(user_id, items, currency, subtotal, discount, tax, total)
