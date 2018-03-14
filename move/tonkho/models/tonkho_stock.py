# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class PackOperation(models.Model):
    _inherit = "stock.pack.operation"
    ghi_chu = fields.Text(string=u'Ghi Chú')
    product_uom_id_show = fields.Many2one('product.uom', 'Unit of Measure Show',compute='product_uom_id_show_')

    def get_qty_done_for_report(self):
        qty_done = self.qty_done
        int_qty_done = int(qty_done)
        if qty_done ==int_qty_done:
            return int_qty_done
        else:
            return qty_done
            
    @api.depends('product_uom_id')
    def product_uom_id_show_(self):
        for r in self:
            r.product_uom_id_show = r.product_uom_id
    
    @api.multi
    def action_split_lots(self):
        action_ctx = dict(self.env.context)
        # If it's a returned stock move, we do not want to create a lot
        returned_move = self.linked_move_operation_ids.mapped('move_id').mapped('origin_returned_move_id')
        picking_type = self.picking_id.picking_type_id
        only_create_pn = self.state not in ['done','cancel']
        print '***only_create_pn***',only_create_pn
        action_ctx.update({
            'serial': self.product_id.tracking == 'serial',
            'only_create': picking_type.use_create_lots and not picking_type.use_existing_lots and not returned_move,
            'only_create_pn':only_create_pn,
            'create_lots': picking_type.use_create_lots,
            'state_done': self.picking_id.state == 'done',
            'show_reserved': any([lot for lot in self.pack_lot_ids if lot.qty_todo > 0.0])})
        view_id = self.env.ref('stock.view_pack_operation_lot_form').id
        return {
            'name': _('Lot/Serial Number Details'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.pack.operation',
            'views': [(view_id, 'form')],
            'view_id': view_id,
            'target': 'new',
            'res_id': self.ids[0],
            'context': action_ctx}
        
    split_lot = action_split_lots
        

class StockLocation(models.Model):
    _inherit = 'stock.location'
    department_id =  fields.Many2one('hr.department')
    partner_id =  fields.Many2one('res.partner')
    
class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    ghi_chu = fields.Text(related='lot_id.ghi_chu')
    ghi_chu_for_create = fields.Text(string=u'Ghi chú Cho Tạo SN')
    pn = fields.Char(related='lot_id.pn', string=u'Part Number')
    pn_for_create = fields.Char(string=u'Part Number For Create')
class StockProductionLot(models.Model):
    _inherit = "stock.production.lot"
    pn = fields.Char(string=u'Part Number')
    ghi_chu = fields.Text(string=u'Ghi chú')
    

class Quant(models.Model):
    """ Quants are the smallest unit of stock physical instances """
    _inherit = "stock.quant"
    pn = fields.Char(related='lot_id.pn')
    
#     company_id = fields.Many2one(
#         'res.company', 'Company',
#         index=True, readonly=True, required=True,
#         default=lambda self: self.env['res.company'].search([('name','=',u'Đài HCM')])[0],#_company_default_get('stock.quant'),
#         help="The company to which the quants belong")
    @api.model
    def quants_move(self, quants, move, location_to, location_from=False, lot_id=False, owner_id=False, src_package_id=False, dest_package_id=False, entire_pack=False):
        """Moves all given stock.quant in the given destination location.  Unreserve from current move.
        :param quants: list of tuple(browse record(stock.quant) or None, quantity to move)
        :param move: browse record (stock.move)
        :param location_to: browse record (stock.location) depicting where the quants have to be moved
        :param location_from: optional browse record (stock.location) explaining where the quant has to be taken
                              (may differ from the move source location in case a removal strategy applied).
                              This parameter is only used to pass to _quant_create_from_move if a negative quant must be created
        :param lot_id: ID of the lot that must be set on the quants to move
        :param owner_id: ID of the partner that must own the quants to move
        :param src_package_id: ID of the package that contains the quants to move
        :param dest_package_id: ID of the package that must be set on the moved quant
        """
        # TDE CLEANME: use ids + quantities dict
        print '***quants**',quants
        if location_to.usage == 'view':
            raise UserError(_('You cannot move to a location of type view %s.') % (location_to.name))

        quants_reconcile_sudo = self.env['stock.quant'].sudo()
        quants_move_sudo = self.env['stock.quant'].sudo()
        check_lot = False
        for quant, qty in quants:
            if not quant:
                #If quant is None, we will create a quant to move (and potentially a negative counterpart too)
                quant = self._quant_create_from_move(
                    qty, move, lot_id=lot_id, owner_id=owner_id, src_package_id=src_package_id, dest_package_id=dest_package_id, force_location_from=location_from, force_location_to=location_to)
                check_lot = True
            else:
                quant._quant_split(qty)
                quants_move_sudo |= quant
            quants_reconcile_sudo |= quant

        if quants_move_sudo:
            moves_recompute = quants_move_sudo.filtered(lambda self: self.reservation_id != move).mapped('reservation_id')
            quants_move_sudo._quant_update_from_move(move, location_to, dest_package_id, lot_id=lot_id, entire_pack=entire_pack)
            moves_recompute.recalculate_move_state()

        if location_to.usage == 'internal':
            # Do manual search for quant to avoid full table scan (order by id)
            self._cr.execute("""
                SELECT 0 FROM stock_quant, stock_location WHERE product_id = %s AND stock_location.id = stock_quant.location_id AND
                ((stock_location.parent_left >= %s AND stock_location.parent_left < %s) OR stock_location.id = %s) AND qty < 0.0 LIMIT 1
            """, (move.product_id.id, location_to.parent_left, location_to.parent_right, location_to.id))
            if self._cr.fetchone():
                quants_reconcile_sudo._quant_reconcile_negative(move)

        # In case of serial tracking, check if the product does not exist somewhere internally already
        # Checking that a positive quant already exists in an internal location is too restrictive.
        # Indeed, if a warehouse is configured with several steps (e.g. "Pick + Pack + Ship") and
        # one step is forced (creates a quant of qty = -1.0), it is not possible afterwards to
        # correct the inventory unless the product leaves the stock.
        picking_type = move.picking_id and move.picking_id.picking_type_id or False
        if check_lot and lot_id and move.product_id.tracking == 'serial' and (not picking_type or (picking_type.use_create_lots or picking_type.use_existing_lots)):
            other_quants = self.search([('product_id', '=', move.product_id.id), ('lot_id', '=', lot_id),
                                        ('qty', '>', 0.0), ('location_id.usage', '=', 'internal')])
            print '**other_quants**',other_quants
            if other_quants:
                # We raise an error if:
                # - the total quantity is strictly larger than 1.0
                # - there are more than one negative quant, to avoid situations where the user would
                #   force the quantity at several steps of the process
                if sum(other_quants.mapped('qty')) > 1.0 or len([q for q in other_quants.mapped('qty') if q < 0]) > 1:
                    lot_name = self.env['stock.production.lot'].browse(lot_id).name
                    raise UserError(_('The serial skjdflkasdjfld number %s is already in stock.') % lot_name + _("Otherwise make sure the right stock/owner is set."))