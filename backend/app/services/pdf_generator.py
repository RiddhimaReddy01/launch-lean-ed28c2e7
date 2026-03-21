"""
PDF Report Generator
Converts idea research data into professional PDF reports
"""

import logging
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
)

logger = logging.getLogger(__name__)


def generate_research_pdf(idea: dict) -> bytes:
    """
    Generate professional PDF report from idea research.

    Args:
        idea: Complete idea dict with all research data

    Returns:
        PDF bytes ready to download
    """

    logger.info(f"Generating PDF for idea: {idea['title']}")

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
    )

    story = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        spaceBefore=0,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#374151'),
        spaceAfter=12,
        spaceBefore=12,
    )

    # ═══════════════════════════════════════════════════════════
    # PAGE 1: TITLE & OVERVIEW
    # ═══════════════════════════════════════════════════════════

    story.append(Paragraph(idea.get("title", "Untitled Idea"), title_style))
    story.append(Paragraph(
        f"Research Report • Generated {idea['created_at'][:10]}",
        styles['Italic']
    ))
    story.append(Spacer(1, 0.3 * inch))

    if idea.get("description"):
        story.append(Paragraph(idea["description"], styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

    # Business Overview
    decomp = idea.get("decomposition", {})
    if decomp:
        story.append(Paragraph("Business Overview", heading_style))

        overview_data = [
            ["Business Type", decomp.get("business_type", "N/A")],
            ["Location", _format_location(decomp.get("location", {}))],
            ["Target Customers", _format_list(decomp.get("target_customers", []))],
            ["Price Tier", decomp.get("price_tier", "N/A")],
        ]

        table = Table(overview_data, colWidths=[1.5 * inch, 3.5 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.3 * inch))

    # ═══════════════════════════════════════════════════════════
    # PAGE 2: MARKET INSIGHTS
    # ═══════════════════════════════════════════════════════════

    discover = idea.get("discover", {})
    if discover:
        story.append(PageBreak())
        story.append(Paragraph("Market Insights", heading_style))

        insights = discover.get("insights", [])
        story.append(Paragraph(
            f"Found {len(insights)} insights from Reddit & Google Search",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))

        for i, insight in enumerate(insights[:5], 1):
            story.append(Paragraph(
                f"<b>{i}. {insight.get('title', 'Untitled')} "
                f"(Score: {insight.get('score', 0)}/10)</b>",
                styles['Heading3']
            ))

            story.append(Paragraph(
                f"Type: {_format_type(insight.get('type', 'pain_point'))} | "
                f"Mentions: {insight.get('mention_count', 0)}",
                styles['Normal']
            ))

            if insight.get("evidence"):
                ev = insight["evidence"][0]
                story.append(Paragraph(
                    f"<i>\"{ev.get('quote', '')}\"</i><br/>"
                    f"<b>Source:</b> {ev.get('source', 'Unknown')}",
                    styles['Italic']
                ))

            story.append(Spacer(1, 0.15 * inch))

    # ═══════════════════════════════════════════════════════════
    # PAGE 3: MARKET ANALYSIS
    # ═══════════════════════════════════════════════════════════

    analyze = idea.get("analyze", {})
    if analyze:
        story.append(PageBreak())
        story.append(Paragraph("Market Analysis", heading_style))

        # Opportunity
        if "opportunity" in analyze:
            opp = analyze["opportunity"]
            story.append(Paragraph("<b>Market Opportunity</b>", styles['Heading3']))

            opp_data = [
                ["Metric", "Value", "Confidence"],
                ["TAM", opp.get("tam", {}).get("formatted", "N/A"),
                 opp.get("tam", {}).get("confidence", "N/A")],
                ["SAM", opp.get("sam", {}).get("formatted", "N/A"),
                 opp.get("sam", {}).get("confidence", "N/A")],
                ["SOM", opp.get("som", {}).get("formatted", "N/A"),
                 opp.get("som", {}).get("confidence", "N/A")],
            ]

            table = Table(opp_data, colWidths=[1.5 * inch, 1.8 * inch, 1.2 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

        # Customers
        if "customers" in analyze:
            story.append(Paragraph("<b>Customer Segments</b>", styles['Heading3']))
            customers = analyze["customers"]

            for seg in customers.get("segments", [])[:3]:
                story.append(Paragraph(
                    f"<b>{seg.get('name', 'Unknown')}</b> "
                    f"({seg.get('estimated_size', 0):,} people)",
                    styles['Normal']
                ))
                story.append(Paragraph(
                    f"Pain Intensity: {seg.get('pain_intensity', 0)}/10<br/>"
                    f"Primary Need: {seg.get('primary_need', 'N/A')}",
                    styles['Normal']
                ))
                story.append(Spacer(1, 0.1 * inch))

        # Competitors
        if "competitors" in analyze:
            story.append(Paragraph("<b>Key Competitors</b>", styles['Heading3']))
            competitors = analyze["competitors"]

            comp_data = [["Company", "Strength", "Gap", "Threat"]]
            for comp in competitors.get("competitors", [])[:3]:
                comp_data.append([
                    comp.get("name", "N/A"),
                    comp.get("key_strength", "N/A")[:20] + "...",
                    comp.get("key_gap", "N/A")[:20] + "...",
                    comp.get("threat_level", "N/A").title(),
                ])

            table = Table(comp_data, colWidths=[1.2 * inch, 1.3 * inch, 1.3 * inch, 1 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.2 * inch))

    # ═══════════════════════════════════════════════════════════
    # PAGE 4: LAUNCH PLAN
    # ═══════════════════════════════════════════════════════════

    setup = idea.get("setup", {})
    if setup:
        story.append(PageBreak())
        story.append(Paragraph("Launch Plan", heading_style))

        # Cost Tiers
        story.append(Paragraph("<b>Cost Tiers</b>", styles['Heading3']))

        cost_data = [["Tier", "Model", "Min", "Max"]]
        for tier in setup.get("cost_tiers", []):
            tr = tier.get("total_range", {})
            cost_data.append([
                tier.get("tier", "").replace("_", " ").title(),
                tier.get("model", "N/A")[:15],
                f"${tr.get('min', 0):,.0f}",
                f"${tr.get('max', 0):,.0f}",
            ])

        table = Table(cost_data, colWidths=[1.2 * inch, 1.3 * inch, 1.2 * inch, 1.3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10b981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
        ]))
        story.append(table)
        story.append(Spacer(1, 0.2 * inch))

        # Timeline
        story.append(Paragraph("<b>Implementation Timeline</b>", styles['Heading3']))

        for phase in setup.get("timeline", [])[:4]:
            story.append(Paragraph(
                f"<b>{phase.get('phase', 'Unknown')}</b> "
                f"({phase.get('weeks', 'N/A')} weeks)",
                styles['Normal']
            ))

            milestones = phase.get("milestones", [])
            milestone_text = "; ".join(milestones[:2])
            if len(milestones) > 2:
                milestone_text += f"; +{len(milestones)-2} more"

            story.append(Paragraph(milestone_text, styles['Italic']))
            story.append(Spacer(1, 0.1 * inch))

    # ═══════════════════════════════════════════════════════════
    # PAGE 5: FINANCIAL PROJECTIONS
    # ═══════════════════════════════════════════════════════════

    financials = idea.get("financials", {})
    if financials:
        story.append(PageBreak())
        story.append(Paragraph("Financial Projections", heading_style))

        y1 = financials.get("year_1", {})
        if y1:
            fin_data = [
                ["Metric", "Year 1"],
                ["Total Revenue", f"${y1.get('total_revenue', 0):,.0f}"],
                ["Total Expenses", f"${y1.get('total_expenses', 0):,.0f}"],
                ["Net Profit", f"${y1.get('net_profit', 0):,.0f}"],
                ["Customers at EOY", f"{y1.get('ending_customers', 0):.0f}"],
            ]

            table = Table(fin_data, colWidths=[2 * inch, 2.5 * inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#8b5cf6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e5e7eb')),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.15 * inch))

        # Breakeven
        breakeven = financials.get("breakeven_analysis", {})
        if breakeven.get("breakeven_month"):
            story.append(Paragraph(
                f"<b>Breakeven: Month {breakeven.get('breakeven_month')} "
                f"({breakeven.get('breakeven_timeframe', 'N/A')})</b>",
                styles['Normal']
            ))
            story.append(Spacer(1, 0.15 * inch))

    # ═══════════════════════════════════════════════════════════
    # PAGE 6: RISK ASSESSMENT
    # ═══════════════════════════════════════════════════════════

    risks = idea.get("risks", {})
    if risks:
        story.append(PageBreak())
        story.append(Paragraph("Risk Assessment", heading_style))

        top_risks = risks.get("top_3_risks", [])
        for risk in top_risks:
            story.append(Paragraph(
                f"<b>{risk.get('risk', 'Unknown')}</b>",
                styles['Normal']
            ))
            story.append(Paragraph(
                f"Severity: {risk.get('severity_score', 0)}/10 | "
                f"Mitigation: {risk.get('mitigation', 'N/A')}",
                styles['Italic']
            ))
            story.append(Spacer(1, 0.15 * inch))

    # ═══════════════════════════════════════════════════════════
    # BUILD PDF
    # ═══════════════════════════════════════════════════════════

    doc.build(story)
    buffer.seek(0)

    logger.info(f"PDF generated successfully for idea: {idea['title']}")

    return buffer.getvalue()


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _format_location(location: dict) -> str:
    """Format location dict as readable string."""
    parts = []
    if location.get("city"):
        parts.append(location["city"])
    if location.get("state"):
        parts.append(location["state"])
    if location.get("metro"):
        parts.append(f"({location['metro']})")

    return ", ".join(parts) if parts else "N/A"


def _format_list(items: list) -> str:
    """Format list as comma-separated string."""
    if isinstance(items, list):
        return ", ".join(str(item) for item in items[:3])
    return str(items)


def _format_type(type_str: str) -> str:
    """Format type string for display."""
    return type_str.replace("_", " ").title()
