# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import timedelta, date

class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"

    # -------------------------
    # Basic Fields
    # -------------------------
    price = fields.Float("Offer Price", required=True)

    status = fields.Selection(
        [
            ('accepted', 'Accepted'),
            ('refused', 'Refused')
        ],
        string="Status",
        copy=False
    )

    partner_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        required=True
    )

    property_id = fields.Many2one(
        "estate.property",
        string="Property",
        required=True
    )

    # -------------------------
    # Chapter 8 Fields
    # -------------------------
    validity = fields.Integer(
        string="Validity (days)",
        default=7
    )

    date_deadline = fields.Date(
        string="Deadline",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
        store=True
    )

    # -------------------------
    # Compute + Inverse
    # -------------------------
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        """Compute the deadline based on creation date + validity."""
        for offer in self:
            if offer.create_date:
                offer.date_deadline = offer.create_date.date() + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False

    def _inverse_date_deadline(self):
        """Adjust validity if the deadline is manually updated."""
        for offer in self:
            if offer.date_deadline and offer.create_date:
                delta = offer.date_deadline - offer.create_date.date()
                offer.validity = delta.days

    # -------------------------
    # Step 4: Confirm Offer
    # -------------------------
    def action_confirm_offer(self):
        """Confirm this offer: mark as accepted, refuse others, update property."""
        for offer in self:
            property_rec = offer.property_id

            # Mark all other offers as refused
            other_offers = property_rec.offer_ids.filtered(lambda o: o.id != offer.id)
            other_offers.write({'status': 'refused'})

            # Accept this offer
            offer.status = 'accepted'

            # Update property selling price, buyer, and state
            property_rec.selling_price = offer.price
            property_rec.buyer_id = offer.partner_id
            property_rec.state = 'offer_accepted'

            def action_refuse_offer(self):
                for offer in self:
                    offer.status = 'refused'
                    return True
