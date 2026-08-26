# Purchasing Form Filling Skill

**Purpose:** Assist in filling CHW school purchasing forms for purchases under $50,000 HKD.

**Scope:** 
- ✅ ≤$5,000 purchases (simple application form)
- ✅ $5,001-$50,000 purchases (oral quotation form)
- ❌ >$50,000 purchases (handled by office colleagues)

---

## When to Use This Skill

Invoke this skill when the user:
- Wants to purchase items/services for school use
- Needs to fill out purchasing application forms
- Asks about procurement procedures for amounts under $50,000
- Needs help with oral quotations or purchase justifications

**Examples:**
- "I need to buy some textbooks for S3 CMP"
- "Help me fill out a purchase form for STEM equipment"
- "How do I get quotes for a $30,000 service?"
- "Create a purchase application for Math Fun Day supplies"

---

## Core Workflow

### Step 1: Determine Purchase Amount Tier

Ask the user:
```
What is the estimated total cost of this purchase?
- Option A: $5,000 or below
- Option B: $5,001 - $50,000
- Option C: Above $50,000 (Note: This will be handled by office colleagues)
```

**If Option C:** Politely inform that purchases above $50,000 require different procedures and should be handled by office administrative staff. Refer to `Administrative/CHW/purchasing/README.md` for details.

### Step 2: Gather Required Information

#### For ALL Purchases:

Collect the following information:

1. **Item/Service Description:**
   - What exactly is being purchased?
   - Specifications, quantities, models
   - Purpose/justification for purchase

2. **Budget Source:**
   - Which budget/fund will cover this?
   - Subject panel budget? Department budget? Special grant?

3. **Timeline:**
   - When are the items needed?
   - Is this urgent?

4. **Supplier Information (if known):**
   - Preferred supplier(s)?
   - Any existing contracts or framework agreements?

#### For $5,001-$50,000 Purchases (Additional):

5. **Quotation Plan:**
   - How many suppliers will you contact?
   - What method will you use (phone, email, fax)?
   - Deadline for receiving quotes?

6. **Selection Criteria:**
   - Price only?
   - Quality, delivery time, after-sales service?

### Step 3: Check Conflict of Interest

**CRITICAL:** Before proceeding, ask:

```
Do you have any connection with the potential supplier(s)?
- Are you a relative, employee, shareholder, or have any other relationship?
- If YES, you must complete a Conflict of Interest Declaration Form and refrain from handling this procurement.
```

If user declares conflict of interest:
- Direct them to complete `利益衝突申報表格` (Annex I)
- Advise them to hand over the procurement to another colleague
- Document the declaration

### Step 4: Guide Through Form Completion

Based on the amount tier, guide the user through the appropriate form.

---

## Form Templates & Instructions

### Tier 1: ≤$5,000 — Simple Application Form

**Form:** `申請購買物品表格($5000元或以下)`

**Location:** `Administrative/CHW/purchasing/templates/`

**Fields to Complete:**

1. **Date / 日期:** Current date
2. **Applicant Name / 申請人姓名:** User's name
3. **Subject Panel/Department / 科目/部門:** User's department
4. **Item Description / 物品描述:**
   - Item name, specifications, quantity
   - Estimated unit price and total
5. **Purpose/Justification / 用途/理由:**
   - Why is this purchase necessary?
   - How will it benefit students/teaching?
6. **Declaration / 聲明:**
   - "特此聲明，上述物品只屬單一的採購，並非把多個部分所組成的物品分單採購"
   - "This is a single procurement, not splitting a larger purchase into parts to circumvent guidelines"

**Approval Chain:**
```
Applicant → Subject Panel Head → Vice Principal → Principal (certifies)
```

**Instructions to User:**
1. Fill in the form with the information gathered
2. Print and sign
3. Submit to your Subject Panel Head for review
4. After Panel Head signs, submit to Vice Principal
5. Finally, submit to Principal for certification
6. Once certified, proceed with purchase
7. After purchase, submit original receipt + approved form to school accountant

---

### Tier 2: $5,001-$50,000 — Oral Quotation Form

**Form:** `按口頭報價購貨表格` (EDB Annex II)

**Location:** `Administrative/CHW/purchasing/templates/`

**Critical Rules (MUST FOLLOW):**

⚠️ **Rule 1: Minimum 2 Quotations**
- Must obtain at least 2 oral quotations from different suppliers
- All quoted items must have identical specifications

⚠️ **Rule 2: Obtain Quotes Personally**
- **You MUST obtain quotes yourself**
- Never ask one supplier to collect other suppliers' quotes
- This is a serious violation of procurement rules

⚠️ **Rule 3: Keep Written Evidence**
- Even though called "oral quotations," keep written records:
  - Email correspondence
  - Fax confirmations
  - Website screenshots with prices
  - Phone call notes (date, time, contact person, quote details)

⚠️ **Rule 4: Select Lowest Conforming Quote**
- Generally select the lowest quote that meets specifications
- If NOT selecting lowest, MUST record detailed reasons

**Fields to Complete:**

1. **Basic Information:**
   - Date, applicant name, subject panel/department
   
2. **Item/Service Details:**
   - Detailed description
   - Specifications
   - Quantity
   - Delivery requirements

3. **Quotation Details (for each supplier):**
   - Supplier name
   - Contact person
   - Quoted price
   - Quotation date
   - Method (phone/email/fax)
   - Key terms (delivery, warranty, etc.)

4. **Recommendation:**
   - Which supplier is recommended?
   - Reasons for selection
   - If not lowest price, explain why

5. **Insufficient Quotations (if applicable):**
   - If unable to get 2+ quotes, explain why
   - Must be endorsed by Panel Head or staff ≥ MPS Point 25

**Approval Chain:**
```
Responsible Teacher (with recommendation) 
  → Subject Panel Head/Dept Head 
  → Vice Principal 
  → Principal (approves)
```

**Step-by-Step Instructions:**

**Phase 1: Obtain Quotations**

1. Identify at least 2-3 potential suppliers
2. Contact each supplier personally:
   ```
   Sample script:
   "Hello, I'm [Name] from Chan Shu Kui Memorial School. 
   We're looking to purchase [item description]. 
   Could you please provide a quotation by [deadline]?
   Please include: price, delivery time, warranty terms."
   ```
3. Record all quotations with dates and contact details
4. Save any written evidence (emails, screenshots, faxes)

**Phase 2: Complete the Form**

1. Fill in all supplier quotations on the form
2. Compare and evaluate:
   - Are specifications identical?
   - Are there significant price differences?
   - Any notable terms differences?
3. Make recommendation:
   - If selecting lowest: "Recommended due to lowest conforming quote"
   - If not selecting lowest: Provide detailed justification (e.g., better quality, faster delivery, better warranty)
4. Sign and date

**Phase 3: Approval Process**

1. Submit to Subject Panel Head/Department Head for review
2. After approval, submit to Vice Principal
3. Finally, submit to Principal for final approval
4. **Keep a copy** of the Principal-approved form for your records

**Phase 4: Purchase & Documentation**

1. Once approved, proceed with purchase from selected supplier
2. After delivery:
   - Inspect goods immediately
   - Report any issues to supplier
3. Submit to school accountant:
   - Original receipt/invoice
   - Copy of Principal-approved Oral Quotation Form
4. **Retain all records for 3 calendar years** for audit purposes

---

## Anti-Splitting Checks

**IMPORTANT:** Before processing any purchase, check for potential order splitting.

Ask the user:
```
Is this part of a larger procurement that's being split into smaller orders?
- Have you made similar purchases recently?
- Are there planned future purchases of the same/similar items?
```

**Red Flags:**
- Multiple purchases of same item within short period
- Total cumulative value approaching tier limits
- Vague justification for separate orders

**Rules:**
- Cumulative purchases of same items via oral quotation must not exceed $50,000 in 12 months
- Cumulative purchases of same items via written quotation must not exceed $200,000 in 12 months

If splitting is suspected:
- Advise user to consolidate into single procurement at appropriate tier
- Escalate to Vice Principal if unclear

---

## Special Cases

### Case 1: Single Source Procurement

**When:** Only one supplier available (copyright, patent, utility company, etc.)

**Action:**
- ≤$50,000: Panel Head or staff ≥ MPS Point 25 must approve and record reasons
- Document why competitive bidding is not feasible
- Justify that price is fair and reasonable

### Case 2: Urgent Purchases

**When:** Emergency situations requiring immediate action

**Action:**
- Still follow proper procedures
- Document urgency and reasons
- May expedite approval chain but cannot skip steps
- For written quotations, Principal may reduce timeline to 2 clear working days (from 3 weeks) with recorded reasons

### Case 3: External Tutors/Coaches

**Regular on-campus tutors:**
- Must provide proof of qualifications
- Must undergo sexual conviction record check (at own expense)
- Results due before first class
- Contract must include non-violation declaration

**One-off guest speakers:**
- No conviction check required
- Must complete External Service Provider/Speaker Declaration form

### Case 4: Pandemic/Disruption Clauses

Ensure supplier specifies terms for inability to deliver due to:
- Pandemic restrictions
- EDB class suspension announcements

Terms should cover: return, rescheduling, refund arrangements.

---

## Common Mistakes to Avoid

❌ **Asking one supplier to collect other quotes**
- Serious violation; responsible teacher must obtain all quotes personally

❌ **Not keeping written evidence for oral quotations**
- Always save emails, screenshots, call notes

❌ **Selecting non-lowest quote without justification**
- Must record detailed reasons if not choosing lowest conforming quote

❌ **Splitting large orders to avoid higher-tier procedures**
- Cumulative limits apply; violations are serious

❌ **Forgetting conflict of interest declarations**
- Must declare annually and for specific procurements if applicable

❌ **Losing documentation**
- Keep all records for 3 calendar years for audit

❌ **Using credit card without prior approval**
- Cash preferred; credit card requires Principal's prior approval

❌ **Not inspecting goods upon delivery**
- Must check immediately and report issues

---

## Post-Purchase Checklist

After completing the purchase, ensure:

- [ ] Goods received and inspected
- [ ] Receiving stamp applied by school office
- [ ] Original receipt obtained
- [ ] Receipt marked "Paid by XX" on top-right corner
- [ ] Thermal receipts photocopied (to prevent fading)
- [ ] Approved form copy attached to receipt
- [ ] All documents submitted to school accountant
- [ ] Records filed for 3-year retention

---

## Reference Documents

All reference documents are located in:
- `Administrative/CHW/purchasing/README.md` — Comprehensive manual
- `Administrative/CHW/purchasing/templates/` — Form templates
- EDB Guidelines (in Chinese and English)

**Key Documents:**
1. 資助學校採購程序指引 (Jun 2023)
2. Guidelines on Procurement Procedures in Aided Schools (Apr 2013)
3. CHW 採購指引 (Aug 2026 revision)

---

## Quick Decision Tree

```
User wants to make a purchase
    │
    ├─ What's the estimated cost?
    │   │
    │   ├─ ≤ $5,000
    │   │   └─ Use Simple Application Form
    │   │       → No quotations needed
    │   │       → Principal certifies essential & fair price
    │   │
    │   ├─ $5,001 - $50,000
    │   │   └─ Use Oral Quotation Form
    │   │       → Get ≥2 oral quotes personally
    │   │       → Keep written evidence
    │   │       → Principal approves
    │   │
    │   └─ > $50,000
    │       └─ Refer to office colleagues
    │           → Requires written quotations or tender
    │
    ├─ Any conflict of interest?
    │   └─ YES → Complete COI form, hand over to colleague
    │
    ├─ Is this splitting a larger order?
    │   └─ YES → Consolidate into single procurement
    │
    └─ Proceed with form completion and approval chain
```

---

## Example Scenarios

### Scenario 1: Buying Textbooks ($3,000)

**User:** "I need to buy reference books for S5 ICT, about $3,000 worth."

**Response:**
1. This is ≤$5,000, so use Simple Application Form
2. Gather info:
   - Book titles, publishers, quantities
   - Budget source (ICT panel budget?)
   - Justification (supplementary learning materials)
3. Help fill form
4. Explain approval chain: Panel Head → VP → Principal
5. Remind to submit receipt after purchase

### Scenario 2: STEM Workshop Equipment ($25,000)

**User:** "We want to buy Arduino kits and sensors for a STEM workshop, around $25,000."

**Response:**
1. This is $5,001-$50,000, so use Oral Quotation Form
2. Critical steps:
   - Identify 3+ suppliers (e.g., local electronics shops, online retailers)
   - YOU must contact each personally
   - Get quotes with identical specs
   - Keep email/screen shot evidence
3. Help compare quotes
4. Recommend lowest conforming quote (or justify otherwise)
5. Complete form with all quote details
6. Approval chain: You → Panel Head → VP → Principal
7. After approval, place order
8. Submit receipt + approved form copy to accountant
9. Retain records for 3 years

### Scenario 3: Suspected Order Splitting

**User:** "I bought $8,000 of lab equipment last month. Now I need another $7,000 of similar items."

**Response:**
⚠️ **Warning:** This appears to be order splitting.
- Cumulative total would be $15,000 within 12 months
- Should have been procured together as single $15,000 purchase
- Action: Consolidate remaining needs and process as single oral quotation procurement
- Consult Vice Principal if uncertain

---

## Tips for Success

✅ **Start early:** Approval chains take time; don't wait until last minute

✅ **Document everything:** Emails, call notes, screenshots—save it all

✅ **Be transparent:** Clear justifications speed up approvals

✅ **Check budgets first:** Confirm funding availability before starting

✅ **Communicate with suppliers:** Clear specifications prevent misunderstandings

✅ **Inspect promptly:** Check goods immediately upon delivery

✅ **File properly:** Keep organized records for 3 years

---

## Escalation Points

Contact these people for guidance:

- **Procurement procedure questions:** School Accountant
- **Budget approval:** Subject Panel Head / Department Head
- **Urgent requests:** Vice Principal (Admin)
- **Policy interpretation:** Principal / School Management Committee

---

## Version & Updates

**Last Updated:** August 2026  
**Based on:** EDB Guidelines (Jun 2023), CHW Internal Policies (Aug 2026)

**Note:** This skill should be reviewed annually to reflect:
- Changes in EDB guidelines
- Updates to school policies
- New form versions
- Revised monetary thresholds

To update this skill, modify the SKILL.md file and commit changes to the repository.
