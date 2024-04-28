# Vendor Management System 

This is a Vendor Management System built using Django and Django REST Framework. It allows you to manage vendor profiles, track purchase orders, and calculate vendor performance metrics.

## Setup Instructions

1. Clone the Repository
git clone https://github.com/yogesh-bhandari07/VMS.git cd VMS

2. Create a Virtual Environment (Optional but Recommended)
python3 -m venv venv source venv/bin/activate # On Windows, use venv\Scripts\activate


3. Install Dependencies

pip install -r requirements.txt
4. Set Up Database

python manage.py migrate

5. Run the Development Server

python manage.py runserver



## API Endpoints

### Authentication

Token-based authentication is required for API endpoints. Obtain a token by sending a POST request to `/api/token/` with username and password in the request body. Use the obtained token as a Bearer token in the Authorization header for subsequent requests.

### Vendor Management

- `POST /api/vendors/`: Create a new vendor.
- `GET /api/vendors/`: List all vendors.
- `GET /api/vendors/{vendor_id}/`: Retrieve a specific vendor's details.
- `PUT /api/vendors/{vendor_id}/`: Update a vendor's details.
- `DELETE /api/vendors/{vendor_id}/`: Delete a vendor.

### Purchase Order Tracking

- `POST /api/purchase_orders/`: Create a purchase order.
- `GET /api/purchase_orders/`: List all purchase orders with an option to filter by vendor.
- `GET /api/purchase_orders/{po_id}/`: Retrieve details of a specific purchase order.
- `PUT /api/purchase_orders/{po_id}/`: Update a purchase order.
- `DELETE /api/purchase_orders/{po_id}/`: Delete a purchase order.

### Vendor Performance Evaluation

- `GET /api/vendors/{vendor_id}/performance/`: Retrieve a vendor's performance metrics.

### Additional Endpoints

- `POST /api/purchase_orders/{po_id}/acknowledge`: Endpoint for vendors to acknowledge purchase orders.

## Testing with Postman

Import the provided Postman collection (`Vendor_Management_System.postman_collection.json`) into your Postman application. Use the collection to interact with the API endpoints. Make sure to obtain a JWT token for authentication before accessing protected endpoints.
