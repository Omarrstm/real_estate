# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import date, timedelta

# -------------------------
# Property Tag Model
# -------------------------
class EstatePropertyTag(models.Model):
    _name = "estate.property.tag"
    _description = "Property Tag"

    name = fields.Char("Name", required=True)


# -------------------------
# Property Model
# -------------------------
class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"
    _order = "id desc"

    # -------------------------
    # Basic fields
    # -------------------------
    name = fields.Char("Title", required=True)
    description = fields.Text("Description")
    postcode = fields.Char("Postcode")
    date_availability = fields.Date(
        "Available From",
        default=lambda self: date.today() + timedelta(days=90),
        copy=False
    )
    expected_price = fields.Float("Expected Price", required=True)
    selling_price = fields.Float("Selling Price", readonly=True, copy=False)
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

    # -------------------------
    # Status
    # -------------------------
    state = fields.Selection([
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('cancelled', 'Cancelled')
    ], string="Status", required=True, copy=False, default='new')

    # -------------------------
    # Relationships
    # -------------------------
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer")
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # -------------------------
    # Chapter 8 Fields (Computed)
    # -------------------------
    total_area = fields.Float(string="Total Area", compute="_compute_total_area")
    best_price = fields.Float(string="Best Offer", compute="_compute_best_price")

    # -------------------------
    # Compute Methods
    # -------------------------
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = (record.living_area or 0) + (record.garden_area or 0)

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                record.best_price = max(record.offer_ids.mapped("price"))
            else:
                record.best_price = 0.0

    # -------------------------
    # Onchange Methods
    # -------------------------
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # -------------------------
    # SQL Constraints
    # -------------------------
    _sql_constraints = [
        (
            'check_expected_price',
            'CHECK(expected_price > 0)',
            'The expected price must be strictly positive.'
        ),
    ]

    # -------------------------
    # Chapter 9 Actions (Buttons)
    # -------------------------
    def action_sold(self):
        """Mark property as sold."""
        for record in self:
            if record.state == 'cancelled':
                raise ValidationError("Cancelled properties cannot be marked as Sold.")
            record.state = 'sold'

    def action_cancel(self):
        """Mark property as cancelled."""
        for record in self:
            if record.state == 'sold':
                raise ValidationError("Sold properties cannot be cancelled.")
            record.state = 'cancelled'

    def action_reset_to_new(self):
        """Reset property state to new."""
        for record in self:
            record.state = 'new'
            record.selling_price = 0.0
            record.buyer_id = False


# -------------------------
# Property Offer Model
# -------------------------
class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    price = fields.Float("Price", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    status = fields.Selection([
        ('new', 'New'),
        ('accepted', 'Accepted'),
        ('refused', 'Refused')
    ], default='new')
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    validity = fields.Integer("Validity (days)")
    date_deadline = fields.Date("Deadline")

    # -------------------------
    # Methods for buttons
    # -------------------------
    def action_confirm_offer(self):
        """Accept this offer and refuse others."""
        for offer in self:
            offer.status = 'accepted'
            offer.property_id.state = 'offer_accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            # Refuse other offers
            other_offers = offer.property_id.offer_ids - offer
            other_offers.write({'status': 'refused'})

    def action_refuse_offer(self):
        """Refuse this offer."""
        for offer in self:
            offer.status = 'refused'
