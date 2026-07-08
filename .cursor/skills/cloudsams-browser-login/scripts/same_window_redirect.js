// CDP Runtime.evaluate payload — run on https://clo.edb.gov.hk/ while logged in.
// POST /RedirectToApp in same tab (bypasses CLO popup WebSAMSRedirect).
(() => {
  const WEB_SAMS_ID = "840"; // CHW: CARMEL HOLY WORD (524573000133)
  const token = document.querySelector('input[name="__RequestVerificationToken"]')?.value;
  if (!token) {
    return { error: "no __RequestVerificationToken — open clo.edb.gov.hk while logged in" };
  }
  const form = document.createElement("form");
  form.method = "post";
  form.action = "/RedirectToApp";
  form.target = "_self";
  for (const [name, value] of [
    ["webSAMS_Id", WEB_SAMS_ID],
    ["__RequestVerificationToken", token],
  ]) {
    const h = document.createElement("input");
    h.type = "hidden";
    h.name = name;
    h.value = value;
    form.appendChild(h);
  }
  document.body.appendChild(form);
  form.submit();
  return { ok: true, webSAMS_Id: WEB_SAMS_ID };
})();
