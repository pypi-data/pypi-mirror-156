import json
import logging
from typing import List

from loguru import logger
from pydantic import BaseModel
import upswingutil as ul
from upswingutil.resource import http_retry
from upswingutil.schema import ResponseDict


class NotificationAuraModel(BaseModel):
    orgId: str
    role: List[str]
    title: str
    body: str
    banner: str
    actions: str
    priority: str
    type: str
    tag: str
    id: str


class NotificationAlvieModel(BaseModel):
    orgId: str
    title: str
    body: str
    banner: str
    actions: str
    priority: str
    type: str
    tag: str
    id: str
    tokens: List[str]


def push_notification_to_aura(data: NotificationAuraModel, G_CLOUD_PROJECT: str = ul.G_CLOUD_PROJECT):
    response = ResponseDict(status=False, message="Init", data={})
    try:
        url = f'https://asia-south1-{G_CLOUD_PROJECT}.cloudfunctions.net/notification'
        http_client = http_retry()
        response_ = http_client.post(url, json=data.dict(), headers={'content-type': 'application/json'})
        if response_.status_code != 200:
            response.message = "Unable to send notification" + response_.reason
        else:
            response.status = True
            response.message = "Sent successfully"
    except Exception as e:
        logging.error(f"Unable to send notification to Aura: {data.orgId} - {data.title}")
    finally:
        return response.dict()


def push_notification_to_alvie(data: NotificationAlvieModel, G_CLOUD_PROJECT: str = ul.G_CLOUD_PROJECT):
    response = ResponseDict(status=False, message="Init", data={})
    try:
        url = f'https://asia-south1-{G_CLOUD_PROJECT}.cloudfunctions.net/notification'
        http_client = http_retry()
        response_ = http_client.post(url, json=data.dict(), headers={'content-type': 'application/json'})
        if response_.status_code != 200:
            response.message = "Unable to send notification" + response_.reason
        else:
            response.status = True
            response.message = "Sent successfully"
    except Exception as e:
        logging.error(f"Unable to send notification to Aura: {data.orgId} - {data.title}")
    finally:
        return response.dict()
