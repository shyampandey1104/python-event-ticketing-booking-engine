import unittest
from ticketing.engine import EventTicketingEngine


class TestEventTicketingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EventTicketingEngine(event_id="EVT-2026-ROCK", event_name="Live Music Festival")
        self.engine.add_seat("A-01", "A", 1, "VIP", 2500.0)
        self.engine.add_seat("A-02", "A", 2, "VIP", 2500.0)
        self.engine.add_seat("B-01", "B", 1, "General", 800.0)

    def test_hold_and_confirm(self):
        hold_info = self.engine.hold_seats(["A-01", "A-02"])
        self.assertTrue(hold_info["success"])
        token = hold_info["hold_token"]

        ticket = self.engine.confirm_booking(
            hold_token=token,
            attendee_name="Aarav Sharma",
            attendee_email="aarav@example.com"
        )
        self.assertEqual(ticket.total_amount, 5000.0)
        self.assertEqual(len(ticket.seats), 2)
        self.assertTrue(self.engine.seats["A-01"].is_booked)

        # Gate check-in
        checkin = self.engine.scan_checkin(ticket.ticket_id, ticket.qr_hash)
        self.assertEqual(checkin["status"], "ADMITTED")

        # Second scan should trigger duplicate
        dup = self.engine.scan_checkin(ticket.ticket_id, ticket.qr_hash)
        self.assertEqual(dup["status"], "DUPLICATE")

    def test_double_hold_fails(self):
        self.engine.hold_seats(["B-01"])
        with self.assertRaises(ValueError):
            self.engine.hold_seats(["B-01"])


if __name__ == "__main__":
    unittest.main()
