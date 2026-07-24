/**
 * errors.js — Centralized HTTP error classes & async handler wrapper.
 *
 * Route handlers should:
 *   - throw AppError (or its subclasses) for expected business-logic failures
 *   - let unexpected errors bubble up — the global error middleware catches them
 */

// ── Custom HTTP Error class ────────────────────────────
class AppError extends Error {
  constructor(message, statusCode = 500, details = null) {
    super(message);
    this.name = 'AppError';
    this.statusCode = statusCode;
    this.details = details;
    // Capture stack trace, excluding constructor call from it
    Error.captureStackTrace?.(this, this.constructor);
  }
}

// ── Shortcut constructors for common HTTP codes ────────
class BadRequestError extends AppError {
  constructor(message = 'Bad request', details = null) {
    super(message, 400, details);
    this.name = 'BadRequestError';
  }
}

class NotFoundError extends AppError {
  constructor(message = 'Resource not found', details = null) {
    super(message, 404, details);
    this.name = 'NotFoundError';
  }
}

class ConflictError extends AppError {
  constructor(message = 'Conflict', details = null) {
    super(message, 409, details);
    this.name = 'ConflictError';
  }
}

class InternalError extends AppError {
  constructor(message = 'Internal server error', details = null) {
    super(message, 500, details);
    this.name = 'InternalError';
  }
}

// ── Async route wrapper (eliminates try/catch in every route) ──
//
// Usage:  app.get('/path', asyncHandler(async (req, res) => { ... }))
//
// Any thrown error is forwarded to Express error-handling middleware.
function asyncHandler(fn) {
  return (req, res, next) => {
    Promise.resolve(fn(req, res, next)).catch(next);
  };
}

module.exports = {
  AppError,
  BadRequestError,
  NotFoundError,
  ConflictError,
  InternalError,
  asyncHandler,
};