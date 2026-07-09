/**
 * Thin wrapper around the SchooLink API (see docs/SchooLink API Specification (CHW)_v1.0.pdf).
 */

function schoolinkRequest_(path, payload) {
  const cfg = getConfig_();
  const options = {
    method: 'post',
    contentType: 'application/json',
    headers: { SchooLinkKey: cfg.key },
    payload: payload ? JSON.stringify(payload) : '',
    muteHttpExceptions: true,
  };
  const resp = UrlFetchApp.fetch(cfg.baseUrl + '/' + path, options);
  const code = resp.getResponseCode();
  let body;
  try {
    body = JSON.parse(resp.getContentText());
  } catch (e) {
    throw new Error(`SchooLink API returned non-JSON (HTTP ${code}): ${resp.getContentText()}`);
  }
  if (code >= 400 || body.success === false) {
    const msg = (body.data && body.data.message) || resp.getContentText();
    throw new Error(`SchooLink API error (HTTP ${code}): ${msg}`);
  }
  return body;
}

function schoolinkGetUsers_() {
  return schoolinkRequest_('api/getUsers', {}).data;
}

/**
 * Sends one notice to one set of usernames who all receive the SAME body.
 * Overdue notices are personalised per student, so callers normally pass
 * a single username per call — see Sender.gs.
 */
function schoolinkSendNotice_(usernames, title, bodyHtml) {
  const cfg = getConfig_();
  return schoolinkRequest_('api/sendNoticeMessage', {
    messageTypeID: cfg.messageTypeId,
    title: title,
    body: bodyHtml,
    usernames: usernames,
  });
}

/**
 * TODO: confirm with vendor how to obtain messageID — the sendNoticeMessage
 * success response in the spec (v1.0, p.23) does not include one, but
 * getMessageReports requires it. Test against the real API and update this
 * once confirmed.
 */
function schoolinkGetMessageReports_(messageId) {
  return schoolinkRequest_('api/getMessageReports', { messageID: messageId }).data;
}
