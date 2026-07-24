/**
 * validation.js — Request validation helpers for the Movie Ticket Booking API.
 */

/**
 * Validate a POST /bookings request body.
 * Returns an object: { valid: boolean, errors: string[] }
 */
function validateBookingBody(body) {
  const errors = [];

  if (!body || typeof body !== 'object') {
    return { valid: false, errors: ['Request body is required'] };
  }

  // movieName: required, non-empty string
  if (body.movieName === undefined || body.movieName === null) {
    errors.push('movieName is required');
  } else if (typeof body.movieName !== 'string') {
    errors.push('movieName must be a string');
  } else if (body.movieName.trim().length === 0) {
    errors.push('movieName cannot be empty');
  }

  // showTime: required, non-empty string
  if (body.showTime === undefined || body.showTime === null) {
    errors.push('showTime is required');
  } else if (typeof body.showTime !== 'string') {
    errors.push('showTime must be a string');
  } else if (body.showTime.trim().length === 0) {
    errors.push('showTime cannot be empty');
  }

  // seatNumber: required, must be a number (integer >= 1)
  if (body.seatNumber === undefined || body.seatNumber === null) {
    errors.push('seatNumber is required');
  } else if (typeof body.seatNumber !== 'number' || !Number.isInteger(body.seatNumber)) {
    errors.push('seatNumber must be an integer');
  } else if (body.seatNumber < 1) {
    errors.push('seatNumber must be a positive integer');
  }

  // customerName: required, non-empty string
  if (body.customerName === undefined || body.customerName === null) {
    errors.push('customerName is required');
  } else if (typeof body.customerName !== 'string') {
    errors.push('customerName must be a string');
  } else if (body.customerName.trim().length === 0) {
    errors.push('customerName cannot be empty');
  }

  return { valid: errors.length === 0, errors };
}

/**
 * Validate a booking ID for DELETE /bookings/:id
 * Returns an object: { valid: boolean, errors: string[] }
 */
function validateBookingId(id) {
  const errors = [];
  const num = Number(id);

  if (id === undefined || id === null) {
    errors.push('Booking ID is required');
  } else if (!Number.isInteger(num) || num < 1) {
    errors.push('Booking ID must be a positive integer');
  }

  return { valid: errors.length === 0, errors };
}

module.exports = { validateBookingBody, validateBookingId };