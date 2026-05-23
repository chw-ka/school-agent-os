#!/usr/bin/env python3
"""Patch MCQ content/answers in Exam02 spec + DOCX (support content, dedupe 販賣機)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(root / "shared-tools" / "paper-generator"))
sys.path.insert(0, str(root / "shared-tools" / "paper-formatter"))

from docx import Document
from f5_ict_blueprint_db_web import apply_mcq, mcq_blocks

spec_path = Path(__file__).resolve().parent / "25_26_S5_ICT_Exam02.spec.json"
docx_path = Path(__file__).resolve().parents[1] / "WrittenExam" / "25_26_S5_ICT_Exam02.docx"

PATCHES: dict[int, list[str]] = {
    6: [
        "下列哪個以 8 位元二進制補碼表示數字的加法運算，會引至上溢錯誤？",
        "",
        "",
        "",
        "",
        "",
        "\tA.\t0000 0010 + 0011 1100",
        "\tB.\t0100 0010 + 0000 0001",
        "\tC.\t1001 1100 + 1111 0110",
        "\tD.\t1011 1010 + 1100 0100",
    ],
    8: [
        "需要多少位元才能表示一個 8x8 的黑白像素圖像？",
        "",
        "",
        "",
        "",
        "",
        "\tA.\t64",
        "\tB.\t64^2",
        "\tC.\t8^2",
        "\tD.\t2^64",
    ],
    7: [
        "以下試算表顯示了產品零售價的計算。C4 中的公式是什麼，以便可以複製到 C5 及其下的儲存格？",
        "",
        "\t\tA\t\t利潤\t12.5%\t\tB\t\t成本\t\tC\t\t零售價",
        "\t\t4\t\t電腦\t8,000\t\t5\t\t電視\t9,000\t\t6\t\t平板電腦\t5,000",
        "\tA.\t=$B$4*(1+$B1)",
        "\tB.\t=$B$4*(1+B$1)",
        "\tC.\t=$B$4*(1+B1)",
        "\tD.\t=$B$4*(1+$B$1)",
    ],
    10: [
        "設計了 M1 和 M2 兩個算法，在自動販賣機內以每 5 個積分輸出一罐汽水。N 代表積分數量。假設 N = 0。以下哪句是正確的？",
        "M1（後測試）：N ← N - 5；輸出一罐汽水；重複直至 N ≤ 4　M2（前測試）：當 N > 4 執行 N ← N - 5、輸出一罐汽水",
        "\tA.\t兩個算法都輸出一罐汽水",
        "\tB.\t只有 M1 輸出一罐汽水",
        "\tC.\t只有 M2 輸出一罐汽水",
        "\tD.\t兩個算法都不會輸出任何汽水",
    ],
    19: [
        "在一般情況下，P、Q 和 R 會是什麼？",
        "用戶 → P → Q → 電腦；R 位於 Q 與電腦之間",
        "\tA.\tP: 應用軟件, Q: 操作系統, R: 硬件",
        "\tB.\tP: 應用軟件, Q: 硬件, R: 操作系統",
        "\tC.\tP: 操作系統, Q: 硬件, R: 應用軟件",
        "\tD.\tP: 硬件, Q: 應用軟件, R: 操作系統",
    ],
    21: [
        "在下列算法中，輸入什麼值不會輸出「完成！」？",
        "",
        "輸入 N",
        "flag ← TRUE",
        "當 flag = TRUE 執行：如果 (N/4) 的餘數 > 0 則 flag ← FALSE",
        "輸出「完成！」",
        "\tA.\t4",
        "\tB.\t2",
        "\tC.\t6",
        "\tD.\t1",
    ],
    23: [
        "下列算法的輸出是什麼？",
        "X ← 9　Y ← 2",
        "重複",
        "   輸出 (X / Y) 的餘數；X ← (X / Y) 的整數部分",
        "直至 X = 0",
        "\tA.\t101",
        "\tB.\t111",
        "\tC.\t10",
        "\tD.\t1001",
    ],
    25: [
        "在以下試算表的 B6 內，輸入了一條基於 B2:B4 來計算班費的公式。同學希望可以縮減學業預算來限制班費為 $1,000。",
        "",
        "當使用「目標搜尋」功能來作「假設」分析時，需要採用下列哪一組數據？",
        "\t\tA\t\t\t\tB",
        "\t1\tS6 開支 (30 名同學)\t$",
        "\t2\t參考書 6,000　3\t影印費 900　4\t遊學團預算 30,000",
        "\t6\t每名同學班費 1,230",
        "",
        "\tA.\t目標儲存格: $B$4, 目標值: 1000, 變數儲存格: $B$6",
        "\tB.\t目標儲存格: $B$6, 目標值: 1000, 變數儲存格: $B$4",
        "\tC.\t目標儲存格: $B$4, 目標值: 30000, 變數儲存格: $B$6",
        "\tD.\t目標儲存格: $B$6, 目標值: 30000, 變數儲存格: $B$4",
    ],
    27: [
        "下圖顯示了「輸入—處理—輸出」周期的基本概念。X 和 Y 是什麼？",
        "輸入 → 處理 → 輸出；X：處理 → 輸入；Y：處理 → 輸出",
        "\tA.\tX: 互聯網, Y: 網絡設備",
        "\tB.\tX: 數據庫, Y: 變數",
        "\tC.\tX: 程式, Y: 儲存器",
        "\tD.\tX: 統一碼, Y: 二進制數字",
    ],
    29: [
        "這演算法的目的是什麼？",
        "j ← 0　輸入 N　當 N <> 888 執行 j ← j + N、輸入 N　輸出 j",
        "\tA.\t找出最大的輸入數值",
        "\tB.\t計算輸入數值的總和",
        "\tC.\t計算輸入數值的平均值",
        "\tD.\t計算輸入數值的次數",
    ],
}

ANSWERS = {
    "mcq-06": "A",
    "mcq-08": "D",
    "mcq-10": "B",
    "mcq-21": "A",
    "mcq-23": "D",
    "mcq-25": "B",
    "mcq-29": "B",
}


def main() -> int:
    if not spec_path.exists():
        print(f"No spec at {spec_path}; patching DOCX only.")
        spec = {"items": [], "meta": {}}
    else:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    for item in spec["items"]:
        mcq_no = int(item["id"].split("-")[1])
        if mcq_no in PATCHES:
            item["text"] = "\n".join(PATCHES[mcq_no])
        if item["id"] in ANSWERS:
            item["answer"] = ANSWERS[item["id"]]

    # Q6 A (補碼), Q8 D (點陣圖), Q23 D (除法 trace) — replaces duplicate 販賣機 variants
    spec["meta"]["mcq_answers"] = "CBBDAADBCBDCACAABDDABDBDDBDACA"
    if spec_path.exists() or spec.get("items"):
        spec_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    doc = Document(str(docx_path))
    blocks = mcq_blocks(doc)
    payload: list[list[str]] = []
    for i in range(1, 31):
        if i in PATCHES:
            row = PATCHES[i]
        else:
            start, end = blocks[i - 1]
            row = [doc.paragraphs[j].text for j in range(start, end)]
        start, end = blocks[i - 1]
        if end - start != len(row):
            raise RuntimeError(f"mcq-{i:02d}: span {end - start} != patch {len(row)}")
        payload.append(row)

    apply_mcq(doc, blocks, payload)
    doc.save(str(docx_path))
    print(f"Updated {spec_path}")
    print(f"Updated {docx_path}")
    print("Patched MCQs:", sorted(PATCHES))
    print("MCQ key:", spec["meta"]["mcq_answers"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
