# Student Report SQL Table Relationships

This document summarizes the relationships inferred from the SQL scripts in
`../sql/` and from read-only metadata queries against the current
`mssql-legacy` database.

No SQL script was edited during this analysis.

## Scope Reviewed

- All `*.sql` files under `../sql/` were scanned for table, view,
  procedure, insert, update, join, and select references.
- Key representative scripts were read in detail:
  - `02 Retrieve Assessment Results/Calculate Assessment.sql`
  - `04 Make Summaries/Calculate Score_special_edition.sql`
  - `06 Make Reports/_Report_2023_S123.sql`
  - `05 Analyse/_獎項計算.sql`
  - `07 Portfolio/Update Student Portfolio 2nd term.sql`
- Live metadata was checked through `mssql-legacy` using read-only `SELECT`
  queries against `INFORMATION_SCHEMA`, `sys.foreign_keys`, `sys.indexes`, and
  selected view definitions.

## High-Level Data Flow

The report system is a staged pipeline:

1. Current student/class/subject setup defines who should receive report rows.
   The central path is `tblStudent -> tblClass -> tblForm`, with student subject
   enrollment in `tblStudentSubject`.
2. Assessment and paper score scripts populate or update paper-score staging:
   `tblAssessment2`, `tblAssessmentClass2`, and `tblStudentAssessment2` feed
   `tblFormPaperScore` and `tblStudentPaperScore`.
3. Score calculation scripts derive normalized, term, yearly, class-rank, and
   form-rank rows into `tblZStudentRank2`.
4. Report-generation scripts flatten student, score, attitude, conduct,
   discipline, service, award, and remark data into `tblZStudentReport2`.
5. Portfolio scripts archive the calculated report data into yearly `tblY*`
   tables such as `tblYStudentScore`, `tblYStudentPaperScore`,
   `tblYStudentConduct`, and `tblYStudentUnitPost`.
6. Analysis scripts mostly read `vwStudent`, `tblZStudentRank2`, and conduct or
   discipline tables to produce award, scholarship, ranking, and checking lists.

## Core Tables

`tblStudent`

- Primary key: `idStudent`.
- Declared relationships:
  - `class -> tblClass.class`
  - `idHouse -> tblUnit.idUnit`
- Report scripts treat this as the root student entity. Many tables are keyed
  directly by `idStudent`.

`tblClass`, `tblForm`, `tblFormGroup`

- `tblClass.class` maps each class to a form.
- `tblForm.form` maps each form to a `formGroup`.
- Most report joins resolve form through `vwStudent` or explicit
  `tblStudent -> tblClass -> tblForm` joins.

`tblSubject` and `tblPaper`

- `tblSubject.idSubject` is the subject master key.
- `tblPaper` has composite primary key `(idPaper, formGroup)`.
- Declared relationships:
  - `tblPaper.formGroup -> tblFormGroup.formGroup`
  - `tblPaper.idSubject -> tblSubject.idSubject`
- Script convention:
  - If `tblPaper.idSubject = tblPaper.idPaper`, the paper is also the subject
    row.
  - If `tblPaper.idSubject` differs from `tblPaper.idPaper`, multiple papers
    roll up to one subject.
  - If `tblPaper.idSubject IS NULL`, the paper can be a compound/master paper
    selected through `vwStudentPaper`.

`tblStudentSubject`

- Primary key: `(idStudent, idSubject)`.
- Declared relationships:
  - `idStudent -> tblStudent.idStudent`
  - `idSubject -> tblSubject.idSubject`
- Includes per-term flags `flgTerm1` and `flgTerm2`.
- `auxiliaryClass` can override the student's real class for subject grouping.

## Important Views

`vwStudent`

- Wraps `tblStudent` joined to `tblClass`.
- Adds `form` and `formGroup` while preserving class, number, name, gender, and
  term flags.
- Most scripts use this instead of joining `tblStudent` and `tblClass`
  repeatedly.

`vwStudentSubject`

- Wraps `tblStudent`, `tblClass`, and `tblStudentSubject`.
- Uses `tblStudentSubject.auxiliaryClass` when present.
- This is the common source for student-subject eligibility.

`vwStudentPaper`

- Expands student-subject enrollment into reportable papers via `tblPaper`.
- Provides the bridge from student-subject records to paper-level score rows.
- This is the main driving view for score calculation and report subject rows.

`vwStudentPaperScore`

- Unpivots `tblStudentPaperScore` term-specific columns into `(term, scoreTest,
  scoreRegular, scoreExam, gradeExam, flgIgnore, flgAbsent)`.

`vwFormPaperWeight`

- Unpivots `tblFormPaperWeight` term-specific columns into `(term, weightTest,
  weightRegular, weightExam)`.

`vwFormPaperScore`

- Unpivots `tblFormPaperScore` term-specific maximum scores into `(term,
  scoreTest, scoreRegular, scoreExam)`.

`vwStudentAssessment2`

- Joins student subject enrollment, assessment class eligibility, assessment
  metadata, form-term dates, and student assessment marks.
- It computes `credit` and feeds `stpCalculateAssessment`.

## Score Calculation Relationships

`tblFormPaperWeight`

- Primary key: `(form, idPaper)`.
- Stores paper weight settings for both terms and total weighting.
- Scripts join it to `vwStudentPaper` by `(form, idPaper)`.

`tblFormPaperScore`

- Stores maximum available test, regular, and exam scores by form and paper.
- `stpCalculateAssessment` inserts missing `(form, idPaper)` rows when
  assessment results imply a subject needs a paper-score row.
- `vwFormPaperScore` exposes term-shaped rows for calculation scripts.

`tblStudentPaperScore`

- Primary key: `(idStudent, idPaper)`.
- Declared relationship: `idStudent -> tblStudent.idStudent`.
- No declared foreign key to `tblPaper` was found, but scripts consistently
  join `idPaper` to `tblPaper.idPaper` or `vwStudentPaper.idPaper`.
- Stores raw/entered scores, grades, ignore flags, absent flags, and remark
  flags for both terms.

`tblZStudentRank2`

- Primary key: `(idStudent, form, idPaper, flgStandard, section, term)`.
- No declared foreign keys were found, but scripts infer:
  - `idStudent -> tblStudent.idStudent`
  - `idPaper -> tblPaper.idPaper`, except `idPaper = ''` is used for aggregate
    average rows.
- `section` values used by scripts:
  - `R`: regular or daily score
  - `E`: exam score
  - `O`: overall score
- `term` values used by scripts:
  - `1`: first term
  - `2`: second term
  - `0`: yearly or final aggregate
- `flgStandard = 0` means original scaled score. `flgStandard = 1` means
  standard-score row.
- Score scripts insert rows here, then update `rankClass` and `rankForm`.

## Assessment Relationships

`tblAssessment2`

- Primary key: `idAssessment`.
- Declared relationship: `idSubject -> tblSubject.idSubject`.
- Stores assessment metadata, score scale, credit, date range, and completion
  status.

`tblAssessmentClass2`

- Maps assessment rows to classes by `(idAssessment, class)`.
- Scripts join it to `tblAssessment2` and `vwStudentSubject2` to determine
  which students are expected to have assessment marks.

`tblStudentAssessment2`

- Primary key: `(idStudent, idAssessment)`.
- Declared relationship: `idStudent -> tblStudent.idStudent`.
- Used by `vwStudentAssessment2` to compute per-assessment credit.
- Current metadata check showed `tblStudentAssessment2` has zero rows, while
  `tblAssessment2` has 919 rows. This means current assessment-to-paper score
  generation may be dormant or data may live elsewhere for the active year.

`stpCalculateAssessment`

- Inserts missing rows into `tblFormPaperScore` and `tblStudentPaperScore`.
- Calculates a 0-100 assessment-derived paper score from
  `vwStudentAssessment2`.
- Updates either `score_test_1` or `score_test_2` in `tblStudentPaperScore`.
- Marks relevant `tblAssessment2` rows as completed, then later script snippets
  reset `flgCompleted` for a date range.

## Report Output Relationships

`tblZStudentReport2`

- Primary key: `(term, Class, Num)`.
- Contains flattened report output with student identity, up to 27 subject rows,
  lesson/assessment attitude columns, average, class/form ranks, attendance,
  conduct, comments, service, remarks, and indicators.
- Report procedures delete rows for a form and term, then insert master rows and
  update each output field group from temporary global tables and source tables.
- It stores `idStudent`, but the declared primary key is still class/number
  based. Treat `idStudent` as the logical identity link.

Report procedure sources:

- Student header:
  - `vwStudent`
  - `tblStaffClass`
  - `tblStaff`
- Subject result rows:
  - `vwStudentPaper`
  - `tblZStudentRank2`
  - `tblStudentPaperScore`
  - `tblPaper`
  - `tblStudentAttitude`
  - `tblAttitude`
- Rank and average:
  - aggregate rows in `tblZStudentRank2` where `idPaper = ''`, `section = 'O'`
- Attendance and lateness:
  - `tblStudentDiscipline`
- Conduct:
  - `tblStudentConduct`
- Class teacher comments:
  - `tblStudentComment`
  - `tblComment`
- Service and ECA:
  - `tblStudentClassPost`
  - `tblClassUnit`
  - `tblStudentUnitPost`
  - `tblUnit`
  - `tblPost`
  - `tblECAComment`
  - `tblStudentSubjectPost`
  - `tblSubject`
- Awards and remarks:
  - `tblStudentAward`
  - `tblStudentReward`
  - `tblStudentReportRemark`

## Conduct, Comment, Discipline, And Attitude Tables

`tblStudentAttitude`

- Primary key: `(idStudent, idSubject)`.
- Declared relationships:
  - `idStudent -> tblStudent.idStudent`
  - `idSubject -> tblSubject.idSubject`
  - lesson and assessment grades -> `tblAttitude.grade`
  - comment fields -> `tblAttitudeComment.idComment`
- Report scripts join by student and subject/paper to output lesson and
  assessment text.

`tblStudentConduct`

- Keyed by `idStudent`.
- Stores five conduct dimensions per term.
- Report scripts map term-specific columns into `Cnd01` through `Cnd05`.

`tblStudentComment`

- Keyed by `idStudent`.
- Stores four comment slots per term, either as comment IDs or custom text.
- Report scripts prefer custom text first, then overwrite from `tblComment`
  where comment IDs exist.

`tblStudentDiscipline`

- Keyed by `idStudent`.
- Stores absence, lateness, demerit, and homework flags per term.
- Used for report attendance fields and scholarship/award filtering.

`tblStudentReward`

- Keyed by `idStudent`.
- Stores merit counts by category and term.
- Report scripts convert counts into text such as large merit, small merit, and
  merit descriptions in `tblZStudentReport2.Rem`.

## Service, Post, And ECA Relationships

`tblStudentClassPost`

- Primary key: `(idStudent, idClassUnit, idPost)`.
- Declared relationships:
  - `idStudent -> tblStudent.idStudent`
  - `idComment -> tblECAComment.idComment`
- Scripts join `idClassUnit` to `tblClassUnit` and `idPost` to `tblPost`.

`tblStudentUnitPost`

- Primary key: `(idStudent, idUnit)`.
- Declared relationships:
  - `idStudent -> tblStudent.idStudent`
  - `(idUnit, idPost) -> tblUnitPost`
  - `idComment -> tblECAComment.idComment`
- Scripts also join directly to `tblUnit` and `tblPost`.
- `tblUnit.idUnitGroup = 7` is treated as service in S1-S3 reports.
- `tblUnit.idUnitGroup = 9` is treated as award-related in report generation.

`tblStudentSubjectPost`

- Primary key: `(idStudent, idSubject, idPost)`.
- Declared relationships:
  - `(idStudent, idSubject) -> tblStudentSubject`
  - `idPost -> tblSubjectPost.idPost`
  - `idComment -> tblECAComment.idComment`
- 2023 report logic moved subject leader information from service into ECA or
  remark-related sections because the service field had too little space.

## Portfolio / Yearly Archive Tables

The `07 Portfolio` scripts copy current-year report data into `tblY*` archive
tables. The active scripts are write scripts and should be treated carefully.

Important archive mappings:

- `tblZStudentRank2` aggregate rows -> `tblYStudentScore`
- `tblStudentConduct` -> `tblYStudentConduct`
- `tblStudentComment` -> `tblYStudentComment`
- `tblStudentDiscipline` -> `tblYStudentDiscipline`
- `tblStudentAward` -> `tblYStudentAward`
- `tblStudentReportRemark` -> `tblYStudentRemark`
- `vwStudentPaper` -> `tblYStudentPaperTerm`
- `tblPaper` -> `tblYPaper`
- `tblStudentAttitude` + `vwStudentSubject` -> `tblYStudentSubjectAttitude`
- `tblZStudentRank2` and `tblStudentPaperScore` -> `tblYStudentPaperScore`
- `tblStudentSubjectPost` -> `tblYStudentSubjectPost`
- `tblStudentUnitPost` -> `tblYStudentUnitPost`
- `tblStudentClassPost` -> `tblYStudentClassPost`

Current live row counts suggest the archive tables are long-lived:

- `tblYStudentScore`: 55,404 rows
- `tblYStudentPaperScore`: 673,020 rows

## Declared Versus Inferred Relationships

Several important report relationships are inferred by scripts rather than
declared as SQL Server foreign keys:

- `tblStudentPaperScore.idPaper -> tblPaper.idPaper`
- `tblZStudentRank2.idStudent -> tblStudent.idStudent`
- `tblZStudentRank2.idPaper -> tblPaper.idPaper`, except aggregate rows where
  `idPaper = ''`
- `tblZStudentReport2.idStudent -> tblStudent.idStudent`
- `tblZStudentReport2` subject columns are not normalized; they are fixed output
  slots populated from temporary result rows.
- Many `tblY*` archive tables carry `idStudent`, `idPaper`, `idSubject`,
  `idUnit`, and `idPost` values copied from current-year tables, but their
  archival purpose means relationships are mostly historical snapshots rather
  than live FK-driven joins.

## Operational Notes From The Scripts

- Most scripts are operational batch scripts, not only stored procedure
  definitions. Many include example executions and manual post-processing
  `UPDATE` statements for exceptional students, subjects, or report display
  issues.
- `tblZStudentRank2` is the most important derived table. If it is stale, report
  output and analysis scripts will be stale.
- `tblZStudentReport2` is a denormalized print/report table. It is not a good
  source for recomputing scores, but it is the source for final report output.
- Backup folders contain older versions of the same flow. They confirm the same
  model: student enrollment -> paper score -> rank table -> report table ->
  yearly archive.
- Some scripts reference older tables such as `tblZStudentRank`,
  `tblZStudentPaperRank`, and older backup procedures. These appear to be
  legacy predecessors of the current `tblZStudentRank2` flow.

## Current Live Row Count Snapshot

- `tblStudent`: 722
- `tblStudentSubject`: 9,886
- `tblStudentPaperScore`: 13,054
- `tblZStudentRank2`: 90,882
- `tblZStudentReport2`: 1,347
- `tblAssessment2`: 919
- `tblStudentAssessment2`: 0
- `tblStudentAttitude`: 8,740
- `tblStudentConduct`: 719
- `tblStudentComment`: 719
- `tblStudentDiscipline`: 722
- `tblStudentAward`: 90
- `tblYStudentScore`: 55,404
- `tblYStudentPaperScore`: 673,020

## Suggested Reading Order For Future Changes

1. Read `vwStudent`, `vwStudentSubject`, and `vwStudentPaper` definitions first.
2. Trace `Calculate Assessment.sql` only if assessment-derived test scores are
   in scope.
3. Trace the active score script for the relevant year or form to understand how
   `tblZStudentRank2` is populated.
4. Trace the active report script to see how `tblZStudentReport2` is flattened.
5. Trace portfolio scripts only when archiving to yearly `tblY*` tables is in
   scope.

