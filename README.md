# bKash Django Demo (No DRF)

A minimal Django project that integrates **bKash Tokenized Checkout** in sandbox, using classic Django views + templates.

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
export DJANGO_SETTINGS_MODULE=bkash_project.settings

# Set your sandbox credentials (replace placeholders)
export BKASH_APP_KEY=your_app_key
export BKASH_APP_SECRET=your_app_secret
export BKASH_USERNAME=your_username
export BKASH_PASSWORD=your_password
# Optional (default already set):
export BKASH_BASE_URL=https://tokenized.sandbox.bka.sh/v1.2.0-beta
export BKASH_CALLBACK_URL=http://127.0.0.1:8000/payments/callback/

python manage.py migrate
python manage.py runserver
```

Open: http://127.0.0.1:8000/payments/checkout/

## Notes

- Uses sessions to store `id_token` and `paymentID` temporarily.
- Stores logs in `PaymentLog` (SQLite).
- No DRF used. Pure Django.
- For production, change `SECRET_KEY`, set proper `ALLOWED_HOSTS`, and switch to live credentials.

## Troubleshooting
- If you see *No redirect URL returned*, ensure your sandbox merchant is set up for **tokenized checkout** and credentials are correct.
- Check console/logs in `PaymentLog` via Django Admin to see raw responses.


## Extras in v2
- `.env` support via **python-dotenv** (`cp .env.example .env` and fill in).
- Simple **shop + cart** using sessions: `/payments/shop/` → `/payments/cart/` → `/payments/checkout/`.
- **Sandbox tester** at `/payments/tester/` to quickly verify token acquisition.
- Health check at `/payments/ping/`.
- Minimal CSS at `/static/demo.css`.




<!-- 

	•	01770618575
	•	01929918378
	•	01619777282
	•	01619777283

	•	OTP: 123456
	•	PIN: 12121

 --># django-bkash
