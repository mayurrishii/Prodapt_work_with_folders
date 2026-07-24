print("We did absolutely nothing today and it was glorious!")
print("But a bad day for streak :(")

"""
Option 1: Movie Ticket Booking API
 
Resource: /bookings
 
GET /bookings — list all bookings
POST /bookings — book a seat, with validation: movieName (string), showTime (string), seatNumber (number), customerName (string) all required
Validation edge case to handle: reject if seatNumber is already booked for that showTime (a business-rule check, not just a type check — good stretch beyond the bookstore example)
Error handling: malformed JSON, booking a sold-out show
DB integration: a JSON file seats-inventory.json tracks available seats per show; booking a seat must decrement availability and append to a bookings log — same two-file transaction/rollback pattern as the bookstore's order flow
Bonus: DELETE /bookings/:id — cancel a booking and restore the seat to availability
 
 
Option 2: Restaurant Table Reservation API
 
Resource: /reservations
 
GET /reservations — list all reservations
GET /reservations/:id — get one reservation
POST /reservations — create one, with validation: customerName (string), partySize (number, 1–12), reservationTime (string) all required
Validation edge case: reject if partySize exceeds the restaurant's largest table capacity (a config value, e.g. MAX_TABLE_SIZE = 8)
Error handling: malformed JSON, reservation time in the past (throw and catch a custom validation error)
DB integration: tables-inventory.json tracks table availability by time slot; confirming a reservation must mark a table as occupied and log the reservation — rollback both if either write fails
Bonus: PUT /reservations/:id — modify party size or time, re-checking capacity
 
 
Option 3: Gym Class Enrollment API
 
Resource: /enrollments
 
GET /enrollments — list all enrollments
POST /enrollments — enroll a member in a class, with validation: memberName (string), className (string), classDate (string) all required
Validation edge case: reject if the class is already at capacity (e.g. max 20 per class) — same "business rule, not just type check" stretch as Option 1
Error handling: malformed JSON, enrolling in a class that doesn't exist in the schedule
DB integration: class-schedule.json tracks enrolled count per class; enrolling must increment the count and append to an enrollment log — same transaction/rollback shape
Bonus: DELETE /enrollments/:id — cancel an enrollment and free up a class slot
"""

print("Bell")