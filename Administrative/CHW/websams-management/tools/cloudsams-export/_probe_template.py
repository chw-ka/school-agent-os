import xlrd
from collections import Counter
from pathlib import Path

p = Path(
    r"c:\Users\localadmin\Projects\school-agent-os\Administrative\CHW\websams-management\cloudsams-templates\asr\_local\extracted-ws\DE_52457320260707_124_3_3_S1_1A.xls"
)
sh = xlrd.open_workbook(p).sheet_by_index(0)
hdr = sh.row_values(0)
for c in range(9, sh.ncols - 1):
    vals = [str(sh.cell_value(r, c)).strip() for r in range(1, sh.nrows)]
    print(hdr[c][-20:], dict(Counter(vals)))
print("--- rows with non-N.T. scores in template ---")
for r in range(1, sh.nrows):
    vals = {
        str(sh.cell_value(r, c)).strip()
        for c in range(9, sh.ncols - 1)
        if str(sh.cell_value(r, c)).strip()
    }
    if vals - {"N.T."}:
        print("row", r, int(sh.cell_value(r, 6)), vals)
