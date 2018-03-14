# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _
from odoo.tools.float_utils import float_compare

class StockPicking(models.Model):
    _inherit = "stock.picking"
#     source_department_id = fields.Many2one('res.partner')
#     dest_department_id = fields.Many2one('res.partner')
    source_member_ids = fields.Many2many('res.partner','source_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Giao')
    dest_member_ids = fields.Many2many('res.partner','dest_member_stock_picking_relate','picking_id','partner_id',string=u'Nhân Viên Nhận')
    ban_giao_or_nghiem_thu = fields.Selection([(u'ban_giao',u'Bàn Giao'),(u'nghiem_thu',u'Nghiệm Thu')],default=u'ban_giao',string=u'Bàn Giao Hay Nghiệm Thu')
    don_vi_nhan = fields.Char(compute='don_vi_nhan_',string=u'Đơn Vị Nhận')
    don_vi_giao = fields.Char(compute='don_vi_giao_',string=u'Đơn Vị Giao')
    pack_operation_product_ids = fields.One2many(
        'stock.pack.operation', 'picking_id', 'Non pack',
        domain=[('product_id', '!=', False)],
        )
    ly_do = fields.Text(u'Lý Do')
    so_ban_in = fields.Integer(u'Số Bản In',default=2)
    ben_giao_giu = fields.Integer(u'Bên Giao Giữ', default=1)
    ben_nhan_giu = fields.Integer(u'Bên Nhận Giữ',default=1)
    totrinh_id = fields.Many2one('totrinh')
    
#     @api.model
#     def create(self, vals):
#         # TDE FIXME: clean that brol
#         defaults = self.default_get(['name', 'picking_type_id'])
#         if vals.get('name', '/') == '/' and defaults.get('name', '/') == '/' and vals.get('picking_type_id', defaults.get('picking_type_id')):
#             name = self.env['stock.picking.type'].browse(vals.get('picking_type_id', defaults.get('picking_type_id'))).sequence_id.next_by_id()
# #             print 'name',name
# #             raise ValueError('name')
# #             vals['name'] = name
#         # TDE FIXME: what ?
#         # As the on_change in one2many list is WIP, we will overwrite the locations on the stock moves here
#         # As it is a create the format will be a list of (0, 0, dict)
#         if vals.get('move_lines') and vals.get('location_id') and vals.get('location_dest_id'):
#             for move in vals['move_lines']:
#                 if len(move) == 3:
#                     move[2]['location_id'] = vals['location_id']
#                     move[2]['location_dest_id'] = vals['location_dest_id']
#         return super(StockPicking, self).create(vals)
    
    
    
    def ban_giao_or_nghiem_thu_show(self):
        adict = {u'ban_giao':u'Bàn Giao',u'nghiem_thu':u'Nghiệm Thu'}
        if self.ban_giao_or_nghiem_thu != False:
            return adict[self.ban_giao_or_nghiem_thu]
        else:
            return False
            
    def don_vi_nhan_(self):
        self.don_vi_nhan = self.location_dest_id.partner_id.name if self.location_dest_id.partner_id.name else self.location_dest_id.name
    def don_vi_giao_(self):
        self.don_vi_giao = self.location_id.partner_id.name if self.location_id.partner_id.name else self.location_id.name
    @api.multi
    def write(self,vals):
        pack_operation_product_ids = vals.get('pack_operation_product_ids')
        if pack_operation_product_ids:
            check_list = any(map(lambda i:i[0]==0,pack_operation_product_ids))
            if check_list:#'pack_operation_product_ids' in vals:
                raise UserWarning(u'Ban khong duoc sua fields pack_operation_product_ids')
        res = super(StockPicking,self).write(vals)
        return res
    
    def _create_lots_for_picking(self):
        Lot = self.env['stock.production.lot']
        for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
            if not pack_op_lot.lot_id:
                lot = Lot.create({'name': pack_op_lot.lot_name, 
                                  'product_id': pack_op_lot.operation_id.product_id.id,
                                  #moi them
                                  'pn':pack_op_lot.pn_for_create,
                                  'ghi_chu':pack_op_lot.ghi_chu_for_create,
                                  })
                pack_op_lot.write({'lot_id': lot.id})
        # TDE FIXME: this should not be done here
        self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()
        
    @api.multi
    def do_transfer(self):
        """ If no pack operation, we do simple action_done of the picking.
        Otherwise, do the pack operations. """
        # TDE CLEAN ME: reclean me, please
        self._create_lots_for_picking()
        no_pack_op_pickings = self.filtered(lambda picking: not picking.pack_operation_ids)
        no_pack_op_pickings.action_done()
        other_pickings = self - no_pack_op_pickings
        for picking in other_pickings:
            print 'truoc picking_recompute_remaining_quantities '
            need_rereserve, all_op_processed = picking.picking_recompute_remaining_quantities()
            todo_moves = self.env['stock.move']
            toassign_moves = self.env['stock.move']
            print 'sau picking_recompute_remaining_quantities','all_op_processed',all_op_processed,'need_rereserve',need_rereserve

            # create extra moves in the picking (unexpected product moves coming from pack operations)
            if not all_op_processed:
                todo_moves |= picking._create_extra_moves()

            if need_rereserve or not all_op_processed:
                moves_reassign = any(x.origin_returned_move_id or x.move_orig_ids for x in picking.move_lines if x.state not in ['done', 'cancel'])
                if moves_reassign and picking.location_id.usage not in ("supplier", "production", "inventory"):
                    # unnecessary to assign other quants than those involved with pack operations as they will be unreserved anyways.
                    print 'truc khi rereserve_quants'
                    picking.with_context(reserve_only_ops=True, no_state_change=True).rereserve_quants(move_ids=picking.move_lines.ids)
                picking.do_recompute_remaining_quantities()
                print 'sau  khi rereserve_quants,do_recompute_remaining_quantities'


            # split move lines if needed
            for move in picking.move_lines:
                print 'truuoc khi action_done '
                rounding = move.product_id.uom_id.rounding
                remaining_qty = move.remaining_qty
                if move.state in ('done', 'cancel'):
                    # ignore stock moves cancelled or already done
                    continue
                elif move.state == 'draft':
                    toassign_moves |= move
                if float_compare(remaining_qty, 0,  precision_rounding=rounding) == 0:
                    if move.state in ('draft', 'assigned', 'confirmed'):
                        todo_moves |= move
                elif float_compare(remaining_qty, 0, precision_rounding=rounding) > 0 and float_compare(remaining_qty, move.product_qty, precision_rounding=rounding) < 0:
                    # TDE FIXME: shoudl probably return a move - check for no track key, by the way
                    new_move_id = move.split(remaining_qty)
                    new_move = self.env['stock.move'].with_context(mail_notrack=True).browse(new_move_id)
                    todo_moves |= move
                    # Assign move as it was assigned before
                    toassign_moves |= new_move

            # TDE FIXME: do_only_split does not seem used anymore
            
            if todo_moves and not self.env.context.get('do_only_split'):
                print 'truoc khi action_done','todo_moves',todo_moves
                todo_moves.action_done()
                print 'sau khi action_done'
            elif self.env.context.get('do_only_split'):
                picking = picking.with_context(split=todo_moves.ids)

            picking._create_backorder()
        return True
    
    
    @api.multi
    def do_new_transfer(self):
        for pick in self:
            pack_operations_delete = self.env['stock.pack.operation']
            if not pick.move_lines and not pick.pack_operation_ids:
                raise UserError(_('Please create some Initial Demand or Mark as Todo and create some Operations. '))
            # In draft or with no pack operations edited yet, ask if we can just do everything
            if pick.state == 'draft' or all([x.qty_done == 0.0 for x in pick.pack_operation_ids]):
                # If no lots when needed, raise error
                picking_type = pick.picking_type_id
                if (picking_type.use_create_lots or picking_type.use_existing_lots):
                    for pack in pick.pack_operation_ids:
                        if pack.product_id and pack.product_id.tracking != 'none':
                            raise UserError(_('Some products require lots/serial numbers, so you need to specify those first!'))
                
                view = self.env.ref('stock.view_immediate_transfer')
                wiz = self.env['stock.immediate.transfer'].create({'pick_id': pick.id})
                # TDE FIXME: a return in a loop, what a good idea. Really.
                return {
                    'name': _('Immediate Transfer?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.immediate.transfer',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }

            # Check backorder should check for other barcodes
            if pick.check_backorder():
                view = self.env.ref('stock.view_backorder_confirmation')
                wiz = self.env['stock.backorder.confirmation'].create({'pick_id': pick.id})
                # TDE FIXME: same reamrk as above actually
                return {
                    'name': _('Create Backorder?'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'stock.backorder.confirmation',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'res_id': wiz.id,
                    'context': self.env.context,
                }
            for operation in pick.pack_operation_ids:
                if operation.qty_done < 0:
                    raise UserError(_('No negative quantities allowed'))
                if operation.qty_done > 0:
                    operation.write({'product_qty': operation.qty_done})
                else:
                    pack_operations_delete |= operation
            if pack_operations_delete:
                pack_operations_delete.unlink()
        print '****do transfer***'
        self.do_transfer()
        return
    @api.multi
    def force_assign(self):
        """ Changes state of picking to available if moves are confirmed or waiting.
        @return: True
        """
        print 'before force_assign**'
        self.mapped('move_lines').filtered(lambda move: move.state in ['confirmed', 'waiting']).force_assign()
        return True
    @api.multi
    def action_assign(self):
        """ Check availability of picking moves.
        This has the effect of changing the state and reserve quants on available moves, and may
        also impact the state of the picking as it is computed based on move's states.
        @return: True
        """
        self.filtered(lambda picking: picking.state == 'draft').action_confirm()
        moves = self.mapped('move_lines').filtered(lambda move: move.state not in ('draft', 'cancel', 'done'))
        if not moves:
            raise UserError(_('Nothing to check the availability for.'))
        moves.action_assign()
        print ' after moves.action_assign()',moves.action_assign()
        return True
    