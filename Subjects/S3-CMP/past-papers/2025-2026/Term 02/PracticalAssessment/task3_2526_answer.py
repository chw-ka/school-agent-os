import json


with open("canteen_sales.json", encoding="utf-8") as f:
    sales = json.load(f)

total_revenue = 0
item_revenue = {}
class_revenue = {}

for s in sales:
    rev = int(s["price"]) * int(s["qty"])
    total_revenue += rev
    item_revenue[s["item"]] = item_revenue.get(s["item"], 0) + rev
    class_revenue[s["class"]] = class_revenue.get(s["class"], 0) + rev

top_item = max(item_revenue, key=item_revenue.get)
top_item_rev = item_revenue[top_item]

lines = []
lines.append("🧾🍟 小食部銷售報告 🍟🧾")
lines.append("")
lines.append(f"💰 總收入：${total_revenue}")
lines.append(f"🏆 最賺錢食品：{top_item}（${top_item_rev}）")
lines.append("")
lines.append("📊 各班別總收入：")
for cls in sorted(class_revenue.keys()):
    lines.append(f"- {cls}: ${class_revenue[cls]}")
lines.append("")
lines.append("記得帶零用錢，支持小食部！")

text = "\n".join(lines)
with open("sales_report.txt", "w", encoding="utf-8") as f:
    f.write(text)
print("Wrote sales_report.txt")

