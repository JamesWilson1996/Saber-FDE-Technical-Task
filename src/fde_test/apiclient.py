import json
import os
import urllib3

from urllib3.util.retry import Retry

import config

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
        payload = {"email": customer.email}
        headers = {"x-api-key": self.x_api_key}
        request_url = self.base_url + "enrichment"
        r = self.http.request("GET", request_url, fields=payload, headers=headers)
        return r
    
    def post_submission(self, customer):
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
        return r