from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, FloatField, TextAreaField, SelectField, DateField, BooleanField, IntegerField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, NumberRange
from datetime import datetime, timedelta, date

from wtforms import StringField, FloatField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from models import PondStatus


class PondForm(FlaskForm):
    name = StringField('Pond Name', validators=[DataRequired()])
    size = FloatField('Size (m²)', validators=[DataRequired()])
    water_capacity = FloatField('Water Capacity (liters)', validators=[DataRequired()])
    fish_count = IntegerField('Fish Count', validators=[DataRequired(), NumberRange(min=0)])
    fish_type = SelectField('Fish Type', choices=[
        ('Tilapia', 'Tilapia'),
        ('Catfish', 'Catfish'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    pond_type = SelectField('Pond Type', choices=[
        ('Concrete', 'Concrete'),
        ('Liner', 'Liner'),
        ('Earthen', 'Earthen'),
        ('Other', 'Other')
    ], validators=[DataRequired()])
    status = SelectField('Status', choices=[(status.value, status.value) for status in PondStatus], default=PondStatus.ACTIVE.value)
    location = StringField('Location (Optional)')
    notes = TextAreaField('Notes (Optional)')
    submit = SubmitField('Create Pond')

class FeedForm(FlaskForm):
    pond_id = SelectField('Pond', coerce=int, validators=[DataRequired()])
    feed_stock_id = SelectField('Feed Type', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount (kg)', validators=[DataRequired(), NumberRange(min=0.001)])
    feeding_date = DateField('Feeding Date', default=date.today)
    unit = SelectField('Unit', choices=[('kg', 'Kilograms (kg)'), ('g', 'Grams (g)')], default='kg')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Feeding')

class TaskForm(FlaskForm):
    pond_id = SelectField('Pond', coerce=int, validators=[DataRequired()])
    staff_id = SelectField('Assign To Staff', coerce=int, validators=[DataRequired()])
    description = StringField('Task Description', validators=[DataRequired()])
    task_type = SelectField('Task Type', choices=[
        ('water_change', 'Water Change'),
        ('cleaning', 'Cleaning'),
        ('maintenance', 'Maintenance'),
        ('medication', 'Medication'),
        ('testing', 'Water Testing'),
        ('harvest', 'Harvesting'),
        ('other', 'Other')
    ])
    priority = SelectField('Priority', choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical')
    ], default='medium')
    due_date = DateField('Due Date', default=date.today() + timedelta(days=1), format='%Y-%m-%d')
    completed = BooleanField('Completed')
    completed_date = DateField('Completion Date', format='%Y-%m-%d', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Task')

class MortalityForm(FlaskForm):
    pond_id = SelectField('Pond', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    species = StringField('Species', validators=[DataRequired()])
    cause = SelectField('Cause', choices=[
        ('disease', 'Disease'),
        ('water_quality', 'Water Quality'),
        ('predation', 'Predation'),
        ('handling', 'Handling Stress'),
        ('unknown', 'Unknown'),
        ('other', 'Other')
    ])
    date = DateField('Date', default=date.today, format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Mortality')

class StockForm(FlaskForm):
    pond_id = SelectField('Pond', coerce=int, validators=[DataRequired()])
    species = StringField('Species', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    size = FloatField('Size (cm)', validators=[DataRequired(), NumberRange(min=0.1)])
    source = StringField('Source', validators=[Optional()])
    stocking_date = DateField('Stocking Date', default=date.today, format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Stock')

class FeedStockForm(FlaskForm):
    name = StringField('Feed Name', validators=[DataRequired()])
    quantity = FloatField('Quantity (kg)', validators=[DataRequired(), NumberRange(min=0.1)])
    supplier = StringField('Supplier', validators=[Optional()])
    purchase_date = DateField('Purchase Date', default=date.today, format='%Y-%m-%d')
    expiry_date = DateField('Expiry Date', format='%Y-%m-%d', validators=[Optional()])
    cost = FloatField('Cost', validators=[DataRequired(), NumberRange(min=0.01)])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Feed Stock')

class ExpenseForm(FlaskForm):
    description = StringField('Description', validators=[DataRequired()])
    category = SelectField('Category', choices=[
        ('feed', 'Feed'),
        ('equipment', 'Equipment'),
        ('salaries', 'Salaries'),
        ('utilities', 'Utilities'),
        ('maintenance', 'Maintenance'),
        ('medicine', 'Medicine'),
        ('other', 'Other')
    ])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    date = DateField('Date', default=date.today, format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Expense')

class CustomerForm(FlaskForm):
    name = StringField('Customer Name', validators=[DataRequired()])
    contact_person = StringField('Contact Person', validators=[Optional()])
    address = StringField('Address', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Customer')

class SaleForm(FlaskForm):
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    species = StringField('Species', validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1)])
    weight = FloatField('Weight (kg)', validators=[DataRequired(), NumberRange(min=0.1)])
    price_per_kg = FloatField('Price per kg', validators=[DataRequired(), NumberRange(min=0.01)])
    sale_date = DateField('Sale Date', default=date.today, format='%Y-%m-%d')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Record Sale')

class InvoiceForm(FlaskForm):
    invoice_number = StringField('Invoice Number', validators=[DataRequired()])
    customer_id = SelectField('Customer', coerce=int, validators=[DataRequired()])
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    tax_amount = FloatField('Tax Amount', validators=[Optional(), NumberRange(min=0)])
    issue_date = DateField('Issue Date', default=date.today, format='%Y-%m-%d')
    due_date = DateField('Due Date', default=date.today() + timedelta(days=30), format='%Y-%m-%d')
    paid = BooleanField('Paid')
    payment_date = DateField('Payment Date', format='%Y-%m-%d', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Generate Invoice')

class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired()])
    address = StringField('Address', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    website = StringField('Website', validators=[Optional()])
    logo = FileField('Company Logo', validators=[Optional(), FileAllowed(['jpg', 'png', 'gif', 'svg'], 'Images only!')])
    tax_id = StringField('Tax ID', validators=[Optional()])
    bank_account = StringField('Bank Account', validators=[Optional()])
    submit = SubmitField('Save Company Details')

class ReportForm(FlaskForm):
    report_type = SelectField('Report Type', choices=[
        ('pond_status', 'Pond Status'),
        ('feed_consumption', 'Feed Consumption'),
        ('mortality', 'Mortality'),
        ('stock', 'Stock Inventory'),
        ('expenses', 'Expenses'),
        ('sales', 'Sales'),
        ('invoices', 'Invoices'),
        ('tasks', 'Tasks'),
        ('staff', 'Staff')
    ])
    start_date = DateField('Start Date', default=date.today() - timedelta(days=30), format='%Y-%m-%d')
    end_date = DateField('End Date', default=date.today(), format='%Y-%m-%d')
    submit = SubmitField('Generate Report')
    
class StaffForm(FlaskForm):
    name = StringField('Staff Name', validators=[DataRequired()])
    position = StringField('Position', validators=[Optional()])
    phone = StringField('Phone', validators=[Optional()])
    email = StringField('Email', validators=[Optional(), Email()])
    address = StringField('Address', validators=[Optional()])
    hire_date = DateField('Hire Date', default=date.today, format='%Y-%m-%d')
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave')
    ], default='active')
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Save Staff')
