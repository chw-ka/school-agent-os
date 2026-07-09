/**
 * Sends one personalised notice per student marked SendToday=TRUE and not
 * already Status=Sent in the "Review" tab. Each student gets their own
 * API call because sendNoticeMessage shares one body across all usernames
 * in a single request — students have different overdue lists.
 */
const REVIEW_COLS_ = {
  studentId: 0, username: 1, classCode: 2, nameEng: 3, nameChi: 4,
  itemCount: 5, maxDays: 6, summary: 7, fine: 8, sendToday: 9,
  notes: 10, status: 11, lastSent: 12,
};

function sendNotices() {
  const ss = SpreadsheetApp.getActive();
  const review = ss.getSheetByName('Review');
  const log = ss.getSheetByName('Send Log');
  const data = review.getDataRange().getValues();
  data.shift(); // header

  let sent = 0, failed = 0, skipped = 0;

  data.forEach(function (row, i) {
    const rowNum = i + 2;
    const c = REVIEW_COLS_;
    if (!row[c.sendToday]) { skipped++; return; }
    if (row[c.status] === 'Sent') { skipped++; return; }

    const username = row[c.username];
    const displayName = row[c.nameChi] || row[c.nameEng];
    const title = '圖書館還書提示';
    const body = buildNoticeBody_(displayName, row[c.summary], row[c.fine]);

    try {
      schoolinkSendNotice_([username], title, body);
      review.getRange(rowNum, c.status + 1).setValue('Sent');
      review.getRange(rowNum, c.lastSent + 1).setValue(new Date());
      log.appendRow([new Date(), row[c.studentId], username, row[c.nameEng], row[c.itemCount], body, 'Success', '']);
      sent++;
    } catch (err) {
      review.getRange(rowNum, c.status + 1).setValue('Error');
      log.appendRow([new Date(), row[c.studentId], username, row[c.nameEng], row[c.itemCount], body, 'Error', err.message]);
      failed++;
    }
  });

  SpreadsheetApp.getUi().alert('發送完成：成功 ' + sent + '，失敗 ' + failed + '，跳過 ' + skipped + '。');
}

function buildNoticeBody_(displayName, summary, fine) {
  let html = '<p>' + displayName + ' 同學：</p><p>你有以下圖書逾期未還，請盡快歸還：</p>';
  html += '<pre>' + summary + '</pre>';
  if (fine) html += '<p>累積罰款：$' + fine + '，請到圖書館櫃台處理。</p>';
  return html;
}
