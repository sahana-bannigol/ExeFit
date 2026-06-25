# Sports Park Fitness Platform

A Web3-integrated fitness management platform built with Django and Ethereum smart contracts. Members can purchase gym memberships via MetaMask, log workouts, earn ERC20 reward tokens, and book fitness activities — all tracked through a traditional web interface backed by on-chain transactions.

---

## Features

- **Blockchain Membership Payments** — Purchase a yearly gym membership by sending 0.05 ETH via MetaMask
- **ERC20 Reward Tokens** — Earn tokens automatically when you complete 4+ workouts in a week
- **Location-Based Check-In** — GPS-verified check-ins using the browser Geolocation API (within 500m of the gym)
- **Activity Booking** — Browse and book gym activities (Gym, Yoga, Pilates, Dance)
- **Dashboard** — View membership status, upcoming bookings, and weekly workout progress
- **On-Chain Audit Trail** — Every membership purchase and token reward is recorded with an Ethereum transaction hash

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 3.1.3 |
| Database | SQLite |
| Blockchain | Ethereum (via Infura) |
| Web3 Library (backend) | web3.py |
| Web3 Library (frontend) | Web3.js v1.7.4 / v1.10.0 |
| Wallet | MetaMask |
| Smart Contracts | Solidity (ERC20 + custom gym logic) |

---

## Smart Contracts

The platform interacts with four deployed Ethereum contracts:

| Contract | Address | Purpose |
|---|---|---|
| Membership Contract | `0xd1ad0048bf7bd6e1c41ef8174f37266f762790f9` | Handles `buyMembership()` (0.05 ETH) and tracks expiry |
| Workout Rewards Contract | `0xd9145CCE52D386f254917e481eB44e9943F39138` | Logs workouts and triggers weekly reward distribution |
| ERC20 Token Contract | `0x528e2dc6f4722e74c06b10efa0e624688138f4a8` | Reward token with `mint()`, `transfer()`, `approve()` |
| Gym Token Management | `0x2CD6D30a792F965065D955330fD0189778e9420a` | Extended token management: tracks member status and totals |

All contract ABIs are embedded in the relevant HTML templates and interact through the connected MetaMask wallet.

---

## Project Structure

```
sports_park/
├── ExeFit/                     # Main Django application
│   ├── migrations/             # Database migrations
│   ├── static/                 # CSS stylesheets
│   ├── templates/              # HTML templates
│   │   ├── home.html
│   │   ├── dashboard.html
│   │   ├── membership.html     # Web3 membership purchase
│   │   ├── rewards.html        # Token reward management
│   │   ├── send_tokens.html    # Admin token minting
│   │   ├── checkin.html        # GPS check-in
│   │   └── activities.html     # Activity booking
│   ├── models.py               # Data models
│   ├── views.py                # View logic
│   └── urls.py                 # URL routing
├── sports_park/                # Django project config
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── manage.py
└── db.sqlite3
```

---

## Data Models

- **UserProfile** — Extends Django's User; stores membership dates and check-in count
- **Membership** — Membership record with price, duration, and Ethereum tx hash
- **Activity** — Fitness class types (name, price, duration)
- **Booking** — Links users to booked activities with date/time and status
- **Attendance** — Check-in records with GPS coordinates
- **Reward** — Tracks weekly workout count and whether a reward was earned (threshold: 4 workouts/week)
- **SmartContractExecution** — Audit log of every on-chain transaction

---

## Prerequisites

- Python 3.7 or higher
- [MetaMask](https://metamask.io/) browser extension (connected to Ethereum mainnet)
- ETH in your wallet for membership purchases (0.05 ETH)

---

## Installation & Setup

### 1. Clone the repository

```bash
git clone <repository-url>
cd sports_park
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install django==3.1.3 web3
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. Create an admin account

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The app will be available at `http://localhost:8000`.

---

## Usage

### Register & Log In

1. Go to `http://localhost:8000/register/` to create an account.
2. Log in at `http://localhost:8000/login/`.

### Purchase a Membership

1. Navigate to **Membership** from the dashboard.
2. Connect your MetaMask wallet.
3. Confirm the transaction (0.05 ETH). The membership status updates on-chain and in the database.

### Check In

1. Go to **Check In** and allow the browser to access your location.
2. If you are within 500m of the gym (50.7347323, -3.5285962), the check-in is recorded.
3. After 4 weekly check-ins you become eligible for reward tokens.

### Book Activities

1. Browse available classes under **Activities**.
2. Click **Book** on any activity. Manage or cancel bookings from your dashboard.

### Rewards

1. Go to **Rewards** to check your weekly workout progress and earned tokens.
2. Admins can distribute tokens via the **Send Tokens** page.

### Admin Panel

Access Django's admin interface at `http://localhost:8000/admin/` to manage users, memberships, activities, and bookings.

---

## Configuration

Key settings live in [sports_park/settings.py](sports_park/settings.py):

| Setting | Value | Notes |
|---|---|---|
| `DEBUG` | `True` | Set to `False` for production |
| `WEB3_PROVIDER_URI` | Infura mainnet endpoint | Replace with your own Infura project ID |
| `CONTRACT_ADDRESS` | `0xd1ad0048...` | Main membership contract |
| `DATABASES` | SQLite | Swap for PostgreSQL in production |

---

## Deployment (Production)

1. Set `DEBUG = False` and configure `ALLOWED_HOSTS` in `settings.py`.
2. Replace the SQLite database with PostgreSQL or another production database.
3. Collect static files:
   ```bash
   python manage.py collectstatic
   ```
4. Serve with Gunicorn behind a reverse proxy (e.g. Nginx):
   ```bash
   gunicorn sports_park.wsgi:application --bind 0.0.0.0:8000
   ```

---

## URL Routes

| URL | View | Description |
|---|---|---|
| `/` | `home` | Landing page |
| `/register/` | `register` | User registration |
| `/login/` | `login` | User login |
| `/logout/` | `logout` | Session logout |
| `/dashboard/` | `dashboard` | Main dashboard |
| `/membership/` | `membership` | Membership purchase (Web3) |
| `/activities/` | `activities` | Browse activities |
| `/book/<id>/` | `book_activity` | Book an activity |
| `/cancel-booking/<id>/` | `cancel_booking` | Cancel a booking |
| `/checkin/` | `checkin` | GPS-based check-in |
| `/rewards/` | `rewards` | View reward tokens |
| `/send_tokens/` | `send_tokens` | Admin token minting |
