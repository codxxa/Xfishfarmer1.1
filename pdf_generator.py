from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.units import inch
from datetime import datetime
import io
import os
from app import db
from models import Pond, Feed, Task, Mortality, Stock, FeedStock, Expense, Customer, Sale, Invoice, Company, Staff

def get_company_info():
    """Get company information for reports"""
    company = Company.query.first()
    if not company:
        return {
            "name": "XFishFarmer Inc.",
            "address": "123 Fish Lane, Ocean City",
            "phone": "555-FISH-999",
            "email": "info@xfishfarmer.com",
            "logo_path": None
        }
    return {
        "name": company.name,
        "address": company.address,
        "phone": company.phone,
        "email": company.email,
        "logo_path": company.logo_path
    }

def get_report_data(report_type, start_date, end_date):
    """Get data for reports based on report type and date range"""
    if report_type == 'pond_status':
        ponds = Pond.query.all()
        return {
            "title": "Pond Status Report",
            "data": ponds,
            "headers": ["Pond Name", "Type", "Size (m²)", "Depth (m)", "Water Capacity (m³)"]
        }
    
    elif report_type == 'feed_consumption':
        feeds = Feed.query.filter(Feed.feeding_date.between(start_date, end_date)).all()
        # Group by pond and feed type
        pond_feed_data = {}
        for feed in feeds:
            pond_name = feed.pond.name
            if pond_name not in pond_feed_data:
                pond_feed_data[pond_name] = {}
            
            if feed.feed_stock.name not in pond_feed_data[pond_name]:
                pond_feed_data[pond_name][feed.feed_stock.name] = 0
            
            pond_feed_data[pond_name][feed.feed_stock.name] += feed.amount
        

        # Convert to list format for table
        table_data = []
        for pond_name, feed_types in pond_feed_data.items():
            for feed_type, amount in feed_types.items():
                table_data.append([pond_name, feed_type, f"{amount:.2f}"])
        
        return {
            "title": "Feed Consumption Report",
            "data": table_data,
            "headers": ["Pond", "Feed Type", "Amount (kg)"]
        }
    
    elif report_type == 'mortality':
        mortalities = Mortality.query.filter(Mortality.date.between(start_date, end_date)).all()
        table_data = []
        for mort in mortalities:
            table_data.append([
                mort.pond.name,
                mort.species,
                str(mort.quantity),
                mort.cause,
                mort.date.strftime('%Y-%m-%d')
            ])
        
        return {
            "title": "Mortality Report",
            "data": table_data,
            "headers": ["Pond", "Species", "Quantity", "Cause", "Date"]
        }
    
    elif report_type == 'stock':
        stocks = Stock.query.filter(Stock.stocking_date.between(start_date, end_date)).all()
        table_data = []
        for stock in stocks:
            table_data.append([
                stock.pond.name,
                stock.species,
                str(stock.quantity),
                f"{stock.size:.2f}",
                stock.stocking_date.strftime('%Y-%m-%d')
            ])
        
        return {
            "title": "Stock Inventory Report",
            "data": table_data,
            "headers": ["Pond", "Species", "Quantity", "Size (cm)", "Stocking Date"]
        }
    
    elif report_type == 'expenses':
        expenses = Expense.query.filter(Expense.date.between(start_date, end_date)).all()
        table_data = []
        for expense in expenses:
            table_data.append([
                expense.description,
                expense.category,
                f"{expense.amount:.2f}",
                expense.date.strftime('%Y-%m-%d')
            ])
        
        # Calculate total expenses
        total_expense = sum(expense.amount for expense in expenses)
        
        return {
            "title": "Expense Report",
            "data": table_data,
            "headers": ["Description", "Category", "Amount", "Date"],
            "total": total_expense
        }
    
    elif report_type == 'sales':
        sales = Sale.query.filter(Sale.sale_date.between(start_date, end_date)).all()
        table_data = []
        for sale in sales:
            table_data.append([
                sale.customer.name,
                sale.species,
                str(sale.quantity),
                f"{sale.weight:.2f}",
                f"{sale.price_per_kg:.2f}",
                f"{sale.total_amount:.2f}",
                sale.sale_date.strftime('%Y-%m-%d')
            ])
        
        # Calculate total sales
        total_sales = sum(sale.total_amount for sale in sales)
        
        return {
            "title": "Sales Report",
            "data": table_data,
            "headers": ["Customer", "Species", "Quantity", "Weight (kg)", "Price/kg", "Total Amount", "Date"],
            "total": total_sales
        }
    
    elif report_type == 'invoices':
        invoices = Invoice.query.filter(Invoice.issue_date.between(start_date, end_date)).all()
        table_data = []
        for invoice in invoices:
            table_data.append([
                invoice.invoice_number,
                invoice.customer.name,
                f"{invoice.amount:.2f}",
                f"{invoice.tax_amount:.2f}" if invoice.tax_amount else "0.00",
                f"{invoice.total_amount:.2f}",
                invoice.issue_date.strftime('%Y-%m-%d'),
                invoice.due_date.strftime('%Y-%m-%d'),
                "Yes" if invoice.paid else "No"
            ])
        
        # Calculate total invoiced amount
        total_invoiced = sum(invoice.total_amount for invoice in invoices)
        # Calculate total paid amount
        total_paid = sum(invoice.total_amount for invoice in invoices if invoice.paid)
        
        return {
            "title": "Invoice Report",
            "data": table_data,
            "headers": ["Invoice #", "Customer", "Amount", "Tax", "Total", "Issue Date", "Due Date", "Paid"],
            "total": total_invoiced,
            "total_paid": total_paid
        }
    
    elif report_type == 'tasks':
        tasks = Task.query.filter(Task.due_date.between(start_date, end_date)).all()
        table_data = []
        for task in tasks:
            table_data.append([
                task.pond.name,
                task.description,
                task.task_type,
                task.due_date.strftime('%Y-%m-%d'),
                "Yes" if task.completed else "No",
                task.completed_date.strftime('%Y-%m-%d') if task.completed_date else "-"
            ])
        
        return {
            "title": "Task Report",
            "data": table_data,
            "headers": ["Pond", "Description", "Type", "Due Date", "Completed", "Completion Date"]
        }
    
    elif report_type == 'staff':
        staff_members = Staff.query.filter(Staff.hire_date.between(start_date, end_date)).all()
        table_data = []
        for staff in staff_members:
            table_data.append([
                staff.name,
                staff.position,
                staff.phone,
                staff.email,
                staff.hire_date.strftime('%Y-%m-%d'),
                staff.status
            ])
        
        return {
            "title": "Staff Report",
            "data": table_data,
            "headers": ["Name", "Position", "Phone", "Email", "Hire Date", "Status"]
        }
    
    # Default case for invalid report types
    return {
        "title": "Invalid Report Type",
        "data": [],
        "headers": [],
        "message": "The selected report type is not valid."
    }

    

def generate_report_pdf(report_type, start_date, end_date):
    """Generate PDF report based on report type and date range"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    
    # Get company info
    company_info = get_company_info()
    
    # Add company logo if available
    if company_info["logo_path"] and os.path.exists(f"static/{company_info['logo_path']}"):
        logo = Image(f"static/{company_info['logo_path']}")
        logo.drawHeight = 0.5 * inch
        logo.drawWidth = 1.5 * inch
        elements.append(logo)
    
    # Add company header
    elements.append(Paragraph(company_info["name"], styles["Heading1"]))
    elements.append(Paragraph(company_info["address"], styles["Normal"]))
    elements.append(Paragraph(f"Phone: {company_info['phone']}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {company_info['email']}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Get report data
    report_data = get_report_data(report_type, start_date, end_date)
    
    if report_data is None:
        # Handle the case where report_data is None
        elements.append(Paragraph("Invalid report type or no data available.", styles["Heading2"]))
    else:
        # Add report title
        elements.append(Paragraph(report_data["title"], styles["Heading2"]))
        elements.append(Paragraph(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}", styles["Normal"]))
        elements.append(Spacer(1, 0.25 * inch))
        
        # Add report table if data is available
        if report_data["data"]:
            if report_type == 'pond_status':
                # Special handling for pond status
                data = [report_data["headers"]]
                for pond in report_data["data"]:
                    data.append([
                        pond.name,
                        pond.pond_type,
                        f"{pond.size:.2f}" if pond.size is not None else "N/A",
                        f"{pond.depth:.2f}" if pond.depth is not None else "N/A",
                        f"{pond.water_capacity:.2f}" if pond.water_capacity is not None else "N/A"
                    ])
            else:
                # For other reports, data is already in table format
                data = [report_data["headers"]] + report_data["data"]
            
            table = Table(data, repeatRows=1)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
                ('TOPPADDING', (0, 1), (-1, -1), 6),
            ]))
            elements.append(table)
            
            # Add total if available
            if "total" in report_data:
                elements.append(Spacer(1, 0.25 * inch))
                elements.append(Paragraph(f"Total: ${report_data['total']:.2f}", styles["Heading3"]))
                
                if "total_paid" in report_data:
                    elements.append(Paragraph(f"Total Paid: ${report_data['total_paid']:.2f}", styles["Heading3"]))
                    elements.append(Paragraph(f"Outstanding: ${(report_data['total'] - report_data['total_paid']):.2f}", styles["Heading3"]))
        else:
            # No data available
            elements.append(Paragraph("No data available for the selected period.", styles["Normal"]))
    
    # Add footer with date and time
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Italic"]))
    
    # Build and return the PDF
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def generate_invoice_pdf(invoice, customer, company):
    """Generate PDF invoice"""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Add custom styles
    styles.add(ParagraphStyle(
        name='RightAlign',
        parent=styles['Normal'],
        alignment=2  # right alignment
    ))
    
    elements = []
    
    # Add company logo if available
    if company.logo_path and os.path.exists(f"static/{company.logo_path}"):
        logo = Image(f"static/{company.logo_path}")
        logo.drawHeight = 0.5 * inch
        logo.drawWidth = 1.5 * inch
        elements.append(logo)
    
    # Add company header
    elements.append(Paragraph(company.name, styles["Heading1"]))
    elements.append(Paragraph(company.address, styles["Normal"]))
    elements.append(Paragraph(f"Phone: {company.phone}", styles["Normal"]))
    elements.append(Paragraph(f"Email: {company.email}", styles["Normal"]))
    if company.tax_id:
        elements.append(Paragraph(f"Tax ID: {company.tax_id}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))
    
    # Add invoice title and number
    elements.append(Paragraph(f"INVOICE #{invoice.invoice_number}", styles["Heading2"]))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Add date information
    date_data = [
        ["Issue Date:", invoice.issue_date.strftime('%Y-%m-%d')],
        ["Due Date:", invoice.due_date.strftime('%Y-%m-%d')]
    ]
    date_table = Table(date_data)
    date_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(date_table)
    elements.append(Spacer(1, 0.25 * inch))
    
    # Add customer information
    elements.append(Paragraph("Bill To:", styles["Heading3"]))
    elements.append(Paragraph(customer.name, styles["Normal"]))
    if customer.contact_person:
        elements.append(Paragraph(f"Attn: {customer.contact_person}", styles["Normal"]))
    if customer.address:
        elements.append(Paragraph(customer.address, styles["Normal"]))
    if customer.phone:
        elements.append(Paragraph(f"Phone: {customer.phone}", styles["Normal"]))
    if customer.email:
        elements.append(Paragraph(f"Email: {customer.email}", styles["Normal"]))
    elements.append(Spacer(1, 0.25 * inch))
    
    # Get sales related to this invoice
    # For this example, we'll create a sample invoice item
    invoice_items = [
        ["Item", "Description", "Quantity", "Unit Price", "Total"]
    ]
    
    # Add a dummy item since we don't have the actual items linked to invoices
    invoice_items.append([
        "1",
        "Fish Sale",
        "1",
        f"${invoice.amount:.2f}",
        f"${invoice.amount:.2f}"
    ])
    
    # Create invoice items table
    items_table = Table(invoice_items, repeatRows=1)
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.25 * inch))
    
    # Add totals
    totals_data = [
        ["Subtotal:", f"${invoice.amount:.2f}"],
        ["Tax:", f"${invoice.tax_amount:.2f}"],
        ["Total:", f"${invoice.total_amount:.2f}"]
    ]
    
    # Add paid/due amount
    if invoice.paid:
        totals_data.append(["Paid:", f"${invoice.total_amount:.2f}"])
        totals_data.append(["Balance Due:", "$0.00"])
    else:
        totals_data.append(["Paid:", "$0.00"])
        totals_data.append(["Balance Due:", f"${invoice.total_amount:.2f}"])
    
    totals_table = Table(totals_data)
    totals_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTNAME', (0, -1), (1, -1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('LINEABOVE', (0, -1), (1, -1), 1, colors.black),
    ]))
    elements.append(totals_table)
    
    # Add payment information
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Payment Information:", styles["Heading3"]))
    if company.bank_account:
        elements.append(Paragraph(f"Bank Account: {company.bank_account}", styles["Normal"]))
    elements.append(Paragraph("Please include the invoice number with your payment.", styles["Normal"]))
    
    # Add notes if available
    if invoice.notes:
        elements.append(Spacer(1, 0.25 * inch))
        elements.append(Paragraph("Notes:", styles["Heading3"]))
        elements.append(Paragraph(invoice.notes, styles["Normal"]))
    
    # Add thank you note
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph("Thank you for your business!", styles["Heading3"]))
    
    # Add footer with date and time
    elements.append(Spacer(1, 0.5 * inch))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles["Italic"]))
    
    # Build and return the PDF
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data