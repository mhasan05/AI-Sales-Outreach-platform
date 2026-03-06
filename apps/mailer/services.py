from email.utils import make_msgid
from django.core.mail import EmailMultiAlternatives, get_connection
from django.utils import timezone

from apps.ai_engine.services import render_template_variables


def get_smtp_connection(smtp_setting):
    return get_connection(
        backend="django.core.mail.backends.smtp.EmailBackend",
        host=smtp_setting.host,
        port=smtp_setting.port,
        username=smtp_setting.username,
        password=smtp_setting.password,
        use_tls=smtp_setting.use_tls,
        use_ssl=smtp_setting.use_ssl,
        fail_silently=False,
    )


def build_from_email(smtp_setting):
    if smtp_setting.from_name:
        return f"{smtp_setting.from_name} <{smtp_setting.from_email}>"
    return smtp_setting.from_email


def send_email_via_smtp(
    smtp_setting,
    to_email,
    subject,
    body,
    reply_to=None,
):
    connection = get_smtp_connection(smtp_setting)
    provider_message_id = make_msgid()

    email = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=build_from_email(smtp_setting),
        to=[to_email],
        reply_to=[reply_to or smtp_setting.reply_to_email] if (reply_to or smtp_setting.reply_to_email) else None,
        connection=connection,
        headers={"Message-ID": provider_message_id},
    )

    sent_count = email.send()
    return {
        "sent_count": sent_count,
        "provider_message_id": provider_message_id,
        "sent_at": timezone.now(),
    }


def render_email_content(subject, body, variables):
    return (
        render_template_variables(subject, variables),
        render_template_variables(body, variables),
    )