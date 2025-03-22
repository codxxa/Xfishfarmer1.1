from flask import render_template, redirect, url_for, flash, request, send_file, abort
from datetime import datetime, timedelta, date
from werkzeug.utils import secure_filename
import os
import io

from app import app, db
from models import Pond, Feed, Task, Mortality, Stock, FeedStock, Expense, Customer, Sale, Invoice, Company, Staff
from forms import (PondForm, FeedForm, TaskForm, MortalityForm, StockForm, FeedStockForm, 
                  ExpenseForm, CustomerForm, SaleForm, InvoiceForm, CompanyForm, ReportForm, StaffForm)
from pdf_generator import generate_report_pdf, generate_invoice_pdf

# Helper Functions
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def save_logo(form_logo):
    if form_logo and form_logo.data and allowed_file(form_logo.data.filename):
        filename = secure_filename(form_logo.data.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        form_logo.data.save(file_path)
        return os.path.join('uploads', filename)
    return None

# Dashboard & Home Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get summary counts for dashboard
    pond_count = Pond.query.count()
    task_count = Task.query.filter_by(completed=False).count()
    mortality_count = Mortality.query.filter(Mortality.date >= date.today() - timedelta(days=30)).count()
    expense_sum = db.session.query(db.func.sum(Expense.amount)).filter(
        Expense.date >= date.today() - timedelta(days=30)).scalar() or 0
    sales_sum = db.session.query(db.func.sum(Sale.total_amount)).filter(
        Sale.sale_date >= date.today() - timedelta(days=30)).scalar() or 0
    
    # Get recent activities
    recent_tasks = Task.query.order_by(Task.due_date.desc()).limit(5).all()
    recent_feedings = Feed.query.order_by(Feed.feeding_date.desc()).limit(5).all()
    recent_mortalities = Mortality.query.order_by(Mortality.date.desc()).limit(5).all()
    
    # Get data for charts
    feed_by_pond = [(str(row[0]), float(row[1])) for row in db.session.query(
        Pond.name, db.func.sum(Feed.amount)
    ).join(Feed).group_by(Pond.id).order_by(db.func.sum(Feed.amount).desc()).limit(5).all()]
    
    mortality_by_cause = [(str(row[0]), int(row[1])) for row in db.session.query(
        Mortality.cause, db.func.sum(Mortality.quantity)
    ).group_by(Mortality.cause).order_by(db.func.sum(Mortality.quantity).desc()).all()]
    
    return render_template('dashboard.html',
                           pond_count=pond_count,
                           task_count=task_count,
                           mortality_count=mortality_count,
                           expense_sum=expense_sum,
                           sales_sum=sales_sum,
                           recent_tasks=recent_tasks,
                           recent_feedings=recent_feedings,
                           recent_mortalities=recent_mortalities,
                           feed_by_pond=feed_by_pond,
                           mortality_by_cause=mortality_by_cause,
                           now=lambda: date.now())
                           
                           
                       
# Pond Management Routes
@app.route('/ponds')
def ponds():
    ponds = Pond.query.all()
    return render_template('ponds/index.html', ponds=ponds)

@app.route('/ponds/create', methods=['GET', 'POST'])
def create_pond():
    form = PondForm()
    if form.validate_on_submit():
        pond = Pond(
            name=form.name.data,
            size=form.size.data,
            water_capacity=form.water_capacity.data,
            pond_type=form.pond_type.data,
            location=form.location.data,
            notes=form.notes.data
        )
        db.session.add(pond)
        db.session.commit()
        flash('Pond created successfully!', 'success')
        return redirect(url_for('ponds'))
    return render_template('ponds/create.html', form=form, title='Create Pond')

@app.route('/ponds/<int:pond_id>/edit', methods=['GET', 'POST'])
def edit_pond(pond_id):
    pond = Pond.query.get_or_404(pond_id)
    form = PondForm(obj=pond)
    if form.validate_on_submit():
        pond.name = form.name.data
        pond.size = form.size.data
        pond.water_capacity = form.water_capacity.data
        pond.pond_type = form.pond_type.data
        pond.location = form.location.data
        pond.notes = form.notes.data
        db.session.commit()
        flash('Pond updated successfully!', 'success')
        return redirect(url_for('ponds'))
    return render_template('ponds/edit.html', form=form, pond=pond, title='Edit Pond')

@app.route('/ponds/<int:pond_id>')
def view_pond(pond_id):
    pond = Pond.query.get_or_404(pond_id)
    # Get related data
    feeds = Feed.query.filter_by(pond_id=pond_id).order_by(Feed.feeding_date.desc()).limit(10).all()
    tasks = Task.query.filter_by(pond_id=pond_id).order_by(Task.due_date.desc()).limit(10).all()
    mortalities = Mortality.query.filter_by(pond_id=pond_id).order_by(Mortality.date.desc()).limit(10).all()
    stocks = Stock.query.filter_by(pond_id=pond_id).order_by(Stock.stocking_date.desc()).all()
    
    return render_template('ponds/view.html', 
                          pond=pond, 
                          feeds=feeds, 
                          tasks=tasks, 
                          mortalities=mortalities, 
                          stocks=stocks)

@app.route('/ponds/<int:pond_id>/delete', methods=['POST'])
def delete_pond(pond_id):
    pond = Pond.query.get_or_404(pond_id)
    db.session.delete(pond)
    db.session.commit()
    flash('Pond deleted successfully!', 'success')
    return redirect(url_for('ponds'))

# Feed Management Routes
@app.route('/feed')
def feed():
    feeds = Feed.query.order_by(Feed.feeding_date.desc()).all()
    return render_template('feed/index.html', feeds=feeds)

@app.route('/feed/create', methods=['GET', 'POST'])
def create_feed():
    form = FeedForm()
    form.pond_id.choices = [(p.id, p.name) for p in Pond.query.all()]
    form.feed_stock_id.choices = [(fs.id, fs.name) for fs in FeedStock.query.all()]
    
    if form.validate_on_submit():
        # Get the feed stock
        feed_stock = FeedStock.query.get_or_404(form.feed_stock_id.data)
        
        # Calculate amount in kg
        amount_in_kg = form.amount.data
        if form.unit.data == 'g':
            amount_in_kg = form.amount.data / 1000  # Convert grams to kg
        
        # Check if enough feed stock is available
        if feed_stock.quantity < amount_in_kg:
            flash(f'Not enough feed stock available. Current stock: {feed_stock.quantity}kg', 'danger')
            return render_template('feed/create.html', form=form, title='Record Feeding')
        
        # Create the feed record
        feed = Feed(
            pond_id=form.pond_id.data,
            feed_stock_id=form.feed_stock_id.data,
            amount=form.amount.data,
            unit=form.unit.data,
            feeding_date=form.feeding_date.data,
            notes=form.notes.data
        )
        
        # Reduce the feed stock quantity
        feed_stock.quantity -= amount_in_kg
        
        # Save changes
        db.session.add(feed)
        db.session.commit()
        
        flash('Feed record created successfully!', 'success')
        return redirect(url_for('feed'))
        
    return render_template('feed/create.html', form=form, title='Record Feeding')

# Task Management Routes
@app.route('/tasks')
def tasks():
    tasks = Task.query.order_by(Task.due_date).all()
    return render_template('tasks/index.html', tasks=tasks)

@app.route('/tasks/create', methods=['GET', 'POST'])
def create_task():
    form = TaskForm()
    form.pond_id.choices = [(p.id, p.name) for p in Pond.query.all()]
    form.staff_id.choices = [(s.id, s.name) for s in Staff.query.all()]
    
    if form.validate_on_submit():
        task = Task(
            pond_id=form.pond_id.data,
            staff_id=form.staff_id.data,
            description=form.description.data,
            task_type=form.task_type.data,
            priority=form.priority.data,
            due_date=form.due_date.data,
            completed=form.completed.data,
            completed_date=form.completed_date.data if form.completed.data else None,
            notes=form.notes.data
        )
        db.session.add(task)
        db.session.commit()
        flash('Task created successfully!', 'success')
        return redirect(url_for('tasks'))
    return render_template('tasks/create.html', form=form, title='Create Task')

@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
def complete_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.completed = True
    task.completed_date = date.today()
    db.session.commit()
    flash('Task marked as completed!', 'success')
    return redirect(url_for('tasks'))

# Mortality Management Routes
@app.route('/mortality')
def mortality():
    mortalities = Mortality.query.order_by(Mortality.date.desc()).all()
    return render_template('mortality/index.html', mortalities=mortalities)

@app.route('/mortality/create', methods=['GET', 'POST'])
def create_mortality():
    form = MortalityForm()
    form.pond_id.choices = [(p.id, p.name) for p in Pond.query.all()]
    if form.validate_on_submit():
        mortality = Mortality(
            pond_id=form.pond_id.data,
            quantity=form.quantity.data,
            species=form.species.data,
            cause=form.cause.data,
            date=form.date.data,
            notes=form.notes.data
        )
        db.session.add(mortality)
        db.session.commit()
        flash('Mortality record created successfully!', 'success')
        return redirect(url_for('mortality'))
    return render_template('mortality/create.html', form=form, title='Record Mortality')

# Stock Management Routes
@app.route('/stock')
def stock():
    stocks = Stock.query.order_by(Stock.stocking_date.desc()).all()
    feed_stocks = FeedStock.query.order_by(FeedStock.purchase_date.desc()).all()
    return render_template('stock/index.html', stocks=stocks, feed_stocks=feed_stocks)

@app.route('/stock/create', methods=['GET', 'POST'])
def create_stock():
    form = StockForm()
    form.pond_id.choices = [(p.id, p.name) for p in Pond.query.all()]
    if form.validate_on_submit():
        stock = Stock(
            pond_id=form.pond_id.data,
            species=form.species.data,
            quantity=form.quantity.data,
            size=form.size.data,
            source=form.source.data,
            stocking_date=form.stocking_date.data,
            notes=form.notes.data
        )
        db.session.add(stock)
        db.session.commit()
        flash('Stock record created successfully!', 'success')
        return redirect(url_for('stock'))
    return render_template('stock/create.html', form=form, title='Record Stock')

@app.route('/feedstock/create', methods=['GET', 'POST'])
def create_feed_stock():
    form = FeedStockForm()
    if form.validate_on_submit():
        feedstock = FeedStock(
            name=form.name.data,
            quantity=form.quantity.data,
            supplier=form.supplier.data,
            purchase_date=form.purchase_date.data,
            expiry_date=form.expiry_date.data,
            cost=form.cost.data,
            notes=form.notes.data
        )
        db.session.add(feedstock)
        db.session.commit()
        flash('Feed stock added successfully!', 'success')
        return redirect(url_for('stock'))
    return render_template('stock/create.html', form=form, title='Add Feed Stock', feed_stock=True)

# Financial Management Routes
@app.route('/finances/expenses', methods=['GET', 'POST'])
def expenses():
    form = ExpenseForm()
    if form.validate_on_submit():
        expense = Expense(
            description=form.description.data,
            category=form.category.data,
            amount=form.amount.data,
            date=form.date.data,
            notes=form.notes.data
        )
        db.session.add(expense)
        db.session.commit()
        flash('Expense recorded successfully!', 'success')
        return redirect(url_for('expenses'))
    
    expenses = Expense.query.order_by(Expense.date.desc()).all()
    return render_template('finances/expenses.html', expenses=expenses, form=form)

@app.route('/finances/sales', methods=['GET', 'POST'])
def sales():
    form = SaleForm()
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]
    
    if form.validate_on_submit():
        # Check if fish is in stock
        available_stock = Stock.query.filter_by(species=form.species.data).first()
        if not available_stock or available_stock.quantity < form.quantity.data:
            flash('Not enough stock available for this species!', 'danger')
            return redirect(url_for('sales'))
            
        # Calculate total amount
        total_amount = form.weight.data * form.price_per_kg.data
        
        sale = Sale(
            customer_id=form.customer_id.data,
            species=form.species.data,
            quantity=form.quantity.data,
            weight=form.weight.data,
            price_per_kg=form.price_per_kg.data,
            total_amount=total_amount,
            sale_date=form.sale_date.data,
            notes=form.notes.data
        )
        
        # Update stock
        available_stock.quantity -= form.quantity.data
        
        # Generate invoice
        invoice_number = f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
        invoice = Invoice(
            invoice_number=invoice_number,
            customer_id=form.customer_id.data,
            amount=total_amount,
            tax_amount=total_amount * 0.1,  # 10% tax
            total_amount=total_amount * 1.1,
            issue_date=date.today(),
            due_date=date.today() + timedelta(days=30),
            notes=f"Generated from sale of {form.quantity.data} {form.species.data}"
        )
        
        db.session.add(sale)
        db.session.add(invoice)
        db.session.commit()
        
        flash('Sale recorded and invoice generated successfully!', 'success')
        return redirect(url_for('sales'))
    
    sales = Sale.query.order_by(Sale.sale_date.desc()).all()
    return render_template('finances/sales.html', sales=sales, form=form)

@app.route('/finances/invoices', methods=['GET', 'POST'])
def invoices():
    form = InvoiceForm()
    form.customer_id.choices = [(c.id, c.name) for c in Customer.query.all()]
    
    if form.validate_on_submit():
        # Calculate total amount with tax
        total_amount = form.amount.data
        if form.tax_amount.data:
            total_amount += form.tax_amount.data
        
        invoice = Invoice(
            invoice_number=form.invoice_number.data,
            customer_id=form.customer_id.data,
            amount=form.amount.data,
            tax_amount=form.tax_amount.data if form.tax_amount.data else 0,
            total_amount=total_amount,
            issue_date=form.issue_date.data,
            due_date=form.due_date.data,
            paid=form.paid.data,
            payment_date=form.payment_date.data if form.paid.data else None,
            notes=form.notes.data
        )
        db.session.add(invoice)
        db.session.commit()
        flash('Invoice generated successfully!', 'success')
        return redirect(url_for('invoices'))
    
    invoices = Invoice.query.order_by(Invoice.issue_date.desc()).all()
    return render_template('finances/invoices.html', invoices=invoices, form=form)

@app.route('/customers', methods=['GET', 'POST'])
def customers():
    form = CustomerForm()
    
    if form.validate_on_submit():
        customer = Customer(
            name=form.name.data,
            contact_person=form.contact_person.data,
            address=form.address.data,
            phone=form.phone.data,
            email=form.email.data,
            notes=form.notes.data
        )
        db.session.add(customer)
        db.session.commit()
        flash('Customer added successfully!', 'success')
        return redirect(url_for('customers'))
    
    customers = Customer.query.all()
    return render_template('finances/customers.html', customers=customers, form=form)

# Company Settings Routes
@app.route('/company/settings', methods=['GET', 'POST'])
def company_settings():
    company = Company.query.first()
    if not company:
        company = Company(
            name="XFishFarmer Inc.",
            address="123 Fish Lane, Ocean City",
            phone="555-FISH-999",
            email="info@xfishfarmer.com"
        )
        db.session.add(company)
        db.session.commit()
    
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        form.populate_obj(company)
        
        # Handle logo upload
        logo_path = save_logo(form.logo)
        if logo_path:
            company.logo_path = logo_path
        
        db.session.commit()
        flash('Company settings updated successfully!', 'success')
        return redirect(url_for('company_settings'))
    
    return render_template('company/settings.html', form=form, company=company)

# Report Generation Routes
@app.route('/reports', methods=['GET', 'POST'])
def reports():
    form = ReportForm()
    
    if form.validate_on_submit():
        report_type = form.report_type.data
        start_date = form.start_date.data
        end_date = form.end_date.data
        
        # Generate PDF report
        pdf_data = generate_report_pdf(report_type, start_date, end_date)
        
        # Send PDF as downloadable file
        pdf_buffer = io.BytesIO(pdf_data)
        pdf_buffer.seek(0)
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f"{report_type}_report_{start_date.strftime('%Y%m%d')}.pdf",
            mimetype='application/pdf'
        )
    
    return render_template('reports/index.html', form=form)

@app.route('/invoices/<int:invoice_id>/pdf')
def invoice_pdf(invoice_id):
    invoice = Invoice.query.get_or_404(invoice_id)
    customer = Customer.query.get_or_404(invoice.customer_id)
    company = Company.query.first()
    
    pdf_data = generate_invoice_pdf(invoice, customer, company)
    
    pdf_buffer = io.BytesIO(pdf_data)
    pdf_buffer.seek(0)
    
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=f"invoice_{invoice.invoice_number}.pdf",
        mimetype='application/pdf'
    )

# Staff Management Routes
@app.route('/staff')
def staff():
    staff_members = Staff.query.all()
    return render_template('staff/index.html', staff_members=staff_members)

@app.route('/staff/create', methods=['GET', 'POST'])
def create_staff():
    form = StaffForm()
    if form.validate_on_submit():
        staff = Staff(
            name=form.name.data,
            position=form.position.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            hire_date=form.hire_date.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(staff)
        db.session.commit()
        flash('Staff member added successfully!', 'success')
        return redirect(url_for('staff'))
    return render_template('staff/create.html', form=form, title='Add Staff Member')

@app.route('/staff/<int:staff_id>/edit', methods=['GET', 'POST'])
def edit_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    form = StaffForm(obj=staff)
    if form.validate_on_submit():
        form.populate_obj(staff)
        db.session.commit()
        flash('Staff information updated successfully!', 'success')
        return redirect(url_for('staff'))
    return render_template('staff/edit.html', form=form, staff=staff, title='Edit Staff')

@app.route('/staff/<int:staff_id>')
def view_staff(staff_id):
    staff = Staff.query.get_or_404(staff_id)
    # Get assigned tasks
    tasks = Task.query.filter_by(staff_id=staff_id).order_by(Task.due_date).all()
    return render_template('staff/view.html', staff=staff, tasks=tasks)

# Error handling
@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_code=404, error_message="Page not found"), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('error.html', error_code=500, error_message="Internal server error"), 500
