import json
import logging
import os
import urllib3
from urllib3.util.retry import Retry

import config

logger = logging.getLogger(__name__)

class APIClient:
    def __init__(self):
        config_data = config.read_config()
        self.base_url = config_data["api_base_url"]
        self.x_api_key = os.getenv("X-API-KEY")
        retry_strategy = Retry(
            total=int(config_data["api_retries"]),
            status_forcelist=[429, 503],
            allowed_methods=["GET", "POST"],
            backoff_factor=1
        )
        self.http = urllib3.PoolManager(retries=retry_strategy)

    def get_enrichment_data(self, customer):
        response_data = {
            "social_handle": "",
            "success": None,
            "reason": None
        }
        payload = {"email": customer.email}
        headers = {"x-api-key": self.x_api_key}
        request_url = self.base_url + "enrichment"
        try:
            r = self.http.request("GET", request_url, fields=payload, headers=headers)
        except Exception as e:
            response_data["success"] = False
            logger.error(f"Customer '{customer.customer_id}' failed to retrieve enrichment data. Reason: {e.reason}. Message: {e._message}")
            return response_data
        if r.status == 200:
            social_handle = r.json()["social_handle"]
            response_data["social_handle"] = social_handle
            response_data["success"] = True
        else:
            error_message = r.json()["detail"]
            response_data["success"] = False
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
        try:
            r = self.http.request("POST", request_url, body=payload, headers=headers)
        except Exception as e:
            error_message = f"Customer '{customer.customer_id}' failed to submit data to API. Reason: {e.reason}. Message: {e._message}"
            response_data["success"] = False
            response_data["reason"] = error_message
            logger.error(error_message)
            return response_data
        if r.status != 200:
            error_message = r.json()["detail"]
            response_data["success"] = False
            response_data["reason"] = f"API Error. Status: {r.status}. Message: {error_message}"
            logger.error("Customer '%s' encountered API error. Message: %s", customer.customer_id, error_message)
        else:
            response = r.json()
            response_data["success"] = response["status"]
            response_data["reason"] = response["message"]

        return response_data