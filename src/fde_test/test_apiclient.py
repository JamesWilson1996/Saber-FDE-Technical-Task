import unittest
from collections import namedtuple
from unittest.mock import patch, Mock

from apiclient import APIClient

class TestAPIClient(unittest.TestCase):
    @patch('apiclient.urllib3.PoolManager.request')
    def test_get_enrichment_data_success(self, mock_request):
        # Arrange
        api_client = APIClient()
        customer = Mock(email="test@example.com")
        mock_response = Mock(status=200)
        mock_response.json.return_value = {"social_handle": "handle123"}
        mock_request.return_value = mock_response
        
        # Act
        result = api_client.get_enrichment_data(customer)
        
        # Assert
        self.assertTrue(result["success"])
        self.assertEqual(result["social_handle"], "handle123")

    @patch('apiclient.urllib3.PoolManager.request')
    def test_get_enrichment_data_failure(self, mock_request):
        # Arrange
        api_client = APIClient()
        customer = Mock(email="test@example.com")
        mock_response = Mock(status=404)
        mock_response.json.return_value = {"detail": "Profile not found"}
        mock_request.return_value = mock_response
        
        # Act
        result = api_client.get_enrichment_data(customer)
        
        # Assert
        self.assertFalse(result["success"])

    @patch('apiclient.urllib3.PoolManager.request')
    def test_post_submission_success(self, mock_request):
        # Arrange
        api_client = APIClient()
        mock_response = Mock(status=200)
        mock_response.json.return_value = {"status": True, "message": None}
        mock_request.return_value = mock_response
        mock_tuple = namedtuple("Pandas", ("customer_id", "name", "email", "total_spend", "social_handle"))
        mock_customer = mock_tuple("123", "test", "test@example.com", 0, "handle123")

        # Act
        result = api_client.post_submission(mock_customer)

        # Assert
        self.assertTrue(result["success"])
        self.assertIsNone(result["reason"])

    @patch('apiclient.urllib3.PoolManager.request')
    def test_post_submission_200_fail(self, mock_request):
        # Arrange
        api_client = APIClient()
        mock_response = Mock(status=200)
        mock_response.json.return_value = {"status": "failure", "message": "Submission failed."}
        mock_request.return_value = mock_response
        mock_tuple = namedtuple("Pandas", ("customer_id", "name", "email", "total_spend", "social_handle"))
        mock_customer = mock_tuple("123", "test", "test@example.com", 0, "handle123")

        # Act
        result = api_client.post_submission(mock_customer)

        # Assert
        self.assertTrue(result["success"] == "failure")
        self.assertTrue(result["reason"] == "Submission failed.")

    @patch('apiclient.urllib3.PoolManager.request')
    def test_post_submission_fail(self, mock_request):
        # Arrange
        api_client = APIClient()
        mock_response = Mock(status=422)
        mock_response.json.return_value = {
            "detail": [
                {
                "loc": [
                    "string",
                    0
                ],
                "msg": "failed validation",
                "type": "validation"
                }
            ]
        }
        mock_request.return_value = mock_response
        mock_tuple = namedtuple("Pandas", ("customer_id", "name", "email", "total_spend", "social_handle"))
        mock_customer = mock_tuple("123", "test", "test@example.com", 0, "handle123")

        # Act
        result = api_client.post_submission(mock_customer)

        # Assert
        self.assertFalse(result["success"])
        self.assertIsNotNone(result["reason"])
    
if __name__ == '__main__':
    unittest.main()