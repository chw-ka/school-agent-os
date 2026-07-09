/**
 * Custom menu — entry point for the colleague running this sheet manually.
 * Wire up a time-driven trigger (Extensions > Apps Script > Triggers) on
 * buildReviewFromImport / sendNotices once the manual flow is validated.
 */
function onOpen() {
  SpreadsheetApp.getUi()
    .createMenu('圖書館通知')
    .addItem('1. 更新學生帳號對照表', 'refreshUsernameLookup')
    .addItem('2. 由 Raw Import 生成 Review', 'buildReviewFromImport')
    .addItem('3. 發送今日通知', 'sendNotices')
    .addToUi();
}
