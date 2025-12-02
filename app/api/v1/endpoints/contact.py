from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import ssl
import certifi

from app.db.session import get_db
from app.models.contact import ContactMessage, NewsletterSubscriber
from app.schemas.contact import (
    ContactMessageCreate,
    ContactMessageResponse,
    NewsletterSubscriberCreate,
    NewsletterSubscriberResponse,
)
from app.api.deps import get_current_user, get_current_admin
from app.models.user import User
from app.core.config import settings

router = APIRouter()

# Create a default SSL context using certifi
ssl._create_default_https_context = lambda: ssl.create_default_context(
    cafile=certifi.where())


def send_email(to_email: str, subject: str, html_content: str):
    """Send email using SendGrid"""
    if not settings.SENDGRID_API_KEY:
        print("Warning: SENDGRID_API_KEY not configured")
        return False

    try:
        message = Mail(
            from_email=settings.SENDGRID_FROM_EMAIL,
            to_emails=to_email,
            subject=subject,
            html_content=html_content
        )

        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        response = sg.send(message)

        print(f"SendGrid response: {response.status_code}")
        if response.status_code not in [200, 201, 202]:
            print(f"SendGrid error response body: {response.body}")
            print(f"SendGrid error response headers: {response.headers}")
        return response.status_code in [200, 201, 202]

    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@router.post("/messages", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
async def create_contact_message(
    message_data: ContactMessageCreate,
    db: Session = Depends(get_db),
):
    """Create a new contact message and send notification email"""

    # Create contact message in database
    contact_message = ContactMessage(**message_data.model_dump())
    db.add(contact_message)
    db.commit()
    db.refresh(contact_message)

    # Send notification email to admin
    admin_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f7e6e1;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #3d2c29;">New Contact Form Submission</h2>
                <div style="margin: 20px 0; padding: 15px; background-color: #f7e6e1; border-radius: 5px;">
                    <p><strong>Name:</strong> {message_data.name}</p>
                    <p><strong>Email:</strong> {message_data.email}</p>
                    <p><strong>Phone:</strong> {message_data.phone or 'Not provided'}</p>
                    <p><strong>Subject:</strong> {message_data.subject}</p>
                    <p><strong>Message:</strong></p>
                    <p style="white-space: pre-wrap;">{message_data.message}</p>
                </div>
                <p style="color: #8b6d5a; font-size: 12px;">Received at: {contact_message.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </body>
    </html>
    """

    send_email(
        settings.ADMIN_EMAIL, f"New Contact Form: {message_data.subject}", admin_html)

    # Send confirmation email to user
    user_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f7e6e1;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #b88e72;">Thank You for Contacting B Boutique!</h2>
                <p>Dear {message_data.name},</p>
                <p>We've received your message and will get back to you within 24 hours.</p>
                <div style="margin: 20px 0; padding: 15px; background-color: #f7e6e1; border-radius: 5px;">
                    <p><strong>Your Message:</strong></p>
                    <p style="white-space: pre-wrap;">{message_data.message}</p>
                </div>
                <p>If you need immediate assistance, please call us at +27 84 586 0645.</p>
                <p style="margin-top: 30px;">Best regards,<br><strong>B Boutique Team</strong></p>
            </div>
        </body>
    </html>
    """

    send_email(message_data.email,
               "Thank you for contacting B Boutique", user_html)

    return contact_message


@router.get("/messages", response_model=List[ContactMessageResponse])
def list_contact_messages(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """List all contact messages (admin only)"""
    messages = db.query(ContactMessage).offset(skip).limit(limit).all()
    return messages


@router.patch("/messages/{message_id}/read")
def mark_message_as_read(
    message_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """Mark contact message as read (admin only)"""
    message = db.query(ContactMessage).filter(
        ContactMessage.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    message.is_read = True
    db.commit()

    return {"message": "Message marked as read"}


@router.post("/newsletter/subscribe", response_model=NewsletterSubscriberResponse, status_code=status.HTTP_201_CREATED)
async def subscribe_to_newsletter(
    subscriber_data: NewsletterSubscriberCreate,
    db: Session = Depends(get_db),
):
    """Subscribe to newsletter"""

    # Check if email already exists
    existing = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == subscriber_data.email
    ).first()

    if existing:
        if existing.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already subscribed to newsletter"
            )
        else:
            # Reactivate subscription
            existing.is_active = True
            db.commit()
            db.refresh(existing)
            subscriber = existing
    else:
        # Create new subscriber
        subscriber = NewsletterSubscriber(**subscriber_data.model_dump())
        db.add(subscriber)
        db.commit()
        db.refresh(subscriber)

    # Send welcome email
    welcome_html = f"""
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f7e6e1;">
            <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 10px; padding: 30px;">
                <h2 style="color: #b88e72;">Welcome to B Boutique Newsletter! 🎉</h2>
                <p>Thank you for subscribing to our newsletter!</p>
                <p>You'll now receive:</p>
                <ul style="color: #3d2c29;">
                    <li>Exclusive early access to new collections</li>
                    <li>Special subscriber-only discounts</li>
                    <li>Insider fashion tips and styling advice</li>
                    <li>Latest trends and seasonal updates</li>
                </ul>
                <p style="margin-top: 30px;">Stay stylish!</p>
                <p><strong>B Boutique Team</strong></p>
                <hr style="border: 1px solid #f7e6e1; margin: 20px 0;">
                <p style="color: #8b6d5a; font-size: 12px;">
                    You can unsubscribe at any time by clicking the unsubscribe link in our emails.
                </p>
            </div>
        </body>
    </html>
    """

    send_email(subscriber_data.email,
               "Welcome to B Boutique Newsletter!", welcome_html)

    return subscriber


@router.post("/newsletter/unsubscribe")
async def unsubscribe_from_newsletter(
    email: str,
    db: Session = Depends(get_db),
):
    """Unsubscribe from newsletter"""

    subscriber = db.query(NewsletterSubscriber).filter(
        NewsletterSubscriber.email == email
    ).first()

    if not subscriber:
        raise HTTPException(
            status_code=404, detail="Email not found in newsletter")

    subscriber.is_active = False
    db.commit()

    return {"message": "Successfully unsubscribed from newsletter"}


@router.get("/newsletter/subscribers", response_model=List[NewsletterSubscriberResponse])
def list_newsletter_subscribers(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    """List all newsletter subscribers (admin only)"""
    query = db.query(NewsletterSubscriber)

    if active_only:
        query = query.filter(NewsletterSubscriber.is_active == True)

    subscribers = query.offset(skip).limit(limit).all()
    return subscribers
