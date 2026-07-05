# CloudSAMS Migration Plan — Student Report (2026–27 Term 1)

**Target go-live**: Term 1, 2026–27 (September 2026)
**Current system**: Legacy MS SQL Server (`db25_26`) + custom WebSAMS intranet
**Target system**: CloudSAMS (EDB cloud platform)

---

## 1. What Is Moving

| Priority | Data Category | Legacy Source Tables | CloudSAMS Module (TBD) |
|----------|---------------|----------------------|------------------------|
| **P0** | Subject scores (test/regular/exam/grade, exempt, absent flags) | `tblStudentPaperScore` | Academic Results |
| **P0** | Subject attitudes (lesson performance, homework diligence) | `tblStudentAttitude` | Subject Attitudes |
| **P0** | Conduct (5 dimensions per term) | `tblStudentConduct` | Conduct |
| **P0** | Class teacher comments (4 slots per term) | `tblStudentComment` | Comments |
| **P0** | Attendance & discipline (absences, lateness, demerit) | `tblStudentDiscipline` | Attendance/Discipline |
| **P0** | Awards & merits (large merit, small merit, etc.) | `tblStudentAward`, `tblStudentReward` | Awards |
| **P0** | Report remarks | `tblStudentReportRemark` | Report Remarks |
| **P1** | ECA / service / class posts | `tblStudentClassPost`, `tblStudentUnitPost`, `tblStudentSubjectPost` | ECA/Service |
| **P2 (optional)** | Report card generation (PDF output) | `tblZStudentReport2` → Word mail merge | CloudSAMS Report Card |
| **P3 (nice-to-have)** | Historical archive (past years) | `tblYStudentScore`, `tblYStudentPaperScore`, etc. | Historical Data |

**Note**: Student and subject enrollment data (`tblStudent`, `tblStudentSubject`) — **confirmed 2026-07-05**: new S1/P1 intake arrives automatically via EDB's central allocation feed, but this has only been verified for *new* intake, not the full continuing S1–S6 roster. If continuing students are missing, there's a real bulk-import fallback (STU module → 註冊 → 註冊檔案上載, Excel template, <100 rows/file recommended). Still need to log in and check the actual roster — see `field-mapping.md` open items.

---

## 2. What Is NOT Moving (This Cycle)

- Score calculation logic (`tblZStudentRank2` computation) — CloudSAMS is expected to handle ranking internally
- The Word mail-merge report generation pipeline — this is P2/optional; keep it running in parallel until CloudSAMS report output is verified

---

## 3. Phases and Timeline

### Phase 0 — Discovery (Week 1–2, July 2026)

**Goal**: Understand what CloudSAMS can accept before writing a single line of code.

- [x] Log into CloudSAMS with admin credentials (done 2026-07-05, browser session)
- [x] Official EDB AUM manuals already downloaded to `cloudsams-manuals/` (all modules, from cdrcloudsams.edb.gov.hk) — use these instead of reverse-engineering the UI where possible
- [ ] Explore all modules relevant to student reports (Academic Results, Conduct, Comments, Awards, ECA, Attendance) — **Academic Results (ASR) done, see `field-mapping.md`; Conduct/Awards/Attendance/ECA still open**
- [ ] For each module, document:
  - What fields exist
  - What the field types/limits are
  - Whether bulk import is supported (Excel/CSV template? API?) — **confirmed for ASR: Excel/ZIP, see `field-mapping.md` for the batch-number/filename mechanism**
  - What format the import template uses
- [ ] Download all available import templates from EDB/CloudSAMS — **blocked: 2026-27 school year doesn't exist in CloudSAMS yet (needs 策劃新學年 first — separate, bigger decision). Attempted confirming the CURRENT year's (2025-26) scheme instead (2026-07-05, with go-ahead) — validation failed: 科目滿分及比重 missing for 公民經濟與社會 (S1/S2) and 普通電腦科 (S3) across all periods. Real setup gap, see `field-mapping.md`. Nothing was locked.**
- [ ] Check whether student enrollment and subject enrollment are already present in CloudSAMS (from EDB feeds)
- [ ] Clarify with EDB support: what migration path exists for schools moving from WebSAMS?

**Output**: Completed `field-mapping.md` (see Section 4 below) with CloudSAMS column filled in. **Live findings now in `field-mapping.md` — see that file for the ASR import/export mechanism, which changes the Phase 2 approach (see note there).**

**Blocker**: Nothing else can proceed until this phase is done.

---

### Phase 1 — Field Mapping & Gap Analysis (Week 2–3, July 2026)

**Goal**: Map every legacy field to its CloudSAMS equivalent. Identify gaps.

- [ ] Fill in `field-mapping.md` using findings from Phase 0
- [ ] For each gap (legacy field with no CloudSAMS equivalent), decide:
  - **Drop**: Not needed in CloudSAMS
  - **Map to closest field**: Acceptable substitute
  - **Use custom/remarks field**: Workaround
  - **Block**: Must be resolved before go-live
- [ ] Confirm with CM (Curriculum Master) / ES / PY which fields are non-negotiable
- [ ] Document any workflow changes teachers will need to make (e.g., if attitude entry screens differ)

**Output**: Signed-off field mapping + gap decision list

---

### Phase 2 — Extraction Scripts (Weeks 3–5, Late July–Early August 2026)

**Goal**: Build Python tools to export each data category from legacy SQL into CloudSAMS import format.

Add scripts to `_platform/shared-tools/student-report/cloudsams-export/`:

| Script | Source | Output |
|--------|--------|--------|
| `export_scores.py` | `tblStudentPaperScore` | CloudSAMS Academic Results import format |
| `export_attitudes.py` | `tblStudentAttitude` | CloudSAMS Subject Attitudes import format |
| `export_conduct.py` | `tblStudentConduct` | CloudSAMS Conduct import format |
| `export_comments.py` | `tblStudentComment` | CloudSAMS Comments import format |
| `export_discipline.py` | `tblStudentDiscipline` | CloudSAMS Attendance import format |
| `export_awards.py` | `tblStudentAward`, `tblStudentReward` | CloudSAMS Awards import format |
| `export_eca.py` | `tblStudentClassPost`, `tblStudentUnitPost` | CloudSAMS ECA/Service import format |

Each script must:
- Accept `--term`, `--form`, `--year` parameters
- Output deterministic CSV/Excel in the exact CloudSAMS import template format
- Include a dry-run mode that validates without writing files
- Work with anonymized test data

**Note**: Do NOT commit any output files containing real student data.

---

### Phase 3 — Test Migration (Weeks 5–7, August 2026)

**Goal**: Import test data into CloudSAMS staging/sandbox and verify correctness.

- [ ] Generate anonymized test dataset (replace real names/IDs with synthetic equivalents)
- [ ] Run all export scripts against test dataset
- [ ] Import into CloudSAMS test environment
- [ ] Spot-check at least 5 students per form (S1–S5) across all data categories
- [ ] Verify score calculation and ranking in CloudSAMS matches legacy system output
- [ ] Test the report card output (if CloudSAMS generates it)
- [ ] Fix errors in export scripts and re-import

**Validation checklist**:
- [ ] All students present (count matches)
- [ ] No missing subject score rows
- [ ] Exempt/absent flags transferred correctly
- [ ] Conduct 5 dimensions all present
- [ ] Comments not truncated
- [ ] Awards correct
- [ ] ECA posts correct
- [ ] Ranking calculation consistent with legacy

---

### Phase 4 — Production Migration (Late August 2026)

**Goal**: Import real 2026–27 Term 1 starting data into CloudSAMS production.

- [ ] Final check: student enrollment confirmed in CloudSAMS
- [ ] Run export scripts against live `db26_27` (or current year DB)
- [ ] Import into CloudSAMS production — one category at a time, smallest to largest
- [ ] Verify import logs for errors
- [ ] Spot-check across all forms before opening to teachers
- [ ] Configure teacher access/permissions in CloudSAMS

**Rollback plan**: Keep legacy MS SQL system in read-only mode until end of Term 1. If CloudSAMS data is found to be incorrect during term, legacy data is available for reference and re-import.

---

### Phase 5 — Report Generation Validation (Optional, During Term 1)

If CloudSAMS generates report cards, evaluate before committing:

- [ ] Generate a CloudSAMS report card for one class
- [ ] Compare against legacy Word/PDF output field by field
- [ ] Decide: use CloudSAMS output, hybrid, or keep legacy pipeline for 2026–27

The legacy Word mail-merge pipeline should remain functional as fallback.

---

### Phase 6 — Historical Archive (After Term 1, Nice-to-have)

Historical data from `tblY*` tables (55,000+ score rows, 673,000+ paper score rows) would be bulk-imported after Term 1 go-live is stable. Requires CloudSAMS to have a historical import path — confirm with EDB.

---

## 4. Field Mapping Document

Create as a separate file: `field-mapping.md`

Structure:

```
Data Category: Subject Scores
Legacy table: tblStudentPaperScore
Key: (idStudent, idPaper)

| Legacy Field    | Type    | CloudSAMS Field | CloudSAMS Module | Notes                   |
|-----------------|---------|-----------------|------------------|-------------------------|
| score_test_2    | decimal | TBD             | TBD              | Test/assessment score   |
| score_regular_2 | decimal | TBD             | TBD              | Classwork/regular score |
| score_exam_2    | decimal | TBD             | TBD              | Exam score              |
| grade_exam_2    | char    | TBD             | TBD              | Grade (PED/MUS)         |
| flgIgnore_2     | bit     | TBD             | TBD              | Exempt flag             |
| flgAbsent_2     | bit     | TBD             | TBD              | Absent flag             |
...
```

Fill in the TBD columns after Phase 0.

---

## 5. Key Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| CloudSAMS doesn't support 5 conduct dimensions as structured scores — **confirmed 2026-07-05**, not just a risk: CloudSAMS conduct is fundamentally a point-accumulation model (merit/demerit levels in ANP module), copied into the report card via a button, not independently importable | High (confirmed) | High | Needs a Phase 1 decision with CM/ES/PY — see options in `field-mapping.md` Conduct section |
| Awards/Discipline (ANP module) has no bulk file import at all — only UI batch-processing (search+select+apply-one-record) — **confirmed 2026-07-05** | High (confirmed) | Medium | Decide: curate a subset, browser-automate the batch UI, or ask EDB support about an API |
| Student/subject enrollment missing in CloudSAMS | Medium | High | Check in Phase 0; understand EDB data feed schedule |
| CloudSAMS import format changes or is poorly documented | Low | Medium | Contact EDB support directly; ask for import guide |
| Timeline too short if gaps are significant | Medium | High | Start Phase 0 immediately; de-scope historical archive |
| Teachers unfamiliar with CloudSAMS data entry | High | Medium | Run a briefing session before Term 1; document differences from legacy |

---

## 6. Immediate Next Steps (This Week)

1. **Get CloudSAMS admin access** — confirm login credentials work
2. **Explore CloudSAMS** — spend 2–3 hours clicking through all academic/conduct/ECA modules
3. **Start `field-mapping.md`** — document what fields exist in CloudSAMS for each P0 category
4. **Contact EDB** — ask for CloudSAMS migration guide and import templates for WebSAMS schools

---

## 7. Related Files

| Resource | Path |
|----------|------|
| Legacy pipeline overview | `../student-report/guides/0_總覽_中一至中五下學期成績表流程.md` |
| Legacy table relationships | `../student-report/reference/STUDENT_REPORT_SQL_TABLE_RELATIONSHIPS.md` |
| Score entry fields detail | `../student-report/guides/3_入分_同事輸入與資料表.md` |
| Export tools (to be created) | `../../shared-tools/student-report/cloudsams-export/` |
| Field mapping (to be created) | `field-mapping.md` (this directory) |
