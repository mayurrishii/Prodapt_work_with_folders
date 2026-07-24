/**
 * test.js — Automated test client for the Movie Ticket Booking API.
 *
 * Run:  node test.js
 * (Make sure the server is NOT already running on port 3000 — this script starts its own.)
 */

const http = require('http');

const BASE_URL = 'http://localhost:3000';

// ── Helpers ─────────────────────────────────────────────

function request(method, path, body) {
  return new Promise((resolve, reject) => {
    const url = new URL(path, BASE_URL);
    const options = {
      method,
      hostname: url.hostname,
      port: url.port,
      path: url.pathname,
      headers: { 'Content-Type': 'application/json' },
    };

    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve({ status: res.statusCode, body: JSON.parse(data) });
        } catch {
          resolve({ status: res.statusCode, body: data });
        }
      });
    });

    req.on('error', reject);

    if (body !== undefined) {
      req.write(JSON.stringify(body));
    }
    req.end();
  });
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// ── Test Runner ─────────────────────────────────────────

let passed = 0;
let failed = 0;

function assert(condition, label) {
  if (condition) {
    console.log(`  ✅ ${label}`);
    passed++;
  } else {
    console.log(`  ❌ ${label}`);
    failed++;
  }
}

// ── Main Test Suite ─────────────────────────────────────

async function runTests() {
  console.log('\n══════════════════════════════════════════════');
  console.log('   MOVIE TICKET BOOKING API — TEST SUITE');
  console.log('══════════════════════════════════════════════\n');

  // ── 1. GET /bookings (empty) ──
  console.log('─── 1. GET /bookings (empty) ───');
  let res = await request('GET', '/bookings');
  assert(res.status === 200, 'Status 200');
  assert(res.body.success === true, 'success = true');
  assert(res.body.count === 0, 'count = 0');
  assert(Array.isArray(res.body.data), 'data is array');

  // ── 2. POST /bookings — successful booking ──
  console.log('\n─── 2. POST /bookings — book seat 1 for Inception 18:00 ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception',
    showTime: '2026-07-24 18:00',
    seatNumber: 1,
    customerName: 'Alice'
  });
  assert(res.status === 201, 'Status 201');
  assert(res.body.success === true, 'success = true');
  assert(res.body.data.id === 1, 'booking id = 1');
  assert(res.body.data.seatNumber === 1, 'seatNumber = 1');
  assert(res.body.data.customerName === 'Alice', 'customerName = Alice');

  // ── 3. POST /bookings — book another seat (same show) ──
  console.log('\n─── 3. POST /bookings — book seat 2 for Inception 18:00 ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception',
    showTime: '2026-07-24 18:00',
    seatNumber: 2,
    customerName: 'Bob'
  });
  assert(res.status === 201, 'Status 201');
  assert(res.body.data.id === 2, 'booking id = 2');

  // ── 4. POST /bookings — duplicate seat (business rule) ──
  console.log('\n─── 4. POST /bookings — duplicate seat 1 (should fail) ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception',
    showTime: '2026-07-24 18:00',
    seatNumber: 1,
    customerName: 'Charlie'
  });
  assert(res.status === 409, 'Status 409 (Conflict)');
  assert(res.body.success === false, 'success = false');
  assert(res.body.error === 'Seat already booked', 'error = Seat already booked');

  // ── 5. POST /bookings — missing fields (validation) ──
  console.log('\n─── 5. POST /bookings — missing fields ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception'
  });
  assert(res.status === 400, 'Status 400');
  assert(res.body.success === false, 'success = false');
  assert(res.body.error === 'Validation failed', 'error = Validation failed');
  assert(res.body.details.length >= 2, 'multiple validation errors');

  // ── 6. POST /bookings — invalid types ──
  console.log('\n─── 6. POST /bookings — invalid types ───');
  res = await request('POST', '/bookings', {
    movieName: 123,
    showTime: true,
    seatNumber: 'abc',
    customerName: 456
  });
  assert(res.status === 400, 'Status 400');
  assert(res.body.details.length >= 3, 'multiple type errors');

  // ── 7. POST /bookings — show not found ──
  console.log('\n─── 7. POST /bookings — non-existent show ───');
  res = await request('POST', '/bookings', {
    movieName: 'Avatar',
    showTime: '2026-07-24 18:00',
    seatNumber: 1,
    customerName: 'Diana'
  });
  assert(res.status === 404, 'Status 404');
  assert(res.body.error === 'Show not found', 'error = Show not found');

  // ── 8. POST /bookings — malformed JSON ──
  console.log('\n─── 8. POST /bookings — malformed JSON ───');
  // We'll send raw invalid JSON via a custom request
  const malformedRes = await new Promise((resolve, reject) => {
    const url = new URL('/bookings', BASE_URL);
    const req = http.request(
      { method: 'POST', hostname: url.hostname, port: url.port, path: url.pathname,
        headers: { 'Content-Type': 'application/json' } },
      (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try { resolve({ status: res.statusCode, body: JSON.parse(data) }); }
          catch { resolve({ status: res.statusCode, body: data }); }
        });
      }
    );
    req.on('error', reject);
    req.write('{"movieName": "Inception", broken json}');
    req.end();
  });
  assert(malformedRes.status === 400, 'Status 400');
  assert(malformedRes.body.error === 'Malformed JSON', 'error = Malformed JSON');

  // ── 9. GET /bookings — verify 2 bookings exist ──
  console.log('\n─── 9. GET /bookings — verify count ───');
  res = await request('GET', '/bookings');
  assert(res.status === 200, 'Status 200');
  assert(res.body.count === 2, 'count = 2');

  // ── 10. DELETE /bookings/:id — cancel booking ──
  console.log('\n─── 10. DELETE /bookings/1 — cancel Alice booking ───');
  res = await request('DELETE', '/bookings/1');
  assert(res.status === 200, 'Status 200');
  assert(res.body.success === true, 'success = true');
  assert(res.body.data.id === 1, 'cancelled booking id = 1');

  // ── 11. GET /bookings — verify 1 booking remains ──
  console.log('\n─── 11. GET /bookings — verify count after cancel ───');
  res = await request('GET', '/bookings');
  assert(res.status === 200, 'Status 200');
  assert(res.body.count === 1, 'count = 1');
  assert(res.body.data[0].id === 2, 'remaining booking id = 2');

  // ── 12. DELETE /bookings/:id — non-existent booking ──
  console.log('\n─── 12. DELETE /bookings/999 — not found ───');
  res = await request('DELETE', '/bookings/999');
  assert(res.status === 404, 'Status 404');
  assert(res.body.error === 'Booking not found', 'error = Booking not found');

  // ── 13. POST /bookings — re-book seat 1 (should work now, since cancelled) ──
  console.log('\n─── 13. POST /bookings — re-book seat 1 for Inception 18:00 ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception',
    showTime: '2026-07-24 18:00',
    seatNumber: 1,
    customerName: 'Eve'
  });
  assert(res.status === 201, 'Status 201');
  assert(res.body.data.id === 3, 'booking id = 3');

  // ── 14. POST /bookings — sell out the show ──
  console.log('\n─── 14. POST /bookings — book remaining seats to sell out ───');
  // Inception 18:00 started with 5 seats. Booked: seat 2 (Bob), seat 1 (Eve). 3 left.
  for (let seat of [3, 4, 5]) {
    res = await request('POST', '/bookings', {
      movieName: 'Inception',
      showTime: '2026-07-24 18:00',
      seatNumber: seat,
      customerName: `User${seat}`
    });
    assert(res.status === 201, `Seat ${seat} booked successfully`);
  }

  // ── 15. POST /bookings — sold-out show ──
  console.log('\n─── 15. POST /bookings — try booking sold-out show ───');
  res = await request('POST', '/bookings', {
    movieName: 'Inception',
    showTime: '2026-07-24 18:00',
    seatNumber: 6,
    customerName: 'Frank'
  });
  assert(res.status === 409, 'Status 409');
  assert(res.body.error === 'Show sold out', 'error = Show sold out');

  // ── 16. DELETE /bookings/:id — invalid ID ──
  console.log('\n─── 16. DELETE /bookings/abc — invalid ID ───');
  res = await request('DELETE', '/bookings/abc');
  assert(res.status === 400, 'Status 400');
  assert(res.body.error === 'Invalid booking ID', 'error = Invalid booking ID');

  // ── 17. GET /nonexistent — 404 route ──
  console.log('\n─── 17. GET /nonexistent — unknown route ───');
  res = await request('GET', '/nonexistent');
  assert(res.status === 404, 'Status 404');
  assert(res.body.error === 'Route not found', 'error = Route not found');

  // ── Summary ──
  console.log('\n══════════════════════════════════════════════');
  console.log(`   RESULTS:  ${passed} passed, ${failed} failed, ${passed + failed} total`);
  console.log('══════════════════════════════════════════════\n');

  process.exit(failed > 0 ? 1 : 0);
}

// ── Start server, wait, run tests, then exit ──
const app = require('./server');

// Give the server a moment to start
sleep(500).then(runTests).catch(err => {
  console.error('Test suite error:', err);
  process.exit(1);
});