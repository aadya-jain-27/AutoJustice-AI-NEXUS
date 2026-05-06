"""
AutoJustice AI NEXUS — Demo Evidence Generator
Generates realistic evidence files (PDFs + TXT) for hackathon demo:
  - 6 GENUINE evidence files (real cybercrime proof)
  - 4 FALSE case evidence files (fake/manipulated — AI should flag these)

Run: python generate_evidence.py
Output: demo_evidence/ folder
"""
from pathlib import Path
from datetime import datetime

OUTPUT_DIR = Path(__file__).parent / "demo_evidence"
OUTPUT_DIR.mkdir(exist_ok=True)

# ── ReportLab imports ─────────────────────────────────────────────────────────
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect, String, Circle, Line
from reportlab.graphics import renderPDF
from reportlab.platypus import Flowable

# ── Color palette ─────────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#1a2a4a")
SAFFRON     = colors.HexColor("#FF9933")
GREEN_IN    = colors.HexColor("#138808")
BLUE        = colors.HexColor("#1565c0")
RED         = colors.HexColor("#c0392b")
ORANGE      = colors.HexColor("#e67e22")
LIGHT_GRAY  = colors.HexColor("#f5f6fa")
MID_GRAY    = colors.HexColor("#bdc3c7")
DARK_GRAY   = colors.HexColor("#2c3e50")
WHITE       = colors.white
BLACK       = colors.black
WA_GREEN    = colors.HexColor("#25D366")   # WhatsApp green
WA_BUBBLE   = colors.HexColor("#DCF8C6")   # WhatsApp outgoing
WA_DARK     = colors.HexColor("#075E54")
SMS_BLUE    = colors.HexColor("#0084FF")
BANK_BLUE   = colors.HexColor("#003087")   # SBI blue
HDFC_RED    = colors.HexColor("#EE3124")
GPAY_BLUE   = colors.HexColor("#4285F4")
UPI_ORANGE  = colors.HexColor("#FF6600")


# ── Helper: quick styles ──────────────────────────────────────────────────────
def S(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=10, textColor=BLACK, leading=14)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)


def bold_style(**kw):   return S("B", fontName="Helvetica-Bold", **kw)
def small_style(**kw):  return S("SM", fontSize=8, textColor=colors.HexColor("#7f8c8d"), **kw)
def mono_style(**kw):   return S("M", fontName="Courier", fontSize=9, **kw)


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 1: SBI Bank SMS Alert (UPI Fraud)
# ─────────────────────────────────────────────────────────────────────────────
def gen_bank_sms_alert():
    path = OUTPUT_DIR / "EVIDENCE_01_SBI_Bank_Alert_UPI_Fraud.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=(9*cm, 16*cm),
                              rightMargin=8*mm, leftMargin=8*mm,
                              topMargin=8*mm, bottomMargin=8*mm)
    story = []

    # Phone status bar
    hdr = Drawing(9*cm - 16*mm, 10*mm)
    hdr.add(Rect(0, 0, 9*cm - 16*mm, 10*mm, fillColor=colors.HexColor("#1a1a2e"), strokeColor=None))
    hdr.add(String(4, 2, "9:41 AM", fontName="Helvetica-Bold", fontSize=9, fillColor=WHITE))
    hdr.add(String(170, 2, "▐▐▐  ⬛", fontName="Helvetica", fontSize=8, fillColor=WHITE))
    story.append(hdr)
    story.append(Spacer(1, 3*mm))

    # App bar
    app_bar = Drawing(9*cm - 16*mm, 14*mm)
    app_bar.add(Rect(0, 0, 9*cm - 16*mm, 14*mm, fillColor=colors.HexColor("#128C7E"), strokeColor=None))
    app_bar.add(String(8, 3, "SMS  —  SBI Alerts", fontName="Helvetica-Bold", fontSize=11, fillColor=WHITE))
    story.append(app_bar)
    story.append(Spacer(1, 4*mm))

    # SMS bubble
    bubble_style = ParagraphStyle("bubble", fontName="Helvetica", fontSize=10,
                                  textColor=BLACK, leading=15, borderPad=8,
                                  backColor=colors.HexColor("#f0f0f0"), borderRadius=8)
    msg = (
        "<b>SBI ALERT:</b><br/>"
        "Dear Customer, Rs.<b>45,000.00</b> debited from A/c "
        "XX<b>9876</b> on <b>14-Apr-24</b> at <b>14:32:11</b>.<br/>"
        "UPI Ref No: <b>400041412345678</b><br/>"
        "Remarks: <b>UPI/payment@axisbank/FRAUD</b><br/>"
        "Available Bal: Rs.12,340.50<br/>"
        "If not done by you call <b>1800-1234</b>"
    )
    story.append(Paragraph(msg, bubble_style))
    story.append(Spacer(1, 3*mm))

    # Second SMS
    msg2 = (
        "<b>SBI ALERT:</b><br/>"
        "A/c XX9876: NEFT Credit Rs.<b>0.00</b> reversal "
        "attempted — FAILED.<br/>"
        "For dispute: <b>sbi.co.in/disputes</b>"
    )
    story.append(Paragraph(msg2, bubble_style))
    story.append(Spacer(1, 5*mm))

    # Timestamp
    story.append(Paragraph("14 April 2024, 2:32 PM", S("ts", fontSize=8,
                            textColor=MID_GRAY, alignment=TA_CENTER)))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "FORENSIC NOTE: This SMS screenshot constitutes digital evidence "
        "under Section 65B, Indian Evidence Act.",
        S("fn", fontSize=7, textColor=colors.HexColor("#e74c3c"))
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 2: WhatsApp Scammer Conversation
# ─────────────────────────────────────────────────────────────────────────────
def gen_whatsapp_fraud():
    path = OUTPUT_DIR / "EVIDENCE_02_WhatsApp_Scammer_Conversation.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=(9*cm, 20*cm),
                              rightMargin=6*mm, leftMargin=6*mm,
                              topMargin=6*mm, bottomMargin=6*mm)
    story = []

    # Status bar
    hdr = Drawing(9*cm - 12*mm, 10*mm)
    hdr.add(Rect(0, 0, 9*cm - 12*mm, 10*mm, fillColor=colors.HexColor("#1a1a2e"), strokeColor=None))
    hdr.add(String(4, 2, "9:41 AM", fontName="Helvetica-Bold", fontSize=9, fillColor=WHITE))
    story.append(hdr)

    # WhatsApp top bar
    wa_bar = Drawing(9*cm - 12*mm, 16*mm)
    wa_bar.add(Rect(0, 0, 9*cm - 12*mm, 16*mm, fillColor=WA_DARK, strokeColor=None))
    wa_bar.add(Circle(18, 8, 12, fillColor=colors.HexColor("#aaaaaa"), strokeColor=None))
    wa_bar.add(String(36, 8, "+91 88877 76665", fontName="Helvetica-Bold",
                      fontSize=10, fillColor=WHITE))
    wa_bar.add(String(36, 1, "last seen today at 2:30 PM", fontName="Helvetica",
                      fontSize=7, fillColor=colors.HexColor("#b2dfdb")))
    story.append(wa_bar)
    story.append(Spacer(1, 3*mm))

    # Chat bubbles helper
    inc_style = ParagraphStyle("inc", fontName="Helvetica", fontSize=9, leading=13,
                               textColor=BLACK, backColor=WHITE,
                               borderPad=6, borderRadius=6, spaceBefore=2)
    out_style = ParagraphStyle("out", fontName="Helvetica", fontSize=9, leading=13,
                               textColor=BLACK, backColor=WA_BUBBLE,
                               borderPad=6, borderRadius=6, spaceBefore=2,
                               alignment=TA_RIGHT)
    time_in  = ParagraphStyle("ti", fontSize=7, textColor=MID_GRAY, spaceBefore=0)
    time_out = ParagraphStyle("to", fontSize=7, textColor=MID_GRAY, alignment=TA_RIGHT, spaceBefore=0)

    def bubble(text, style, time_str, ts):
        story.append(Paragraph(text, style))
        story.append(Paragraph(time_str + "  " + ts, ts_style(style)))

    def ts_style(s):
        return time_in if s == inc_style else time_out

    story.append(Paragraph("2:28 PM", ParagraphStyle("d", fontSize=7,
                            textColor=MID_GRAY, alignment=TA_CENTER)))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        "Hi, I am Ravi from your office accounts team. "
        "Sir asked me to tell you urgent payment needed today.", inc_style))
    story.append(Paragraph("2:28 PM", time_in))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Ok what payment? Which sir?", out_style))
    story.append(Paragraph("2:29 PM  ✓✓", time_out))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        "Mr. Mahesh sir. Vendor payment Rs.45,000 urgent. "
        "Please send on this UPI: <b>payment@axisbank</b> "
        "He will explain later, meeting going on.", inc_style))
    story.append(Paragraph("2:29 PM", time_in))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Done. Sent via Google Pay.", out_style))
    story.append(Paragraph("2:32 PM  ✓✓", time_out))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("Thank you! sir will call you.", inc_style))
    story.append(Paragraph("2:33 PM", time_in))
    story.append(Spacer(1, 2*mm))

    # After realization
    story.append(Paragraph("3:15 PM", ParagraphStyle("d2", fontSize=7,
                            textColor=MID_GRAY, alignment=TA_CENTER)))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        "WAIT — I called Mahesh sir. He says he never asked for payment. "
        "Who are you??? This is FRAUD!!", out_style))
    story.append(Paragraph("3:16 PM  ✓", time_out))
    story.append(Spacer(1, 2*mm))

    # Shows delivered but not read (fraudster seen)
    story.append(Paragraph("[Message delivered, not read]",
                            ParagraphStyle("nr", fontSize=7, textColor=RED, alignment=TA_RIGHT)))
    story.append(Spacer(1, 3*mm))

    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 2*mm))
    story.append(Paragraph(
        "Fraudster phone: +91-8887776665 | Chat exported 14-Apr-2024 | "
        "SHA-256 verified | Section 65B Compliant",
        S("fn2", fontSize=7, textColor=RED)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 3: Google Pay UPI Transaction Receipt
# ─────────────────────────────────────────────────────────────────────────────
def gen_upi_receipt():
    path = OUTPUT_DIR / "EVIDENCE_03_GooglePay_UPI_Transaction_Receipt.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=(9*cm, 18*cm),
                              rightMargin=8*mm, leftMargin=8*mm,
                              topMargin=8*mm, bottomMargin=8*mm)
    story = []

    # Google Pay header
    hdr = Drawing(9*cm - 16*mm, 20*mm)
    hdr.add(Rect(0, 0, 9*cm - 16*mm, 20*mm, fillColor=GPAY_BLUE, strokeColor=None))
    hdr.add(String(10, 7, "G Pay   Transaction Receipt", fontName="Helvetica-Bold",
                   fontSize=12, fillColor=WHITE))
    story.append(hdr)
    story.append(Spacer(1, 4*mm))

    # Amount
    story.append(Paragraph(
        "<font color='#c0392b' size='28'><b>₹45,000.00</b></font>",
        ParagraphStyle("amt", fontName="Helvetica-Bold", fontSize=28,
                       textColor=RED, alignment=TA_CENTER)))
    story.append(Paragraph("DEBITED from your account",
                            S("db", textColor=RED, alignment=TA_CENTER, fontSize=10)))
    story.append(Spacer(1, 4*mm))

    # Status badge
    story.append(Paragraph(
        "● COMPLETED",
        ParagraphStyle("st", fontName="Helvetica-Bold", fontSize=11,
                       textColor=colors.HexColor("#16a34a"), alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 5*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY))
    story.append(Spacer(1, 3*mm))

    # Details table
    data = [
        ["To UPI ID",     "payment@axisbank"],
        ["From Account",  "SBI A/c XX9876"],
        ["Date & Time",   "14 Apr 2024, 2:32 PM"],
        ["Transaction ID","GP2404141234567800"],
        ["UPI Ref No",    "400041412345678"],
        ["Remarks",       "FRAUD - Social Engg"],
        ["Status",        "SUCCESS (DISPUTED)"],
    ]

    label_s = ParagraphStyle("lbl", fontName="Helvetica", fontSize=9,
                             textColor=colors.HexColor("#7f8c8d"))
    value_s = ParagraphStyle("val", fontName="Helvetica-Bold", fontSize=9,
                             textColor=DARK_GRAY)

    tbl_data = [[Paragraph(k, label_s), Paragraph(v, value_s)] for k, v in data]
    tbl = Table(tbl_data, colWidths=["42%", "58%"])
    tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1),
         [WHITE, colors.HexColor("#f8f9fa")]),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 4),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#dee2e6")),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

    # Dispute note
    story.append(Paragraph(
        "⚠ DISPUTE FILED: Unauthorized transaction. "
        "Complaint raised with SBI on 14-Apr-2024. "
        "Ref: DISPUTE-SBI-2024-041400123",
        ParagraphStyle("disp", fontName="Helvetica", fontSize=8,
                       textColor=RED, backColor=colors.HexColor("#fdecea"),
                       borderPad=6, borderRadius=4, leading=12)
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Digital Evidence — Section 65B IEA | SHA-256 Certified",
        S("cert", fontSize=7, textColor=MID_GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 4: Fake Investment App Screenshot
# ─────────────────────────────────────────────────────────────────────────────
def gen_fake_investment_app():
    path = OUTPUT_DIR / "EVIDENCE_04_Fake_Investment_App_Screenshot.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=(9*cm, 20*cm),
                              rightMargin=6*mm, leftMargin=6*mm,
                              topMargin=6*mm, bottomMargin=6*mm)
    story = []

    # Fake app top bar
    bar = Drawing(9*cm - 12*mm, 16*mm)
    bar.add(Rect(0, 0, 9*cm - 12*mm, 16*mm,
                 fillColor=colors.HexColor("#6c3483"), strokeColor=None))
    bar.add(String(8, 5, "CryptoProfit India  v2.1", fontName="Helvetica-Bold",
                   fontSize=11, fillColor=WHITE))
    story.append(bar)
    story.append(Spacer(1, 4*mm))

    # Fake profit display
    story.append(Paragraph(
        "Welcome, <b>Rajesh Kumar Gupta</b>",
        S("wl", fontSize=11, textColor=DARK_GRAY)
    ))
    story.append(Spacer(1, 3*mm))

    profit_s = ParagraphStyle("pr", fontName="Helvetica-Bold", fontSize=26,
                              textColor=colors.HexColor("#16a34a"), alignment=TA_CENTER)
    story.append(Paragraph("+₹37,500.00", profit_s))
    story.append(Paragraph("Total Profit (30% monthly returns)",
                            S("sub", fontSize=9, textColor=MID_GRAY, alignment=TA_CENTER)))
    story.append(Spacer(1, 4*mm))

    # Portfolio table
    portfolio = [
        ["Investment",   "₹1,25,000.00"],
        ["Returns (30%)", "₹37,500.00"],
        ["Portfolio",    "₹1,62,500.00"],
        ["Locked Until", "30 Apr 2024"],
        ["Plan",         "Gold Pro (Guaranteed)"],
    ]
    lbl = ParagraphStyle("l", fontName="Helvetica", fontSize=9,
                         textColor=colors.HexColor("#7f8c8d"))
    val = ParagraphStyle("v", fontName="Helvetica-Bold", fontSize=9,
                         textColor=DARK_GRAY)
    tbl_data = [[Paragraph(k, lbl), Paragraph(v, val)] for k, v in portfolio]
    tbl = Table(tbl_data, colWidths=["50%", "50%"])
    tbl.setStyle(TableStyle([
        ("ROWBACKGROUNDS", (0,0), (-1,-1),
         [WHITE, colors.HexColor("#f3e5f5")]),
        ("TOPPADDING",   (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING",  (0,0), (-1,-1), 6),
        ("GRID", (0,0), (-1,-1), 0.3, colors.HexColor("#e0e0e0")),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 4*mm))

    # Withdrawal blocked message
    story.append(Paragraph(
        "⛔ WITHDRAWAL REQUEST BLOCKED\n\n"
        "To withdraw your profits, you must first pay "
        "Tax Clearance Fee: <b>₹15,000</b>\n\n"
        "Pay to: TAX.REFUND@PAYTM\n"
        "Contact Support: +44-7911-000123",
        ParagraphStyle("blk", fontName="Helvetica", fontSize=9,
                       textColor=RED, backColor=colors.HexColor("#fdecea"),
                       borderPad=8, borderRadius=6, leading=14)
    ))
    story.append(Spacer(1, 3*mm))

    # Real website gone
    story.append(Paragraph(
        "⚠ NOTE: Website cryptoprofit-india.com — CURRENTLY OFFLINE\n"
        "This screenshot taken: 20-Mar-2024 at 11:45 AM\n"
        "Instagram handle: @investment_profits_india (DELETED)",
        S("note", fontSize=8, textColor=colors.HexColor("#9a3412"),
          backColor=colors.HexColor("#fff7ed"), borderPad=6)
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Evidence preserved under Section 65B IEA | Digital Forensics Unit",
        S("cert2", fontSize=7, textColor=MID_GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 5: Sextortion Threat Screenshot (Telegram)
# ─────────────────────────────────────────────────────────────────────────────
def gen_sextortion_threat():
    path = OUTPUT_DIR / "EVIDENCE_05_Sextortion_Blackmail_Threat_Telegram.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=(9*cm, 18*cm),
                              rightMargin=6*mm, leftMargin=6*mm,
                              topMargin=6*mm, bottomMargin=6*mm)
    story = []

    # Telegram header
    tg_bar = Drawing(9*cm - 12*mm, 16*mm)
    tg_bar.add(Rect(0, 0, 9*cm - 12*mm, 16*mm,
                    fillColor=colors.HexColor("#0088cc"), strokeColor=None))
    tg_bar.add(Circle(18, 8, 12, fillColor=colors.HexColor("#aaaaaa"), strokeColor=None))
    tg_bar.add(String(36, 8, "Unknown Contact",
                      fontName="Helvetica-Bold", fontSize=10, fillColor=WHITE))
    tg_bar.add(String(36, 1, "@fake_girl_2024  |  Telegram",
                      fontName="Helvetica", fontSize=7,
                      fillColor=colors.HexColor("#b3e5fc")))
    story.append(tg_bar)
    story.append(Spacer(1, 3*mm))

    inc_s = ParagraphStyle("i", fontName="Helvetica", fontSize=9, leading=13,
                           textColor=BLACK, backColor=WHITE,
                           borderPad=6, borderRadius=6, spaceBefore=2)
    out_s = ParagraphStyle("o", fontName="Helvetica", fontSize=9, leading=13,
                           textColor=BLACK, backColor=WA_BUBBLE,
                           borderPad=6, borderRadius=6, spaceBefore=2,
                           alignment=TA_RIGHT)
    t_s   = ParagraphStyle("ts", fontSize=7, textColor=MID_GRAY)
    t_sr  = ParagraphStyle("tsr", fontSize=7, textColor=MID_GRAY, alignment=TA_RIGHT)

    story.append(Paragraph("12 April 2024 — 11:15 PM",
                            ParagraphStyle("d", fontSize=7, textColor=MID_GRAY,
                                           alignment=TA_CENTER)))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        "Hey! I am Priya. I saw your profile, you look nice. "
        "Let's video call? 😊", inc_s))
    story.append(Paragraph("11:16 PM", t_s))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph("[Video call — 4 minutes 32 seconds]", out_s))
    story.append(Paragraph("11:21 PM ✓✓", t_sr))
    story.append(Spacer(1, 2*mm))

    story.append(Paragraph(
        "I have recorded the full video call. "
        "I will send it to all your contacts unless you pay "
        "<b>₹50,000</b> on Bitcoin wallet:\n\n"
        "<b>1A2B3C4D5E6F7G8H9I0J1K2L3M4N5O6P</b>\n\n"
        "You have 24 hours. Don't contact police.",
        ParagraphStyle("thr", fontName="Helvetica", fontSize=9,
                       textColor=RED, backColor=colors.HexColor("#fdecea"),
                       borderPad=8, borderRadius=6, leading=14)
    ))
    story.append(Paragraph("11:35 PM", t_s))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph(
        "⚠ VICTIM NOTE: I did NOT pay. Reporting to cyber police.\n"
        "Screenshot captured: 12-Apr-2024, 11:36 PM\n"
        "Account @fake_girl_2024 — reported and blocked",
        S("vn", fontSize=8, textColor=colors.HexColor("#9a3412"),
          backColor=colors.HexColor("#fff7ed"), borderPad=6)
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Evidence: IPC 354A / BNS 74 / IT Act 66E | Section 65B Certified",
        S("leg", fontSize=7, textColor=MID_GRAY, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# GENUINE EVIDENCE 6: Digital Arrest Scam (Fake CBI Officer)
# ─────────────────────────────────────────────────────────────────────────────
def gen_digital_arrest_scam():
    path = OUTPUT_DIR / "EVIDENCE_06_Digital_Arrest_Fake_CBI_Scam.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # Fake CBI letterhead
    hdr = Drawing(17*cm, 25*mm)
    hdr.add(Rect(0, 0, 17*cm, 25*mm, fillColor=colors.HexColor("#1a2a4a"), strokeColor=None))
    hdr.add(String(10, 12, "CENTRAL BUREAU OF INVESTIGATION — CYBER CRIME UNIT",
                   fontName="Helvetica-Bold", fontSize=13, fillColor=WHITE))
    hdr.add(String(10, 3, "IMPORTANT LEGAL NOTICE — IMMEDIATE ACTION REQUIRED",
                   fontName="Helvetica-Bold", fontSize=10,
                   fillColor=colors.HexColor("#FF9933")))
    story.append(hdr)
    story.append(Spacer(1, 5*mm))

    # FAKE notice content
    story.append(Paragraph(
        "<b>NOTE: THIS IS A FRAUDULENT DOCUMENT — SUBMITTED AS EVIDENCE OF DIGITAL ARREST SCAM</b>",
        ParagraphStyle("warn", fontName="Helvetica-Bold", fontSize=10,
                       textColor=WHITE, backColor=RED,
                       alignment=TA_CENTER, borderPad=6)
    ))
    story.append(Spacer(1, 5*mm))

    notice_s = ParagraphStyle("ns", fontName="Helvetica", fontSize=10,
                              textColor=DARK_GRAY, leading=16)
    story.append(Paragraph(
        "Case No.: CBI/CC/2024/04/MH/00789<br/><br/>"
        "To: <b>Arjun Mehta</b>, S/o Ramesh Mehta<br/>"
        "Address: Flat 4B, Andheri West, Mumbai – 400053<br/><br/>"
        "Subject: <b>ARREST WARRANT — Money Laundering &amp; Drug Trafficking</b><br/><br/>"
        "Dear Sir/Madam,<br/><br/>"
        "You are hereby notified that your Aadhaar No. (XXXX-XXXX-7823) and bank account "
        "have been linked to an illegal money laundering network operating from Dubai. "
        "You are under <b>Digital Arrest</b> until the matter is resolved.<br/><br/>"
        "You must immediately:<br/>"
        "1. Transfer Rs. <b>2,00,000</b> to the secure government escrow account below<br/>"
        "2. DO NOT leave your home or contact anyone<br/>"
        "3. Keep this Skype call connected: <b>cbi.officer.sharma</b><br/><br/>"
        "Escrow Account: <b>SBI 987654321012 IFSC: SBIN0001234</b><br/><br/>"
        "Failure to comply will result in immediate physical arrest.",
        notice_s
    ))
    story.append(Spacer(1, 5*mm))

    # Fake signature block
    sig_data = [[
        Paragraph("DySP Vikram Sharma\nCBI Cyber Crime Unit\nBadge: CBI-CC-2847\nPhone: 011-24367000", notice_s),
        Paragraph("[FAKE SEAL]", ParagraphStyle("seal", fontName="Helvetica-Bold",
                                                 fontSize=20, textColor=MID_GRAY,
                                                 alignment=TA_CENTER,
                                                 borderPad=10))
    ]]
    sig_tbl = Table(sig_data, colWidths=["60%", "40%"])
    sig_tbl.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.5, MID_GRAY),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
    ]))
    story.append(sig_tbl)
    story.append(Spacer(1, 8*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=RED))
    story.append(Spacer(1, 3*mm))

    # Victim account
    story.append(Paragraph(
        "VICTIM STATEMENT:<br/>"
        "I, Arjun Mehta, received this document on WhatsApp from +91-7654321098 "
        "on 16 Apr 2024. The caller kept me on a Skype video call for 6 hours "
        "threatening arrest. I transferred Rs. 2,00,000 before my son stopped me. "
        "The CBI later confirmed this is FAKE — CBI never conducts 'digital arrests'. "
        "Reference: cybercrime.gov.in/digital-arrest-scam",
        ParagraphStyle("vs", fontName="Helvetica", fontSize=9,
                       textColor=DARK_GRAY, backColor=colors.HexColor("#fff7ed"),
                       borderPad=10, borderRadius=6, leading=14)
    ))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Scammer Phone: +91-7654321098 | Fake Skype: cbi.officer.sharma | "
        "Fake Escrow Bank: SBI 987654321012 | Submitted: 16 April 2024 | "
        "Section 65B Certificate Attached",
        S("cert3", fontSize=8, textColor=RED)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FALSE CASE EVIDENCE 1: Keyword Stuffing Attempt (TXT)
# ─────────────────────────────────────────────────────────────────────────────
def gen_false_keyword_stuffing():
    path = OUTPUT_DIR / "FALSE_01_Keyword_Stuffing_Attempt.txt"
    content = """CYBERCRIME REPORT - URGENT
===========================
bomb threat terrorism kill murder hack blackmail extort ransom nude child drugs
weapon terrorist attack sextortion suicide kidnap illegal threat hack bomb explosion
rape murder threat drugs weapon explosive device child abuse trafficking fraud
URGENT URGENT URGENT - police action required immediately
hacker terrorist bomb explosion nuclear weapon drug trafficking child pornography
blackmail extortion ransom bitcoin cryptocurrency money laundering
===========================
NOTE: This file contains ONLY keywords with no real narrative.
The AI fake detection system should flag this as KEYWORD STUFFING.
Authenticity score should be very low (< 15%).
Layer 1 Detection: High-risk keyword density without context.
"""
    path.write_text(content, encoding="utf-8")
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FALSE CASE EVIDENCE 2: Copy-Paste Template (TXT)
# ─────────────────────────────────────────────────────────────────────────────
def gen_false_template():
    path = OUTPUT_DIR / "FALSE_02_Copy_Paste_Template_Report.txt"
    content = """COMPLAINT REPORT
================
To,
The Superintendent of Police,
[City Name]

Subject: Complaint against [Name of Accused Person]

Respected Sir/Madam,

I am writing to inform you about the incident that happened to me on [DATE].
The person named [INSERT NAME HERE] did [CRIME TYPE] to me at [LOCATION].

I have suffered a loss of Rs. [AMOUNT] due to this incident.

Please take strict action against the above-mentioned person.

Kindly look into this matter and do the needful as early as possible.

Thanking You,
[Your Name]
[Your Address]
[Your Phone Number]

---
NOTE FOR DEMO: This is a copy-pasted template with placeholder text.
AI should detect: "INSERT NAME HERE", "[DATE]", "[AMOUNT]" etc.
Expected: FAKE RECOMMENDATION = REJECT
Authenticity: ~10-15%
"""
    path.write_text(content, encoding="utf-8")
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FALSE CASE EVIDENCE 3: Inconsistent Story (PDF)
# ─────────────────────────────────────────────────────────────────────────────
def gen_false_inconsistent():
    path = OUTPUT_DIR / "FALSE_03_Inconsistent_Contradictory_Complaint.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    story = []

    story.append(Paragraph(
        "COMPLAINT REPORT — CASE STUDY: AI DETECTS INCONSISTENCIES",
        ParagraphStyle("ht", fontName="Helvetica-Bold", fontSize=14,
                       textColor=NAVY, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "⚠ THIS IS A DEMO FALSE CASE — For showing judges how AI detects fake reports",
        ParagraphStyle("warn2", fontName="Helvetica-Bold", fontSize=10,
                       textColor=WHITE, backColor=ORANGE,
                       alignment=TA_CENTER, borderPad=6)
    ))
    story.append(Spacer(1, 6*mm))

    body_s = ParagraphStyle("bs", fontName="Helvetica", fontSize=10,
                            textColor=DARK_GRAY, leading=16)
    flag_s = ParagraphStyle("fs", fontName="Helvetica-Bold", fontSize=9,
                            textColor=RED, backColor=colors.HexColor("#fdecea"),
                            borderPad=6, borderRadius=4, leading=13)

    story.append(Paragraph("<b>Complainant Statement (as submitted):</b>", body_s))
    story.append(Spacer(1, 3*mm))

    story.append(Paragraph(
        "My name is Vikram Thakur. On 10th April 2024 at 3 PM, I transferred "
        "Rs. 75,000 to a fake investment company on Instagram. However, I was "
        "in Delhi at the time but the Instagram account was accessed from my "
        "Mumbai phone. The transaction was done via NEFT from my Chennai bank. "
        "I reported this to Chandigarh police first. The fraudster called me "
        "from a +91 number but the call logs show an international +44 number. "
        "I lost Rs. 75,000 but I also want compensation of Rs. 5,00,000 for "
        "mental harassment. My Aadhaar shows my address as Mumbai but I live "
        "in Chandigarh for 10 years. The same person also defrauded my cousin "
        "who filed the same complaint yesterday with the same transaction ID.",
        body_s
    ))
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph("<b>AI-Detected Inconsistencies (for demo):</b>",
                           ParagraphStyle("ah", fontName="Helvetica-Bold",
                                         fontSize=11, textColor=NAVY)))
    story.append(Spacer(1, 3*mm))

    flags = [
        ("L1 — Location Contradiction:",
         "Complainant says 'in Delhi' but device used was in Mumbai. "
         "Transaction from Chennai. Address shows Chandigarh. Four locations in one incident."),
        ("L2 — Gemini Coherence Check FAILED:",
         "Narrative contains contradictions — same transaction ID submitted by two different "
         "complainants. Gemini AI marks coherence score: 0.09 (very low)."),
        ("L3 — Evidence Correlation FAIL:",
         "Claimed transaction ID does not match any real NEFT format. "
         "No evidence file uploaded for Rs. 75,000 claim."),
        ("L4 — Entity Inconsistency:",
         "Complainant phone number matches fraudster phone in a previous report. "
         "Possible counter-complaint scenario."),
        ("L5 — Duplicate Fingerprint:",
         "SHA-256 hash of this complaint is 94% similar to a complaint REJECTED 3 days ago."),
        ("L6 — Behavioral Score:",
         "This IP address submitted 3 complaints in 24 hours. "
         "Reporter trust score: 0.05 (near-zero). Account previously blocked."),
    ]

    for title, detail in flags:
        story.append(Paragraph(f"<b>{title}</b> {detail}", flag_s))
        story.append(Spacer(1, 2*mm))

    story.append(Spacer(1, 5*mm))
    result_s = ParagraphStyle("res", fontName="Helvetica-Bold", fontSize=13,
                              textColor=WHITE, backColor=RED,
                              alignment=TA_CENTER, borderPad=8)
    story.append(Paragraph("AI VERDICT: REJECT | AUTHENTICITY: 11% | COMPLAINT CLOSED", result_s))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "Under BNS Section 229 — Filing a false police complaint carries up to "
        "2 years imprisonment and/or fine. This case has been forwarded to the "
        "Anti-False Complaints Cell.",
        body_s
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# FALSE CASE EVIDENCE 4: Fabricated Bank Statement (PDF)
# ─────────────────────────────────────────────────────────────────────────────
def gen_false_fabricated_statement():
    path = OUTPUT_DIR / "FALSE_04_Fabricated_Bank_Statement_TAMPERED.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    story = []

    # HDFC-style header
    hdr = Drawing(17*cm, 20*mm)
    hdr.add(Rect(0, 0, 17*cm, 20*mm, fillColor=HDFC_RED, strokeColor=None))
    hdr.add(String(10, 8,
                   "HDFC BANK — ACCOUNT STATEMENT (SUSPECTED FABRICATION)",
                   fontName="Helvetica-Bold", fontSize=12, fillColor=WHITE))
    story.append(hdr)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph(
        "⚠ FORENSIC FLAG: ELA (Error Level Analysis) detected image manipulation. "
        "Font inconsistency found in rows 3 & 7. Metadata shows file edited in "
        "Adobe Photoshop CS6 — NOT original bank export.",
        ParagraphStyle("ff", fontName="Helvetica-Bold", fontSize=10,
                       textColor=WHITE, backColor=RED,
                       borderPad=8, borderRadius=4, leading=14)
    ))
    story.append(Spacer(1, 5*mm))

    # Account info
    story.append(Paragraph(
        "<b>Account Holder:</b> Vikram Thakur &nbsp;&nbsp; "
        "<b>A/c No:</b> 502001234<b>56789</b> &nbsp;&nbsp; "
        "<b>Period:</b> Apr 1–15, 2024",
        S("ai", fontSize=10, textColor=DARK_GRAY)
    ))
    story.append(Spacer(1, 4*mm))

    # Transaction table with tampered rows highlighted
    headers = ["Date", "Description", "Debit (₹)", "Credit (₹)", "Balance (₹)"]
    rows = [
        ["01 Apr", "Opening Balance",        "",        "",            "2,45,000.00"],
        ["03 Apr", "UPI - groceries",         "1,200",   "",            "2,43,800.00"],
        ["05 Apr", "SALARY CREDIT",           "",        "65,000",      "3,08,800.00"],
        ["07 Apr", "UPI - investment@fake",  "75,000",   "",            "2,33,800.00"],  # TAMPERED
        ["08 Apr", "ATM Withdrawal",         "5,000",    "",            "2,28,800.00"],
        ["10 Apr", "Netflix subscription",   "499",      "",            "2,28,301.00"],
        ["12 Apr", "TRANSFER - FD",          "2,00,000", "",            "28,301.00"],    # TAMPERED
        ["14 Apr", "UPI - fuel",             "2,500",    "",            "25,801.00"],
        ["15 Apr", "Closing Balance",         "",         "",            "25,801.00"],
    ]

    hdr_s = ParagraphStyle("hs", fontName="Helvetica-Bold", fontSize=9,
                           textColor=WHITE)
    cell_s = ParagraphStyle("cs", fontName="Helvetica", fontSize=9,
                            textColor=DARK_GRAY)
    red_s  = ParagraphStyle("rs", fontName="Helvetica-Bold", fontSize=9,
                            textColor=RED)

    tbl_data = [[Paragraph(h, hdr_s) for h in headers]]
    TAMPERED_ROWS = {3, 6}  # rows with inconsistent font (Photoshop edit)
    for i, row in enumerate(rows):
        style = red_s if i in TAMPERED_ROWS else cell_s
        tbl_data.append([Paragraph(c, style) for c in row])

    tbl = Table(tbl_data, colWidths=["12%","38%","14%","14%","22%"])
    tbl.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), HDFC_RED),
        ("ROWBACKGROUNDS", (0,1), (-1,-1),
         [WHITE, colors.HexColor("#fff5f5")]),
        ("BACKGROUND",  (0,4), (-1,4), colors.HexColor("#fdecea")),  # TAMPERED row
        ("BACKGROUND",  (0,7), (-1,7), colors.HexColor("#fdecea")),  # TAMPERED row
        ("GRID",        (0,0), (-1,-1), 0.3, MID_GRAY),
        ("TOPPADDING",  (0,0), (-1,-1), 5),
        ("BOTTOMPADDING",(0,0), (-1,-1), 5),
        ("LEFTPADDING", (0,0), (-1,-1), 5),
        ("ALIGN",       (2,0), (-1,-1), "RIGHT"),
    ]))
    story.append(tbl)
    story.append(Spacer(1, 5*mm))

    story.append(Paragraph(
        "🔬 IMAGE FORENSICS REPORT:<br/>"
        "• ELA Tamper Score: <b>78%</b> (TAMPERED — threshold 55%)<br/>"
        "• Rows highlighted in red show pixel-level inconsistency<br/>"
        "• EXIF Metadata: Last modified by 'Adobe Photoshop 23.0' on 15-Apr-2024<br/>"
        "• Original bank statement NOT provided<br/>"
        "• SHA-256 hash of this file does NOT match bank's digital signature<br/>"
        "• Conclusion: <b>Document fabricated to inflate claimed loss amount</b>",
        ParagraphStyle("forensics", fontName="Helvetica", fontSize=9,
                       textColor=DARK_GRAY, backColor=colors.HexColor("#fff7ed"),
                       borderPad=10, borderRadius=6, leading=15)
    ))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph(
        "AutoJustice AI Forensics | ELA Analysis | SHA-256 Chain Verified | "
        "Section 65B IEA | Tampered Evidence — NOT ADMISSIBLE",
        S("cert4", fontSize=8, textColor=RED, alignment=TA_CENTER)
    ))

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# BONUS: Chain of Custody Certificate
# ─────────────────────────────────────────────────────────────────────────────
def gen_chain_of_custody():
    path = OUTPUT_DIR / "CHAIN_OF_CUSTODY_CERTIFICATE.pdf"
    doc  = SimpleDocTemplate(str(path), pagesize=A4,
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
    story = []

    import hashlib, os

    # Header
    hdr = Drawing(17*cm, 28*mm)
    hdr.add(Rect(0, 0, 17*cm, 28*mm, fillColor=NAVY, strokeColor=None))
    # Tricolor bar
    hdr.add(Rect(0, 24*mm, 17*cm/3, 4*mm, fillColor=SAFFRON, strokeColor=None))
    hdr.add(Rect(17*cm/3, 24*mm, 17*cm/3, 4*mm, fillColor=WHITE, strokeColor=None))
    hdr.add(Rect(17*cm*2/3, 24*mm, 17*cm/3, 4*mm, fillColor=GREEN_IN, strokeColor=None))
    hdr.add(String(10, 12,
                   "AUTOJUSTICE AI NEXUS — SECTION 65B CHAIN OF CUSTODY CERTIFICATE",
                   fontName="Helvetica-Bold", fontSize=11, fillColor=WHITE))
    hdr.add(String(10, 3,
                   "Indian Evidence Act | DPDP Act 2023 | BNS 2023 | Digital Forensics",
                   fontName="Helvetica", fontSize=9,
                   fillColor=colors.HexColor("#FF9933")))
    story.append(hdr)
    story.append(Spacer(1, 6*mm))

    story.append(Paragraph(
        "CERTIFICATE OF DIGITAL EVIDENCE INTEGRITY",
        ParagraphStyle("cert_h", fontName="Helvetica-Bold", fontSize=14,
                       textColor=NAVY, alignment=TA_CENTER)
    ))
    story.append(Spacer(1, 3*mm))
    story.append(HRFlowable(width="100%", thickness=2, color=SAFFRON))
    story.append(Spacer(1, 5*mm))

    body = ParagraphStyle("cb", fontName="Helvetica", fontSize=10,
                          textColor=DARK_GRAY, leading=16)
    story.append(Paragraph(
        "I, the authorized custodian of the AutoJustice AI NEXUS digital forensics "
        "system, hereby certify that the following digital evidence files were "
        "collected, preserved, and processed in accordance with:",
        body
    ))
    story.append(Spacer(1, 3*mm))

    laws = [
        "• Section 65B, Indian Evidence Act, 1872 — Electronic Record Certificate",
        "• Section 79A, IT Act 2000 — Electronic Evidence Examiner Guidelines",
        "• Digital Personal Data Protection Act, 2023 — Data Minimization Compliance",
        "• Bharatiya Nagarik Suraksha Sanhita, 2023 — Chain of Custody Requirements",
    ]
    for law in laws:
        story.append(Paragraph(law, ParagraphStyle("law", fontName="Helvetica",
                                                    fontSize=10, textColor=BLUE,
                                                    leading=16, leftIndent=10)))
    story.append(Spacer(1, 5*mm))

    # Evidence file hashes table
    evidence_files = []
    for f in sorted(OUTPUT_DIR.glob("EVIDENCE_*.pdf")):
        data = f.read_bytes()
        sha  = hashlib.sha256(data).hexdigest()
        evidence_files.append([f.name, f"{len(data)/1024:.1f} KB", sha[:32] + "..."])

    if evidence_files:
        story.append(Paragraph("<b>Evidence Files — SHA-256 Hash Registry:</b>",
                               ParagraphStyle("eh", fontName="Helvetica-Bold",
                                              fontSize=10, textColor=NAVY)))
        story.append(Spacer(1, 3*mm))

        hdr_s  = ParagraphStyle("hh", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE)
        cell_s = ParagraphStyle("ech", fontName="Courier", fontSize=7, textColor=DARK_GRAY)
        name_s = ParagraphStyle("en", fontName="Helvetica", fontSize=8, textColor=DARK_GRAY)

        tbl_data = [[Paragraph(h, hdr_s) for h in ["File Name", "Size", "SHA-256 (truncated)"]]]
        for fname, sz, sha in evidence_files:
            tbl_data.append([
                Paragraph(fname, name_s),
                Paragraph(sz, cell_s),
                Paragraph(sha, cell_s),
            ])

        tbl = Table(tbl_data, colWidths=["42%", "12%", "46%"])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), NAVY),
            ("ROWBACKGROUNDS", (0,1), (-1,-1),
             [WHITE, colors.HexColor("#f0f4f8")]),
            ("GRID",        (0,0), (-1,-1), 0.3, MID_GRAY),
            ("TOPPADDING",  (0,0), (-1,-1), 4),
            ("BOTTOMPADDING",(0,0), (-1,-1), 4),
            ("LEFTPADDING", (0,0), (-1,-1), 4),
        ]))
        story.append(tbl)

    story.append(Spacer(1, 6*mm))
    story.append(HRFlowable(width="100%", thickness=1, color=NAVY))
    story.append(Spacer(1, 4*mm))

    # Generated timestamp
    now = datetime.utcnow().strftime("%d %B %Y at %H:%M:%S UTC")
    story.append(Paragraph(
        f"Certificate generated by AutoJustice AI NEXUS on {now}.<br/>"
        f"Computer system was in normal working condition at time of generation.<br/>"
        f"System Version: 2.0.0 | Station: Cyber Crime Police Station, Mumbai",
        ParagraphStyle("cert_foot", fontName="Helvetica", fontSize=9,
                       textColor=DARK_GRAY, leading=14)
    ))
    story.append(Spacer(1, 5*mm))

    # Signature block
    sig_data = [[
        Paragraph("Authorized Custodian<br/>AutoJustice AI NEXUS System<br/>___________________<br/>Digital Signature", body),
        Paragraph("Investigating Officer<br/>Cyber Crime Police Station<br/>___________________<br/>Badge No: MH-CC-001", body),
        Paragraph("Station House Officer<br/>Cyber Crime Unit<br/>___________________<br/>Date: " + datetime.utcnow().strftime("%d/%m/%Y"), body),
    ]]
    sig_tbl = Table(sig_data, colWidths=["33%", "34%", "33%"])
    sig_tbl.setStyle(TableStyle([
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, MID_GRAY),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(sig_tbl)

    doc.build(story)
    print("  [OK] " + path.name)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  AutoJustice AI NEXUS — Evidence File Generator")
    print("=" * 60)
    print(f"\n  Output folder: {OUTPUT_DIR}\n")

    print("  Generating GENUINE evidence files...")
    gen_bank_sms_alert()
    gen_whatsapp_fraud()
    gen_upi_receipt()
    gen_fake_investment_app()
    gen_sextortion_threat()
    gen_digital_arrest_scam()

    print("\n  Generating FALSE case evidence files...")
    gen_false_keyword_stuffing()
    gen_false_template()
    gen_false_inconsistent()
    gen_false_fabricated_statement()

    print("\n  Generating Chain of Custody Certificate...")
    gen_chain_of_custody()

    files = list(OUTPUT_DIR.iterdir())
    print(f"\n  ✓ {len(files)} files generated in demo_evidence/")
    print("\n  HOW TO USE FOR DEMO:")
    print("  ─────────────────────────────────────────────────────")
    print("  GENUINE CASES → Upload EVIDENCE_01 to EVIDENCE_06")
    print("    The AI will give HIGH/MEDIUM risk, GENUINE rating")
    print("    Complaint Report PDF will auto-generate")
    print()
    print("  FALSE CASES   → Upload FALSE_01 to FALSE_04")
    print("    The AI will give LOW risk, REJECT/REVIEW rating")
    print("    Show judges the 6-layer fake detection in action")
    print()
    print("  CHAIN OF CUSTODY → Show judges the Section 65B cert")
    print("  ─────────────────────────────────────────────────────")
    print(f"\n  Files saved to: {OUTPUT_DIR.resolve()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
