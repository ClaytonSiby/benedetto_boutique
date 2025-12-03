# Stripe Payment Integration Guide

## 🚀 Quick Start (POC/Development)

### 1. **Create Stripe Account**

1. Go to [https://dashboard.stripe.com/register](https://dashboard.stripe.com/register)
2. Sign up with your email
3. Complete the account setup (no bank account needed for testing!)

### 2. **Get Your Test API Keys**

1. In Stripe Dashboard, click **Developers** → **API Keys**
2. Toggle to **Test Mode** (top right)
3. Copy your keys:
   - **Publishable key**: `pk_test_...` (used in frontend)
   - **Secret key**: `sk_test_...` (used in backend)

### 3. **Add Keys to Your Backend `.env`**

Add these lines to `/backend/.env`:

```bash
# Stripe Payment Settings (Test Mode)
STRIPE_SECRET_KEY=sk_test_YOUR_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_PUBLISHABLE_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE
STRIPE_CURRENCY=ZAR
```

**Note**: Leave `STRIPE_WEBHOOK_SECRET` empty for now (we'll set it up later)

### 4. **Test Your Setup**

Start your backend:
```bash
cd backend
uvicorn app.main:app --reload
```

Test the config endpoint:
```bash
curl http://localhost:8000/api/v1/payments/config
```

You should see:
```json
{
  "publishableKey": "pk_test_...",
  "currency": "zar"
}
```

---

## 💰 Pricing & Free Tier

### **Test Mode (POC/Development)**
✅ **100% FREE**
- Unlimited test transactions
- All features enabled (cards, bank transfers, etc.)
- Test webhooks
- Full API access
- No credit card required
- No time limit

### **Production Mode** (When you go live)
**Transaction Fees in South Africa:**
- **2.9% + ZAR 2.00** per successful card charge
- **No monthly fees**
- **No setup fees**
- Only pay for successful transactions

**Example:**
- Order: R 1,000
- Stripe Fee: R 31 (2.9% + R 2)
- You receive: R 969

---

## 🏦 Linking Bank Account (Production Only)

**Note**: You DON'T need a bank account for testing/POC!

### When You're Ready to Go Live:

1. **Complete Stripe Account Setup**
   - Go to **Settings** → **Business Profile**
   - Fill in business details
   - Verify your identity

2. **Add Bank Account**
   - Go to **Settings** → **Bank Accounts and Scheduling**
   - Click **Add Bank Account**
   - Enter your South African bank details:
     - Account holder name
     - Account number
     - Bank name
     - Branch code

3. **Verify Bank Account**
   - Stripe will make 2 small deposits (e.g., R0.32 and R0.45)
   - Check your bank statement
   - Enter the amounts in Stripe Dashboard to verify

4. **Set Payout Schedule**
   - Daily (default): Funds arrive in 2 business days
   - Weekly: Funds arrive every week
   - Monthly: Funds arrive every month

---

## 🔧 Frontend Integration

### Install Stripe.js in your frontend:

```bash
cd frontend
npm install @stripe/stripe-js @stripe/react-stripe-js
```

### Create Checkout Component:

```typescript
// src/components/StripeCheckout.tsx
'use client';

import { useEffect, useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  PaymentElement,
  useStripe,
  useElements,
} from '@stripe/react-stripe-js';
import { api } from '@/lib/api';

// Initialize Stripe
let stripePromise: Promise<any> | null = null;

const getStripe = async () => {
  if (!stripePromise) {
    const { data } = await api.get('/api/v1/payments/config');
    stripePromise = loadStripe(data.publishableKey);
  }
  return stripePromise;
};

function CheckoutForm({ orderId, onSuccess }: { orderId: string; onSuccess: () => void }) {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!stripe || !elements) return;

    setLoading(true);
    setError(null);

    try {
      const { error: submitError } = await stripe.confirmPayment({
        elements,
        confirmParams: {
          return_url: `${window.location.origin}/orders/${orderId}/success`,
        },
      });

      if (submitError) {
        setError(submitError.message || 'Payment failed');
      } else {
        onSuccess();
      }
    } catch (err: any) {
      setError(err.message || 'Payment failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <PaymentElement />
      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-600 text-sm">
          {error}
        </div>
      )}
      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {loading ? 'Processing...' : 'Pay Now'}
      </button>
    </form>
  );
}

export default function StripeCheckout({
  orderId,
  onSuccess,
}: {
  orderId: string;
  onSuccess: () => void;
}) {
  const [clientSecret, setClientSecret] = useState<string | null>(null);
  const [stripePromise, setStripePromise] = useState<any>(null);

  useEffect(() => {
    // Load Stripe
    getStripe().then(setStripePromise);

    // Create payment intent
    api
      .post(`/api/v1/payments/create-payment-intent?order_id=${orderId}`)
      .then((res) => {
        setClientSecret(res.data.clientSecret);
      })
      .catch((err) => {
        console.error('Failed to create payment intent:', err);
      });
  }, [orderId]);

  if (!clientSecret || !stripePromise) {
    return (
      <div className="flex items-center justify-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <Elements stripe={stripePromise} options={{ clientSecret }}>
      <CheckoutForm orderId={orderId} onSuccess={onSuccess} />
    </Elements>
  );
}
```

### Use in Your Checkout Page:

```typescript
// src/app/checkout/page.tsx
'use client';

import { useRouter } from 'next/navigation';
import StripeCheckout from '@/components/StripeCheckout';

export default function CheckoutPage() {
  const router = useRouter();
  const orderId = 'your-order-id'; // Get from cart/order creation

  const handleSuccess = () => {
    router.push(`/orders/${orderId}/success`);
  };

  return (
    <div className="max-w-2xl mx-auto py-12 px-4">
      <h1 className="text-3xl font-bold mb-8">Complete Your Payment</h1>
      <StripeCheckout orderId={orderId} onSuccess={handleSuccess} />
    </div>
  );
}
```

---

## 🧪 Testing Your Integration

### Test Card Numbers (Use in Test Mode):

| Card Number | Scenario |
|-------------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Card declined |
| `4000 0000 0000 9995` | Insufficient funds |
| `4000 0025 0000 3155` | 3D Secure authentication required |

**Details for all test cards:**
- Expiry: Any future date (e.g., 12/25)
- CVC: Any 3 digits (e.g., 123)
- Postal Code: Any valid code

### Test Your Payment Flow:

1. Create an order in your app
2. Go to checkout
3. Use test card `4242 4242 4242 4242`
4. Complete the payment
5. Check in Stripe Dashboard → **Payments** to see the test payment

---

## 🔔 Setting Up Webhooks (For Production)

Webhooks notify your backend when payments succeed/fail.

### Local Development (Using Stripe CLI):

1. **Install Stripe CLI**:
   ```bash
   brew install stripe/stripe-cli/stripe
   ```

2. **Login to Stripe**:
   ```bash
   stripe login
   ```

3. **Forward webhooks to your local backend**:
   ```bash
   stripe listen --forward-to localhost:8000/api/v1/payments/webhook
   ```

4. **Copy the webhook secret** (starts with `whsec_...`) and add to `.env`:
   ```bash
   STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
   ```

### Production Setup:

1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add Endpoint**
3. Enter your webhook URL: `https://yourdomain.com/api/v1/payments/webhook`
4. Select events to listen for:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
5. Copy the **Signing Secret** and add to production `.env`

---

## 📊 Monitoring Payments

### Stripe Dashboard:
- **Payments**: See all transactions
- **Customers**: View customer details
- **Disputes**: Handle chargebacks
- **Reports**: Download financial reports

### Your Database:
All payments are stored in your `payments` table with:
- Transaction ID (Stripe Payment Intent ID)
- Status (pending, completed, failed)
- Amount and currency
- Order link

---

## 🛡️ Security Best Practices

1. **Never expose secret keys** in frontend code
2. **Use HTTPS** in production
3. **Verify webhook signatures** (already implemented)
4. **Store minimal payment data** (use Stripe's hosted data)
5. **Enable 3D Secure** for extra protection
6. **Monitor for fraud** in Stripe Dashboard

---

## 🚀 Going Live Checklist

- [ ] Complete Stripe account verification
- [ ] Link bank account and verify
- [ ] Switch from Test Mode to Live Mode in Dashboard
- [ ] Update `.env` with live API keys (starts with `pk_live_` and `sk_live_`)
- [ ] Set up production webhooks
- [ ] Test live payment with real card (R1 test)
- [ ] Enable Radar (Stripe's fraud detection) - FREE!
- [ ] Set up payout schedule
- [ ] Test refund flow

---

## 📞 Support

- **Stripe Documentation**: https://stripe.com/docs
- **Stripe Support**: https://support.stripe.com
- **Test Mode Dashboard**: https://dashboard.stripe.com/test
- **API Reference**: https://stripe.com/docs/api

---

## 🎉 Summary

**For POC/Testing (RIGHT NOW):**
1. Create Stripe account
2. Get test API keys from Dashboard
3. Add to backend `.env`
4. Use test cards for payments
5. **Cost: R0** ✅

**For Production (LATER):**
1. Complete business verification
2. Link bank account
3. Switch to live keys
4. Set up webhooks
5. **Cost: 2.9% + R2 per transaction**

**Your backend is already integrated! Just add the API keys and start testing! 🎊**
