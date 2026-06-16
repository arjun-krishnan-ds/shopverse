from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO


class InvoiceService:

    @staticmethod
    def generate_invoice(order):

        buffer = BytesIO()

        doc = SimpleDocTemplate(buffer)

        styles = getSampleStyleSheet()

        elements = []

        elements.append(Paragraph(f"Invoice #{order.id}", styles["Title"]))
        elements.append(Spacer(1, 10))

        elements.append(Paragraph(f"Customer: {order.user}", styles["Normal"]))
        elements.append(Paragraph(f"Total: ₹{order.total}", styles["Normal"]))

        elements.append(Spacer(1, 20))

        for item in order.items.all():
            elements.append(
                Paragraph(
                    f"{item.product_name} x {item.quantity} - ₹{item.price}",
                    styles["Normal"]
                )
            )

        doc.build(elements)

        buffer.seek(0)

        return buffer