/*
  開放中一至中五「下學期」內聯網入分 — 預覽腳本
  =============================================
  用途：步驟 2 完成後、開放 studentNet/report 前，在 SSMS 先跑「一、預覽」確認。
  執行「二、寫入」前請備份或確認無其他同事同時改 tblFormInputControl。

  對應指引：guides/3b_內聯網開放入分與權限.md

  重要：tblFormInputControl 主鍵只得 form（每級一行），term 欄表示「而家開緊邊個學期入分」，
  唔係 (form, term) 各一行。開放下學期 = UPDATE term=2 + flgActiveSubject/Class=1，勿 INSERT。

  群組 7 Score Input Users：flgActive = 1 方可進 /studentNet/report/
*/

/* =============================================================================
   一、預覽（只讀 — 建議全部執行並保留結果）
   ============================================================================= */

-- 1.1 現況：各級各學期入分開關
SELECT form, term,
       flgTest, flgRegular, flgExam, flgConduct,
       flgActiveSubject, flgActiveClass, flgActiveAssessment
FROM dbo.tblFormInputControl
ORDER BY term, form;

-- 1.2 中一至中五是否仍指向上學期（term=1 → 開放時應改為 term=2）
SELECT form, term,
       flgActiveSubject, flgActiveClass,
       CASE WHEN term = 2 AND flgActiveSubject = 1 THEN N'OPEN'
            WHEN term = 2 AND flgActiveSubject = 0 THEN N'term2 but CLOSED'
            WHEN term = 1 THEN N'NEEDS UPDATE to term=2'
            ELSE N'CHECK' END AS status
FROM dbo.tblFormInputControl
WHERE form BETWEEN 1 AND 5
ORDER BY form;

-- 1.3 用戶群組（入分權限）
SELECT idUserGroup, nameChinese, flgActive
FROM dbo.tblUserGroup
WHERE idUserGroup IN (6, 7);

SELECT COUNT(*) AS score_input_users_in_group_7
FROM dbo.tblUser
WHERE idUserGroup = 7;

-- 1.4 下學期有任教、可受惠老師人數（form 1–5）
SELECT ss.form, COUNT(DISTINCT ss.idStaff) AS staff_with_term2_subject
FROM dbo.vwStaffSubject ss
WHERE ss.flgTeach = 1
  AND ss.flgTerm2 = 1
  AND ss.idSubject <> N'OTH'
  AND ss.form BETWEEN 1 AND 5
GROUP BY ss.form
ORDER BY ss.form;

-- 1.5 開放後應為（預期 form 1–5：term=2, flgActiveSubject=1, flgActiveClass=1）
SELECT form,
       CAST(2 AS tinyint) AS term_after,
       flgTest, flgRegular, flgExam, flgConduct,
       CAST(1 AS bit) AS flgActiveSubject_after,
       CAST(1 AS bit) AS flgActiveClass_after
FROM dbo.tblFormInputControl
WHERE form BETWEEN 1 AND 5
ORDER BY form;


/* =============================================================================
   二、寫入（確認預覽無誤後，逐段執行；建議先 BEGIN TRAN … ROLLBACK 試跑）
   ============================================================================= */

-- 2.1 開放下學期入分（中一至中五）
UPDATE dbo.tblFormInputControl
SET term = 2,
    flgActiveSubject = 1,
    flgActiveClass   = 1
WHERE form BETWEEN 1 AND 5;

-- 2.2 關閉中六下學期入分（form 6 可保持 term=2，靠 flgActive*=0 即可）
--     注意：教務 admin 帳（report admin:1）仍可能見 form 6，見 3b 指引「admin 繞過」
UPDATE dbo.tblFormInputControl
SET flgActiveSubject = 0,
    flgActiveClass   = 0,
    flgActiveAssessment = 0
WHERE form = 6;

-- 2.3 核對
SELECT form, term, flgTest, flgRegular, flgExam, flgConduct,
       flgActiveSubject, flgActiveClass, flgActiveAssessment
FROM dbo.tblFormInputControl
ORDER BY form;


/* =============================================================================
   三、截止入分（步驟 3 完成、計分前可執行）
   ============================================================================= */

/*
UPDATE dbo.tblFormInputControl
SET flgActiveSubject = 0,
    flgActiveClass   = 0
WHERE form BETWEEN 1 AND 5 AND term = 2;
*/
