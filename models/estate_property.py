from odoo import models, fields
from datetime import date, timedelta

class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char("Name", required=True)


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    # Basic fields
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        default=lambda self: date.today() + timedelta(days=90),
        copy=False
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float(
        "Selling Price",
        readonly=True,
        copy=False
    )
    bedrooms = fields.Integer("Bedrooms", default=2)
    living_area = fields.Integer("Living Area (sqm)")
    facades = fields.Integer("Facades")
    garage = fields.Boolean("Garage")
    garden = fields.Boolean("Garden")
    garden_area = fields.Integer("Garden Area (sqm)")
    garden_orientation = fields.Selection([
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West')
    ], string="Garden Orientation")
    active = fields.Boolean("Active", default=True)

    # Status
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], string="Status", required=True, copy=False, default='new')

    # Relationships
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesperson_id = fields.Many2one("res.users", string="Salesperson",
                                     default=lambda self: self.env.user)
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")  # <-- This is required

    # SQL constraints
    _sql_constraints = [
        (
            'check_expected_price',
            'CHECK(expected_price > 0)',
            'The expected price must be strictly positive.'
        ),
    ]
    offer_ids = fields.One2many(
    "estate.property.offer",
    "property_id",
    string="Offers"
)

