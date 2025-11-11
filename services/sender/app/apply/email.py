from __future__ import annotations

import smtplib
from email.message import EmailMessage
from typing import Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape
from job_agent_shared import build_s3_client, S3Url


def render_email(template_dir: str, template_name: str, context: dict) -> str:
    env = Environment(loader=FileSystemLoader(template_dir), autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template(template_name)
    return template.render(**context)


def build_message(from_addr: str, to_addr: str, subject: str, body: str, resume_s3_url: Optional[str]) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = from_addr
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    if resume_s3_url:
        s3 = build_s3_client()
        s3url = S3Url.parse(resume_s3_url)
        obj = s3.get_object(Bucket=s3url.bucket, Key=s3url.key)
        data = obj["Body"].read()
        filename = s3url.key.split("/")[-1]
        msg.add_attachment(data, maintype="application", subtype="pdf", filename=filename)
    return msg


def send_email(host: str, port: int, user: str | None, password: str | None, use_tls: bool, msg: EmailMessage) -> None:
    if use_tls:
        server = smtplib.SMTP(host, port)
        server.starttls()
    else:
        server = smtplib.SMTP(host, port)
    if user and password:
        server.login(user, password)
    server.send_message(msg)
    server.quit()


