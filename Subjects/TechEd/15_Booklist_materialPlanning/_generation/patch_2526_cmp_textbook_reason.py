"""Patch 25_26_S2-3CMP_更改課本原因.docx — point 2 + S3 publisher wording."""
from __future__ import annotations

from pathlib import Path

from docx import Document

ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "25_26_S2-3CMP_更改課本原因.docx"

S2_OLD_PREFIX = "參考教育局的適用書目表，出版科技教育課程下相關課題之出版社有"
S3_OLD_PREFIX = S2_OLD_PREFIX

S2_NEW = (
    "參考教育局的適用書目表，出版科技教育課程的出版社包括「香港大學電機電子工程系」（下稱出版社A）"
    "及「卓思出版社有限公司」（下稱出版社B）。本校中二「生成式人工智能」單元內容緊貼現時科技發展，"
    "屬新興課題；就相關內容而言，出版社A及出版社B目前均未有載列於適用書目表、且能完全配合本校課程編排"
    "之獲批課本。由於教材送審與批核需時，短期內難以趕及編課需要，此與科技教育範疇更新迅速有關。"
    "基於上述情況，學校現申請繼續採用出版社A透過 iClass 提供之《明德電腦——生成式人工智能》（2026版本）；"
    "該課本內容切合本校課程安排，供學生上課及課後使用，直至適用書目表有相應獲批課本可供選用。"
)

S3_NEW = (
    "參考教育局的適用書目表，出版科技教育課程的出版社包括「香港大學電機電子工程系」（下稱出版社A）"
    "及「卓思出版社有限公司」（下稱出版社B）。本校中三「Python 與人工智能」單元同樣涵蓋程式設計、"
    "電腦視覺及人工智能應用等發展迅速的內容；就相關課題而言，出版社A及出版社B目前均未有載列於適用書目表、"
    "且能完全配合本校初中課程之獲批課本。教材送審與批核需時，難以配合校本教學進度，"
    "此與科技發展快於教材審批周期有關。基於上述情況，學校現申請繼續採用《初中 AI and Python》（2023版本）"
    "（iClass eBook）；送呈書單之出版社為「香港大學電子學習發展實驗室」，章節及實驗活動與校本教學進度相若，"
    "供學生上課、課後閱讀及溫習，直至適用書目表有相應獲批課本可供選用。"
)

S3_APPLY_OLD = "現申請下年度（2026-2027年度）使用卓思出版社有限公司（iClass）之電子課本，包括："
S3_APPLY_NEW = (
    "現申請下年度（2026-2027年度）使用《初中 AI and Python》（2023版本）"
    "（iClass eBook；送呈書單之出版社為香港大學電子學習發展實驗室），包括："
)


def patch_paragraphs(doc: Document) -> int:
    n = 0
    for p in doc.paragraphs:
        t = p.text
        if t.startswith(S2_OLD_PREFIX) and "生成式人工智能" in t:
            p.text = S2_NEW
            n += 1
        elif t.startswith(S3_OLD_PREFIX) and "Python 與人工智能" in t:
            p.text = S3_NEW
            n += 1
        elif t == S3_APPLY_OLD:
            p.text = S3_APPLY_NEW
            n += 1
    return n


def main() -> None:
    doc = Document(str(DOCX))
    changed = patch_paragraphs(doc)
    if changed < 2:
        raise SystemExit(f"Expected >=2 paragraph updates, got {changed}")
    doc.save(DOCX)
    print(f"Patched {DOCX} ({changed} paragraphs)")


if __name__ == "__main__":
    main()
