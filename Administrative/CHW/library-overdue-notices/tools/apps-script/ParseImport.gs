/**
 * Aggregates "Raw Import" (one row per overdue item) into "Review"
 * (one row per student), matching each student to a SchooLink username
 * via "Username Lookup". Rows with a blank StudentID (staff / department
 * placeholder accounts such as BIB2023, HIS2022) are skipped.
 */
function buildReviewFromImport() {
  const ss = SpreadsheetApp.getActive();
  const raw = ss.getSheetByName('Raw Import');
  const review = ss.getSheetByName('Review');
  const lookup = ss.getSheetByName('Username Lookup');

  const data = raw.getDataRange().getValues();
  data.shift(); // header: StudentID, ClassCode, NameEng, NameChi, BorrowDate, CallNumber, Title

  const lookupData = lookup.getDataRange().getValues();
  lookupData.shift();
  const usernameByStudentId = {};
  lookupData.forEach(function (r) {
    const username = r[1];
    const studentId = r[5];
    if (studentId) usernameByStudentId[String(studentId)] = username;
  });

  const byStudent = {};
  const now = new Date();
  data.forEach(function (row) {
    const studentId = row[0];
    if (!studentId) return; // not a student row — skip (staff/dept placeholder)
    const key = String(studentId);
    if (!byStudent[key]) {
      byStudent[key] = {
        studentId: key,
        classCode: row[1],
        nameEng: row[2],
        nameChi: row[3],
        items: [],
        maxDays: 0,
      };
    }
    const days = daysBetween_(row[4], now);
    byStudent[key].items.push({ borrowDate: row[4], callNumber: row[5], title: row[6], days: days });
    byStudent[key].maxDays = Math.max(byStudent[key].maxDays, days);
  });

  const rows = Object.keys(byStudent).map(function (key) {
    const s = byStudent[key];
    const username = usernameByStudentId[s.studentId] || ('S' + s.studentId); // fallback guess
    const summary = s.items
      .map(function (i) { return formatDate_(i.borrowDate) + '｜' + i.callNumber + '｜' + i.title + '（逾期 ' + i.days + ' 日）'; })
      .join('\n');
    return [
      s.studentId, username, s.classCode, s.nameEng, s.nameChi,
      s.items.length, s.maxDays, summary, '', true, '', 'Not Sent', '',
    ];
  });

  if (review.getLastRow() > 1) {
    review.getRange(2, 1, review.getLastRow() - 1, 13).clearContent();
  }
  if (rows.length) {
    review.getRange(2, 1, rows.length, 13).setValues(rows);
  }
  SpreadsheetApp.getUi().alert('已彙總 ' + rows.length + ' 名學生嘅逾期紀錄到 Review。');
}

function daysBetween_(borrowDateValue, now) {
  const borrow = new Date(borrowDateValue);
  return Math.max(0, Math.floor((now - borrow) / (1000 * 60 * 60 * 24)));
}

function formatDate_(dateValue) {
  return Utilities.formatDate(new Date(dateValue), Session.getScriptTimeZone(), 'yyyy-MM-dd');
}
