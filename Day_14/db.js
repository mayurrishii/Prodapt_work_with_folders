/**
 * db.js — Simple JSON-file DB with a two-file transaction / rollback pattern.
 *
 * Every write follows this sequence:
 *   1. Read fresh state from both files (inventory + bookings)
 *   2. Apply in-memory changes
 *   3. Write inventory FIRST (to a temp file → rename = atomic)
 *   4. Write bookings SECOND
 *   5. If step 3 fails → rollback (restore originals); never touch bookings
 *   6. If step 4 fails → rollback inventory to its pre-write state
 *
 * This ensures the two files never drift — either both commit or both roll back.
 */

const fs = require('fs');
const path = require('path');

const INVENTORY_PATH = path.join(__dirname, 'seeds-inventory.json');
const BOOKINGS_PATH = path.join(__dirname, 'bookings.json');
const INVENTORY_TEMP = path.join(__dirname, 'seeds-inventory.tmp.json');
const BOOKINGS_TEMP = path.join(__dirname, 'bookings.tmp.json');

// ── helpers ──────────────────────────────────────────────

function readJSON(filePath) {
  const raw = fs.readFileSync(filePath, 'utf-8');
  return JSON.parse(raw);
}

function atomicWrite(targetPath, tempPath, data) {
  fs.writeFileSync(tempPath, JSON.stringify(data, null, 2), 'utf-8');
  fs.renameSync(tempPath, targetPath);
}

// ── public API ───────────────────────────────────────────

/**
 * Read the latest state from both files.
 * @returns {{ inventory: object[], bookings: object[] }}
 */
function readState() {
  const inventory = readJSON(INVENTORY_PATH);
  const bookings = readJSON(BOOKINGS_PATH);
  return { inventory, bookings };
}

/**
 * Atomically persist both files.  If either write fails the other is rolled back.
 * @param {object[]} inventory
 * @param {object[]} bookings
 */
function writeState(inventory, bookings) {
  const invBackup = readJSON(INVENTORY_PATH);
  const bkBackup = readJSON(BOOKINGS_PATH);

  try {
    // 1. Write inventory
    atomicWrite(INVENTORY_PATH, INVENTORY_TEMP, inventory);
  } catch (err) {
    // Rollback impossible because inventory write never truly started — just re-throw
    throw new Error(`Failed to write inventory: ${err.message}`);
  }

  try {
    // 2. Write bookings
    atomicWrite(BOOKINGS_PATH, BOOKINGS_TEMP, bookings);
  } catch (err) {
    // Rollback inventory to its pre-write state
    try {
      atomicWrite(INVENTORY_PATH, INVENTORY_TEMP, invBackup);
    } catch (rollbackErr) {
      throw new Error(
        `CRITICAL: inventory written but bookings failed AND rollback failed. ` +
        `Inventory may be corrupt. Original error: ${err.message}. ` +
        `Rollback error: ${rollbackErr.message}`
      );
    }
    throw new Error(`Booking write failed, inventory rolled back: ${err.message}`);
  }

  // Cleanup temp files (best-effort)
  try { fs.unlinkSync(INVENTORY_TEMP); } catch (_) { /* ignore */ }
  try { fs.unlinkSync(BOOKINGS_TEMP); } catch (_) { /* ignore */ }
}

/**
 * Find a show (inventory record) by movieName + showTime.
 * Returns the record or undefined.
 */
function findShow(inventory, movieName, showTime) {
  return inventory.find(
    s => s.movieName === movieName && s.showTime === showTime
  );
}

module.exports = { readState, writeState, findShow };