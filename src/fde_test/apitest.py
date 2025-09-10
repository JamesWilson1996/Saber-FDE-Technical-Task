# test_apiclient.py
import unittest
from apiclient import APIClient, Retry
import requests_mock
import config

class MockCustomer:
    def __init__(self):
        self.customer_id = "customer123"
        self.name = "John Doe"
        self.email = "john.doe@example.com"
        self.total_spend = 500
        self.social_handle = "@johndoe"

class TestAPIClient(unittest.TestCase):
    def setUp(self):
        self.base_url = 'http://localhost:5000'
        self.x_api_key = "your_x_api_key_here"  # Replace with actual API key or use environment variable
        config.read_config.return_value = {"api_base_url": self.base_url}
        
        self.client = APIClient()
    
    @requests_mock.mock()
    def test_get_enrichment_data_success(self, mock_request):
        customer = MockCustomer()
        
        # Mock the API response
        mock_request.get(f"{self.base_url}/enrichment", json={
            "social_handle": customer.social_handle,
            "detail": "Enrichment data fetched successfully"
        })
        
        # Call the method
        result = self.client.get_enrichment_data(customer)
        
        # Assert the expected outcome
        self.assertTrue(result["success"])
        self.assertEqual(result["social_handle"], customer.social_handle)
    
    @requests_mock.mock()
    def test_get_enrichment_data_failure(self, mock_request):
        customer = MockCustomer()
        
        # Mock the API response to simulate a failure
        mock_request.get(f"{self.base_url}/enrichment", status_code=404, json={
            "detail": "No enrichment data found for customer"
        })
        
        # Call the method and assert it raises an exception
        with self.assertLogs(APIClient.__name__, level='ERROR') as caplog:
            result = self.client.get_enrichment_data(customer)
        
        # Assert error log message
        error_message = "API Error. Status: 404. Message: No enrichment data found for customer"
        self.assertIn(error_message, caplog.output[0])
    
    @requests_mock.mock()
    def test_post_submission_success(self, mock_request):
        customer = MockCustomer()
        
        # Mock the API response
        mock_request.post(f"{self.base_url}/submission", status_code=200)
        
        # Call the method
        result = self.client.post_submission(customer)
        
        # Assert the expected outcome
        self.assertTrue(result["success"])
    
    @requests_mock.mock()
    def test_post_submission_failure(self, mock_request):
        customer = MockCustomer()
        
        # Mock the API response to simulate a failure
        mock_request.post(f"{self.base_url}/submission", status_code=500, json={
            "detail": "Error processing submission"
        })
        
        # Call the method and assert it raises an exception
        with self.assertLogs(APIClient.__name__, level='ERROR') as caplog:
            result = self.client.post_submission(customer)
        
        # Assert error log message
        error_message = "API Error. Status: 500. Message: Error processing submission"
        self.assertIn(error_message, caplog.output[0])

if __name__ == '__main__':
    unittest.main()