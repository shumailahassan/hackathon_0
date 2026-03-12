"""
Odoo Accounting Agent Skill
This skill allows the AI Employee to interact with a self-hosted Odoo Community instance
using JSON-RPC for accounting tasks like creating invoices, tracking expenses, etc.
"""

import xmlrpc.client
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class OdooAccountingSkill:
    """
    Agent Skill for interacting with Odoo Community accounting system via JSON-RPC
    """

    def __init__(self, host: str = "localhost", port: int = 8069, database: str = "odoo_db",
                 username: str = "admin", password: str = "admin"):
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.url = f"http://{host}:{port}"

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Initialize connection
        self.uid = None
        self.models = None
        self.connect()

    def connect(self) -> bool:
        """Connect to the Odoo instance"""
        try:
            common = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/common')
            self.uid = common.authenticate(self.database, self.username, self.password, {})
            self.models = xmlrpc.client.ServerProxy(f'{self.url}/xmlrpc/2/object')

            if self.uid:
                self.logger.info(f"Successfully connected to Odoo at {self.url}")
                return True
            else:
                self.logger.error("Failed to authenticate with Odoo")
                return False
        except Exception as e:
            self.logger.error(f"Error connecting to Odoo: {e}")
            return False

    def create_invoice(self, partner_id: int, lines: List[Dict], reference: str = None,
                      date_invoice: str = None) -> Optional[int]:
        """
        Create an invoice in Odoo

        Args:
            partner_id: Customer ID in Odoo
            lines: List of invoice lines (product_id, quantity, price_unit)
            reference: Invoice reference
            date_invoice: Invoice date (YYYY-MM-DD)

        Returns:
            Invoice ID if successful, None otherwise
        """
        try:
            # Default invoice values
            vals = {
                'partner_id': partner_id,
                'move_type': 'out_invoice',  # Sales invoice
                'invoice_line_ids': []
            }

            if reference:
                vals['ref'] = reference

            if date_invoice:
                vals['invoice_date'] = date_invoice
            else:
                vals['invoice_date'] = datetime.now().strftime('%Y-%m-%d')

            # Add invoice lines
            for line in lines:
                line_vals = {
                    'product_id': line.get('product_id'),
                    'quantity': line.get('quantity', 1),
                    'price_unit': line.get('price_unit', 0.0),
                    'name': line.get('name', 'Service'),
                }
                vals['invoice_line_ids'].append((0, 0, line_vals))

            # Create the invoice
            invoice_id = self.models.execute_kw(
                self.database, self.uid, self.password,
                'account.move', 'create', [vals]
            )

            self.logger.info(f"Successfully created invoice with ID: {invoice_id}")
            return invoice_id

        except Exception as e:
            self.logger.error(f"Error creating invoice: {e}")
            return None

    def search_partner(self, domain: List) -> List[Dict]:
        """
        Search for partners/customers in Odoo

        Args:
            domain: Search domain (e.g., [['name', 'ilike', 'John']])

        Returns:
            List of partner records
        """
        try:
            partner_ids = self.models.execute_kw(
                self.database, self.uid, self.password,
                'res.partner', 'search', [domain]
            )

            if not partner_ids:
                return []

            partners = self.models.execute_kw(
                self.database, self.uid, self.password,
                'res.partner', 'read', [partner_ids, ['id', 'name', 'email', 'phone', 'street', 'city']]
            )

            return partners

        except Exception as e:
            self.logger.error(f"Error searching partners: {e}")
            return []

    def create_partner(self, name: str, email: str = None, phone: str = None,
                      street: str = None, city: str = None) -> Optional[int]:
        """
        Create a new partner/customer in Odoo

        Args:
            name: Partner name
            email: Email address
            phone: Phone number
            street: Street address
            city: City

        Returns:
            Partner ID if successful, None otherwise
        """
        try:
            vals = {'name': name}

            if email:
                vals['email'] = email
            if phone:
                vals['phone'] = phone
            if street:
                vals['street'] = street
            if city:
                vals['city'] = city

            partner_id = self.models.execute_kw(
                self.database, self.uid, self.password,
                'res.partner', 'create', [vals]
            )

            self.logger.info(f"Successfully created partner with ID: {partner_id}")
            return partner_id

        except Exception as e:
            self.logger.error(f"Error creating partner: {e}")
            return None

    def get_product(self, product_id: int) -> Optional[Dict]:
        """
        Get product information from Odoo

        Args:
            product_id: Product ID

        Returns:
            Product record or None
        """
        try:
            products = self.models.execute_kw(
                self.database, self.uid, self.password,
                'product.product', 'read', [[product_id], ['id', 'name', 'list_price', 'categ_id']]
            )

            return products[0] if products else None

        except Exception as e:
            self.logger.error(f"Error getting product: {e}")
            return None

    def search_products(self, domain: List) -> List[Dict]:
        """
        Search for products in Odoo

        Args:
            domain: Search domain (e.g., [['name', 'ilike', 'Product']])

        Returns:
            List of product records
        """
        try:
            product_ids = self.models.execute_kw(
                self.database, self.uid, self.password,
                'product.product', 'search', [domain]
            )

            if not product_ids:
                return []

            products = self.models.execute_kw(
                self.database, self.uid, self.password,
                'product.product', 'read', [product_ids, ['id', 'name', 'list_price', 'categ_id']]
            )

            return products

        except Exception as e:
            self.logger.error(f"Error searching products: {e}")
            return []

    def create_expense(self, employee_id: int, product_id: int, amount: float,
                      description: str, date: str = None) -> Optional[int]:
        """
        Create an expense record in Odoo

        Args:
            employee_id: Employee ID
            product_id: Product/expense category ID
            amount: Expense amount
            description: Expense description
            date: Expense date (YYYY-MM-DD)

        Returns:
            Expense ID if successful, None otherwise
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')

            vals = {
                'employee_id': employee_id,
                'product_id': product_id,
                'total_amount': amount,
                'name': description,
                'date': date
            }

            expense_id = self.models.execute_kw(
                self.database, self.uid, self.password,
                'hr.expense', 'create', [vals]
            )

            self.logger.info(f"Successfully created expense with ID: {expense_id}")
            return expense_id

        except Exception as e:
            self.logger.error(f"Error creating expense: {e}")
            return None

    def get_account_balance(self, account_id: int) -> float:
        """
        Get account balance in Odoo

        Args:
            account_id: Account ID

        Returns:
            Account balance
        """
        try:
            accounts = self.models.execute_kw(
                self.database, self.uid, self.password,
                'account.account', 'read', [[account_id], ['balance']]
            )

            if accounts:
                return accounts[0]['balance']
            return 0.0

        except Exception as e:
            self.logger.error(f"Error getting account balance: {e}")
            return 0.0


# Agent Skill Functions
def create_invoice_in_odoo(partner_id: int, lines: List[Dict], reference: str = None,
                          date_invoice: str = None) -> Dict:
    """
    Agent Skill function to create an invoice in Odoo

    Args:
        partner_id: Customer ID in Odoo
        lines: List of invoice lines with product_id, quantity, price_unit
        reference: Invoice reference
        date_invoice: Invoice date (YYYY-MM-DD)

    Returns:
        dict: Result of the operation
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        invoice_id = skill.create_invoice(partner_id, lines, reference, date_invoice)

        if invoice_id:
            return {
                "success": True,
                "invoice_id": invoice_id,
                "message": f"Invoice created successfully with ID: {invoice_id}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create invoice"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_odoo_partners(name_query: str) -> Dict:
    """
    Agent Skill function to search for partners in Odoo

    Args:
        name_query: Name to search for (partial match)

    Returns:
        dict: List of matching partners
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        domain = [['name', 'ilike', name_query]]
        partners = skill.search_partner(domain)

        return {
            "success": True,
            "partners": partners,
            "count": len(partners)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_odoo_partner(name: str, email: str = None, phone: str = None,
                       street: str = None, city: str = None) -> Dict:
    """
    Agent Skill function to create a new partner in Odoo

    Args:
        name: Partner name
        email: Email address
        phone: Phone number
        street: Street address
        city: City

    Returns:
        dict: Result of the operation
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        partner_id = skill.create_partner(name, email, phone, street, city)

        if partner_id:
            return {
                "success": True,
                "partner_id": partner_id,
                "message": f"Partner created successfully with ID: {partner_id}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create partner"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def search_odoo_products(name_query: str) -> Dict:
    """
    Agent Skill function to search for products in Odoo

    Args:
        name_query: Product name to search for (partial match)

    Returns:
        dict: List of matching products
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        domain = [['name', 'ilike', name_query]]
        products = skill.search_products(domain)

        return {
            "success": True,
            "products": products,
            "count": len(products)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def create_expense_in_odoo(employee_id: int, product_id: int, amount: float,
                          description: str, date: str = None) -> Dict:
    """
    Agent Skill function to create an expense in Odoo

    Args:
        employee_id: Employee ID
        product_id: Product/expense category ID
        amount: Expense amount
        description: Expense description
        date: Expense date (YYYY-MM-DD)

    Returns:
        dict: Result of the operation
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        expense_id = skill.create_expense(employee_id, product_id, amount, description, date)

        if expense_id:
            return {
                "success": True,
                "expense_id": expense_id,
                "message": f"Expense created successfully with ID: {expense_id}"
            }
        else:
            return {
                "success": False,
                "error": "Failed to create expense"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def get_odoo_account_balance(account_id: int) -> Dict:
    """
    Agent Skill function to get account balance in Odoo

    Args:
        account_id: Account ID

    Returns:
        dict: Account balance information
    """
    try:
        skill = OdooAccountingSkill()
        if not skill.connect():
            return {"success": False, "error": "Could not connect to Odoo"}

        balance = skill.get_account_balance(account_id)

        return {
            "success": True,
            "account_id": account_id,
            "balance": balance
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# Example usage
if __name__ == "__main__":
    # Example usage of the Odoo Accounting Skill
    print("Testing Odoo Accounting Skill...")

    # Create a partner
    partner_result = create_odoo_partner(
        name="Test Customer",
        email="test@example.com",
        phone="123-456-7890",
        street="123 Main St",
        city="Anytown"
    )
    print("Create Partner Result:", partner_result)

    # Search for partners
    search_result = search_odoo_partners("Test")
    print("Search Partners Result:", search_result)