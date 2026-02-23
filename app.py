# app.py

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
from io import BytesIO
import os
from PIL import Image
import pandas as pd
from reportlab.pdfgen import canvas
import numpy as np
from collections import defaultdict
import pytesseract

# Path to Tesseract executable (check this path on your system)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def run_ocr_on_path(path: str) -> str:
    """
    Run PaddleOCR on an image file path and reconstruct proper readable lines.
    """
    result = ocr_engine.ocr(path)

    if not result:
        return ""

    all_lines = []

    pages = result  # PaddleOCR returns [[box,text], [box,text], ...] inside a list

    for page in pages:
        rows = defaultdict(list)

        for line in page:
            try:
                box = line[0]
                text = line[1][0]
            except:
                continue

            if not text:
                continue

            # y-position of the line (center of bounding box)
            y_center = (box[0][1] + box[2][1]) / 2
            row_key = round(y_center / 12) * 12  # group rows
            x_left = box[0][0]  # sort left → right

            rows[row_key].append((x_left, text.strip()))

        # Now sort rows (top→bottom) and segments (left→right)
        for row_key in sorted(rows.keys()):
            segments = sorted(rows[row_key], key=lambda s: s[0])
            line_text = " ".join(seg[1] for seg in segments)
            if line_text.strip():
                all_lines.append(line_text)

    return "\n".join(all_lines)



# -------------------------------
# App setup
# -------------------------------

app = FastAPI(title="NYAAY.AI - Legal Assistance Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DISCLAIMER_TEXT = (
    "This is an AI-generated informational response based on Indian law and your inputs. "
    "It is NOT legal advice. Consult a qualified advocate for any real legal action."
)

# -------------------------------
# Load IPC dataset
# -------------------------------

IPC_DF = None

def load_ipc_dataset():
    """
    Loads IPC dataset with columns:
    URL, Description, Offense, Punishment, Cognizable, Bailable, Court
    """
    global IPC_DF
    ipc_path = os.path.join("data", "ipc_sections.csv")  # adjust if needed
    if os.path.exists(ipc_path):
        IPC_DF = pd.read_csv(ipc_path)
    else:
        IPC_DF = pd.DataFrame(
            columns=[
                "URL",
                "Description",
                "Offense",
                "Punishment",
                "Cognizable",
                "Bailable",
                "Court",
            ]
        )

load_ipc_dataset()

# -------------------------------
# Initialize PaddleOCR
# -------------------------------


# -------------------------------
# Pydantic models
# -------------------------------

class AnalyzeRequest(BaseModel):
    user_query: str
    document_text: Optional[str] = None


class Classification(BaseModel):
    category: str
    sub_category: Optional[str] = None
    tags: List[str]


class DocumentAnalysis(BaseModel):
    document_type: Optional[str] = None
    summary_points: List[str] = []
    red_flags: List[str] = []


class LawReference(BaseModel):
    act: str
    section: str
    title: str
    description: str
    nature: str  # "Civil", "Criminal", or "Both/Civil/Criminal"
    # EXTRA FIELDS FROM DATASET FOR CLEAR PICTURE:
    punishment: Optional[str] = None
    cognizable: Optional[str] = None
    bailable: Optional[str] = None
    court: Optional[str] = None
    url: Optional[str] = None


class AnalyzeResponse(BaseModel):
    issue_summary: str
    classification: Classification
    document_analysis: Optional[DocumentAnalysis] = None
    rights_and_laws: List[LawReference]
    actions: List[str]
    complaint_template: str
    disclaimer: str


class PdfRequest(BaseModel):
    issue_summary: str
    complaint_template: str


class TemplateFillRequest(BaseModel):
    template_text: str
    full_name: str
    address: str
    opposite_party_name: Optional[str] = None
    opposite_party_address: Optional[str] = None
    date: Optional[str] = None
    mobile_number: Optional[str] = None
    email_id: Optional[str] = None
    signature: Optional[str] = None


class TemplateFillResponse(BaseModel):
    filled_template: str



# -------------------------------
# Core logic helpers
# -------------------------------

def summarize_issue(user_query: str, document_text: Optional[str]) -> str:
    text = (user_query or "").strip()
    if document_text:
        text += " " + document_text.strip()
    text = " ".join(text.split())
    return text[:450] + "..." if len(text) > 450 else text


def classify_issue(user_query: str, document_text: Optional[str]) -> Classification:
    text = (user_query or "") + " " + (document_text or "")
    text_lower = text.lower()

    category = "Other"
    sub_category = None
    tags: List[str] = []

    if any(k in text_lower for k in ["tenant", "landlord", "rent", "lease", "evict", "eviction", "security deposit"]):
        category = "Tenancy / Housing"
        if "evict" in text_lower or "eviction" in text_lower:
            sub_category = "Illegal eviction"
            tags.append("illegal eviction")
        if "security deposit" in text_lower or "deposit" in text_lower:
            tags.append("security deposit")

    elif any(k in text_lower for k in ["refund", "warranty", "defective", "service", "customer care", "product"]):
        category = "Consumer"
        if "defective" in text_lower or "damaged" in text_lower:
            sub_category = "Defective product"
            tags.append("defective product")
        if "refund" in text_lower or "no refund" in text_lower:
            tags.append("non-refund")
            tags.append("breach of contract")

    elif any(k in text_lower for k in ["online", "cyber", "instagram", "facebook", "whatsapp", "otp", "upi", "fraud", "scam"]):
        category = "Cybercrime / Online Harassment / Online Fraud"
        if "harass" in text_lower or "abuse" in text_lower:
            sub_category = "Online harassment"
            tags.append("harassment")
            tags.append("cyberbullying")
        if "fraud" in text_lower or "scam" in text_lower or "cheat" in text_lower:
            sub_category = sub_category or "Online fraud"
            tags.append("fraud")
            tags.append("cheating")

    elif any(k in text_lower for k in ["husband", "wife", "dowry", "domestic violence", "beat", "physical", "marriage"]):
        category = "Domestic Violence / Matrimonial"
        if "dowry" in text_lower:
            tags.append("dowry")
        if "violence" in text_lower or "beat" in text_lower or "assault" in text_lower:
            tags.append("domestic violence")

    elif any(k in text_lower for k in ["boss", "salary", "job", "company", "termination", "office", "hr"]):
        category = "Employment / Workplace"
        if "salary" in text_lower and "not paid" in text_lower:
            sub_category = "Salary not paid"
            tags.append("salary not paid")
        if "termination" in text_lower or "fired" in text_lower:
            sub_category = sub_category or "Wrongful termination"
            tags.append("wrongful termination")

    elif any(k in text_lower for k in ["loan", "emi", "bank", "cheque", "bounce", "recovery", "debt"]):
        category = "Banking / Loan / Money Recovery"
        if "cheque" in text_lower and "bounce" in text_lower:
            sub_category = "Cheque bounce"
            tags.append("non-payment")

    elif any(k in text_lower for k in ["assault", "threat", "hit me", "kill", "murder", "abuse", "fight", "police"]):
        category = "IPC – General Criminal Offence"
        if "threat" in text_lower:
            tags.append("threats")
        if "abuse" in text_lower or "defame" in text_lower:
            tags.append("defamation")
        if "assault" in text_lower or "hit me" in text_lower:
            tags.append("assault")

    # Generic tags
    if any(w in text_lower for w in ["fraud", "scam", "cheat"]):
        if "fraud" not in tags:
            tags.append("fraud")
    if any(w in text_lower for w in ["harass", "abuse"]):
        if "harassment" not in tags:
            tags.append("harassment")
    if "contract" in text_lower or "agreement" in text_lower:
        tags.append("breach of contract")

    tags = sorted(set(tags))

    return Classification(
        category=category,
        sub_category=sub_category,
        tags=tags,
    )


def guess_document_type(document_text: str) -> str:
    text = document_text.lower()
    if "this agreement" in text or "witnesseth" in text or "party of the first part" in text:
        return "Contract / Agreement"
    if "invoice" in text or "bill" in text:
        return "Invoice / Bill"
    if "fir no" in text or "first information report" in text:
        return "FIR"
    if "legal notice" in text or "through my advocate" in text:
        return "Legal Notice"
    if "dear sir" in text or "dear madam" in text:
        return "Letter / Email"
    return "General Document"


def detect_red_flags(document_text: str) -> List[str]:
    text = document_text.lower()
    red_flags: List[str] = []

    patterns = [
        ("Penalty clause", ["penalty", "penal interest", "late fee"]),
        ("No-refund clause", ["non-refundable", "no refund", "refund shall not be given"]),
        ("One-sided obligations", ["sole discretion", "without prior notice", "you agree to indemnify"]),
        ("Jurisdiction heavily biased", ["exclusive jurisdiction", "only courts at", "sole jurisdiction"]),
        ("Unclear termination", ["may terminate at any time", "without assigning any reason"]),
        ("Unclear liability", ["no liability", "without any liability", "we shall not be responsible"]),
    ]

    for label, keys in patterns:
        if any(k in text for k in keys):
            red_flags.append(label)

    return sorted(set(red_flags))


def summarize_document(document_text: str) -> List[str]:
    text = " ".join(document_text.split())
    chunks = []
    current = ""
    for token in text.split("."):
        token = token.strip()
        if not token:
            continue
        if len(current) + len(token) < 140:
            current = (current + " " + token).strip()
        else:
            chunks.append(current + ".")
            current = token
        if len(chunks) >= 5:
            break
    if current and len(chunks) < 5:
        chunks.append(current + ".")
    return chunks or [text[:180] + "..."]


def analyze_document(document_text: str) -> DocumentAnalysis:
    if not document_text:
        return DocumentAnalysis(
            document_type=None,
            summary_points=[],
            red_flags=[],
        )

    doc_type = guess_document_type(document_text)
    summary_points = summarize_document(document_text)
    red_flags = detect_red_flags(document_text)

    return DocumentAnalysis(
        document_type=doc_type,
        summary_points=summary_points,
        red_flags=red_flags,
    )


def _extract_section_number(url: str) -> str:
    """
    Try to extract section number from URL like:
    https://lawrato.com/indian-kanoon/ipc/section-140
    """
    if not url:
        return ""
    part = url.split("section-")[-1]
    part = part.strip().strip("/")
    # just return the tail as-is
    return part


def match_ipc_sections(text: str, tags: List[str]) -> List[LawReference]:
    """
    Match IPC sections from dataset based on description + offense text
    and user tags. Returns rich LawReference objects with all columns.
    """
    if IPC_DF is None or IPC_DF.empty:
        return []

    text_lower = text.lower()
    matches = []

    for _, row in IPC_DF.iterrows():
        try:
            url = str(row.get("URL", "")).strip()
            description = str(row.get("Description", "")).strip()
            offense = str(row.get("Offense", "")).strip()
            punishment = str(row.get("Punishment", "")).strip()
            cognizable = str(row.get("Cognizable", "")).strip()
            bailable = str(row.get("Bailable", "")).strip()
            court = str(row.get("Court", "")).strip()

            search_blob = (offense + " " + description).lower()

            score = 0

            # simple keyword match with complaint text
            for word in text_lower.split():
                if word and word in search_blob:
                    score += 1

            # tag match – higher weight
            for tag in tags:
                if tag.lower() in search_blob:
                    score += 3

            if score <= 0:
                continue

            section_number = _extract_section_number(url)
            title = offense if offense else f"IPC Section {section_number or 'N/A'}"
            desc_for_user = (
                description[:220] + "..."
                if len(description) > 220
                else description
            )

            matches.append(
                (
                    score,
                    LawReference(
                        act="Indian Penal Code, 1860",
                        section=f"Section {section_number}" if section_number else "IPC Section",
                        title=title,
                        description=desc_for_user,
                        nature="Criminal",  # IPC is criminal law
                        punishment=punishment or None,
                        cognizable=cognizable or None,
                        bailable=bailable or None,
                        court=court or None,
                        url=url or None,
                    ),
                )
            )
        except Exception:
            continue

    # sort by score and return top few
    matches.sort(key=lambda x: x[0], reverse=True)
    top_refs = [m[1] for m in matches[:5]]
    return top_refs


def generic_law_refs_for_category(category: str, tags: List[str]) -> List[LawReference]:
    refs: List[LawReference] = []

    if category == "Consumer":
        refs.append(
            LawReference(
                act="Consumer Protection Act, 2019",
                section="General rights",
                title="Right against unfair trade practices and defective goods/services",
                description="You can approach Consumer Commission if a product/service is defective, deficient, or unfair.",
                nature="Civil",
            )
        )

    if category == "Cybercrime / Online Harassment / Online Fraud":
        refs.append(
            LawReference(
                act="Information Technology Act, 2000",
                section="Sections 66C, 66D etc.",
                title="Cyber offences like identity theft and cheating by personation",
                description="Covers unauthorised use of credentials, OTP fraud, online cheating and related cyber offences.",
                nature="Criminal",
            )
        )

    if category == "Domestic Violence / Matrimonial":
        refs.append(
            LawReference(
                act="Protection of Women from Domestic Violence Act, 2005",
                section="General protection",
                title="Protection from physical, verbal, emotional and economic abuse",
                description="You can seek protection orders, residence orders and monetary relief through the Magistrate.",
                nature="Civil/Criminal",
            )
        )

    if category == "Employment / Workplace" and any(t in tags for t in ["harassment", "sexual harassment"]):
        refs.append(
            LawReference(
                act="POSH Act, 2013",
                section="Workplace sexual harassment",
                title="Protection from sexual harassment at workplace",
                description="Employer must have an Internal Complaints Committee (ICC) to address such complaints.",
                nature="Civil",
            )
        )

    return refs


def build_rights_and_laws(category: str, tags: List[str], combined_text: str) -> List[LawReference]:
    ipc_refs = match_ipc_sections(combined_text, tags)
    generic_refs = generic_law_refs_for_category(category, tags)

    # remove duplicates by (act, section, title)
    seen = set()
    result: List[LawReference] = []
    for ref in ipc_refs + generic_refs:
        key = (ref.act, ref.section, ref.title)
        if key not in seen:
            seen.add(key)
            result.append(ref)
    return result


def generate_actions(category: str, tags: List[str]) -> List[str]:
    actions: List[str] = []

    actions.append(
        "1. Collect and safely store all relevant documents, messages, emails, screenshots and payment proofs."
    )

    if category in ["Consumer", "Tenancy / Housing", "Employment / Workplace"]:
        actions.append(
            "2. First try to resolve the issue in writing (email/WhatsApp/letter) in a polite and clear manner."
        )
        actions.append(
            "3. If there is no proper response, consider sending a formal legal notice through an advocate."
        )

    if category in ["Cybercrime / Online Harassment / Online Fraud", "IPC – General Criminal Offence", "Domestic Violence / Matrimonial"]:
        actions.append(
            "2. For serious threats, violence, fraud or online offences, you can approach the local police station or cyber cell with all evidence."
        )

    if category == "Consumer":
        actions.append(
            "4. You may file a consumer complaint before the appropriate Consumer Commission if the value and facts justify it."
        )

    if category == "Tenancy / Housing":
        actions.append(
            "4. Check your rent agreement and local state tenancy laws. Avoid handing over possession or keys without proper written record."
        )

    if category == "Employment / Workplace":
        actions.append(
            "4. If it relates to harassment at workplace, you can approach HR or the Internal Complaints Committee (ICC), if applicable."
        )

    actions.append(
        "5. Laws and procedures vary by state and facts. Consult a qualified advocate to get personalised advice before taking legal action."
    )

    return actions


def guess_template_type(category: str) -> str:
    if category in ["Cybercrime / Online Harassment / Online Fraud", "IPC – General Criminal Offence", "Domestic Violence / Matrimonial"]:
        return "police_complaint"
    if category == "Consumer":
        return "consumer_complaint"
    if category in ["Tenancy / Housing", "Employment / Workplace", "Banking / Loan / Money Recovery"]:
        return "legal_notice"
    return "general_complaint"


def generate_complaint_template(template_type: str, issue_summary: str, classification: Classification) -> str:
    cat = classification.category
    sub = classification.sub_category or ""
    tags_text = ", ".join(classification.tags) if classification.tags else ""

    if template_type == "police_complaint":
        return f"""
To,
The Station House Officer,
[POLICE STATION NAME],
[PLACE]

Date: [DATE]

Subject: Complaint regarding {sub or cat}

Respected Sir/Madam,

1. I, [FULL NAME], residing at [FULL ADDRESS], respectfully submit this complaint for your necessary action.
2. The brief facts of the incident are as follows:
   (a) On or about [INCIDENT DATE], at around [TIME], at [PLACE], the following incident occurred:
       [INCIDENT DETAILS – WRITE CLEARLY IN SIMPLE POINTS].
   (b) The persons involved / accused are: [NAMES / DETAILS IF KNOWN].
3. Because of the above acts, I am facing serious hardship and mental stress. The issue broadly relates to: {cat}. Key aspects include: {tags_text or "N/A"}.
4. I request you to kindly register my complaint, investigate the matter, and take appropriate action under the relevant provisions of the Indian Penal Code and other applicable laws.

I am enclosing copies of the relevant documents/evidence for your reference.

Thank you,

Yours faithfully,

[FULL NAME]
[MOBILE NUMBER]
[EMAIL ID]
[SIGNATURE]
""".strip()

    if template_type == "consumer_complaint":
        return f"""
BEFORE THE HON'BLE CONSUMER DISPUTES REDRESSAL COMMISSION
[LEVEL AND PLACE]

IN THE MATTER OF:

[COMPLAINANT NAME],
[COMPLAINANT ADDRESS],
...Complainant

Versus

[OPPOSITE PARTY NAME],
[OPPOSITE PARTY ADDRESS],
...Opposite Party

COMPLAINT UNDER THE CONSUMER PROTECTION ACT, 2019

Most Respectfully Showeth:

1. That the Complainant is a consumer within the meaning of the Consumer Protection Act, 2019.
2. That the Opposite Party is engaged in the business of providing goods/services, namely [DETAILS OF GOODS/SERVICES].
3. Brief facts of the case:
   (a) The Complainant availed the said goods/services on [DATE] for a consideration of Rs. [AMOUNT].
   (b) The following issues/deficiencies arose: {issue_summary}
4. Due to the above deficiency in service / defect in goods, the Complainant has suffered loss, mental agony and harassment.
5. Cause of action arose on [DATE] when the Opposite Party failed to rectify/replace/refund despite requests.

PRAYER

In view of the above, the Complainant humbly prays that this Hon'ble Commission may be pleased to:

a) Direct the Opposite Party to refund Rs. [AMOUNT] with interest.
b) Award compensation of Rs. [COMPENSATION AMOUNT] for mental agony and harassment.
c) Award litigation costs of Rs. [LITIGATION COST].
d) Pass any other order(s) as this Hon'ble Commission may deem fit and proper.

Place: [PLACE]
Date: [DATE]

[COMPLAINANT SIGNATURE]
[COMPLAINANT NAME]
""".strip()

    if template_type == "legal_notice":
        return f"""
LEGAL NOTICE

From:
[YOUR FULL NAME]
[YOUR ADDRESS]
[CONTACT DETAILS]

To:
[OPPOSITE PARTY NAME]
[OPPOSITE PARTY ADDRESS]

Date: [DATE]

Subject: Legal Notice regarding {sub or cat}

Sir/Madam,

1. Under instructions and on behalf of my client, [YOUR FULL NAME], I hereby serve upon you the following legal notice:
2. That you and my client had the following arrangement/relationship: [BRIEFLY DESCRIBE AGREEMENT/EMPLOYMENT/TENANCY ETC.].
3. That the factual background is as under:
   (a) [FACT 1 – WITH DATE AND PLACE]
   (b) [FACT 2]
   (c) [FACT 3]
   The dispute broadly relates to: {issue_summary}
4. That your above acts/omissions amount to breach of legal and contractual obligations and have caused my client financial loss and mental harassment.
5. By this notice, I hereby call upon you to:
   (a) [PAY / PERFORM / REFUND] Rs. [AMOUNT] within [NUMBER OF DAYS] days from receipt of this notice; and
   (b) Cease and desist from repeating the complained acts.

Failing compliance within the above period, my client shall be constrained to initiate appropriate civil/criminal proceedings at your risk as to cost and consequences.

This notice is issued without prejudice to all other rights and remedies available in law and equity.

Yours faithfully,

[YOUR FULL NAME]
[CONTACT DETAILS]
[SIGNATURE]
""".strip()

    return f"""
GENERAL COMPLAINT TEMPLATE

To,
[AUTHORITY / ORGANISATION NAME],
[ADDRESS]

Date: [DATE]

Subject: Complaint regarding {sub or cat}

Respected Sir/Madam,

1. I, [FULL NAME], residing at [FULL ADDRESS], wish to submit this complaint for your consideration.
2. The facts of my case are as follows:
   [DETAILED FACTS IN NUMBERED POINTS – INCLUDE DATES, PLACES, AMOUNTS].
3. In summary, the issue relates to: {issue_summary}
4. Due to the above, I have suffered loss and mental harassment.

I therefore request you to kindly look into the matter and take appropriate action as per law.

Thank you,

Yours faithfully,

[FULL NAME]
[MOBILE NUMBER]
[EMAIL ID]
[SIGNATURE]
""".strip()

def fill_template_text(template: str, data: "TemplateFillRequest") -> str:
    """
    Replace placeholders in the template with user-provided details.
    """
    mapping = {
        "[FULL NAME]": data.full_name,
        "[YOUR FULL NAME]": data.full_name,
        "[COMPLAINANT NAME]": data.full_name,
        "[COMPLAINANT SIGNATURE]": data.full_name,  # optional

        "[FULL ADDRESS]": data.address,
        "[YOUR ADDRESS]": data.address,
        "[COMPLAINANT ADDRESS]": data.address,

        "[OPPOSITE PARTY NAME]": data.opposite_party_name or "",
        "[OPPOSITE PARTY ADDRESS]": data.opposite_party_address or "",

        "[DATE]": data.date or "",
        "[MOBILE NUMBER]": data.mobile_number or "",
        "[EMAIL ID]": data.email_id or "",
        "[CONTACT DETAILS]": f"{data.mobile_number or ''} {data.email_id or ''}".strip(),
        "[SIGNATURE]": data.signature or data.full_name,  # default to name if empty
    }

    for placeholder, value in mapping.items():
        if value is not None:
            template = template.replace(placeholder, value)

    return template



def build_pdf(issue_summary: str, complaint_template: str) -> BytesIO:
    buffer = BytesIO()
    c = canvas.Canvas(buffer)

    textobject = c.beginText(40, 800)
    textobject.setFont("Helvetica", 10)

    def add_wrapped_lines(label: str, content: str):
        textobject.textLine(label)
        textobject.textLine("")
        for line in content.split("\n"):
            while len(line) > 90:
                textobject.textLine(line[:90])
                line = line[90:]
            textobject.textLine(line)
        textobject.textLine("")

    add_wrapped_lines("ISSUE SUMMARY:", issue_summary)
    add_wrapped_lines("COMPLAINT TEMPLATE:", complaint_template)

    c.drawText(textobject)
    c.showPage()
    c.save()
    buffer.seek(0)
    return buffer


# -------------------------------
# Routes
# -------------------------------

@app.get("/")
async def root():
    return {"message": "NYAAY.AI backend is running"}


@app.post("/api/ocr")
async def ocr_upload(file: UploadFile = File(...)):
    """
    OCR endpoint using Tesseract (pytesseract).
    Works best for typed English documents (JPG/PNG screenshots, scans).
    """
    try:
        contents = await file.read()

        # Try to open the uploaded file as an image
        try:
            image = Image.open(BytesIO(contents))
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Please upload an image (JPG/PNG)."
            )

        # Convert to grayscale (often improves OCR quality)
        image = image.convert("L")

        # Upscale small images (e.g. WhatsApp screenshots) for better text recognition
        w, h = image.size
        if max(w, h) < 1200:
            scale = 1200 / max(w, h)
            image = image.resize(
                (int(w * scale), int(h * scale)),
                Image.BICUBIC
            )

        # Run Tesseract OCR
        raw_text = pytesseract.image_to_string(image, lang="eng")

        # Clean up: remove blank lines and extra spaces
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        extracted_text = "\n".join(lines)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=500,
                detail="OCR produced empty or unreadable text."
            )

        return {"document_text": extracted_text}

    except HTTPException:
        # Re-raise clean HTTP errors
        raise
    except Exception as e:
        # Catch-all for unexpected issues
        raise HTTPException(
            status_code=500,
            detail=f"OCR failed: {e}"
        )

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze_legal_issue(payload: AnalyzeRequest):
    if not payload.user_query and not payload.document_text:
        raise HTTPException(status_code=400, detail="Either user_query or document_text is required.")

    issue_summary = summarize_issue(payload.user_query, payload.document_text)
    classification = classify_issue(payload.user_query, payload.document_text)

    document_analysis: Optional[DocumentAnalysis] = None
    if payload.document_text:
        document_analysis = analyze_document(payload.document_text)

    combined_text = (payload.user_query or "") + " " + (payload.document_text or "")
    rights_and_laws = build_rights_and_laws(classification.category, classification.tags, combined_text)

    actions = generate_actions(classification.category, classification.tags)

    template_type = guess_template_type(classification.category)
    complaint_template = generate_complaint_template(template_type, issue_summary, classification)

    response = AnalyzeResponse(
        issue_summary=issue_summary,
        classification=classification,
        document_analysis=document_analysis,
        rights_and_laws=rights_and_laws,
        actions=actions,
        complaint_template=complaint_template,
        disclaimer=DISCLAIMER_TEXT,
    )

    return response


@app.post("/api/fill-template", response_model=TemplateFillResponse)
async def fill_template_endpoint(payload: TemplateFillRequest):
    """
    Take the base template + user details and return a filled template.
    """
    filled = fill_template_text(payload.template_text, payload)
    return TemplateFillResponse(filled_template=filled)


@app.post("/api/download-pdf")
async def download_pdf(payload: PdfRequest):
    pdf_buffer = build_pdf(payload.issue_summary, payload.complaint_template)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="nyayai_result.pdf"'},
    )


# -------------------------------
# Run with:  uvicorn app:app --reload --port 8000
# -------------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
