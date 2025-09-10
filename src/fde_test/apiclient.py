import json
import logging
import os
import urllib3

from urllib3.util.retry import Retry

import config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        self.base_url = config.read_config()["api_base_url"]
        self.x_api_key = os.getenv("X-API-KEY")
        retry_strategy = Retry(
            total=5,
            status_forcelist=[429, 503],
            allowed_methods=["GET", "POST"],
            backoff_factor=1
        )
        self.http = urllib3.PoolManager(retries=retry_strategy)

    def get_enrichment_data(self, customer):
        response_data = {
            "social_handle": None,
            "success": None,
            "reason": None
        }
        payload = {"email": customer.email}
        headers = {"x-api-key": self.x_api_key}
        request_url = self.base_url + "enrichment"
        r = self.http.request("GET", request_url, fields=payload, headers=headers)
        if r.status == 200:
            social_handle = r.json()["social_handle"]
            response_data["social_handle"] = social_handle
            response_data["success"] = True
        else:
            error_message = r.json()["detail"]
            response_data["success"] = False
            response_data["reason"] = f"API Error. Status: {r.status}. Message: {error_message}"
            logger.error("Customer '%s' encountered API error. Message: %s", customer.customer_id, error_message)
        return response_data
    
    def post_submission(self, customer):
        response_data = {
            "success": None,
            "reason": None
        }
        request_url = self.base_url + "submission"
        headers = {"x-api-key": self.x_api_key, 'Content-Type': 'application/json'}
        payload = json.dumps({
            "customer_id": customer.customer_id,
            "name": customer.name,
            "email": customer.email,
            "total_spend": customer.total_spend,
            "social_handle": customer.social_handle
        })
        r = self.http.request("POST", request_url, body=payload, headers=headers)
        if r.status != 200:
            error_message = r.json()["detail"]
            response_data["success"] = False,
            response_data["reason"] = f"API Error. Status: {r.status}. Message: {error_message}"
            logger.error("Customer '%s' encountered API error. Message: %s", customer.customer_id, error_message)
        else:
            response_data["success"] = True
        return response_data