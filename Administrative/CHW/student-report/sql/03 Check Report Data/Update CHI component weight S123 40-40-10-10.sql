-- 中一至中三：中文分卷整體比重 (tblFormPaperWeight.weight)
-- CH1 閱讀 40、CH2 寫作 40、CH3 聆聽 10、CH4 說話 10
-- 影響：stpCalculateScore 合併 CHI 總分；成績表「各科比重為」顯示
-- 改後須重做：計分 (5) → 快照 (6) → 核對稿 (7)（若已有分數）

-- 改前備份
SELECT form, idPaper, weight, weight_test_2, weight_regular_2, weight_exam_2
FROM dbo.tblFormPaperWeight
WHERE form IN (1, 2, 3) AND idPaper IN ('CH1', 'CH2', 'CH3', 'CH4')
ORDER BY form, idPaper;

UPDATE dbo.tblFormPaperWeight
SET weight = CASE idPaper
    WHEN 'CH1' THEN 40
    WHEN 'CH2' THEN 40
    WHEN 'CH3' THEN 10
    WHEN 'CH4' THEN 10
END
WHERE form IN (1, 2, 3)
  AND idPaper IN ('CH1', 'CH2', 'CH3', 'CH4');

-- 改後確認（加總應為 100）
SELECT form, idPaper, weight,
       SUM(weight) OVER (PARTITION BY form) AS weight_sum_chi_parts
FROM dbo.tblFormPaperWeight
WHERE form IN (1, 2, 3) AND idPaper IN ('CH1', 'CH2', 'CH3', 'CH4')
ORDER BY form, idPaper;
