import os

from pai_forms_util import load_ch4t1_forms_scores, resolve_student_key

FORMS_SCORES = None


def _get_forms_scores():
    global FORMS_SCORES
    if FORMS_SCORES is None:
        FORMS_SCORES = load_ch4t1_forms_scores()
    return FORMS_SCORES


def test(submissions):
    forms_scores = _get_forms_scores()
    for idx, row in submissions.iterrows():
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        key = resolve_student_key(row)
        if key and key in forms_scores:
            mark, comments = forms_scores[key]
            submissions.loc[idx, "marks"] = mark
            submissions.loc[idx, "comments"] = comments
            continue

        filepath = row.get("filepath")
        if filepath and os.path.exists(str(filepath)):
            submissions.loc[idx, "comments"] = (
                "未找到 MS Forms 回應（本任務以 Forms 作答為準，請確認已填寫表單）\n"
            )
        else:
            submissions.loc[idx, "comments"] = (
                "未填寫 MS Forms（本任務無需提交程式碼，請於 MS Forms 作答）\n"
            )
    return submissions
