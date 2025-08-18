# 🏥 DENTAL RESCUE BOT - COMPLETE MEMBERSHIP SYSTEM OVERVIEW

## 📊 **WHERE EVERYTHING IS STORED** - Your Complete Control Center

### **DATABASE COLLECTIONS:**

#### **1. `practices` Collection** - **Master Practice Management**
```json
{
  "id": "practice-uuid",
  "name": "Dr. Smith's Dental Practice",
  "email": "admin@practice.com",
  "phone": "(555) 123-4567",
  "address": {
    "street": "123 Main St",
    "city": "Anytown", 
    "state": "CA",
    "zipCode": "12345"
  },
  "subscription": {
    "status": "trial_pending_payment|trial|active|cancelled|inactive",
    "plan": "basic",
    "trialEndsAt": "2025-02-15T00:00:00Z",
    "chargeDate": "2025-02-15T00:00:00Z",
    "monthlyAmount": 49.0,
    "stripeCustomerId": "cus_stripe_customer_id",
    "stripeSubscriptionId": "sub_stripe_subscription_id"
  },
  "isActive": true,
  "createdAt": "2025-01-01T00:00:00Z"
}
```

#### **2. `users` Collection** - **All User Accounts & Passwords**
```json
{
  "id": "user-uuid", 
  "email": "admin@practice.com",
  "password": "$2b$12$hashedPasswordHere",  // bcrypt hashed - YOU CAN RESET THIS
  "firstName": "John",
  "lastName": "Smith",
  "role": "practice_admin|patient",
  "practiceId": "links-to-practice-id",
  "isActive": true,
  "loginCount": 25,
  "lastLoginAt": "2025-01-15T10:30:00Z",
  "createdAt": "2025-01-01T00:00:00Z"
}
```

#### **3. `payment_transactions` Collection** - **All Payment History**
```json
{
  "id": "transaction-uuid",
  "session_id": "stripe_checkout_session_id", 
  "practice_id": "practice-uuid",
  "amount": 49.0,
  "currency": "usd",
  "payment_status": "pending|paid|failed|refunded",
  "stripe_status": "open|complete|expired",
  "created_at": "2025-01-01T00:00:00Z"
}
```

#### **4. `payment_setups` Collection** - **Credit Card Authorization Tracking**
```json
{
  "id": "setup-uuid",
  "practice_id": "practice-uuid",
  "session_id": "stripe_session_id",
  "purpose": "payment_method_setup",
  "amount": 0.50,  // Authorization amount (refunded)
  "status": "pending|completed|failed"
}
```

#### **5. `procedures` Collection** - **Post-Operative Library** ✅ **FULLY STORED**
- **80+ complete dental procedures** extracted from your PDFs
- **All data stored in your database** - no external dependencies
- Includes: instructions, warnings, diet restrictions, medications, timelines

#### **6. `admin_actions` Collection** - **Your Management Activity Log**
```json
{
  "admin_email": "admin@theoncallbot.com",
  "practice_id": "practice-uuid",
  "action": "cancel_subscription|extend_trial|reset_password",
  "reason": "Non-payment",
  "timestamp": "2025-01-01T00:00:00Z"
}
```

---

## 🔐 **PASSWORD MANAGEMENT - COMPLETE ACCESS**

### **How Passwords Work:**
1. **Practice Admin Registration:** They set password during signup
2. **Patient Invites:** Temporary passwords generated, they set real password on first login
3. **Password Storage:** bcrypt hashed in `users.password` field
4. **Your Access:** You can reset ANY password through admin dashboard

### **Admin Password Reset Capability:**
```
POST /api/admin/reset-password
{
  "user_id": "user-uuid",
  "new_password": "newpassword123"
}
```

---

## 💳 **CREDIT CARD & PAYMENT FLOW** - **CARD REQUIRED UPFRONT**

### **NEW Registration Process:**
```
1. Practice fills registration form
2. ⚠️  CREDIT CARD REQUIRED immediately 
3. $0.50 authorization charge (refunded)
4. Trial activated for 15 days
5. Automatic $49 charge on day 15
6. Monthly billing continues
```

### **Payment Timeline:**
- **Day 0:** Registration + Credit card setup ($0.50 auth, refunded)
- **Day 1-15:** Full trial access with card on file  
- **Day 15:** First $49 charge automatically processed
- **Day 45, 75, etc.:** Monthly $49 charges continue

### **If Payment Fails:**
- Account automatically deactivated
- Practice loses access
- Admin dashboard shows "Payment Failed" status

---

## 🎛️ **YOUR ADMIN DASHBOARD** - **Complete Control**

### **Login Access:**
```
POST /api/admin/login
{
  "email": "admin@theoncallbot.com",
  "password": "your-super-admin-password-123"
}
```
⚠️ **CHANGE THIS PASSWORD in `/app/backend/routes/admin.py` line 21**

### **Dashboard Features:**

#### **📈 Revenue Overview:**
- Total practices: 156
- Active subscriptions: 89  
- Monthly revenue: $4,361
- Failed payments: 3

#### **🏥 Practice Management:**
- View all practices with search/filter
- See subscription status, trial dates, payment history
- Cancel accounts for non-payment
- Extend trials manually
- Deactivate/reactivate accounts

#### **👥 User Management:**
- View all users for any practice
- Reset passwords instantly
- See login activity and counts
- Deactivate individual users

#### **💰 Payment Management:**
- View all transactions across all practices
- See failed payments and retry attempts
- Refund payments when needed
- Track authorization charges

#### **📊 Admin Actions:**
```
GET /api/admin/practices              // All practices
GET /api/admin/payments               // All payments  
POST /api/admin/manage-practice       // Cancel/activate accounts
POST /api/admin/reset-password        // Reset any password
GET /api/admin/users/{practice_id}    // All users in practice
```

---

## 🚨 **MEMBERSHIP CANCELLATION - FOR NON-PAYMENT**

### **Automatic Process:**
1. **Payment fails** on monthly charge date
2. **Stripe webhook** notifies your system
3. **Account automatically deactivated** 
4. **Practice loses access** immediately
5. **Status changed** to "cancelled" or "inactive"

### **Manual Cancellation (Your Control):**
```
POST /api/admin/manage-practice
{
  "practice_id": "practice-uuid",
  "action": "cancel_subscription",
  "reason": "Non-payment - 3 failed attempts"
}
```

### **What Happens When Cancelled:**
- `practices.isActive` → `false`
- `practices.subscription.status` → `cancelled`
- All users in practice: `users.isActive` → `false`
- Practice admin cannot log in
- Patients lose access to notes

---

## 🔍 **FINDING SPECIFIC DATA**

### **To Find a Practice's Payment Info:**
```bash
# MongoDB query to find practice payment status
db.practices.findOne({"email": "practice@email.com"})
db.payment_transactions.find({"practice_id": "practice-uuid"})
```

### **To See All Failed Payments:**
```bash
db.payment_transactions.find({"payment_status": "failed"})
```

### **To Find User Password (hashed):**
```bash
db.users.findOne({"email": "user@email.com"}, {"password": 1})
```

---

## 🎯 **NEXT STEPS TO COMPLETE**

### **1. Frontend Payment Integration** 
- Modify registration form to collect credit card
- Add Stripe Elements for secure card input
- Handle payment setup success/failure

### **2. Admin Dashboard Frontend**
- Build React admin interface
- Connect to admin API endpoints  
- Add practice management tools

### **3. Automated Billing System**
- Background job to process monthly charges
- Email notifications for payment failures
- Automatic account deactivation

### **4. Trial Management**  
- Email notifications before trial expires
- Payment retry logic for failed charges
- Grace period handling

---

## 📞 **ADMIN DASHBOARD ACCESS**

**Your Admin Login:**
- URL: `https://your-domain.com/admin`
- Email: `admin@theoncallbot.com` 
- Password: `your-super-admin-password-123` ⚠️ **CHANGE THIS**

**Admin Capabilities:**
- ✅ View all practices and users
- ✅ Cancel subscriptions for non-payment  
- ✅ Reset any user password
- ✅ Extend trial periods
- ✅ View all payment transactions
- ✅ Track revenue and statistics
- ✅ Manual account activation/deactivation

**Everything is stored in YOUR database. You have complete control over all user data, passwords, payments, and practice management.**