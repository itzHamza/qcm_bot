from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.set_font("Arial", size=12)
pdf.cell(200, 10, txt="This is a dummy PDF for testing.", ln=True, align="C")
pdf.output("jules-scratch/verification/dummy.pdf")
