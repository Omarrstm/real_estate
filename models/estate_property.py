# -*- coding: utf-8 -*-
from odoo import fields, models
from datetime import date, timedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    # Basic fields with defaults, read-only, and copy rules
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        default=lambda self: date.today() + timedelta(days=90),  # 3 months from today
        copy=False  # not duplicated when duplicating the record
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float(
        "Selling Price",
        readonly=True,  # read-only in UI
        copy=False      # not duplicated when duplicating
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

    # Reserved field: automatically hides inactive records
    active = fields.Boolean("Active", default=True)

    # State field for workflow/status
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled')
        ],
        string="Status",
        required=True,
        copy=False,
        default='new'
    )

    # SQL constraints
    _sql_constraints = [
        (
            'check_expected_price',
            'CHECK(expected_price > 0)',
            'The expected price must be strictly positive.'
        ),
    ]
