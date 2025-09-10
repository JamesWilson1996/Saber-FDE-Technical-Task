import logging
import numpy as np

from pathlib import Path

import config
from apiclient import APIClient
from databaseclient import SQLiteConnection
from logger import setup_logging

logger = logging.getLogger(__name__)

def main():
    setup_logging()
    config_data = config.read_config()
    api_client = APIClient()
    db_client = SQLiteConnection(config_data["db_source"], uri=config_data["db_uri"])

    #Build Customer DataFrame from DB
    customer_df = db_client.query_customer_spend(city=config_data["city"], date_time=config_data["date_time"])
    customer_df.insert(4, "social_handle", None)
    customer_df.insert(5, "success", None)
    customer_df.insert(6, "reason", None)
    customer_df["total_spend"] = np.floor(100 * customer_df["total_spend"]) / 100 #Round down to 2 decimal places... Encountered scenarios where many decimal places were observed.
    
    #Enrich Customer Data
    logger.info("Starting enrichment...")
    for customer in customer_df.itertuples():
        if not customer.email:
            customer_df.loc[customer.Index, ["success", "reason"]] = [False, "Missing email"]
            logger.error(f"Customer '{customer.customer_id}' missing email.")
        else:
            r = api_client.get_enrichment_data(customer)
            if r.status == 200:
                social_handle = r.json()["social_handle"]
                customer_df.loc[customer.Index, ["social_handle", "success"]] = [social_handle, True]
            else:
                error_message = r.json()["detail"]
                customer_df.loc[customer.Index, ["success", "reason"]] = [False, f"API Error. Status: {r.status}. Message: {error_message}"]
                logger.error("Customer '%s' encountered API error. Message: %s", customer.customer_id, error_message)

    #Submit Enriched Data
    logger.info("Starting submissions...")
    for customer in customer_df.loc[customer_df["success"] == True].itertuples():
        r = api_client.post_submission(customer)
        if r.status != 200:
            error_message = r.json()["detail"]
            customer_df.loc[customer.Index, ["success", "reason"]] = [False, f"API Error. Status: {r.status}. Message: {error_message}"]
            logger.error("Customer '%s' encountered API error. Message: %s", customer.customer_id, error_message)

    logger.info("Submissions Complete... Writing output file...")
    (Path.cwd() / config_data["output_dir"]).mkdir(exist_ok=True)
    file_path = f"{config_data["output_dir"]}{config_data["output_file"]}"
    customer_df.to_csv(file_path)
    logger.info("Process Complete")

if __name__ == "__main__":
    main()