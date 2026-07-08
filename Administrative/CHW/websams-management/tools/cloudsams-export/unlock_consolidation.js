// Run via browser CDP Runtime.evaluate (async)
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const levels = ["S1", "S2", "S3", "S4", "S5", "S6"];
  const rowIdxs = [0, 1, 2]; // T1A1, T1A2, T1
  const results = [];

  async function unlockRow(rowIdx) {
    const tr = jQuery("table tbody tr").eq(rowIdx);
    if (!tr.length) return "no row";
    const cb = document.getElementById(
      "fmAsrConsolidationConsolidationSearch:tableConso_" + rowIdx + "_checkbox"
    );
    if (cb && cb.getAttribute("aria-checked") !== "true") cb.click();
    const before = tr.text().replace(/\s+/g, " ").trim();
    if (!before.includes("鎖定")) return { before, after: before, skipped: true };

    const scopeIdx = before.includes("其他鎖定") ? 1 : before.includes("全部鎖定") ? 2 : 0;
    document.getElementById("fmAsrConsolidationConsolidationSearch:unlockScopeButton").click();
    await sleep(1200);
    const radio = document.getElementById(
      "fmAsrConsolidationConsolidationSearch:j_idt186:" + scopeIdx
    );
    if (radio) radio.click();
    const btn = document.getElementById("fmAsrConsolidationConsolidationSearch:unlockButton");
    if (btn) btn.click();
    await sleep(2000);
    const after = jQuery("table tbody tr").eq(rowIdx).text().replace(/\s+/g, " ").trim();
    return { before, after, scopeIdx, skipped: false };
  }

  for (const lvl of levels) {
    PF("clsLvl").selectValue(lvl, false);
    await sleep(600);
    document.getElementById("fmAsrConsolidationConsolidation:pnlSearch:searchButton").click();
    await sleep(2800);
    for (const rowIdx of rowIdxs) {
      const r = await unlockRow(rowIdx);
      results.push({ lvl, rowIdx, ...r });
    }
  }
  return results;
})();
