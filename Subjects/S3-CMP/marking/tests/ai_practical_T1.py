import json
import components_util as components_util
import aia_util as aia_utils


def find_component_by_name(components, component_name):
    """Find a component by name (case-insensitive)"""
    for screen_name in components:
        form = components[screen_name].get("Properties", {})
        result = _search_component_by_name(form, component_name)
        if result:
            return result
    return None


def find_component_by_type(components, component_type):
    """Find a component by type (returns first match)"""
    for screen_name in components:
        form = components[screen_name].get("Properties", {})
        result = _search_component_by_type(form, component_type)
        if result:
            return result
    return None


def find_all_components_by_type(components, component_type):
    """Find all components by type"""
    results = []
    for screen_name in components:
        form = components[screen_name].get("Properties", {})
        _collect_components_by_type(form, component_type, results)
    return results


def _search_component_by_type(component, target_type):
    """Recursively search for a component by type"""
    comp_type = component.get("$Type", "")
    if comp_type == target_type:
        return component
    
    if "$Components" in component:
        for subcomponent in component["$Components"]:
            result = _search_component_by_type(subcomponent, target_type)
            if result:
                return result
    
    return None


def _collect_components_by_type(component, target_type, results):
    """Recursively collect all components by type"""
    comp_type = component.get("$Type", "")
    if comp_type == target_type:
        results.append(component)
    
    if "$Components" in component:
        for subcomponent in component["$Components"]:
            _collect_components_by_type(subcomponent, target_type, results)


def find_component_by_name_or_type(components, component_name, component_type, property_checks=None):
    """
    Find a component by name first, if not found, try to find by type.
    If property_checks is provided (dict of property_name: expected_value),
    when searching by type, will try to find a component that matches the properties.
    """
    # First try by name
    component = find_component_by_name(components, component_name)
    if component:
        return component, "name"
    
    # If not found by name, try by type
    if property_checks:
        # Find all components of this type and check which one matches properties
        all_components = find_all_components_by_type(components, component_type)
        for comp in all_components:
            # Check if this component matches the expected properties
            matches = True
            for prop_name, expected_value in property_checks.items():
                actual_value = comp.get(prop_name, "")
                if str(actual_value) != str(expected_value):
                    matches = False
                    break
            if matches:
                return comp, "type"
        # If no component matches all properties, return the first one found
        if all_components:
            return all_components[0], "type"
    else:
        # No property checks, just return first by type
        component = find_component_by_type(components, component_type)
        if component:
            return component, "type"
    
    return None, None


def _search_component_by_name(component, target_name):
    """Recursively search for a component by name (case-insensitive)"""
    comp_name = component.get("$Name", "")
    if comp_name.lower() == target_name.lower():
        return component
    
    if "$Components" in component:
        for subcomponent in component["$Components"]:
            result = _search_component_by_name(subcomponent, target_name)
            if result:
                return result
    
    return None


def is_component_in_arrangement(components, component_name, arrangement_name):
    """Check if a component is nested inside a specific arrangement (case-insensitive)"""
    arrangement = find_component_by_name(components, arrangement_name)
    if not arrangement:
        return False
    
    def search_in_arrangement(comp, target_name):
        comp_name = comp.get("$Name", "")
        if comp_name.lower() == target_name.lower():
            return True
        if "$Components" in comp:
            for sub in comp["$Components"]:
                if search_in_arrangement(sub, target_name):
                    return True
        return False
    
    return search_in_arrangement(arrangement, component_name)


def evaluate(components):
    """Evaluate the practical assessment task 1"""
    score = 0
    remarks = []
    
    # 1️⃣ File upload check (1 mark) - handled in test() function
    
    # 2️⃣ Check component naming (5 marks - 1 mark each)
    naming_score = 0
    required_names = ["label1", "count", "HArrangement", "plus", "minus"]
    found_names = []
    missing_names = []
    
    for name in required_names:
        if find_component_by_name(components, name):
            found_names.append(name)
            naming_score += 1
            remarks.append(f"✅ {name} 命名正確 (+1)")
        else:
            missing_names.append(name)
            remarks.append(f"❌ {name} 命名不正確 (+0)")
    
    score += naming_score
    
    # 3️⃣ Check property settings (14 marks)
    properties_score = 0
    
    # Check Screen1 properties
    screen1 = None
    for screen_name in components:
        if screen_name == "Screen1":
            screen1 = components[screen_name].get("Properties", {})
            break
    
    if screen1:
        # Screen1: AlignHorizontal = 3
        align_h = screen1.get("AlignHorizontal", "")
        if str(align_h) == "3":
            properties_score += 1
            remarks.append("✅ Screen1 AlignHorizontal 正確 (+1)")
        else:
            remarks.append(f"❌ Screen1 AlignHorizontal 應設為 3，目前為 {align_h} (+0)")
    else:
        remarks.append("未找到 Screen1")
    
    # Check label1 properties - try to find by Text="COUNTER" if searching by type
    label1, found_by = find_component_by_name_or_type(
        components, "label1", "Label", 
        property_checks={"Text": "COUNTER"}
    )
    if label1:
        name_note = " (未正確命名，但已找到元件)" if found_by == "type" else ""
        # Text = "COUNTER"
        text = label1.get("Text", "")
        if text == "COUNTER":
            properties_score += 1
            remarks.append(f"✅ label1 Text 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ label1 Text 應設為 'COUNTER'，目前為 '{text}' (+0){name_note}")
        
        # FontSize = 60
        font_size = label1.get("FontSize", "")
        if str(font_size) == "60":
            properties_score += 1
            remarks.append(f"✅ label1 FontSize 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ label1 FontSize 應設為 60，目前為 {font_size} (+0){name_note}")
    else:
        remarks.append("未找到 label1 元件")
    
    # Check count properties - try to find by Text="0" if searching by type
    count, found_by = find_component_by_name_or_type(
        components, "count", "Label",
        property_checks={"Text": "0"}
    )
    if count:
        name_note = " (未正確命名，但已找到元件)" if found_by == "type" else ""
        # Text = "0"
        text = count.get("Text", "")
        if text == "0":
            properties_score += 1
            remarks.append(f"✅ count Text 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ count Text 應設為 '0'，目前為 '{text}' (+0){name_note}")
        
        # FontSize = 150
        font_size = count.get("FontSize", "")
        if str(font_size) == "150":
            properties_score += 1
            remarks.append(f"✅ count FontSize 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ count FontSize 應設為 150，目前為 {font_size} (+0){name_note}")
        
        # TextAlignment = 1
        text_align = count.get("TextAlignment", "")
        if str(text_align) == "1":
            properties_score += 1
            remarks.append(f"✅ count TextAlignment 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ count TextAlignment 應設為 1，目前為 {text_align} (+0){name_note}")
        
        # Width = -2 (fill parent)
        width = count.get("Width", "")
        if str(width) == "-2":
            properties_score += 1
            remarks.append(f"✅ count Width 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ count Width 應設為 -2 (填滿)，目前為 {width} (+0){name_note}")
    else:
        remarks.append("未找到 count 元件")
    
    # Check HArrangement properties
    h_arrangement, found_by = find_component_by_name_or_type(components, "HArrangement", "HorizontalArrangement")
    if h_arrangement:
        name_note = " (未正確命名，但已找到元件)" if found_by == "type" else ""
        # Width = -2 (fill parent)
        width = h_arrangement.get("Width", "")
        if str(width) == "-2":
            properties_score += 1
            remarks.append(f"✅ HArrangement Width 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ HArrangement Width 應設為 -2 (填滿)，目前為 {width} (+0){name_note}")
    else:
        remarks.append("未找到 HArrangement 元件")
    
    # Check plus button properties - try to find by Text="+" if searching by type
    plus, found_by = find_component_by_name_or_type(
        components, "plus", "Button",
        property_checks={"Text": "+"}
    )
    if plus:
        name_note = " (未正確命名，但已找到元件)" if found_by == "type" else ""
        # Text = "+"
        text = plus.get("Text", "")
        if text == "+":
            properties_score += 1
            remarks.append(f"✅ plus Text 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ plus Text 應設為 '+'，目前為 '{text}' (+0){name_note}")
        
        # FontSize = 150
        font_size = plus.get("FontSize", "")
        if str(font_size) == "150":
            properties_score += 1
            remarks.append(f"✅ plus FontSize 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ plus FontSize 應設為 150，目前為 {font_size} (+0){name_note}")
        
        # Width = 50 (percentage) - stored as "-1050" in components
        width = plus.get("Width", "")
        if str(width) == "-1050" or str(width) == "50":
            properties_score += 1
            remarks.append(f"✅ plus Width 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ plus Width 應設為 50 比例，目前為 {width} (+0){name_note}")
    else:
        remarks.append("未找到 plus 元件")
    
    # Check minus button properties - try to find by Text="-" if searching by type
    minus, found_by = find_component_by_name_or_type(
        components, "minus", "Button",
        property_checks={"Text": "-"}
    )
    if minus:
        name_note = " (未正確命名，但已找到元件)" if found_by == "type" else ""
        # Text = "-"
        text = minus.get("Text", "")
        if text == "-":
            properties_score += 1
            remarks.append(f"✅ minus Text 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ minus Text 應設為 '-'，目前為 '{text}' (+0){name_note}")
        
        # FontSize = 150
        font_size = minus.get("FontSize", "")
        if str(font_size) == "150":
            properties_score += 1
            remarks.append(f"✅ minus FontSize 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ minus FontSize 應設為 150，目前為 {font_size} (+0){name_note}")
        
        # Width = 50 (percentage) - stored as "-1050" in components
        width = minus.get("Width", "")
        if str(width) == "-1050" or str(width) == "50":
            properties_score += 1
            remarks.append(f"✅ minus Width 正確 (+1){name_note}")
        else:
            remarks.append(f"❌ minus Width 應設為 50 比例，目前為 {width} (+0){name_note}")
    else:
        remarks.append("未找到 minus 元件")
    
    score += properties_score
    
    # 4️⃣ Check if buttons are in HArrangement (deduct 1 mark if not)
    arrangement_check = True
    if plus and minus and h_arrangement:
        plus_in_arrangement = is_component_in_arrangement(components, "plus", "HArrangement")
        minus_in_arrangement = is_component_in_arrangement(components, "minus", "HArrangement")
        
        if not plus_in_arrangement or not minus_in_arrangement:
            arrangement_check = False
            score -= 1
            missing = []
            if not plus_in_arrangement:
                missing.append("plus")
            if not minus_in_arrangement:
                missing.append("minus")
            remarks.append(f"❌ 按鈕未放入水平配置: {', '.join(missing)} (-1)")
    else:
        # Can't check if components don't exist
        if not h_arrangement:
            remarks.append("⚠️ 無法檢查按鈕是否在水平配置中（缺少 HArrangement） (+0)")
        elif not plus or not minus:
            remarks.append("⚠️ 無法檢查按鈕是否在水平配置中（缺少按鈕元件） (+0)")
    
    if arrangement_check and plus and minus and h_arrangement:
        remarks.append("✅ 按鈕已正確放入水平配置 (不扣分)")
    
    # Add summary of marks breakdown
    remarks.append(f"\n📊 評分明細：命名 {naming_score}/5 + 屬性設定 {properties_score}/14 = {score}/19 分（不含檔案上傳）")
    
    return round(score, 2), "\n".join(remarks)


def test(submissions):
    submissions = aia_utils.read_all_aias(submissions)
    for idx, row in submissions.iterrows():
        print("=========================================")
        print(submissions.loc[idx, "class"], submissions.loc[idx, "classnumber"])
        print("=========================================")
        submissions.loc[idx, "marks"] = 0
        submissions.loc[idx, "comments"] = ""

        # 1️⃣ File upload check (1 mark)
        if row["filepath"] is None:
            submissions.loc[idx, "marks"] = 0
            submissions.loc[idx, "comments"] = "❌ 沒有提交檔案 - 0分/20分"
            continue
        else:
            submissions.loc[idx, "marks"] += 1
            file_upload_feedback = "✅ 正確地上傳檔案 (+1)"

        # Evaluate the AIA content
        try:
            components = json.loads(row["components"])
            section_mark, remarks = evaluate(components)
            
            submissions.loc[idx, "marks"] += section_mark
            total_marks = submissions.loc[idx, "marks"]
            
            # Format overall feedback with grade
            if total_marks >= 18:
                overall_feedback = f"✅ 優秀！總分 {total_marks}/20"
            elif total_marks >= 15:
                overall_feedback = f"✅ 良好！總分 {total_marks}/20"
            elif total_marks >= 12:
                overall_feedback = f"⚠️ 基本合格！總分 {total_marks}/20"
            elif total_marks >= 8:
                overall_feedback = f"❌ 需要改進！總分 {total_marks}/20"
            else:
                overall_feedback = f"❌ 不及格！總分 {total_marks}/20"
            
            # Combine all feedback items with | separator
            all_feedback = [file_upload_feedback]
            if remarks:
                # Split remarks by newline and filter out empty lines
                remark_lines = [r.strip() for r in remarks.split("\n") if r.strip()]
                all_feedback.extend(remark_lines)
            
            detailed_feedback = " | ".join(all_feedback)
            submissions.loc[idx, "comments"] = f"{overall_feedback} | {detailed_feedback}"
                
        except Exception as e:
            submissions.loc[idx, "marks"] = 1  # Still get file upload mark
            submissions.loc[idx, "comments"] = f"❌ 不及格！總分 1/20 | ✅ 正確地上傳檔案 (+1) | ❌ 無法解析AIA檔案: {str(e)} (+0)"

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
