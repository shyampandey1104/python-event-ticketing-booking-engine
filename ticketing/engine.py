"""Event Ticketing, Seat Reservation Matrix & QR Check-in Engine."""

import time
import hashlib
import uuid
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class Seat(BaseModel):
    seat_id: str
    row: str
    number: int
    tier: str  # VIP, Premium, General
    price: float
    is_booked: bool = False
    hold_token: Optional[str] = None
    hold_expiry_timestamp: Optional[float] = None


class Ticket(BaseModel):
    ticket_id: str
    event_id: str
    attendee_name: str
    attendee_email: str
    seats: List[str]
    total_amount: float
    qr_hash: str
    is_checked_in: bool = False
    checked_in_at: Optional[float] = None


class EventTicketingEngine:
    """Manages seat matrices, temporary hold locking, checkout, and gate check-in."""

    def __init__(self, event_id: str, event_name: str, hold_duration_seconds: int = 600):
        self.event_id = event_id
        self.event_name = event_name
        self.hold_duration = hold_duration_seconds
        self.seats: Dict[str, Seat] = {}
        self.issued_tickets: Dict[str, Ticket] = {}

    def add_seat(self, seat_id: str, row: str, number: int, tier: str, price: float) -> Seat:
        seat = Seat(seat_id=seat_id, row=row, number=number, tier=tier, price=price)
        self.seats[seat_id] = seat
        return seat

    def hold_seats(self, seat_ids: List[str]) -> Dict[str, Any]:
        """Locks seats for 10 minutes (hold_duration) for a customer checkout session."""
        now = time.time()
        # Verify availability
        for s_id in seat_ids:
            if s_id not in self.seats:
                raise ValueError(f"Seat {s_id} does not exist.")
            seat = self.seats[s_id]
            if seat.is_booked:
                raise ValueError(f"Seat {s_id} is already permanently booked.")
            if seat.hold_token and seat.hold_expiry_timestamp and seat.hold_expiry_timestamp > now:
                raise ValueError(f"Seat {s_id} is currently held by another checkout session.")

        # Grant hold
        hold_token = str(uuid.uuid4())
        expiry = now + self.hold_duration
        for s_id in seat_ids:
            self.seats[s_id].hold_token = hold_token
            self.seats[s_id].hold_expiry_timestamp = expiry

        return {
            "success": True,
            "hold_token": hold_token,
            "expires_in_seconds": self.hold_duration,
            "held_seats": seat_ids
        }

    def confirm_booking(
        self,
        hold_token: str,
        attendee_name: str,
        attendee_email: str
    ) -> Ticket:
        """Converts held seats into a confirmed booking and produces QR hash."""
        now = time.time()
        claimed_seats = [
            s for s in self.seats.values()
            if s.hold_token == hold_token and (s.hold_expiry_timestamp or 0) >= now
        ]

        if not claimed_seats:
            raise ValueError("No valid or active hold found for the provided token.")

        total_amount = sum(s.price for s in claimed_seats)
        ticket_id = f"TKT-{uuid.uuid4().hex[:8].upper()}"

        # Generate cryptographic verification hash for QR code
        raw_signature = f"{ticket_id}:{self.event_id}:{attendee_email}:{total_amount}"
        qr_hash = hashlib.sha256(raw_signature.encode()).hexdigest()

        # Mark seats permanently booked
        seat_ids = []
        for s in claimed_seats:
            s.is_booked = True
            s.hold_token = None
            s.hold_expiry_timestamp = None
            seat_ids.append(s.seat_id)

        ticket = Ticket(
            ticket_id=ticket_id,
            event_id=self.event_id,
            attendee_name=attendee_name,
            attendee_email=attendee_email,
            seats=seat_ids,
            total_amount=round(total_amount, 2),
            qr_hash=qr_hash,
            is_checked_in=False
        )

        self.issued_tickets[ticket_id] = ticket
        return ticket

    def scan_checkin(self, ticket_id: str, qr_hash: str) -> Dict[str, Any]:
        """Validates ticket at venue entrance gate."""
        ticket = self.issued_tickets.get(ticket_id)
        if not ticket:
            return {"status": "INVALID", "message": "Ticket does not exist."}

        if ticket.qr_hash != qr_hash:
            return {"status": "COUNTERFEIT", "message": "QR signature verification failed!"}

        if ticket.is_checked_in:
            return {
                "status": "DUPLICATE",
                "message": f"Ticket already used at {ticket.checked_in_at}."
            }

        ticket.is_checked_in = True
        ticket.checked_in_at = time.time()
        return {
            "status": "ADMITTED",
            "attendee": ticket.attendee_name,
            "seats": ticket.seats,
            "message": "Welcome! Access granted."
        }
