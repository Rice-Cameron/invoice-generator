import os
from datetime import datetime
from django.conf import settings
from django.template.loader import render_to_string
from django.core.files.base import ContentFile
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration


class InvoicePDFGenerator:
    """
    Service for generating PDF invoices using WeasyPrint.
    """
    
    def __init__(self, invoice):
        self.invoice = invoice
        self.font_config = FontConfiguration()
    
    def generate_pdf(self):
        """
        Generate PDF for the invoice and save it to the invoice model.
        """
        # Generate HTML content
        html_content = self._generate_html()
        
        # Convert to PDF
        pdf_content = self._convert_to_pdf(html_content)
        
        # Save to invoice model
        filename = f"invoice_{self.invoice.invoice_number}_{datetime.now().strftime('%Y%m%d')}.pdf"
        self.invoice.pdf_file.save(filename, ContentFile(pdf_content), save=True)
        
        return self.invoice.pdf_file
    
    def _generate_html(self):
        """
        Generate HTML content for the invoice.
        """
        context = {
            'invoice': self.invoice,
            'user': self.invoice.user,
            'client': self.invoice.client,
            'items': self.invoice.items.all(),
            'generated_date': datetime.now().strftime('%B %d, %Y'),
        }
        
        return render_to_string('invoices/invoice_template.html', context)
    
    def _convert_to_pdf(self, html_content):
        """
        Convert HTML content to PDF using WeasyPrint.
        """
        # Create HTML object
        html = HTML(string=html_content)
        
        # Create CSS object with custom styles
        css = CSS(
            string=self._get_css_styles(),
            font_config=self.font_config
        )
        
        # Generate PDF
        pdf_content = html.write_pdf(stylesheets=[css], font_config=self.font_config)
        
        return pdf_content
    
    def _get_css_styles(self):
        """
        Get CSS styles for the invoice PDF.
        """
        return """
        @page {
            size: A4;
            margin: 2cm;
            @top-center {
                content: "Invoice";
                font-size: 10pt;
                color: #666;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Helvetica', 'Arial', sans-serif;
            font-size: 12pt;
            line-height: 1.4;
            color: #333;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2cm;
            border-bottom: 2px solid #333;
            padding-bottom: 1cm;
        }
        
        .header h1 {
            font-size: 24pt;
            margin: 0;
            color: #333;
        }
        
        .header .subtitle {
            font-size: 14pt;
            color: #666;
            margin-top: 0.5cm;
        }
        
        .invoice-info {
            display: table;
            width: 100%;
            margin-bottom: 2cm;
        }
        
        .invoice-info .left {
            display: table-cell;
            width: 50%;
            vertical-align: top;
        }
        
        .invoice-info .right {
            display: table-cell;
            width: 50%;
            vertical-align: top;
            text-align: right;
        }
        
        .invoice-details {
            background: #f9f9f9;
            padding: 1cm;
            border-radius: 5px;
        }
        
        .invoice-details h3 {
            margin: 0 0 0.5cm 0;
            color: #333;
        }
        
        .invoice-details p {
            margin: 0.2cm 0;
        }
        
        .bill-to {
            margin-bottom: 2cm;
        }
        
        .bill-to h3 {
            margin: 0 0 0.5cm 0;
            color: #333;
        }
        
        .bill-to p {
            margin: 0.2cm 0;
        }
        
        .items-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 2cm;
        }
        
        .items-table th {
            background: #f5f5f5;
            padding: 0.5cm;
            text-align: left;
            border-bottom: 1px solid #ddd;
            font-weight: bold;
        }
        
        .items-table td {
            padding: 0.5cm;
            border-bottom: 1px solid #eee;
        }
        
        .items-table .description {
            width: 50%;
        }
        
        .items-table .quantity {
            width: 15%;
            text-align: center;
        }
        
        .items-table .rate {
            width: 15%;
            text-align: right;
        }
        
        .items-table .amount {
            width: 20%;
            text-align: right;
        }
        
        .totals {
            margin-left: auto;
            width: 300px;
        }
        
        .totals table {
            width: 100%;
            border-collapse: collapse;
        }
        
        .totals td {
            padding: 0.3cm;
            border-bottom: 1px solid #eee;
        }
        
        .totals .label {
            text-align: left;
        }
        
        .totals .amount {
            text-align: right;
            font-weight: bold;
        }
        
        .totals .total-row {
            border-top: 2px solid #333;
            font-size: 14pt;
            font-weight: bold;
        }
        
        .notes {
            margin-top: 2cm;
            padding: 1cm;
            background: #f9f9f9;
            border-radius: 5px;
        }
        
        .notes h3 {
            margin: 0 0 0.5cm 0;
            color: #333;
        }
        
        .footer {
            margin-top: 2cm;
            text-align: center;
            font-size: 10pt;
            color: #666;
            border-top: 1px solid #ddd;
            padding-top: 1cm;
        }
        """ 