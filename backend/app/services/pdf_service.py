from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from sqlalchemy.orm import Session
from app.models.settings import Settings
from app.models.medicine import Medicine
import os


class PDFService:

    @staticmethod
    def _register_font(font_name="DejaVuSans", font_path=None):
        """
        Ensure a Unicode TTF is registered so symbols like '৳' render correctly.
        Try common system path first, then project static fonts folder.
        """
        # Common system path for DejaVu
        possible = [
            font_path,
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/local/share/fonts/DejaVuSans.ttf",
            os.path.join("app", "static", "fonts", "DejaVuSans.ttf"),
            os.path.join("static", "fonts", "DejaVuSans.ttf"),
        ]
        for p in possible:
            if not p:
                continue
            if os.path.exists(p):
                try:
                    pdfmetrics.registerFont(TTFont(font_name, p))
                    return font_name
                except Exception:
                    pass
        # fallback: try to register built-in Helvetica (won't show ৳ correctly)
        return "Helvetica"

    @staticmethod
    def generate_sale_invoice(sale, logo_path="/mnt/data/b1bc071f-b9b3-43aa-989a-ef0865e15d86.png"):
        """
        Generate a styled invoice PDF Buffer.

        - sale must have attributes: invoice_number, sale_date (string), customer_name,
          items (iterable of objects with medicine_id, quantity, selling_price),
          subtotal, discount_amount, total_amount.
        - logo_path: optional path to pharmacy logo image (PNG/JPG). Default uses uploaded file path.
        """

        # Register Unicode font that supports the ৳ symbol
        font_name = PDFService._register_font()

        buffer = BytesIO()
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )

        styles = getSampleStyleSheet()
        # base styles using registered font
        base_normal = ParagraphStyle(
            "BaseNormal",
            parent=styles["Normal"],
            fontName=font_name,
            fontSize=11,
            leading=14,
        )
        title_style = ParagraphStyle(
            "Title",
            parent=base_normal,
            fontName=font_name,
            fontSize=22,
            leading=26,
            spaceAfter=4,
        )
        small_style = ParagraphStyle(
            "Small",
            parent=base_normal,
            fontSize=10,
            leading=12,
        )
        right_style = ParagraphStyle(
            "Right",
            parent=base_normal,
            alignment=TA_RIGHT,
            fontSize=12,
            leading=14
        )
        label_style = ParagraphStyle(
            "Label",
            parent=base_normal,
            fontSize=13,
            leading=16,
            spaceAfter=6,
            fontName=font_name,
        )
        bold_right = ParagraphStyle(
            "BoldRight",
            parent=right_style,
            fontName=font_name,
        )

        elements = []

        # Get pharmacy settings & DB
        from app.db.session import SessionLocal
        db = SessionLocal()
        try:
            settings = db.query(Settings).first()

            pharmacy_name = settings.pharmacy_name if settings and settings.pharmacy_name else "Your Pharmacy Name"
            address = settings.address if settings and settings.address else "Address here"
            phone = settings.phone if settings and settings.phone else "0123456789"
        finally:
            db.close()

        # Header: left (pharmacy info) & right (invoice no + date)
        left_html = f'<b><font size=17>{pharmacy_name}</font></b><br/>' \
                    f'<font size=11>{address}</font><br/>' \
                    f'<font size=11>Phone: {phone}</font>'
        right_html = (
            '<font size=11>Invoice No</font><br/>'
            f'<b><font size=14>{sale.invoice_number}</font></b><br/><br/>'
            '<font size=11>Date</font><br/>'
            f'<b><font size=14>{sale.sale_date}</font></b>'
        )

        header_cells = []
        # left cell: optionally include logo above pharmacy name if provided
        if logo_path and os.path.exists(logo_path):
            try:
                img = Image(logo_path)
                # shrink logo to fit height ~40
                img.drawHeight = 40
                img.drawWidth = img.imageWidth * (40.0 / img.imageHeight)
                left_flow = []
                left_flow.append(img)
                left_flow.append(Spacer(1, 6))
                left_flow.append(Paragraph(left_html, base_normal))
                header_cells.append(left_flow)
            except Exception:
                header_cells.append(Paragraph(left_html, base_normal))
        else:
            header_cells.append(Paragraph(left_html, base_normal))

        header_cells.append(Paragraph(right_html, right_style))

        header_table = Table([header_cells], colWidths=[330, 200])
        header_table.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 0),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 24))

        # Customer block
        elements.append(Paragraph("<b>Customer</b>", label_style))
        elements.append(Paragraph(f"{sale.customer_name or 'Walk-in Customer'}", base_normal))
        elements.append(Spacer(1, 20))

        # Items table header + rows
        items_data = []
        # header row
        items_data.append([
            Paragraph("<b>Item</b>", base_normal),
            Paragraph("<b>Qty</b>", base_normal),
            Paragraph("<b>Price</b>", base_normal),
            Paragraph("<b>Total</b>", base_normal),
        ])

        # rows
        from app.db.session import SessionLocal
        med_db = SessionLocal()
        try:
            for item in sale.items:
                med = med_db.query(Medicine).filter(Medicine.id == item.medicine_id).first()
                name = med.name if med else f"Medicine ID: {item.medicine_id}"
                qty = str(item.quantity)
                price = f"{item.selling_price:.0f} Tk"
                total = f"{item.quantity * item.selling_price:.0f} Tk"

                items_data.append([
                    Paragraph(name, base_normal),
                    Paragraph(qty, base_normal),
                    Paragraph(price, base_normal),
                    Paragraph(total, base_normal),
                ])
        finally:
            med_db.close()

        items_table = Table(items_data, colWidths=[290, 60, 80, 80], hAlign="LEFT")
        items_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f2f2f2")),
            ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.lightgrey),
            ("ALIGN", (1, 1), (-1, -1), "LEFT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ]))

        elements.append(items_table)
        elements.append(Spacer(1, 30))

        # Totals (right aligned)
        totals_data = [
            ["", "", Paragraph("Subtotal:", base_normal), Paragraph(f" {sale.subtotal:.0f} Tk", base_normal)],
            ["", "", Paragraph("Discount:", base_normal), Paragraph(f" {sale.discount_amount:.0f} Tk", base_normal)],
            ["", "", Paragraph("<b>Total:</b>", base_normal), Paragraph(f"<b> {sale.total_amount:.0f} Tk</b>", base_normal)],
        ]
        totals_table = Table(totals_data, colWidths=[290, 60, 80, 80], hAlign="RIGHT")
        totals_table.setStyle(TableStyle([
            ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
        ]))

        # Add a little spacer to push totals to the right side visually (mimics screenshot)
        elements.append(Spacer(1, 10))
        elements.append(totals_table)

        pdf.build(elements)
        buffer.seek(0)
        return buffer
