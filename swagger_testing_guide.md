# Swagger API Testing Guide: Step-by-Step

Follow this guide to test the full "Online Dukan" shopping cycle directly from the Swagger UI at `/api/schema/swagger-ui/`.

---

## 🔑 Step 0: Authentication (Users & Auth)

### 1. Register a User
*   **Endpoint**: `POST /api/users/register/`
*   **Action**: Click "Try it out".
*   **Data**: Enter a unique `username`, `email`, and `password`.
*   **Result**: You will get an `access` and `refresh` token in the response.

### 2. Login (Optional)
*   **Endpoint**: `POST /api/users/login/`
*   **Data**: Enter the credentials you just created.
*   **Result**: Copy the `access` token.

### 3. Authorize in Swagger
*   Scroll to the top and click the green **Authorize** button.
*   Enter: `Bearer <your_access_token>`
*   Click **Authorize** then **Close**. Now all requests will be authenticated.

---

## 📦 Step 1: Catalog (Browse Products)

### 1. View Categories
*   **Endpoint**: `GET /api/shop/categories/`
*   **Action**: List available categories. Note an `id` for filtering.

### 2. View Products
*   **Endpoint**: `GET /api/shop/products/`
*   **Action**: Browse available products. Note the `id` and check the `stock` amount.

---

## 🛒 Step 2: Cart (Add Items)

### 1. Add Product to Cart
*   **Endpoint**: `POST /api/shop/cart/add/`
*   **Data**:
    ```json
    {
      "product_id": 1, 
      "quantity": 2
    }
    ```
*   **Validation**: Ensure `quantity` does not exceed the `stock` found in Step 1.

### 2. Check Cart Content
*   **Endpoint**: `GET /api/shop/cart/`
*   **Action**: Verify that the product is there and note the item `id` (this is the CartItem ID, used in checkout).

---

## 💳 Step 3: Checkout (Place Order)

### 1. Checkout
*   **Endpoint**: `POST /api/shop/orders/checkout/`
*   **Data**:
    ```json
    {
      "address": "123 Green St, Nukus",
      "cart_item_ids": [1] 
    }
    ```
*   **Important**: Use the item IDs from your cart response (Step 2.2).
*   **Result**: Your cart will be cleared, and a new Order will be created.

---

## ⭐ Step 4: Reviews (Feedback)

### 1. Leave a Review
*   **Endpoint**: `POST /api/shop/reviews/`
*   **Data**:
    ```json
    {
      "product": 1,
      "rating": 5,
      "comment": "Perfect service!"
    }
    ```
*   **Verification**: The `user_name` will be automatically populated from your authenticated session.

---

### 💡 Pro Tips
*   **JWT Expiry**: If you get a `401 Unauthorized`, re-login and update the **Authorize** token.
*   **Admin Tasks**: Certain endpoints (like creating products) require an admin user (`is_staff=True`).
