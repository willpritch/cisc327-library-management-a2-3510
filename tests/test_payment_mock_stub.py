import pytest
from unittest.mock import Mock
from services.library_service import pay_late_fees, refund_late_fee_payment
from services.payment_service import PaymentGateway

@pytest.fixture
def stub_fee_ok(mocker):
    return mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"status": "ok", "fee": 10.0, "days_overdue": 3},
    )

@pytest.fixture
def stub_fee_zero(mocker):
    return mocker.patch(
        "services.library_service.calculate_late_fee_for_book",
        return_value={"status": "ok", "fee": 0.0, "days_overdue": 0},
    )

@pytest.fixture
def mock_gateway():
    return Mock(spec=PaymentGateway)

def test_pay_late_fees_success(stub_fee_ok, mock_gateway):
    mock_gateway.process_payment.return_value = {"status": "success", "transaction_id": "TX1"}
    ok, msg = pay_late_fees("123456", 1, mock_gateway)
    mock_gateway.process_payment.assert_called_once_with("123456", 10.0)
    assert ok and "successful" in msg

def test_pay_late_fees_declined(stub_fee_ok, mock_gateway):
    mock_gateway.process_payment.return_value = {"status": "declined"}
    ok, msg = pay_late_fees("123456", 1, mock_gateway)
    mock_gateway.process_payment.assert_called_once()
    assert not ok and "declined" in msg

def test_pay_late_fees_invalid_patron_no_call(mock_gateway):
    ok, msg = pay_late_fees("abc", 1, mock_gateway)
    mock_gateway.process_payment.assert_not_called()
    assert not ok and "Invalid patron ID" in msg

def test_pay_late_fees_zero_fee_no_call(stub_fee_zero, mock_gateway):
    ok, msg = pay_late_fees("123456", 1, mock_gateway)
    mock_gateway.process_payment.assert_not_called()
    assert not ok and "No late fee" in msg

def test_pay_late_fees_gateway_exception(stub_fee_ok, mock_gateway):
    mock_gateway.process_payment.side_effect = Exception("Network")
    ok, msg = pay_late_fees("123456", 1, mock_gateway)
    assert not ok and "Error:" in msg

def test_refund_success(mock_gateway):
    mock_gateway.refund_payment.return_value = {"status": "refund_success"}
    ok, msg = refund_late_fee_payment("TX123", 10.0, mock_gateway)
    mock_gateway.refund_payment.assert_called_once_with("TX123", 10.0)
    assert ok and "successful" in msg

def test_refund_invalid_txn(mock_gateway):
    ok, msg = refund_late_fee_payment("", 10.0, mock_gateway)
    mock_gateway.refund_payment.assert_not_called()
    assert not ok and "Invalid transaction" in msg

def test_refund_invalid_amount(mock_gateway):
    ok, msg = refund_late_fee_payment("TX123", -1.0, mock_gateway)
    mock_gateway.refund_payment.assert_not_called()
    assert not ok and "Invalid refund amount" in msg
