from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate,
    Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
pt = 1

OUTPUT = "/Users/radalzubi/Desktop/wg1/Husam Khoury/project_brief.pdf"
W, H   = A4
ML = MR = 50 * pt
MT = 42 * pt
MB = 34 * pt

NAVY  = colors.HexColor("#1C2951")
GRAY  = colors.HexColor("#555555")
LGRAY = colors.HexColor("#888888")
DARK  = colors.HexColor("#1a1a1a")

def S(name, **kw):
    defaults = dict(fontName="Helvetica", fontSize=8.5, leading=11.2,
                    spaceAfter=0, textColor=DARK, alignment=TA_JUSTIFY)
    defaults.update(kw)
    return ParagraphStyle(name, **defaults)

title_s   = S("t",  fontName="Helvetica-Bold",    fontSize=16,  leading=20,  alignment=TA_CENTER, textColor=NAVY, spaceAfter=3*pt)
sub_s     = S("st", fontName="Helvetica-Oblique", fontSize=9.5, leading=12,  alignment=TA_CENTER, textColor=GRAY, spaceAfter=7*pt)
hdr_s     = S("h",  fontName="Helvetica-Bold",    fontSize=8.5, leading=11,  spaceBefore=7*pt, spaceAfter=2*pt, textColor=NAVY, alignment=TA_LEFT)
body_s    = S("b",  fontName="Helvetica",         fontSize=8.5, leading=11.2, alignment=TA_JUSTIFY)
refhdr_s  = S("rh", fontName="Helvetica-Bold",    fontSize=7,   leading=9,   textColor=LGRAY, alignment=TA_LEFT, spaceAfter=2*pt)
ref_s     = S("r",  fontName="Helvetica",         fontSize=7,   leading=9.2, textColor=LGRAY, alignment=TA_LEFT)
foot_s    = S("f",  fontName="Helvetica",         fontSize=7.8, leading=10.5, textColor=GRAY, alignment=TA_LEFT)

story = []

# ── TITLE
story.append(Paragraph("Wasel", title_s))
story.append(Paragraph("To Move Jordan Forward, Fairly", sub_s))
story.append(HRFlowable(width="100%", thickness=0.6, color=colors.HexColor("#CCCCCC"), spaceAfter=8*pt))

# ── CONCEPT
story.append(Paragraph("CONCEPT", hdr_s))
story.append(Paragraph(
    "We are a Ride Hailing platform that charges a flat tiered monthly fee instead of taking a "
    "commission on every ride, allowing the driver to keep 100% of the fare. In doing so we allow "
    "the drivers to generate more income per hour. Here, pricing is done based only on supply and "
    "demand with no corporate incentives through commission, eliminating price inflation. This "
    "creates an income that remains stable, more measurable and confident.",
    body_s))
story.append(Spacer(1, 5*pt))
story.append(Paragraph(
    "We aim to disrupt the current Ride Hailing market in underserved economies, where we can "
    "maximize the value to drivers that need it the most. We hope to address a larger market in "
    "doing so, by creating a benefit that incentivizes a greater portion of people to make more "
    "with us. In essence, we do not hire drivers. We work with them.",
    body_s))

# ── THE PROBLEM
story.append(Paragraph("THE PROBLEM", hdr_s))
story.append(Paragraph(
    "Dominant Ride Hailing platforms all charge a market standard of 30% of each ride. This means "
    "the average driver in Jordan making 581 JOD a month will net 407 JOD after commission is "
    "taken. This difference, based on interviews with drivers and industry contacts, is the core "
    "pain point app-licensed drivers report. As a result, out of 60,000 total ride hailing drivers "
    "in Jordan, only around 12,000 operate on large licensed apps. The current economic model "
    "under-utilizes the potential driver pool.",
    body_s))
story.append(Spacer(1, 4*pt))
story.append(Paragraph(
    "Furthermore, a commission-based model incentivizes platforms to inflate surge pricing to "
    "maximize corporate returns at the expense of both riders and drivers. This creates a net "
    "negative for all stakeholders using licensed apps as their primary means of transportation.",
    body_s))
story.append(Spacer(1, 4*pt))
story.append(Paragraph(
    "The Land Transport Regulatory Commission (LTRC) expressed concerns about high commission "
    "rates and increased efforts to shut down unlicensed operations. They opened the permit to "
    "new companies to promote domestic and foreign investment while simultaneously addressing the "
    "commission problem. This creates a window for Wasel to use government intent to solve a "
    "social and economic problem while generating a profit.",
    body_s))

# ── OUR APPROACH
story.append(Paragraph("OUR APPROACH", hdr_s))
story.append(Paragraph(
    "This will be done using specific tiered access fees that change with ride volume for the "
    "driver. Each tier comes with benefits such as higher trip allocation, better riders, priority "
    "support, and insurance incentives. With a 30% commission, drivers spend 1/3 of their time "
    "paying Uber. With our model, this is reduced to almost 1/26th of their time. These tiers "
    "serve as the main revenue source, alongside ancillary streams such as insurance brokering "
    "and ad space. Additional features such as carpooling and on-demand large-item transport may "
    "be added post-launch.",
    body_s))

# ── DRIVER IMPACT
story.append(Paragraph("DRIVER IMPACT", hdr_s))
story.append(Paragraph(
    "A driver who earned 581 JOD and netted 407 JOD after 30% commission will net 561 JOD with "
    "Wasel. This is a substantial improvement, representing almost 30% more monthly take-home "
    "income. This does not account for tips, or the additional earnings during surge periods "
    "where Wasel takes no cut. The platform also creates an incentive to work more, since the "
    "value of the driver\u2019s time is 100% theirs. The app comes with quality-of-life "
    "incentives including better and subsidized insurance rates.",
    body_s))

# ── RIDER IMPACT
story.append(Paragraph("RIDER IMPACT", hdr_s))
story.append(Paragraph(
    "Because of the way the financial model is structured, peak hour pricing is drastically "
    "cheaper for riders. Surge pricing is not inflated by platform extraction, so riders benefit "
    "directly from the flat-fee model. Student discounts, referral programs, and on-ground "
    "ambassadors are all part of a broader rider acquisition strategy.",
    body_s))

# ── PROOF OF CONCEPT
story.append(Paragraph("PROOF OF CONCEPT", hdr_s))
story.append(Paragraph(
    "Empower, founded in 2019 in the USA, is a Ride Hailing platform using a similar financial "
    "model. It has grown rapidly in Washington DC, Miami, and New York City, penetrating a highly "
    "competitive market in under a year. They now see approximately 200,000 rides per week, and "
    "riders report paying and waiting 20% less on average.",
    body_s))
story.append(Spacer(1, 4*pt))
story.append(Paragraph(
    "This is a problem that extends beyond Jordan. We intend to expand into Iraqi and Egyptian "
    "markets, with a longer view on Syria, Lebanon, and Palestine. The subscription TAM in Jordan "
    "is estimated at 11.9 million JOD. The combined TAM across Jordan, Iraq, and Egypt is "
    "estimated at 78 million JOD. This does not account for any expansion of services or "
    "vertical integration.",
    body_s))

# ── REFERENCES
story.append(Spacer(1, 6*pt))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=3*pt))
story.append(Paragraph("SELECTED REFERENCES", refhdr_s))
refs = [
    ("1.", "Husna.fm. Number of licensed ride hailing drivers in Jordan. "
           "https://husna.fm/%D9%85%D8%AD%D9%84%D9%8A/%D8%B9%D8%AF%D8%AF-%D8%B3%D8%A7%D8%A6%D9%82%D9%8A-"
           "%D8%AA%D8%B7%D8%A8%D9%8A%D9%82%D8%A7%D8%AA-%D8%A7%D9%84%D9%86%D9%82%D9%84-%D8%A7%D9%84%D8%A3%D8%B1%D8%AF%D9%86"),
    ("2.", "Astute Analytica. MENA Ride Hailing Market Report 2024 to 2032."),
    ("3.", "Jordan Times. Driver protest and platform boycott coverage. March 2024."),
    ("4.", "Land Transport Regulatory Commission. Licensed vehicle data. December 2024."),
    ("5.", "Statista. Jordan ride hailing market size projections 2025 to 2029."),
    ("6.", "Jabbar Internet Group. Portfolio and investment history. jabbar.net."),
]
for num, text in refs:
    story.append(Paragraph(f"<b>{num}</b> {text}", ref_s))

# ── FOOTER
story.append(Spacer(1, 8*pt))
story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#CCCCCC"), spaceAfter=4*pt))
CW = (W - ML - MR) / 2
footer_data = [[
    Paragraph("<b>Rad AlZubi</b>  |  <b>Mustafa Sabieha</b><br/>Founders, Wasel  |  hello@wasel.jo", foot_s),
    Paragraph(
        "<b>wasel.jo</b><br/>Confidential, prepared for Hussam Khoury, Jabbar Internet Group",
        ParagraphStyle("fr", fontName="Helvetica", fontSize=7.5, leading=10.5,
                       textColor=LGRAY, alignment=2)
    )
]]
ft = Table(footer_data, colWidths=[CW, CW])
ft.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "TOP")]))
story.append(ft)

doc = BaseDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    title="Wasel Project Brief", author="Rad AlZubi",
)
frame = Frame(ML, MB, W - ML - MR, H - MT - MB, id="main")
doc.addPageTemplates([PageTemplate(id="main", frames=[frame])])
doc.build(story)
print("PDF saved \u2192", OUTPUT)
