"""
PDF Rapor Üretici — Öğrenci ve Sınıf Raporları
reportlab kullanılarak üretilir.
"""
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── Türkçe karakter destekli font kaydı ──────────────────────────────────────
try:
    pdfmetrics.registerFont(TTFont("Arial",     "C:/Windows/Fonts/arial.ttf"))
    pdfmetrics.registerFont(TTFont("Arial-Bold","C:/Windows/Fonts/arialbd.ttf"))
    FONT_NORMAL = "Arial"
    FONT_BOLD   = "Arial-Bold"
except Exception:
    FONT_NORMAL = FONT_NORMAL
    FONT_BOLD   = FONT_BOLD

# ── Renk Paleti ──────────────────────────────────────────────────────────────
PRIMARY    = colors.HexColor("#4361ee")
SUCCESS    = colors.HexColor("#10b981")
WARNING    = colors.HexColor("#f59e0b")
DANGER     = colors.HexColor("#ef4444")
DARK       = colors.HexColor("#1e293b")
MUTED      = colors.HexColor("#64748b")
LIGHT_BG   = colors.HexColor("#f1f5f9")
BORDER     = colors.HexColor("#e2e8f0")
WHITE      = colors.white

# ── Performans rengi ──────────────────────────────────────────────────────────
def perf_color(label: str):
    mapping = {
        "Üstün Başarılı":       colors.HexColor("#059669"),
        "Ortalamanın Üstünde":  colors.HexColor("#10b981"),
        "Geliştirilmeli":       colors.HexColor("#f59e0b"),
        "Sınırda":              colors.HexColor("#f97316"),
        "Kritik Seviye":        colors.HexColor("#ef4444"),
    }
    return mapping.get(label, MUTED)

def score_color(score):
    if score is None:
        return MUTED
    if score >= 70:
        return SUCCESS
    if score >= 60:
        WARNING
    return DANGER

def _styles():
    styles = getSampleStyleSheet()
    return {
        "title":    ParagraphStyle("title",    fontSize=18, fontName=FONT_BOLD,
                                   textColor=WHITE, alignment=TA_CENTER, leading=22),
        "subtitle": ParagraphStyle("subtitle", fontSize=11, fontName=FONT_NORMAL,
                                   textColor=colors.HexColor("#c7d2fe"), alignment=TA_CENTER),
        "h2":       ParagraphStyle("h2",       fontSize=12, fontName=FONT_BOLD,
                                   textColor=PRIMARY, leading=18),
        "h3":       ParagraphStyle("h3",       fontSize=10, fontName=FONT_BOLD,
                                   textColor=DARK, leading=14),
        "body":     ParagraphStyle("body",     fontSize=9,  fontName=FONT_NORMAL,
                                   textColor=DARK, leading=13),
        "small":    ParagraphStyle("small",    fontSize=8,  fontName=FONT_NORMAL,
                                   textColor=MUTED, leading=12),
        "label":    ParagraphStyle("label",    fontSize=8,  fontName=FONT_BOLD,
                                   textColor=MUTED),
        "value":    ParagraphStyle("value",    fontSize=9,  fontName=FONT_BOLD,
                                   textColor=DARK),
        "center":   ParagraphStyle("center",   fontSize=9,  fontName=FONT_NORMAL,
                                   alignment=TA_CENTER, textColor=DARK),
        "right":    ParagraphStyle("right",    fontSize=9,  fontName=FONT_NORMAL,
                                   alignment=TA_RIGHT, textColor=DARK),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Öğrenci Performans Raporu
# ─────────────────────────────────────────────────────────────────────────────

def generate_student_pdf(student: dict, analysis: dict, recommendations: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
        title=f"Öğrenci Raporu - {student.get('full_name', '')}",
    )
    S = _styles()
    story = []

    # ── Başlık Bandı ─────────────────────────────────────────────────────────
    header_table = Table(
        [[Paragraph("EduTrack", S["title"]),
          Paragraph("Öğrenci Performans Raporu", S["subtitle"])]],
        colWidths=["50%", "50%"]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), PRIMARY),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("ROUNDEDCORNERS", [8, 8, 8, 8]),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Öğrenci Bilgileri ─────────────────────────────────────────────────────
    grade_a   = analysis.get("grade_analysis", {})
    att_a     = analysis.get("attendance_analysis", {})
    act_a     = analysis.get("activity_analysis", {})
    perf_label = analysis.get("performance_label", "—")
    trend_info = analysis.get("grade_trend", {})

    overall_avg = grade_a.get("overall_average", "—")
    absence_rate = att_a.get("absence_rate", 0)

    # Çok boyutlu kompozit skor (Rapor formülü: not%70 + devamsızlık%20 + aktivite%10)
    if isinstance(overall_avg, (int, float)):
        att_score    = max(0, 100 - absence_rate)
        active_count = act_a.get("active_activities", 0)
        act_bonus    = min(active_count * 2, 10)   # max 10 puan
        composite    = round(overall_avg * 0.70 + att_score * 0.20 + act_bonus, 1)
    else:
        composite = "—"

    info_data = [
        [Paragraph("<b>Ad Soyad</b>", S["label"]),
         Paragraph(student.get("full_name", "—"), S["value"]),
         Paragraph("<b>Öğrenci No</b>", S["label"]),
         Paragraph(student.get("student_number", "—"), S["value"])],
        [Paragraph("<b>Sınıf</b>", S["label"]),
         Paragraph(student.get("class_name", "—"), S["value"]),
         Paragraph("<b>Performans</b>", S["label"]),
         Paragraph(perf_label, S["value"])],
        [Paragraph("<b>Rapor Tarihi</b>", S["label"]),
         Paragraph(datetime.now().strftime("%d.%m.%Y %H:%M"), S["value"]),
         Paragraph("<b>Trend</b>", S["label"]),
         Paragraph(trend_info.get("trend", "—"), S["value"])],
    ]
    info_table = Table(info_data, colWidths=["22%","28%","22%","28%"])
    info_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), LIGHT_BG),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 0.5*cm))

    # ── Özet Stat Kutuları ────────────────────────────────────────────────────
    stat_data = [[
        Paragraph(f"<b>{overall_avg}</b><br/><font size='8' color='#64748b'>Genel Ortalama</font>", S["center"]),
        Paragraph(f"<b>{grade_a.get('passing_courses','—')}/{grade_a.get('total_courses','—')}</b><br/><font size='8' color='#64748b'>Geçilen / Toplam Ders</font>", S["center"]),
        Paragraph(f"<b>%{absence_rate}</b><br/><font size='8' color='#64748b'>Devamsızlık Oranı</font>", S["center"]),
        Paragraph(f"<b>{composite}</b><br/><font size='8' color='#64748b'>Kompozit Skor</font>", S["center"]),
    ]]
    stat_table = Table(stat_data, colWidths=["25%","25%","25%","25%"])
    stat_bg_colors = [
        ("BACKGROUND", (0,0), (0,0), colors.HexColor("#eff6ff")),
        ("BACKGROUND", (1,0), (1,0), colors.HexColor("#f0fdf4")),
        ("BACKGROUND", (2,0), (2,0), colors.HexColor("#fef9c3") if absence_rate < 20 else colors.HexColor("#fee2e2")),
        ("BACKGROUND", (3,0), (3,0), colors.HexColor("#f5f3ff")),
    ]
    stat_table.setStyle(TableStyle([
        *stat_bg_colors,
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("GRID", (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN", (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Ders Notları Tablosu ──────────────────────────────────────────────────
    story.append(Paragraph("Ders Notları", S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    course_breakdown = grade_a.get("course_breakdown", [])
    if course_breakdown:
        headers = ["Ders Adı", "Ders Kodu", "Ortalama", "Harf", "Durum"]
        rows = [headers]
        for c in course_breakdown:
            score = c.get("score")
            status_text = "Geçti" if c.get("is_passing") else ("Kaldı" if c.get("is_passing") is False else "—")
            rows.append([
                c.get("course_name", "—"),
                c.get("course_code", "—"),
                f"{score:.1f}" if isinstance(score, (int, float)) else "—",
                c.get("letter_grade") or "—",
                status_text,
            ])

        grade_table = Table(rows, colWidths=["38%","18%","15%","12%","17%"])
        ts = TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("ALIGN",         (2,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.4, BORDER),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ])
        for i, c in enumerate(course_breakdown, start=1):
            sc = c.get("score")
            if isinstance(sc, (int, float)):
                col = SUCCESS if sc >= 70 else (WARNING if sc >= 60 else DANGER)
                ts.add("TEXTCOLOR", (2,i), (2,i), col)
                ts.add("FONTNAME",  (2,i), (2,i), FONT_BOLD)
            if c.get("is_passing") is False:
                ts.add("TEXTCOLOR", (4,i), (4,i), DANGER)
            elif c.get("is_passing"):
                ts.add("TEXTCOLOR", (4,i), (4,i), SUCCESS)
        grade_table.setStyle(ts)
        story.append(grade_table)
    else:
        story.append(Paragraph("Not verisi bulunmamaktadır.", S["small"]))

    story.append(Spacer(1, 0.6*cm))

    # ── Devamsızlık Özeti ─────────────────────────────────────────────────────
    att_courses = analysis.get("attendance_per_course", [])
    if att_courses:
        story.append(Paragraph("Ders Bazlı Devamsızlık", S["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

        att_rows = [["Ders", "Toplam", "Devamsız", "Geç", "Katılım %", "Durum"]]
        for r in att_courses:
            att_rows.append([
                r.get("course_name", "—"),
                str(r.get("total_weeks", 0)),
                str(r.get("missed_weeks", 0)),
                str(r.get("late_weeks", 0)),
                f"%{r.get('attendance_pct', 0)}",
                r.get("status", "—"),
            ])
        att_table = Table(att_rows, colWidths=["34%","12%","12%","10%","16%","16%"])
        att_ts = TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), colors.HexColor("#0f172a")),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("ALIGN",         (1,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.4, BORDER),
            ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
        ])
        for i, r in enumerate(att_courses, start=1):
            status = r.get("status", "")
            col = DANGER if status == "Kritik" else (WARNING if status == "Uyarı" else SUCCESS)
            att_ts.add("TEXTCOLOR", (5,i), (5,i), col)
            att_ts.add("FONTNAME",  (5,i), (5,i), FONT_BOLD)
        att_table.setStyle(att_ts)
        story.append(att_table)
        story.append(Spacer(1, 0.6*cm))

    # ── Öneriler ──────────────────────────────────────────────────────────────
    if recommendations:
        story.append(Paragraph("Sistem Önerileri", S["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))
        for rec in recommendations[:6]:  # max 6 öneri
            priority = rec.get("priority", "low")
            p_color  = DANGER if priority == "high" else (WARNING if priority == "medium" else SUCCESS)
            p_label  = "Yüksek" if priority == "high" else ("Orta" if priority == "medium" else "Düşük")
            rec_row  = Table([[
                Paragraph(f"<b>{rec.get('title','')}</b>", S["h3"]),
                Paragraph(p_label, ParagraphStyle("pl", fontSize=7, fontName=FONT_BOLD,
                                                   textColor=p_color, alignment=TA_RIGHT)),
            ]], colWidths=["85%","15%"])
            rec_row.setStyle(TableStyle([
                ("TOPPADDING", (0,0), (-1,-1), 0),
                ("BOTTOMPADDING", (0,0), (-1,-1), 0),
                ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ]))
            story.append(KeepTogether([
                rec_row,
                Paragraph(rec.get("message","")[:200], S["small"]),
                Spacer(1, 0.1*cm),
                HRFlowable(width="100%", thickness=0.3, color=BORDER, spaceAfter=4),
            ]))

    # ── Alt Bilgi ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    footer_table = Table([[
        Paragraph("EduTrack — Öğrenci Not ve Performans Analiz Sistemi", S["small"]),
        Paragraph(f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                  ParagraphStyle("fr", fontSize=8, fontName=FONT_NORMAL, alignment=TA_RIGHT, textColor=MUTED)),
    ]], colWidths=["60%","40%"])
    footer_table.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 0.5, BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(footer_table)

    doc.build(story)
    return buffer.getvalue()


# ─────────────────────────────────────────────────────────────────────────────
# Sınıf Raporu
# ─────────────────────────────────────────────────────────────────────────────

def generate_class_pdf(class_name: str, analysis: dict, students: list) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        topMargin=1.5*cm, bottomMargin=2*cm,
        leftMargin=2*cm, rightMargin=2*cm,
        title=f"Sınıf Raporu - {class_name}",
    )
    S = _styles()
    story = []

    # ── Başlık Bandı ─────────────────────────────────────────────────────────
    header_table = Table(
        [[Paragraph("EduTrack", S["title"]),
          Paragraph(f"{class_name} — Sınıf Raporu", S["subtitle"])]],
        colWidths=["40%","60%"]
    )
    header_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#0f172a")),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 16),
        ("RIGHTPADDING",  (0,0), (-1,-1), 16),
        ("ALIGN",  (0,0), (-1,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.4*cm))

    # ── Sınıf İstatistikleri ──────────────────────────────────────────────────
    stat_data = [[
        Paragraph(f"<b>{analysis.get('class_average','—')}</b><br/><font size='8' color='#64748b'>Sınıf Ortalaması</font>", S["center"]),
        Paragraph(f"<b>{analysis.get('class_median','—')}</b><br/><font size='8' color='#64748b'>Medyan</font>", S["center"]),
        Paragraph(f"<b>{analysis.get('highest_average','—')}</b><br/><font size='8' color='#64748b'>En Yüksek</font>", S["center"]),
        Paragraph(f"<b>{analysis.get('lowest_average','—')}</b><br/><font size='8' color='#64748b'>En Düşük</font>", S["center"]),
        Paragraph(f"<b>{analysis.get('std_deviation','—')}</b><br/><font size='8' color='#64748b'>Std. Sapma</font>", S["center"]),
        Paragraph(f"<b>{len(analysis.get('at_risk_students',[]))}</b><br/><font size='8' color='#64748b'>Risk Altında</font>", S["center"]),
    ]]
    stat_table = Table(stat_data, colWidths=["16.6%"]*6)
    stat_table.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (1,0), colors.HexColor("#eff6ff")),
        ("BACKGROUND",    (2,0), (2,0), colors.HexColor("#f0fdf4")),
        ("BACKGROUND",    (3,0), (3,0), colors.HexColor("#fff1f2")),
        ("BACKGROUND",    (4,0), (4,0), colors.HexColor("#fef9c3")),
        ("BACKGROUND",    (5,0), (5,0), colors.HexColor("#fff1f2")),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("GRID",          (0,0), (-1,-1), 0.5, BORDER),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(stat_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Öğrenci Listesi ───────────────────────────────────────────────────────
    story.append(Paragraph("Öğrenci Performans Listesi", S["h2"]))
    story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    # Öğrencileri overall_average'a göre sırala
    sorted_students = sorted(
        [s for s in students if s.get("overall_average") is not None],
        key=lambda x: x.get("overall_average", 0), reverse=True
    )
    no_grade = [s for s in students if s.get("overall_average") is None]
    sorted_students.extend(no_grade)

    headers = ["Sıra", "Ad Soyad", "Öğrenci No", "Ortalama", "Performans", "Durum"]
    rows = [headers]
    class_avg = analysis.get("class_average", 0)

    for rank, s in enumerate(sorted_students, start=1):
        avg = s.get("overall_average")
        avg_str = f"{avg:.1f}" if isinstance(avg, (int, float)) else "—"
        durum = "Geçti" if isinstance(avg, (int, float)) and avg >= 60 else ("Kaldı" if isinstance(avg, (int, float)) else "—")
        rows.append([
            str(rank),
            s.get("full_name", "—"),
            s.get("student_number", "—"),
            avg_str,
            s.get("performance_label") or "—",
            durum,
        ])

    student_table = Table(rows, colWidths=["8%","30%","20%","14%","16%","12%"])
    st = TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), PRIMARY),
        ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
        ("FONTNAME",      (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE",      (0,0), (-1,-1), 8.5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 6),
        ("RIGHTPADDING",  (0,0), (-1,-1), 6),
        ("ALIGN",         (0,0), (0,-1), "CENTER"),
        ("ALIGN",         (3,0), (-1,-1), "CENTER"),
        ("GRID",          (0,0), (-1,-1), 0.4, BORDER),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS",(0,1), (-1,-1), [WHITE, LIGHT_BG]),
    ])
    for i, s in enumerate(sorted_students, start=1):
        avg = s.get("overall_average")
        if isinstance(avg, (int, float)):
            col = SUCCESS if avg >= 70 else (WARNING if avg >= 60 else DANGER)
            st.add("TEXTCOLOR", (3,i), (3,i), col)
            st.add("FONTNAME",  (3,i), (3,i), FONT_BOLD)
            if avg < 60:
                st.add("TEXTCOLOR", (5,i), (5,i), DANGER)
            else:
                st.add("TEXTCOLOR", (5,i), (5,i), SUCCESS)
    student_table.setStyle(st)
    story.append(student_table)
    story.append(Spacer(1, 0.6*cm))

    # ── Risk Öğrencileri ──────────────────────────────────────────────────────
    risk_students = analysis.get("at_risk_students", [])
    if risk_students:
        story.append(Paragraph("Risk Altındaki Öğrenciler", S["h2"]))
        story.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

        risk_rows = [["Ad Soyad", "Öğrenci No", "Ortalama", "Durum"]]
        for r in risk_students:
            risk_rows.append([
                r.get("full_name", "—"),
                r.get("student_number", "—"),
                str(r.get("average", "—")),
                "Risk Altında",
            ])
        risk_table = Table(risk_rows, colWidths=["40%","25%","20%","15%"])
        risk_table.setStyle(TableStyle([
            ("BACKGROUND",    (0,0), (-1,0), DANGER),
            ("TEXTCOLOR",     (0,0), (-1,0), WHITE),
            ("FONTNAME",      (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE",      (0,0), (-1,-1), 8.5),
            ("TOPPADDING",    (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
            ("LEFTPADDING",   (0,0), (-1,-1), 6),
            ("RIGHTPADDING",  (0,0), (-1,-1), 6),
            ("ALIGN",         (2,0), (-1,-1), "CENTER"),
            ("GRID",          (0,0), (-1,-1), 0.4, BORDER),
            ("ROWBACKGROUNDS",(0,1), (-1,-1), [colors.HexColor("#fff5f5"), WHITE]),
            ("TEXTCOLOR",     (2,1), (2,-1), DANGER),
            ("FONTNAME",      (2,1), (2,-1), FONT_BOLD),
        ]))
        story.append(risk_table)

    # ── Alt Bilgi ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 1*cm))
    footer_table = Table([[
        Paragraph("EduTrack — Öğrenci Not ve Performans Analiz Sistemi", S["small"]),
        Paragraph(f"Oluşturulma: {datetime.now().strftime('%d.%m.%Y %H:%M')}",
                  ParagraphStyle("fr", fontSize=8, fontName=FONT_NORMAL, alignment=TA_RIGHT, textColor=MUTED)),
    ]], colWidths=["60%","40%"])
    footer_table.setStyle(TableStyle([
        ("LINEABOVE", (0,0), (-1,0), 0.5, BORDER),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(footer_table)

    doc.build(story)
    return buffer.getvalue()
