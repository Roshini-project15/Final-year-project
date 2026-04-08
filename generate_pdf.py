from fpdf import FPDF
import os

class IEEE_PDF(FPDF):
    def header(self):
        if self.page_no() == 1:
            pass # No header on first page standard

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def create_pdf(input_md, output_pdf):
    pdf = IEEE_PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    with open(input_md, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            pdf.ln(5)
            continue
            
        if line.startswith('# '):
            pdf.set_font('helvetica', 'B', 16)
            pdf.multi_cell(0, 10, line[2:].upper(), align='C')
            pdf.ln(5)
        elif line.startswith('**Abstract**'):
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 10, 'Abstract', ln=1)
            pdf.set_font('helvetica', 'I', 10)
            pdf.multi_cell(0, 5, line.replace('**Abstract**—', ''))
            pdf.ln(2)
        elif line.startswith('**Keywords**'):
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(20, 10, 'Keywords—', ln=0)
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 10, line.replace('**Keywords**—', ''))
        elif line.startswith('## '):
            pdf.ln(5)
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(0, 10, line[3:].upper(), ln=1)
        elif line.startswith('### '):
            pdf.set_font('helvetica', 'B', 11)
            pdf.cell(0, 10, line[4:], ln=1)
        elif line.startswith('*   **'):
            # This is a list item with bold
            text = line.replace('*   **', '').replace('**', '')
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 5, f'• {text}')
        elif line.startswith('[') and ']' in line:
            # Reference
            pdf.set_font('helvetica', '', 9)
            pdf.multi_cell(0, 5, line)
        else:
            pdf.set_font('helvetica', '', 10)
            pdf.multi_cell(0, 6, line)

    pdf.output(output_pdf)
    print(f"PDF generated: {output_pdf}")

if __name__ == "__main__":
    create_pdf('research_paper.md', 'AutoSystem_IEEE_Research_Paper.pdf')
