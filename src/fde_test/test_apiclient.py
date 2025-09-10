import unittest
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
        self.assertEqual(result["reason"], "API Error. Status: 404. Message: Profile not found")

    #TODO ADD TESTS FOR post_submission
    
if __name__ == '__main__':
    unittest.main()