# Python Event Ticketing & Seat Reservation Engine 🎟️

![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Build](https://img.shields.io/badge/Build-Passing-brightgreen.svg)

A high-concurrency event ticketing, tiered seat reservation matrix, and fraud-proof QR gate check-in engine built in Python. Designed for concerts, tech summits, sports stadiums, and auditoriums.

---

## 🚀 Key Features

- **Dynamic Tiered Seat Matrix**: Assign seats across VIP, Premium, and General Admission tiers with customizable row-level pricing.
- **Race Condition Prevention (10-Minute Hold Lock)**: Temporary reservation locks ensure customers can complete checkout without race conditions or double bookings.
- **SHA-256 Tamper-Proof QR Check-in**: Secure digital signature verification on ticket tokens prevents counterfeiting and fraudulent passes.
- **Real-Time Gate Scanner**: Detects duplicate scans, expired holds, and invalid passes in sub-millisecond lookups.

---

## 📦 Installation & Setup

```bash
git clone https://github.com/shyampandey1104/python-event-ticketing-booking-engine.git
cd python-event-ticketing-booking-engine
pip install -r requirements.txt
```

---

## 🛠️ Usage Example

```python
from ticketing.engine import EventTicketingEngine

engine = EventTicketingEngine("CONCERT-2026", "Indie Rock Night")
engine.add_seat("A-01", row="A", number=1, tier="VIP", price=2500.0)

# Lock seat for customer session
hold = engine.hold_seats(["A-01"])

# Confirm booking upon payment
ticket = engine.confirm_booking(
    hold_token=hold["hold_token"],
    attendee_name="Priya Patel",
    attendee_email="priya@example.com"
)

# Gate check-in
entry = engine.scan_checkin(ticket.ticket_id, ticket.qr_hash)
print(f"Status: {entry['status']} - {entry['message']}")
```

---

## 🧪 Testing

```bash
pytest tests/
```

---

## 📄 License
MIT License. Created with ❤️ by [Shyam Pandey](https://github.com/shyampandey1104).
