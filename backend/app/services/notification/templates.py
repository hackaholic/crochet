"""Branded email and SMS notification templates for Sulocraft."""

def render_otp_sms(otp_code: str) -> str:
    """Format plain-text OTP verification SMS."""
    return f"Your Sulocraft verification code is: {otp_code}. Valid for 5 minutes. Do not share this code."


def render_order_confirmation_sms(order_number: str, total_amount: float, tracking_url: str) -> str:
    """Format plain-text order confirmation SMS."""
    return (
        f"Thank you for choosing Sulocraft! Order #{order_number} for Rs.{int(total_amount):,} "
        f"is confirmed and will be handcrafted with care. Track status: {tracking_url}"
    )


def render_order_status_sms(
    order_number: str,
    status: str,
    carrier: str | None = None,
    tracking_number: str | None = None,
    tracking_url: str = "",
) -> str:
    """Format plain-text order status SMS."""
    status_clean = status.replace("_", " ").title()
    carrier_info = f" via {carrier} (#{tracking_number})" if carrier and tracking_number else ""
    return (
        f"Sulocraft Update: Your order #{order_number} is now {status_clean}{carrier_info}. "
        f"View details: {tracking_url}"
    )


def render_order_confirmation_email(order_data: dict) -> tuple[str, str]:
    """Generate HTML and plain text for order confirmation.

    Returns:
        tuple[str, str]: (html_body, text_body)
    """
    order_number = order_data.get("orderNumber", "")
    customer_name = order_data.get("shippingAddress", {}).get("name", "Valued Customer")
    total_amount = order_data.get("totalAmount", 0)
    payment_method = order_data.get("paymentMethod", "ONLINE")
    tracking_url = order_data.get("trackingUrl", f"https://sulocraft.com/account/orders/{order_number}")
    items = order_data.get("items", [])

    items_html_rows = ""
    items_text_rows = ""
    for item in items:
        p_name = item.get("productName", "Artisanal Crochet Creation")
        v_name = item.get("variantName", "")
        qty = item.get("quantity", 1)
        price = item.get("unitPrice", 0)
        line_total = item.get("lineTotal", price * qty)
        variant_desc = f" ({v_name})" if v_name else ""

        items_html_rows += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #f0e6e0;">
                <strong style="color: #2b1f1d;">{p_name}</strong>{variant_desc}<br>
                <span style="color: #7d6b67; font-size: 13px;">Qty: {qty} &times; &#8377;{price:,}</span>
            </td>
            <td style="padding: 12px 0; border-bottom: 1px solid #f0e6e0; text-align: right; font-weight: 600; color: #2b1f1d;">
                &#8377;{line_total:,}
            </td>
        </tr>
        """
        items_text_rows += f"- {p_name}{variant_desc} | Qty: {qty} x Rs.{price:,} = Rs.{line_total:,}\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Sulocraft - Order Confirmed #{order_number}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #faf7f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #faf7f5; padding: 30px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
                    <!-- Header -->
                    <tr>
                        <td style="background-color: #832729; padding: 32px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 26px; font-weight: 700; letter-spacing: 1px;">SULOCRAFT</h1>
                            <p style="margin: 8px 0 0; color: #f5dcd7; font-size: 14px;">Handmade with Love & Artisanal Craft</p>
                        </td>
                    </tr>
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 36px 30px;">
                            <h2 style="margin: 0 0 16px; color: #2b1f1d; font-size: 20px;">Thank You, {customer_name}!</h2>
                            <p style="margin: 0 0 24px; color: #5a4b48; font-size: 15px; line-height: 1.6;">
                                Your order <strong>#{order_number}</strong> has been received and confirmed. Each Sulocraft creation is carefully handcrafted by our artisans.
                            </p>
                            <!-- Order Summary Box -->
                            <div style="background-color: #faf7f5; border-radius: 8px; padding: 20px; margin-bottom: 28px;">
                                <table width="100%" cellspacing="0" cellpadding="0">
                                    <tr>
                                        <td style="color: #7d6b67; font-size: 13px;">Order Number:</td>
                                        <td style="text-align: right; font-weight: 600; color: #2b1f1d;">#{order_number}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #7d6b67; font-size: 13px; padding-top: 8px;">Payment Method:</td>
                                        <td style="text-align: right; font-weight: 600; color: #2b1f1d; padding-top: 8px;">{payment_method}</td>
                                    </tr>
                                    <tr>
                                        <td style="color: #7d6b67; font-size: 13px; padding-top: 8px;">Order Total:</td>
                                        <td style="text-align: right; font-weight: 700; color: #832729; font-size: 18px; padding-top: 8px;">&#8377;{int(total_amount):,}</td>
                                    </tr>
                                </table>
                            </div>
                            <!-- Items Table -->
                            <h3 style="margin: 0 0 12px; color: #2b1f1d; font-size: 16px; border-bottom: 2px solid #832729; padding-bottom: 6px;">Your Items</h3>
                            <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 28px;">
                                {items_html_rows}
                            </table>
                            <!-- Action Button -->
                            <div style="text-align: center; margin: 32px 0 16px;">
                                <a href="{tracking_url}" style="background-color: #832729; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px; display: inline-block;">
                                    Track Your Order
                                </a>
                            </div>
                        </td>
                    </tr>
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f7f3ef; padding: 24px 30px; text-align: center; color: #8a7a76; font-size: 13px; border-top: 1px solid #ede4df;">
                            <p style="margin: 0 0 6px;">Need help? Reach out to <a href="mailto:support@sulocraft.com" style="color: #832729; text-decoration: none;">support@sulocraft.com</a></p>
                            <p style="margin: 0;">&copy; Sulocraft. All rights reserved.</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    text = f"""SULOCRAFT - ORDER CONFIRMED #{order_number}

Thank you for your order, {customer_name}!

Order Number: #{order_number}
Payment Method: {payment_method}
Total: Rs.{int(total_amount):,}

Items:
{items_text_rows}

Track your order status: {tracking_url}

Need help? Contact support@sulocraft.com
"""

    return html, text


def render_order_status_email(
    order_data: dict,
    new_status: str,
    carrier: str | None = None,
    tracking_number: str | None = None,
) -> tuple[str, str]:
    """Generate HTML and plain text for order status updates."""
    order_number = order_data.get("orderNumber", "")
    customer_name = order_data.get("shippingAddress", {}).get("name", "Valued Customer")
    tracking_url = order_data.get("trackingUrl", f"https://sulocraft.com/account/orders/{order_number}")
    status_clean = new_status.replace("_", " ").title()

    carrier_html = ""
    carrier_text = ""
    if carrier and tracking_number:
        carrier_html = f"""
        <div style="background-color: #f0f7f4; border: 1px solid #d4ebd9; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 0; color: #216335; font-size: 14px;">
                <strong>Courier:</strong> {carrier}<br>
                <strong>Tracking Number:</strong> {tracking_number}
            </p>
        </div>
        """
        carrier_text = f"\nCourier: {carrier}\nTracking Number: {tracking_number}\n"

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Sulocraft - Order #{order_number} {status_clean}</title>
</head>
<body style="margin: 0; padding: 0; background-color: #faf7f5; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background-color: #faf7f5; padding: 30px 15px;">
        <tr>
            <td align="center">
                <table role="presentation" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 16px rgba(0,0,0,0.06);">
                    <tr>
                        <td style="background-color: #832729; padding: 28px 30px; text-align: center;">
                            <h1 style="margin: 0; color: #ffffff; font-size: 24px; font-weight: 700;">SULOCRAFT</h1>
                        </td>
                    </tr>
                    <tr>
                        <td style="padding: 36px 30px;">
                            <h2 style="margin: 0 0 16px; color: #2b1f1d; font-size: 20px;">Order Status Update</h2>
                            <p style="margin: 0 0 20px; color: #5a4b48; font-size: 15px; line-height: 1.6;">
                                Hello {customer_name}, your order <strong>#{order_number}</strong> is now:
                            </p>
                            <div style="background-color: #faf7f5; border-left: 4px solid #832729; padding: 16px 20px; border-radius: 4px; margin-bottom: 24px;">
                                <span style="font-size: 18px; font-weight: 700; color: #832729;">{status_clean}</span>
                            </div>
                            {carrier_html}
                            <div style="text-align: center; margin: 32px 0 16px;">
                                <a href="{tracking_url}" style="background-color: #832729; color: #ffffff; text-decoration: none; padding: 14px 32px; border-radius: 8px; font-weight: 600; font-size: 15px; display: inline-block;">
                                    View Order Timeline
                                </a>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td style="background-color: #f7f3ef; padding: 20px 30px; text-align: center; color: #8a7a76; font-size: 13px;">
                            &copy; Sulocraft. Handcrafted with love.
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

    text = f"""SULOCRAFT - ORDER UPDATE #{order_number}

Hello {customer_name},

Your order #{order_number} status is now: {status_clean}.
{carrier_text}
Track online: {tracking_url}
"""

    return html, text
