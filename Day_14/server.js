/**
 * server.js — Movie Ticket Booking API (Express + JSON file DB)
 *
 * Endpoints:
 *   GET    /bookings       — list all bookings
 *   POST   /bookings       — book a seat (with validation & business rules)
 *   DELETE /bookings/:id   — cancel a booking & restore seat availability
 */

const express = require('express');
const { readState, writeState, findShow } = require('./db');
const { validateBookingBody, validateBookingId } = require('./validation');

const app = express();
const PORT = process.env.PORT || 3000;

// ── Middleware ──────────────────────────────────────────

// Built-in JSON body parser — will catch malformed JSON automatically
app.use(express.json());

// Serve the static demo UI from the "public" folder
app.use(express.static('public'));

// ── Error-handling middleware (must be defined after routes) ──
// (We define a helper reference; actual handler is below)

// ── Routes ──────────────────────────────────────────────

/**
 * GET /inventory
 * Returns the current inventory with live availableSeats counts.
 */
app.get('/inventory', (req, res) => {
  try {
    const { inventory } = readState();
    return res.json({ success: true, data: inventory });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to read inventory' });
  }
});

/**
 * POST /reset
 * Resets all data: clears bookings and restores inventory to full availability.
 */
app.post('/reset', (req, res) => {
  try {
    const { inventory, bookings } = readState();
    if (bookings.length === 0 && inventory.every(s => s.availableSeats === s.totalSeats)) {
      return res.json({ success: true, message: 'Data already clean' });
    }

    // Restore all seats
    for (const show of inventory) {
      show.availableSeats = show.totalSeats;
    }

    // Clear bookings
    const emptyBookings = [];

    try {
      writeState(inventory, emptyBookings);
    } catch (writeErr) {
      return res.status(500).json({
        success: false,
        error: 'Reset failed: ' + writeErr.message
      });
    }

    return res.json({ success: true, message: 'Data reset complete — all bookings cleared, inventory restored' });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Reset failed: ' + err.message });
  }
});

/**
 * GET /bookings/:id
 * Returns a single booking by its ID.
 */
app.get('/bookings/:id', (req, res) => {
  try {
    const { id } = req.params;
    const bookingId = Number(id);

    if (!Number.isInteger(bookingId) || bookingId < 1) {
      return res.status(400).json({ success: false, error: 'Invalid booking ID' });
    }

    const { bookings } = readState();
    const booking = bookings.find(b => b.id === bookingId);

    if (!booking) {
      return res.status(404).json({
        success: false,
        error: 'Booking not found',
        details: `No booking found with ID ${bookingId}`
      });
    }

    return res.json({ success: true, data: booking });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to read booking' });
  }
});

/**
 * GET /bookings
 * Returns a list of all bookings in the system.
 */
app.get('/bookings', (req, res) => {
  try {
    const { bookings } = readState();
    // Return empty array instead of error when no bookings exist
    return res.json({ success: true, count: bookings.length, data: bookings });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Failed to read bookings data' });
  }
});

/**
 * POST /bookings
 * Book a seat for a show.
 * Validates: all fields required, correct types, business rules (seat not already booked, show exists, seats available).
 * Two-file transaction: decrement inventory + append to bookings log (rollback on failure).
 */
app.post('/bookings', (req, res) => {
  try {
    const body = req.body;

    // ── 1. Validate input types & presence ──
    const { valid, errors } = validateBookingBody(body);
    if (!valid) {
      return res.status(400).json({ success: false, error: 'Validation failed', details: errors });
    }

    const { movieName, showTime, seatNumber, customerName } = body;

    // ── 2. Read current state ──
    let inventory, bookings;
    try {
      const state = readState();
      inventory = state.inventory;
      bookings = state.bookings;
    } catch (readErr) {
      return res.status(500).json({ success: false, error: 'Failed to read database' });
    }

    // ── 3. Find the show in inventory ──
    const show = findShow(inventory, movieName.trim(), showTime.trim());
    if (!show) {
      return res.status(404).json({
        success: false,
        error: 'Show not found',
        details: `No show found for "${movieName}" at "${showTime}"`
      });
    }

    // ── 4. Business rule: check if seat is already booked for this showTime ──
    const alreadyBooked = bookings.some(
      b => b.movieName === movieName.trim() &&
           b.showTime === showTime.trim() &&
           b.seatNumber === seatNumber
    );
    if (alreadyBooked) {
      return res.status(409).json({
        success: false,
        error: 'Seat already booked',
        details: `Seat ${seatNumber} is already booked for "${movieName}" at "${showTime}"`
      });
    }

    // ── 5. Business rule: check if show is sold out ──
    if (show.availableSeats <= 0) {
      return res.status(409).json({
        success: false,
        error: 'Show sold out',
        details: `No seats available for "${movieName}" at "${showTime}"`
      });
    }

    // ── 6. Create booking record ──
    const newId = bookings.length > 0 ? Math.max(...bookings.map(b => b.id)) + 1 : 1;
    const newBooking = {
      id: newId,
      movieName: movieName.trim(),
      showTime: showTime.trim(),
      seatNumber,
      customerName: customerName.trim(),
      createdAt: new Date().toISOString()
    };

    // ── 7. Update inventory (decrement availableSeats) ──
    show.availableSeats -= 1;

    // ── 8. Persist both files (transaction with rollback) ──
    bookings.push(newBooking);
    try {
      writeState(inventory, bookings);
    } catch (writeErr) {
      // Rollback the in-memory changes we just made
      show.availableSeats += 1;
      bookings.pop();
      return res.status(500).json({
        success: false,
        error: 'Database write failed, transaction rolled back',
        details: writeErr.message
      });
    }

    // ── 9. Return success ──
    return res.status(201).json({
      success: true,
      message: 'Booking confirmed',
      data: newBooking
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

/**
 * DELETE /bookings/:id
 * Cancel a booking and restore the seat to availability.
 */
app.delete('/bookings/:id', (req, res) => {
  try {
    const { id } = req.params;

    // ── 1. Validate ID ──
    const { valid, errors } = validateBookingId(id);
    if (!valid) {
      return res.status(400).json({ success: false, error: 'Invalid booking ID', details: errors });
    }

    const bookingId = Number(id);

    // ── 2. Read current state ──
    let inventory, bookings;
    try {
      const state = readState();
      inventory = state.inventory;
      bookings = state.bookings;
    } catch (readErr) {
      return res.status(500).json({ success: false, error: 'Failed to read database' });
    }

    // ── 3. Find the booking ──
    const bookingIndex = bookings.findIndex(b => b.id === bookingId);
    if (bookingIndex === -1) {
      return res.status(404).json({
        success: false,
        error: 'Booking not found',
        details: `No booking found with ID ${bookingId}`
      });
    }

    const booking = bookings[bookingIndex];

    // ── 4. Find the corresponding show in inventory ──
    const show = findShow(inventory, booking.movieName, booking.showTime);
    if (!show) {
      // If show no longer exists in inventory, still allow cancellation (just restore what we can)
      // Remove the booking and write state
      bookings.splice(bookingIndex, 1);
      try {
        writeState(inventory, bookings);
      } catch (writeErr) {
        return res.status(500).json({
          success: false,
          error: 'Database write failed during cancellation',
          details: writeErr.message
        });
      }
      return res.status(200).json({
        success: true,
        message: 'Booking cancelled (show no longer in inventory, seat not restored)',
        data: booking
      });
    }

    // ── 5. Restore seat availability ──
    // But first: ensure we don't exceed totalSeats
    if (show.availableSeats < show.totalSeats) {
      show.availableSeats += 1;
    }

    // ── 6. Remove booking ──
    bookings.splice(bookingIndex, 1);

    // ── 7. Persist both files (transaction with rollback) ──
    try {
      writeState(inventory, bookings);
    } catch (writeErr) {
      // Rollback in-memory changes
      show.availableSeats -= 1;
      bookings.splice(bookingIndex, 0, booking);
      return res.status(500).json({
        success: false,
        error: 'Database write failed, transaction rolled back',
        details: writeErr.message
      });
    }

    // ── 8. Return success ──
    return res.status(200).json({
      success: true,
      message: 'Booking cancelled, seat restored',
      data: booking
    });
  } catch (err) {
    return res.status(500).json({ success: false, error: 'Internal server error' });
  }
});

// ── 404 handler for unknown routes ──
app.use((req, res) => {
  return res.status(404).json({
    success: false,
    error: 'Route not found',
    details: `No endpoint: ${req.method} ${req.originalUrl}`
  });
});

// ── Global error handler (catches malformed JSON, unexpected throws) ──
app.use((err, req, res, _next) => {
  // Handle malformed JSON (body-parser error)
  if (err.type === 'entity.parse.failed' || err instanceof SyntaxError) {
    return res.status(400).json({
      success: false,
      error: 'Malformed JSON',
      details: err.message
    });
  }

  console.error('Unhandled error:', err);
  return res.status(500).json({
    success: false,
    error: 'Internal server error'
  });
});

// ── Start server ───────────────────────────────────────
app.listen(PORT, () => {
  console.log(`🎬 Movie Ticket Booking API running at http://localhost:${PORT}`);
  console.log(`   Endpoints:`);
  console.log(`   GET    /bookings        — list all bookings`);
  console.log(`   POST   /bookings        — book a seat`);
  console.log(`   DELETE /bookings/:id    — cancel a booking`);
});

module.exports = app; // Export for testing