import pytest
from unittest.mock import patch, MagicMock
from shop.tasks import send_order_notification_task
from shop.factories import OrderFactory
from users.factories import UserFactory

@pytest.mark.django_db
class TestOrderTasks:
    @patch('requests.post')
    def test_send_notification_success(self, mock_post):
        # Setup
        user = UserFactory(telegram_id=123456789)
        order = OrderFactory(user=user, total_price=500)
        
        # Configure mock response
        mock_post.return_value.status_code = 200
        
        # Execute (call the function directly, not .delay() for unit test)
        send_order_notification_task(order.id)
        
        # Assert
        assert mock_post.called
        args, kwargs = mock_post.call_args
        assert kwargs['json']['chat_id'] == 123456789
        assert "500" in kwargs['json']['text']

    @patch('requests.post')
    def test_send_notification_no_telegram_id(self, mock_post):
        user = UserFactory(telegram_id=None)
        order = OrderFactory(user=user)
        
        send_order_notification_task(order.id)
        
        assert not mock_post.called

    @patch('requests.post')
    def test_send_notification_retry_on_failure(self, mock_post):
        user = UserFactory(telegram_id=123456789)
        order = OrderFactory(user=user)
        
        # Mock a connection error or 500
        mock_post.side_effect = Exception("Telegram API Down")
        
        # We test that it raises an exception (Celery's autoretry will catch it)
        with pytest.raises(Exception):
            send_order_notification_task(order.id)
