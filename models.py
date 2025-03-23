from datetime import datetime, date
from app import db
from enum import Enum
from sqlalchemy import Enum as SQLAlchemyEnum


class PondStatus(Enum):
    ACTIVE = "ACTIVE"
    MAINTENANCE = "MAINTENANCE"
    INACTIVE = "INACTIVE"
    OTHER = "OTHER"

class Pond(db.Model):
    __tablename__ = 'ponds'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    size = db.Column(db.Float, nullable=False)
    water_capacity = db.Column(db.Float, nullable=False)
    fish_count = db.Column(db.Integer, nullable=True)  # New field
    fish_type = db.Column(db.String(50), nullable=False)  # New field for fish type
    pond_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200))
    mortalities = db.relationship('Mortality', backref='pond    ', lazy=True, cascade="all, delete-orphan")
    
    notes = db.Column(db.Text)
    status = db.Column(SQLAlchemyEnum(PondStatus), default=PondStatus.ACTIVE, nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    

class Feed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False)
    feed_stock_id = db.Column(db.Integer, db.ForeignKey('feed_stock.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in kg or g
    unit = db.Column(db.String(5), nullable=False, default='kg')  # kg or g
    feeding_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    pond = db.relationship('Pond', backref='feeds', lazy=True)
    feed_stock = db.relationship('FeedStock', backref='feedings', lazy=True)

    def __repr__(self):
        return f"Feed('{self.feed_stock.name if self.feed_stock else 'Unknown'}', {self.amount}{self.unit}, {self.feeding_date})"

class Staff(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    hire_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(20), default='active')  # active, inactive, on leave
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tasks = db.relationship('Task', backref='assigned_to', lazy=True)
    
    def __repr__(self):
        return f"Staff('{self.name}', '{self.position}')"

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    task_type = db.Column(db.String(50), nullable=False)  # e.g., water change, cleaning, medication
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    completed = db.Column(db.Boolean, default=False)
    completed_date = db.Column(db.Date, nullable=True)
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship to the Pond model
    pond = db.relationship('Pond', backref='tasks', lazy=True)

    def __repr__(self):
        return f"Task('{self.description}', '{self.task_type}', {self.due_date})"

class Mortality(db.Model):

    
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False)  # Foreign key to Pond
    quantity = db.Column(db.Integer, nullable=False)
    species = db.Column(db.String(100), nullable=False)
    cause = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Mortality({self.quantity} {self.species}, '{self.cause}')"
    
class Stock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pond_id = db.Column(db.Integer, db.ForeignKey('ponds.id'), nullable=False)
    species = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    size = db.Column(db.Float, nullable=False)  # Size in cm
    source = db.Column(db.String(100), nullable=True)
    stocking_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Define the relationship to the Pond model
    pond = db.relationship('Pond', backref='stocks', lazy=True)

    def __repr__(self):
        return f"Stock({self.quantity} {self.species}, {self.size}cm)"

class FeedStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Float, nullable=False)  # Quantity in kg
    supplier = db.Column(db.String(100), nullable=True)
    purchase_date = db.Column(db.Date, nullable=False, default=date.today)
    expiry_date = db.Column(db.Date, nullable=True)
    cost = db.Column(db.Float, nullable=False)  # Cost in currency
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"FeedStock('{self.name}', {self.quantity}kg)"

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # e.g., feed, equipment, salaries
    amount = db.Column(db.Float, nullable=False)  # Amount in currency
    date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Expense('{self.description}', {self.amount})"

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    contact_person = db.Column(db.String(100), nullable=True)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    sales = db.relationship('Sale', backref='customer', lazy=True)
    invoices = db.relationship('Invoice', backref='customer', lazy=True)

    def __repr__(self):
        return f"Customer('{self.name}')"

class Sale(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    species = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=False)  # Weight in kg
    price_per_kg = db.Column(db.Float, nullable=False)  # Price per kg
    total_amount = db.Column(db.Float, nullable=False)  # Total amount in currency
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Sale({self.quantity} {self.species}, {self.weight}kg, {self.total_amount})"

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), nullable=False, unique=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)  # Amount in currency
    tax_amount = db.Column(db.Float, nullable=True)  # Tax amount in currency
    total_amount = db.Column(db.Float, nullable=False)  # Total amount in currency
    issue_date = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    paid = db.Column(db.Boolean, default=False)
    payment_date = db.Column(db.Date, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Invoice('{self.invoice_number}', {self.total_amount})"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    website = db.Column(db.String(100), nullable=True)
    logo_path = db.Column(db.String(255), nullable=True)
    tax_id = db.Column(db.String(50), nullable=True)
    bank_account = db.Column(db.String(50), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    date_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"Company('{self.name}')"
