import aia_util as aia_utils
import multiprocessing
from unittest.mock import patch, MagicMock
from contextlib import redirect_stdout
import io

def run_task12(code, return_dict):
    buffer = io.StringIO()
    mock_gtts = MagicMock()
    mock_gtts.save = MagicMock()
    mock_playsound = MagicMock()

    try:
        with patch("builtins.input", return_value="Hello world"), \
             patch("gtts.gTTS", return_value=mock_gtts), \
             patch("playsound.playsound", mock_playsound), \
             redirect_stdout(buffer):

            exec(code, {})

        return_dict["runs"] = True
        return_dict["output"] = buffer.getvalue().strip()
        return_dict["used_save"] = mock_gtts.save.called
        return_dict["used_playsound"] = mock_playsound.called
    except Exception as e:
        return_dict["runs"] = False
        return_dict["error"] = str(e)

def evaluate_task12(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code = f.read()
    except:
        return 0, "❌ 無法讀取檔案"

    structure_score = 0
    explanation = []

    # 結構檢查
    if "from gtts" in code and "from playsound" in code:
        structure_score += 1
        explanation.append("✅ 正確 import (+1)")

    if "input(" in code:
        structure_score += 1
        explanation.append("✅ 有 input (+1)")

    if "gTTS(" in code:
        structure_score += 2
        explanation.append("✅ 有建立 gTTS 語音物件 (+2)")

    if ".save(" in code:
        structure_score += 2
        explanation.append("✅ 有 save mp3 (+2)")

    if "playsound(" in code:
        structure_score += 2
        explanation.append("✅ 有播放 mp3 (+2)")

    if "print(" in code:
        structure_score += 1
        explanation.append("✅ 有 print 確認訊息 (+1)")

    # 執行邏輯測試
    manager = multiprocessing.Manager()
    return_dict = manager.dict()
    p = multiprocessing.Process(target=run_task12, args=(code, return_dict))
    p.start()
    p.join(timeout=5)

    logic_score = 0
    if p.is_alive():
        p.terminate()
        p.join()
        return min(structure_score, 9), "⚠️ 執行超時，只計結構分 | " + " | ".join(explanation)

    if return_dict.get("runs"):
        logic_score += 3
        explanation.append("✅ 程式成功執行 (+3)")

        if return_dict.get("used_save") and return_dict.get("used_playsound"):
            logic_score += 3
            explanation.append("✅ 有播放及儲存語音 (+3)")
        else:
            explanation.append("⚠️ 沒有正確呼叫 save() 或 playsound()")
    else:
        explanation.append("❌ 執行錯誤：" + return_dict.get("error", "Unknown error"))

    final_score = min(structure_score + logic_score, 15)
    return final_score, " | ".join(explanation)


def test(submissions):
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # (2 marks) No marks if no file found
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "No file found in the submission\n"
            continue

        # (1 mark) The python code is runnable
        section_description = "The python code is runnable"
        filepath = row["filepath"]
        section_mark, remarks = evaluate_task12(filepath)

        submissions.loc[idx, "marks"] += section_mark
        submissions.loc[idx, "comments"] += aia_utils.get_comments(section_description, section_mark, 5)

        if (remarks != ""):
            submissions.loc[idx, "comments"] += "\n" + remarks

        print("=========================================")
        print("Marks:", submissions.loc[idx, "marks"])
        print(submissions.loc[idx, "comments"])
        print("=========================================")

    return submissions


if __name__ == "__main__":
    submissions = aia_utils.read_teams_aias()
    submissions = test(submissions)
    print(submissions)
    submissions.to_csv("marksheets.csv")