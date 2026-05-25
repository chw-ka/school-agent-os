"""Paragraph ranges for F5 ICT Exam02 乙／丙 slots (24_25 template layout)."""

from __future__ import annotations

# slot_id -> (start_para, end_para_inclusive, marks)
WRITTEN_SLOT_PARAGRAPHS: dict[str, tuple[int, int, int]] = {
    "b-01": (313, 322, 4),
    "b-02": (323, 335, 5),
    "b-03": (336, 353, 4),
    "b-04": (354, 376, 4),
    "b-05": (377, 393, 4),
    "b-06": (394, 422, 9),
    "c-01": (425, 439, 6),
    "c-02": (440, 456, 4),
    "c-03": (457, 481, 4),
    "c-05": (496, 540, 6),
    "c-06": (541, 565, 7),
    "c-07": (566, 594, 7),
    "c-08": (595, 624, 6),
}

PART_B_RANGE = (313, 422)
PART_C_RANGE = (423, 624)
