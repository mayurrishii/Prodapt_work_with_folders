/**
 * server.js — Movie Ticket Booking API (Express + JSON file DB)
 *
 * Endpoints:
 *   GET    /inventory      — live seat availability
 *   POST   /reset          — reset all data (admin)
 *   GET    /bookings       — list all bookings
 *   GET    /bookings/:id   — get a single booking
 *   POST   /bookings       — book a seat (with validation & business rules)
 *   DELETE /bookings/:id   — cancel a booking & restore seat availability
 *
 * ─── Architecture ───────────────────────────────────────
 * ZERO try/catch blocks anywhere in route handlers.
 * Every handler:
 *   - Is wrapped with asyncHandler (catches thrown promises → next(err))
 *   - Throws AppError subclasses for known failure modes
 *   - Uses writeState's onRollback callback for persistence rollback
 *   - Lets unexpected errors bubble up to the global error middleware
 *
 * The single centralized error middleware at the bottom handles ALL errors
 * including malformed JSON and unexpected crashes.
 */

const express = require('express');
const { readState, writeState, findShowOrThrow } = require('./db');
const { validateBookingBody, validateBookingId } = require('./validation');
const {
  asyncHandler,
  BadRequestError,
  NotFoundError,
  ConflictError,
  AppError,
} = require('./errors');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ──────────────────────────────────────────
app.use(express.json());
app.use(express.static('public'));

// ── Routes ──────────────────────────────────────────────

/**
 * GET /inventory
 */
app.get(
  '/inventory',
  asyncHandler((_req, res) => {
    const { inventory } = readState();
    res.json({ success: true, data: inventory });
  }),
);

/**
 * POST /reset — clears all bookings and restores inventory to full.
 */
app.post(
  '/reset',
  asyncHandler((_req, res) => {
    const { inventory, bookings } = readState();

    if (bookings.length === 0 && inventory.every(s => s.availableSeats === s.totalSeats)) {
      return res.json({ success: true, message: 'Data already clean' });
    }

    for (const show of inventory) {
      show.availableSeats = show.totalSeats;
    }

    writeState(inventory, []);
    res.json({ success: true, message: 'Data reset complete — all bookings cleared, inventory restored' });
  }),
);

/**
 * GET /bookings/:id
 */
app.get(
  '/bookings/:id',
  asyncHandler((req, res) => {
    const { id } = req.params;
    const bookingId = Number(id);

    if (!Number.isInteger(bookingId) || bookingId < 1) {
      throw new BadRequestError('Invalid booking ID');
    }

    const { bookings } = readState();
    const booking = bookings.find(b => b.id === bookingId);

    if (!booking) {
      throw new NotFoundError('Booking not found', `No booking found with ID ${bookingId}`);
    }

    res.json({ success: true, data: booking });
  }),
);

/**
 * GET /bookings
 */
app.get(
  '/bookings',
  asyncHandler((_req, res) => {
    const { bookings } = readState();
    res.json({ success: true, count: bookings.length, data: bookings });
  }),
);

/**
 * POST /bookings — book a seat.
 *
 * Validation sequence (in order):
 *   1. Field types & presence
 *   2. Show existence in inventory
 *   3. Seat not already booked (business rule)
 *   4. Show not sold out (business rule)
 *   5. Persist both files (two-file transaction with onRollback callback)
 *
 * ZERO try/catch — persistence errors bubble up through asyncHandler.
 */
app.post(
  '/bookings',
  asyncHandler((req, res) => {
    const body = req.body;

    // 1. Field validation
    const { valid, errors } = validateBookingBody(body);
    if (!valid) {
      throw new BadRequestError('Validation failed', errors);
    }

    const { movieName, showTime, seatNumber, customerName } = body;

    // 2. Read current state
    const { inventory, bookings } = readState();

    // 3. Find show (throws NotFoundError if missing)
    const show = findShowOrThrow(inventory, movieName.trim(), showTime.trim());

    // 4. Check duplicate seat (business rule)
    const alreadyBooked = bookings.some(
      b =>
        b.movieName === movieName.trim() &&
        b.showTime === showTime.trim() &&
        b.seatNumber === seatNumber,
    );
    if (alreadyBooked) {
      throw new ConflictError(
        'Seat already booked',
        `Seat ${seatNumber} is already booked for "${movieName}" at "${showTime}"`,
      );
    }

    // 5. Check sold out (business rule)
    if (show.availableSeats <= 0) {
      throw new ConflictError(
        'Show sold out',
        `No seats available for "${movieName}" at "${showTime}"`,
      );
    }

    // 6. Create booking record
    const newId = bookings.length > 0 ? Math.max(...bookings.map(b => b.id)) + 1 : 1;
    const newBooking = {
      id: newId,
      movieName: movieName.trim(),
      showTime: showTime.trim(),
      seatNumber,
      customerName: customerName.trim(),
      createdAt: new Date().toISOString(),
    };

    // 7. Decrement seat
    show.availableSeats -= 1;

    // 8. Persist with rollback callback — if write fails, in-memory changes are reverted
    bookings.push(newBooking);
    writeState(inventory, bookings, () => {
      show.availableSeats += 1;
      bookings.pop();
    });

    res.status(201).json({
      success: true,
      message: 'Booking confirmed',
      data: newBooking,
    });
  }),
);

/**
 * DELETE /bookings/:id — cancel a booking and restore the seat.
 *
 * ZERO try/catch — the onRollback callback handles in-memory rollback.
 */
app.delete(
  '/bookings/:id',
  asyncHandler((req, res) => {
    const { id } = req.params;

    // 1. Validate ID
    const { valid, errors } = validateBookingId(id);
    if (!valid) {
      throw new BadRequestError('Invalid booking ID', errors);
    }

    const bookingId = Number(id);

    // 2. Read state
    const { inventory, bookings } = readState();

    // 3. Find booking
    const bookingIndex = bookings.findIndex(b => b.id === bookingId);
    if (bookingIndex === -1) {
      throw new NotFoundError('Booking not found', `No booking found with ID ${bookingId}`);
    }

    const booking = bookings[bookingIndex];

    // 4. Find corresponding show & restore seat
    const show = inventory.find(
      s => s.movieName === booking.movieName && s.showTime === booking.showTime,
    );

    if (show && show.availableSeats < show.totalSeats) {
      show.availableSeats += 1;
    }

    // 5. Remove booking
    bookings.splice(bookingIndex, 1);

    // 6. Persist with rollback callback
    writeState(inventory, bookings, () => {
      if (show) show.availableSeats -= 1;
      bookings.splice(bookingIndex, 0, booking);
    });

    const message = show
      ? 'Booking cancelled, seat restored'
      : 'Booking cancelled (show no longer in inventory, seat not restored)';

    res.status(200).json({
      success: true,
      message,
      data: booking,
    });
  }),
);

// ── 404 handler for unknown routes ──
app.use((_req, res) => {
  res.status(404).json({
    success: false,
    error: 'Route not found',
    details: 'No endpoint matches the requested URL',
  });
});

// ── SINGLE centralized error handler ────────────────────
// Catches EVERYTHING:
//   - AppError subclasses thrown by route handlers
//   - Malformed JSON from express.json()
//   - Any unexpected error
app.use((err, _req, res, _next) => {
  // Handle malformed JSON (express.json() error)
  if (err.type === 'entity.parse.failed' || err instanceof SyntaxError) {
    return res.status(400).json({
      success: false,
      error: 'Malformed JSON',
      details: err.message,
    });
  }

  // Handle known AppErrors (thrown by our route handlers & db layer)
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      success: false,
      error: err.message,
      ...(err.details ? { details: err.details } : {}),
    });
  }

  // Unknown / unexpected errors
  console.error('Unhandled error:', err);
  return res.status(500).json({
    success: false,
    error: 'Internal server error',
  });
});

// ── Start server ───────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🎬 Movie Ticket Booking API running at http://localhost:${PORT}`);
  console.log(`   Endpoints:`);
  console.log(`   GET    /inventory       — seat availability`);
  console.log(`   GET    /bookings        — list all bookings`);
  console.log(`   GET    /bookings/:id    — get one booking`);
  console.log(`   POST   /bookings        — book a seat`);
  console.log(`   DELETE /bookings/:id    — cancel a booking`);
  console.log(`   POST   /reset           — reset all data`);
});

module.exports = app;