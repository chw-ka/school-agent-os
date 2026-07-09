/**
 * Refreshes the "Username Lookup" tab from SchooLink getUsers, keeping
 * students (userTypeID 320) only. Run this periodically (e.g. weekly) —
 * no need to call it on every send.
 */
function refreshUsernameLookup() {
  const ss = SpreadsheetApp.getActive();
  const sheet = ss.getSheetByName('Username Lookup');
  const users = schoolinkGetUsers_();
  const students = users.filter(function (u) { return u.userTypeID === '320'; });

  const existing = sheet.getDataRange().getValues();
  existing.shift(); // header
  const knownStudentIdByUsername = {};
  existing.forEach(function (row) {
    const username = row[1];
    const studentId = row[5];
    if (username && studentId) knownStudentIdByUsername[username] = studentId;
  });

  const rows = students.map(function (u) {
    // Best-guess StudentID from username pattern "S<id>" — UNCONFIRMED,
    // carry over any manually-reconciled value from before if present.
    const guess = /^S(\d+)$/.exec(u.username);
    const studentId = knownStudentIdByUsername[u.username] || (guess ? guess[1] : '');
    return [u.userID, u.username, u.userTypeID, u.nameEng, u.nameChi, studentId, new Date()];
  });

  if (sheet.getLastRow() > 1) {
    sheet.getRange(2, 1, sheet.getLastRow() - 1, 7).clearContent();
  }
  if (rows.length) {
    sheet.getRange(2, 1, rows.length, 7).setValues(rows);
  }
  SpreadsheetApp.getUi().alert('已更新 ' + rows.length + ' 個學生帳號。StudentID 欄有猜測值，首次使用請人手抽樣核對。');
}
