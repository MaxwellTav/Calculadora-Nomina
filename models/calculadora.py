from odoo import models, fields, api
from datetime import date

class CalculadoraNomina(models.Model):
    _name = 'calculadora.nomina'
    _description = 'Calculadora de Nómina'

    name = fields.Char('Nombre', required=True)
    cedula = fields.Char('Cédula', required=True)
    salario = fields.Float('Salario Fijo', required=True)
    fecha_ingreso = fields.Date('Fecha de Ingreso', required=True)
    fecha_salida = fields.Date('Fecha de Salida', required=False)
    tipo_periodo = fields.Selection([
        ('semanal', 'Semanal'),
        ('quincenal', 'Quincenal'),
        ('mensual', 'Mensual'),
    ], string='Tipo de Periodo', required=True)

    aviso_previo = fields.Boolean('¿Ha sido avisado previamente?')
    incluir_cesantia = fields.Boolean('¿Incluir cesantía?', default=True)
    incluir_vacaciones = fields.Boolean('¿Incluir vacaciones?', default=True)
    incluir_navidad = fields.Boolean('¿Incluir navidad?', default=True)

    dias_laborados = fields.Integer('Días trabajados', compute='_compute_dias', store=True)
    total_recibir = fields.Float('Total a Recibir', compute='_compute_total', store=True)

    @api.depends('fecha_ingreso', 'fecha_salida')
    def _compute_dias(self):
        for rec in self:
            if rec.fecha_salida == False:
                rec.dias_laborados = 0
            else:
                fecha_fin = rec.fecha_salida or date.today()
                rec.dias_laborados = (fecha_fin - rec.fecha_ingreso).days
    
    @api.depends('salario', 'dias_laborados', 'incluir_cesantia', 'incluir_vacaciones', 'incluir_navidad', 'aviso_previo')
    def _compute_total(self):
        for rec in self:
            diario = rec.salario / 30
            total = diario * rec.dias_laborados

            if rec.incluir_cesantia:
                total += rec.salario
            
            if rec.incluir_vacaciones:
                total += (rec.salario / 23.83) * 14

            if rec.incluir_navidad:
                total += rec.salario / 12

            if not rec.aviso_previo:
                total += rec.salario / 2
            
            rec.total_recibir = total
    
    def action_imprimir_pdf(self):
        return self.env.ref('calculadora_nomina.reporte_calculadora_nomina').report_action(self)

