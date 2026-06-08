/**
 * World Cup 2026 Predictor — Google Sheet backend (with PINs)
 * ----------------------------------------------------------
 * Stores predictions and results, and serves them back for the leaderboard.
 *
 * PINs (self-service): the first time a name submits, the PIN it sends is
 * saved as that name's PIN. After that, any write under that name must send
 * the matching PIN. The organiser name "__RESULTS__" sets the organiser PIN
 * the first time results are saved; that PIN also works as an admin override
 * (used when the organiser imports someone's backup code).
 *
 * PINs live in a separate "pins" tab and are NEVER served back to the page.
 *
 * You do NOT need to understand this. After pasting it in, redeploy:
 *   Deploy > Manage deployments > edit (pencil) > Version: New version > Deploy
 */

var SHEET_NAME = 'data';
var PIN_SHEET  = 'pins';
var ADMIN_NAME = '__RESULTS__';

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['timestamp', 'stage', 'name', 'type', 'data']);
  }
  return sh;
}

function getPinSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(PIN_SHEET);
  if (!sh) {
    sh = ss.insertSheet(PIN_SHEET);
    sh.appendRow(['name', 'pin']);
  }
  return sh;
}

function getPin_(name) {
  var v = getPinSheet_().getDataRange().getValues();
  for (var i = 1; i < v.length; i++) {
    if (String(v[i][0]) === String(name)) return String(v[i][1]);
  }
  return '';
}

function setPin_(name, pin) {
  var sh = getPinSheet_();
  var v = sh.getDataRange().getValues();
  for (var i = 1; i < v.length; i++) {
    if (String(v[i][0]) === String(name)) { sh.getRange(i + 1, 2).setValue(String(pin)); return; }
  }
  sh.appendRow([String(name), String(pin)]);
}

function claimedNames_() {
  var v = getPinSheet_().getDataRange().getValues();
  var out = [];
  for (var i = 1; i < v.length; i++) {
    if (v[i][0] !== '' && String(v[i][0]) !== ADMIN_NAME) out.push(String(v[i][0]));
  }
  return out;
}

function validPin_(p) { return /^[0-9]{4}$/.test(String(p == null ? '' : p)); }

// Core write path, shared by JSONP (doGet action=submit) and doPost.
function writeSubmission_(p) {
  var name = String(p.name || '');
  if (!name) return { ok: false, error: 'no_name' };

  var pin      = String(p.pin || '');
  var adminPin = String(p.adminPin || '');
  var orgPin   = getPin_(ADMIN_NAME);

  var isAdmin = false;
  if (adminPin !== '') {
    if (orgPin !== '' && adminPin === orgPin) isAdmin = true;
    else return { ok: false, error: 'bad_pin' };   // admin override attempted but PIN wrong
  }

  if (!isAdmin) {
    var stored = getPin_(name);
    if (stored === '') {
      if (!validPin_(pin)) return { ok: false, error: 'pin_required' };
      setPin_(name, pin);          // claim this name
    } else if (pin !== stored) {
      return { ok: false, error: 'bad_pin' };
    }
  }

  var data = {};
  try { data = p.data ? JSON.parse(p.data) : {}; } catch (e) { data = {}; }

  getSheet_().appendRow([
    new Date(),
    String(p.stage || ''),
    name,
    String(p.type || 'prediction'),
    JSON.stringify(data)
  ]);
  return { ok: true };
}

function jsonOut_(payload, cb) {
  if (cb) {
    return ContentService
      .createTextOutput(cb + '(' + payload + ')')
      .setMimeType(ContentService.MimeType.JAVASCRIPT);
  }
  return ContentService
    .createTextOutput(payload)
    .setMimeType(ContentService.MimeType.JSON);
}

// Reads (action=all) and writes (action=submit) both come through here so the
// page can read the response over JSONP.
function doGet(e) {
  var p  = (e && e.parameter) || {};
  var cb = p.callback;

  if (p.action === 'submit') {
    var lock = LockService.getScriptLock();
    lock.waitLock(20000);
    try {
      return jsonOut_(JSON.stringify(writeSubmission_(p)), cb);
    } finally {
      lock.releaseLock();
    }
  }

  var values = getSheet_().getDataRange().getValues();
  var rows = [];
  for (var i = 1; i < values.length; i++) {
    var data = {};
    try { data = values[i][4] ? JSON.parse(values[i][4]) : {}; } catch (x) { data = {}; }
    rows.push({
      ts: values[i][0],
      stage: values[i][1],
      name: values[i][2],
      type: values[i][3] || 'prediction',
      data: data
    });
  }
  return jsonOut_(JSON.stringify({ rows: rows, claimed: claimedNames_() }), cb);
}

// Kept working as a fallback (same PIN rules). The page uses JSONP above.
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var b = JSON.parse(e.postData.contents);
    var res = writeSubmission_({
      stage: b.stage, name: b.name, type: b.type,
      data: JSON.stringify(b.data || {}), pin: b.pin, adminPin: b.adminPin
    });
    return ContentService.createTextOutput(JSON.stringify(res)).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({ ok: false, error: String(err) })).setMimeType(ContentService.MimeType.JSON);
  } finally {
    lock.releaseLock();
  }
}
