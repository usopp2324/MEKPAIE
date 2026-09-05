"""
PDF generation for payslips using ReportLab.
"""
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from PIL import Image as PILImage
from xml.sax.saxutils import escape
from app.paths import PDF_DIR


NAVY = colors.HexColor("#B8CDE3")
BLUE = colors.HexColor('#145DA0')
LIGHT_BLUE = colors.HexColor('#EAF2FB')
PALE_BLUE = colors.HexColor('#F5F9FE')
LINE_BLUE = colors.HexColor('#B8CDE3')
TEXT_BLUE = colors.HexColor('#183B63')


class PDFPayslipGenerator:
    """Generate professional PDF payslips."""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.pdf_dir = PDF_DIR
        self.pdf_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_payslip(
        self,
        company_info: Dict[str, Any],
        employee_info: Dict[str, Any],
        payroll_data: Dict[str, Any],
        month: int,
        year: int,
        filename: Optional[str] = None
    ) -> str:
        """
        Generate professional payslip PDF.
        
        Args:
            company_info: Company details
            employee_info: Employee details
            payroll_data: Calculated payroll data
            month: Month number (1-12)
            year: Year
            filename: Custom filename (optional)
            
        Returns:
            Path to generated PDF
        """
        if not filename:
            filename = (
                f"Bulletin_{employee_info.get('first_name', 'Unknown')}_"
                f"{employee_info.get('last_name', 'Unknown')}_"
                f"{self._get_month_name(month)}_{year}.pdf"
            )
        
        pdf_path = self.pdf_dir / filename
        
        # Create PDF document
        doc = SimpleDocTemplate(
            str(pdf_path),
            pagesize=A4,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.1*cm,
            bottomMargin=1.2*cm,
            title=f"Bulletin de paie - {employee_info.get('first_name', '')} {employee_info.get('last_name', '')}",
            author="MEKPAIE"
        )
        
        # Create story (list of elements)
        story = []
        
        # Add the complete document header.
        story.extend(self._create_header(company_info, employee_info, month, year))
        story.append(Spacer(1, 0.2*cm))
        
        # Add earnings table
        story.extend(self._create_earnings_section(payroll_data))
        story.append(Spacer(1, 0.2*cm))
        
        # Add deductions table
        story.extend(self._create_deductions_section(payroll_data))
        story.append(Spacer(1, 0.2*cm))
        
        # Add net salary highlight
        story.extend(self._create_net_salary_section(payroll_data))
        story.append(Spacer(1, 0.3*cm))

        story.extend(self._create_ir_detail_section(payroll_data, employee_info))
        story.append(Spacer(1, 0.3*cm))

        # Add final summary table at the end of the bulletin
        story.extend(self._create_final_summary_table(payroll_data, employee_info))
        story.append(Spacer(1, 0.3*cm))
        
        # Add employer contributions
        story.extend(self._create_employer_section(payroll_data))
        story.append(Spacer(1, 0.3*cm))
        
        # Add footer
        story.extend(self._create_footer())
        
        # Build PDF
        doc.build(story, onFirstPage=self._draw_page_footer, onLaterPages=self._draw_page_footer)
        
        return str(pdf_path)
    
    def _create_header(self, company_info: Dict, employee_info: Dict, month: int, year: int) -> list:
        """Create the compact company, title, and employee header."""
        styles = getSampleStyleSheet()

        company_style = ParagraphStyle(
            'CompanyHeader', parent=styles['Normal'], fontName='Helvetica',
            fontSize=7.5, leading=9, textColor=colors.black
        )
        company_name = escape(str(company_info.get('name', '')))
        company_text = (
            f"<b>{company_name}</b><br/>"
            f"{escape(str(company_info.get('address', '')))}<br/>"
            f"Tél: {escape(str(company_info.get('phone', '')))}<br/>"
            f"ICE: {escape(str(company_info.get('ice', '')))}<br/>"
            f"IF: {escape(str(company_info.get('fiscal_id', '')))}<br/>"
            f"CNSS: {escape(str(company_info.get('cnss', '')))}"
        )

        logo_path = company_info.get('logo_path')
        if logo_path and Path(logo_path).exists():
            try:
                with PILImage.open(logo_path) as logo:
                    width, height = logo.size
                ratio = width / height if height else 1
                image_height = 2.9 * cm
                image_width = min(image_height * ratio, 5.0 * cm)
                logo_element = Image(logo_path, width=image_width, height=image_height)
            except Exception:
                logo_element = Paragraph('<b>MEKINDUSTRIE</b>', company_style)
        else:
            logo_element = Paragraph('<b>MEKINDUSTRIE</b>', company_style)

        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'], fontSize=14,
            leading=17, textColor=colors.black, alignment=TA_CENTER,
            fontName='Helvetica-Bold', spaceAfter=2
        )
        month_style = ParagraphStyle(
            'PayrollMonth', parent=styles['Normal'], fontSize=9,
            leading=11, textColor=colors.black, alignment=TA_CENTER
        )
        title_block = [
            Paragraph('BULLETIN DE PAIE', title_style),
            Paragraph(f'{self._get_month_name(month)} {year}', month_style),
        ]

        employee_style = ParagraphStyle(
            'EmployeeHeader', parent=styles['Normal'], fontName='Helvetica',
            fontSize=7.2, leading=8.5, textColor=colors.black
        )
        employee_rows = [
            [Paragraph('<b>INFORMATIONS DU SALARIÉ</b>', employee_style), ''],
            [f"Nom: {escape(str(employee_info.get('last_name', '')))}",
             f"Prénom: {escape(str(employee_info.get('first_name', '')))}"],
            [f"N° Matricule: {escape(str(employee_info.get('matricule', '')))}",
             f"Date d'entrée: {escape(str(employee_info.get('hire_date', '')))}"],
            [f"Situation familiale: {escape(str(employee_info.get('marital_status', '')))}",
             f"Nombre d'enfants: {escape(str(employee_info.get('children_count', '')))}"],
            [f"Ancienneté: {escape(str(employee_info.get('seniority', '')))}",
             f"CIN: {escape(str(employee_info.get('cin', '')))}"],
            [f"CNSS: {escape(str(employee_info.get('cnss', '')))}",
             f"Fonction: {escape(str(employee_info.get('position', '')))}"],
            [f"Adresse: {escape(str(employee_info.get('address', '')))}",
             f"Catégorie: {escape(str(employee_info.get('categorie', 'Mensuel')))}" ],
        ]
        employee_table = Table(employee_rows, colWidths=[5.4*cm, 5.4*cm])
        employee_table.setStyle(TableStyle([
            ('SPAN', (0, 0), (-1, 0)),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6E6E6')),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOX', (0, 0), (-1, -1), 0.7, colors.black),
            ('INNERGRID', (0, 1), (-1, -1), 0.35, colors.HexColor('#777777')),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 4),
            ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
        ]))

        right_block = [title_block, Spacer(1, 0.18*cm), employee_table]
        header_table = Table([
            [[logo_element, Paragraph(company_text, company_style)], right_block]
        ], colWidths=[7.0*cm, 11.0*cm])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('BOX', (0, 0), (-1, -1), 0.8, colors.black),
            ('LINEAFTER', (0, 0), (0, 0), 0.7, colors.black),
        ]))

        separator = Table([['']], colWidths=[18*cm])
        separator.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 1.0, colors.black),
        ]))
        return [header_table, separator]
    
    def _create_earnings_section(self, payroll_data: Dict) -> list:
        """Create earnings/gains section."""
        elements = []

        hours_or_days = float(payroll_data.get('hours_or_days_worked', 0) or 0)
        display_worked_days = self._truncate_display_value(hours_or_days / 8.0 if hours_or_days > 0 and hours_or_days > 30 else hours_or_days)
        holiday_days = float(payroll_data.get('holiday_days_in_month', 0) or 0)
        holiday_amount = float(payroll_data.get('holiday_paid_amount', 0) or 0)
        overtime_amount_25 = float(payroll_data.get('overtime_amount_25', 0) or 0)
        overtime_amount_50 = float(payroll_data.get('overtime_amount_50', 0) or 0)
        worked_holiday = bool(payroll_data.get('employee_worked_holiday_day', False))
        all_days_without_absence = bool(payroll_data.get('all_days_worked_without_absence', False))
        holiday_chome_paye = "Oui" if holiday_days > 0 and not worked_holiday and all_days_without_absence else "Non"
        holiday_travaille = "Oui" if holiday_days > 0 and worked_holiday and all_days_without_absence else "Non"
        regular_base_salary = float(payroll_data.get('regular_base_salary', payroll_data.get('base_salary', 0)) or 0)
        total_gains = float(payroll_data.get('base_salary', regular_base_salary) or 0)

        earnings_data = [
            ['GAINS', 'BASE', 'MONTANT'],
            ['Jours travaillés', '', str(display_worked_days)],
            ['Montant férié payé', '', f"{holiday_amount:.2f}"],
            ['Salaire par heure/jour', '', f"{payroll_data.get('rate_per_unit', 0):.2f} DH"],
            ['Salaire de base régulier', '', f"{regular_base_salary:.2f}"],
        ]
        if overtime_amount_25 or overtime_amount_50:
            earnings_data.extend([
                ['Heures supplémentaires 25%', f"{payroll_data.get('overtime_hours_25', 0):.2f} h", f"{overtime_amount_25:.2f}"],
                ['Heures supplémentaires 50%', f"{payroll_data.get('overtime_hours_50', 0):.2f} h", f"{overtime_amount_50:.2f}"],
            ])
        earnings_data.append(['TOTAL GAINS', '', f"{total_gains:.2f}"])

        earnings_table = Table(earnings_data, colWidths=[10*cm, 4*cm, 4*cm])
        earnings_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('BACKGROUND', (0, -1), (-1, -1), BLUE),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, PALE_BLUE]),
            ('GRID', (0, 0), (-1, -1), 0.4, LINE_BLUE),
            ('LINEBELOW', (0, -1), (-1, -1), 1.2, NAVY),
        ]))
        
        elements.append(earnings_table)
        
        return elements
    
    def _create_deductions_section(self, payroll_data: Dict) -> list:
        """Create deductions section."""
        elements = []
        
        deductions_data = [
            ['COTISATION', 'MONTANT'],
            ['Cotisation CNSS (4.48%)', f"{payroll_data.get('cnss_employee', 0):.2f}"],
            ['Cotisation AMO (2.26%)', f"{payroll_data.get('amo_employee', 0):.2f}"],
            ['TOTAL DE COTISATION', f"{payroll_data.get('total_deductions', 0):.2f}"],
        ]
        
        deductions_table = Table(deductions_data, colWidths=[12*cm, 6*cm])
        deductions_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('BACKGROUND', (0, -1), (-1, -1), BLUE),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, PALE_BLUE]),
            ('GRID', (0, 0), (-1, -1), 0.4, LINE_BLUE),
            ('LINEBELOW', (0, -1), (-1, -1), 1.2, NAVY),
        ]))
        
        elements.append(deductions_table)
        
        return elements
    
    def _create_net_salary_section(self, payroll_data: Dict) -> list:
        """Create net salary highlight section."""
        elements = []
        styles = getSampleStyleSheet()
        
        net_style = ParagraphStyle(
            'NetSalary',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.white,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        net_data = [
            [Paragraph(f"NET IMPOSABLE: {payroll_data.get('net_taxable_salary', 0):.2f} DH", net_style)],
        ]
        
        net_table = Table(net_data, colWidths=[18*cm])
        net_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), NAVY),
            ('BOX', (0, 0), (-1, -1), 0.8, BLUE),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        elements.append(net_table)
        
        return elements

    def _create_ir_detail_section(self, payroll_data: Dict, employee_info: Optional[Dict[str, Any]] = None) -> list:
        """Create premiums section for simplified payroll."""
        category = str((employee_info or {}).get('categorie', 'Mensuel') or 'Mensuel').lower()
        transport_enabled = bool((employee_info or {}).get('transport_premium_enabled', False))
        hours_or_days = float(payroll_data.get('hours_or_days_worked', 0) or 0)
        if category == 'horaire':
            worked_days = self._truncate_display_value(hours_or_days / 8.0)
        else:
            worked_days = self._truncate_display_value(hours_or_days)

        premiums_data = [
            ['PRIMES', 'JOURS TRAVAILLÉS', 'MONTANT'],
            ['Prime de salissure', str(worked_days), f"{payroll_data.get('salary_premium', 0):.2f}"],
            ['Prime de pannier', str(worked_days), f"{payroll_data.get('wage_premium', 0):.2f}"],
        ]
        if transport_enabled:
            premiums_data.append(['Prime de transport', str(worked_days), f"{payroll_data.get('transport_premium', 0):.2f}"])

        table = Table(premiums_data, colWidths=[6.5*cm, 5.5*cm, 6*cm])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (2, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, PALE_BLUE]),
            ('GRID', (0, 0), (-1, -1), 0.4, LINE_BLUE),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        return [table]
    
    
    def _create_employer_section(self, payroll_data: Dict) -> list:
        """Create employer contributions section - simplified for new model."""
        # Employer contributions are not calculated in the simplified model
        # Return empty list or minimal placeholder
        return []
    
    def _create_final_summary_table(self, payroll_data: Dict, employee_info: Optional[Dict[str, Any]] = None) -> list:
        """Create the final working-days and absences summary table at the end of the payslip."""
        styles = getSampleStyleSheet()
        section_style = ParagraphStyle(
            'SummarySection',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
            textColor=colors.white,
            spaceAfter=2,
        )
        cell_style = ParagraphStyle(
            'SummaryCell',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=7,
            leading=8,
            alignment=TA_CENTER,
            textColor=colors.black,
        )

        category = str((employee_info or {}).get('categorie', 'Mensuel') or 'Mensuel').lower()
        hours_or_days = float(payroll_data.get('hours_or_days_worked', 0) or 0)
        if category == 'horaire':
            declared_cnss = self._truncate_display_value(hours_or_days / 8.0)
            worked_days = self._truncate_display_value(hours_or_days / 8.0)
        else:
            declared_cnss = self._truncate_display_value(hours_or_days)
            worked_days = self._truncate_display_value(hours_or_days)

        ferie = float(payroll_data.get('holiday_paid_days', 0) or 0)
        conge_chome_paye = float(payroll_data.get('holiday_paid_days', 0) or 0)
        conge_paye_non_chome = float(payroll_data.get('holiday_unpaid_days', 0) or 0)
        solde_conges = float(payroll_data.get('leave_balance', 0) or 0)
        justifiee = str(payroll_data.get('absence_justified', '') or '')
        autorisee = str(payroll_data.get('absence_authorized', '') or '')
        at = str(payroll_data.get('absence_at', '') or '')
        maladie = str(payroll_data.get('absence_sickness', '') or '')

        ferie_display = f'{ferie:.0f}' if ferie > 0 else ''
        conge_chome_display = f'{conge_chome_paye:.0f}' if conge_chome_paye > 0 else ''
        conge_non_chome_display = f'{conge_paye_non_chome:.0f}' if conge_paye_non_chome > 0 else ''
        solde_display = f'{solde_conges:.2f}' if solde_conges > 0 else ''

        professional_fees = float(payroll_data.get('base_salary', 0) or 0) * 0.20
        total_premiums = sum(
            float(payroll_data.get(premium_key, 0) or 0)
            for premium_key in ('salary_premium', 'wage_premium', 'transport_premium')
        )
        net_to_pay = float(payroll_data.get('net_taxable_salary', 0) or 0) + total_premiums

        main_table_data = [
            [
                Paragraph('Nombre jours ouvrables', section_style),
                '',
                '',
                '',
                '',
                '',
                Paragraph('Absences', section_style),
                '',
                '',
                '',
                Paragraph('Frais profession.', section_style),
                Paragraph('Net à payer', section_style),
            ],
            [
                Paragraph('Déclarés CNSS', cell_style),
                Paragraph('Travaillés', cell_style),
                Paragraph('Férié', cell_style),
                Paragraph('Congé chômé payé', cell_style),
                Paragraph('Congé payé non chômé', cell_style),
                Paragraph('Solde congés', cell_style),
                Paragraph('Justifiée', cell_style),
                Paragraph('Autorisée', cell_style),
                Paragraph('AT', cell_style),
                Paragraph('Maladie', cell_style),
                Paragraph('20,00%', cell_style),
                Paragraph('', cell_style),
            ],
            [
                f'{declared_cnss:.2f}',
                f'{worked_days:.2f}',
                ferie_display,
                conge_chome_display,
                conge_non_chome_display,
                solde_display,
                justifiee,
                autorisee,
                at,
                maladie,
                f'{professional_fees:.2f} DH',
                f'{net_to_pay:.2f} DH',
            ],
        ]

        summary_table = Table(
            main_table_data,
            colWidths=[1.4*cm, 1.4*cm, 1.2*cm, 1.7*cm, 1.8*cm, 1.6*cm, 1.3*cm, 1.4*cm, 1.2*cm, 1.4*cm, 1.8*cm, 1.8*cm]
        )
        summary_table.setStyle(TableStyle([
            ('GRID', (0, 0), (-1, -1), 0.35, colors.black),
            ('BACKGROUND', (0, 0), (-1, 0), NAVY),
            ('BACKGROUND', (0, 1), (-1, 1), LIGHT_BLUE),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 6.0),
            ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
            ('TOPPADDING', (0, 0), (-1, -1), 3),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
            ('SPAN', (0, 0), (5, 0)),
            ('SPAN', (6, 0), (9, 0)),
            ('SPAN', (10, 0), (10, 0)),
            ('SPAN', (11, 0), (11, 0)),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ]))

        return [summary_table]

    def _create_footer(self) -> list:
        """Create footer section."""
        elements = []
        styles = getSampleStyleSheet()
        
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer = Paragraph(
            "MEK industrie SARL - HAY RIAD Lot AL MAJD N 261-IF:18762714-RC:74857-CNSS:4770823-ICE 001520530000067-tel/fax:0539955323",
            footer_style
        )
        elements.append(footer)
        
        return elements

    def _draw_page_footer(self, canvas, doc):
        """Draw a restrained footer on every page."""
        canvas.saveState()
        canvas.setStrokeColor(LINE_BLUE)
        canvas.setLineWidth(0.5)
        canvas.line(1 * cm, 0.85 * cm, self.page_width - 1 * cm, 0.85 * cm)
        canvas.setFont('Helvetica', 7.5)
        canvas.setFillColor(TEXT_BLUE)
        canvas.drawString(1 * cm, 0.55 * cm, 'MEKPAIE | Bulletin de paie')
        canvas.drawRightString(self.page_width - 1 * cm, 0.55 * cm, f'Page {doc.page}')
        canvas.restoreState()
    
    @staticmethod
    def _truncate_display_value(value: Any) -> int:
        """Convert fractional day/hour values to whole numbers for display only."""
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _get_month_name(month: int) -> str:
        """Get French month name."""
        months = {
            1: "Janvier", 2: "Février", 3: "Mars", 4: "Avril",
            5: "Mai", 6: "Juin", 7: "Juillet", 8: "Août",
            9: "Septembre", 10: "Octobre", 11: "Novembre", 12: "Décembre"
        }
        return months.get(month, "Mois")
