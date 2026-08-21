# 📄 **Pharmacy Management System — Requirements Document**

## **1. Project Overview**

The Pharmacy Management System will be a **web-based application** designed for a **single pharmacy**, covering full workflows including purchases, inventory, sales, batch tracking, customers, and analytics.

Mobile app will be developed later using the same backend APIs.

---

# **2. System Goals**

* Automate pharmacy operations
* Track medicine inventory accurately
* Track batches and expiry dates
* Speed up billing and reduce errors
* Maintain purchase & supplier records
* Generate professional reports
* Provide secure multi-user access

---

# **3. User Roles**

### **1. Admin**

* Full access to all modules
* Manage users, roles, pharmacy settings

### **2. Pharmacist**

* Manage medicines, batches, inventory
* Handle sales and approvals

### **3. Cashier**

* Perform sales
* View past invoices

### **4. Accountant (optional)**

* View financial reports
* Track purchases and expenses

---

# **4. Core Modules & Features**

## **4.1 Authentication & Security**

* Login with email/password
* JWT-based authentication
* Role-based access control (RBAC)
* Password reset
* Activity logs (optional)

---

## **4.2 Dashboard**

Admin and pharmacist dashboard with:

* Total medicines
* Low stock items
* Near-expiry items
* Daily sales summary
* Today’s total purchase
* Top selling items (graph)

---

## **4.3 Medicine Management**

### **Medicine Information**

* Medicine name
* Generic name
* Brand name
* Category (tablet, syrup, injection, etc.)
* Unit type (strip, bottle, piece, mL)
* Strength (500mg, etc.)
* Description
* Barcode/code (optional)
* Medicine image (optional)

### **Medicine Operations**

* Create / update / delete medicine
* View stock by batch
* Search medicine by name, generic, or brand
* Mark a medicine as inactive

---

## **4.4 Batch / Lot Management**

### **Batch Details**

* Batch/Lot number
* Expiry date
* Manufacturing date (optional)
* Purchase price
* Selling price / MRP
* Available quantity
* Supplier reference

### **Batch Features**

* Track stock PER batch
* Deduct stock from nearest-expiry batch (FIFO)
* Expiry alerts in dashboard
* Mark expired stock

---

## **4.5 Supplier Management**

* Add/update suppliers
* Supplier name
* Contact person
* Phone
* Email
* Address
* Past purchase history

---

## **4.6 Purchase Management**

### **Purchase Entry**

* Create purchase invoice
* Add multiple medicines
* Add batch details for each medicine
* Auto-update stock
* Supplier assignment
* Invoice upload (optional)

### **Purchase Operations**

* Edit purchase
* Return purchase items
* View purchase history
* Search purchases by supplier/date

---

## **4.7 Inventory Management**

### **Inventory Features**

* Real-time stock
* Stock by batch
* Low stock list
* Near-expiry list
* Expired stock list
* Stock adjustment (admin-only)

---

## **4.8 POS (Billing & Sales)**

### **Sales Workflow**

* Fast medicine search
* Add multiple medicines to cart
* Auto price fetch
* Adjust quantity
* Discount (flat or percentage)
* Auto stock deduction by batch
* Payment type (cash, card, digital)
* Generate invoice (print or PDF)

### **Invoice**

* Invoice number
* Customer details (optional)
* Line items with price, qty, batch
* Total, discount, grand total

---

## **4.9 Customer Management**

* Add a customer
* Name, phone
* Purchase history
* Search customers

Optional: Loyalty points (future)

---

## **4.10 Reporting & Analytics**

### **Sales Reports**

* Daily sales
* Monthly sales
* Sales by medicine
* Sales by category
* Top selling items

### **Inventory Reports**

* Current stock
* Low stock
* Expired items
* Near-expiry items

### **Purchase Reports**

* Purchases by supplier
* Monthly purchase
* Return items

### **Profit Reports**

* Profit per sale
* Monthly profit
* Gross margin

### **Export Options**

* PDF
* CSV

---

## **4.11 Settings**

* Pharmacy name & details
* Tax/VAT settings
* Currency
* Logo upload
* User role permissions

---

# **5. Technical Requirements**

## **Frontend**

* React
* Tailwind CSS
* Responsive UI

## **Backend**

* FastAPI (Python)
* REST APIs
* JWT authentication
* API Documentation (Swagger)

## **Database**

* PostgreSQL
* Entities: users, medicines, batches, suppliers, purchases, sales, inventory, reports

## **Deployment**

* Initially EC2
* Later plan: Docker → ECS
* S3 for static files
* CloudWatch for logs

---

# **6. Non-Functional Requirements**

* Should handle 10k–50k medicine rows
* 99% uptime target
* Secure password hashing
* Fast search (<200ms)
* Daily backup (DB snapshot)
* Audit logs for admin

---

# **7. Future Enhancements (Optional)**

* Barcode scanner support
* Mobile app (React Native / Flutter)
* Prescription OCR