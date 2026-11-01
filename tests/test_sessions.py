import pytest

from sessions import add_to_cart, get_cart, remove_from_cart, save_session, sessions

# A customer ID that the sample data does not use, so real sessions are untouched.
TEST_CUSTOMER_ID = 999_999


@pytest.fixture(autouse=True)
def delete_test_session():
    sessions.delete_one({"customer_id": TEST_CUSTOMER_ID})
    yield
    sessions.delete_one({"customer_id": TEST_CUSTOMER_ID})


def test_save_session_creates_empty_cart():
    save_session(TEST_CUSTOMER_ID)

    assert get_cart(TEST_CUSTOMER_ID) == []


def test_adding_same_product_twice_increases_quantity():
    save_session(TEST_CUSTOMER_ID)
    add_to_cart(TEST_CUSTOMER_ID, 5, 2)
    add_to_cart(TEST_CUSTOMER_ID, 7, 1)
    add_to_cart(TEST_CUSTOMER_ID, 5, 1)

    assert get_cart(TEST_CUSTOMER_ID) == [
        {"product_id": 5, "quantity": 3},
        {"product_id": 7, "quantity": 1},
    ]


def test_remove_from_cart():
    add_to_cart(TEST_CUSTOMER_ID, 5, 2)
    add_to_cart(TEST_CUSTOMER_ID, 7, 1)

    remove_from_cart(TEST_CUSTOMER_ID, 5)

    assert get_cart(TEST_CUSTOMER_ID) == [{"product_id": 7, "quantity": 1}]


def test_get_cart_without_session_is_empty():
    assert get_cart(TEST_CUSTOMER_ID) == []
