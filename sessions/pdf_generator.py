"""PDF generation for exam results using ReportLab"""
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.platypus import Image as RLImage
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from .models import ExamSession


def generate_exam_result_pdf(session: ExamSession) -> BytesIO:
    """
    Generate a PDF report for an exam session result.
    
    Args:
        session: ExamSession instance
        
    Returns:
        BytesIO: PDF file buffer
    """
    buffer = BytesIO()
    
    # Create the PDF document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1e40af'),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = styles['Normal']
    
    # Header
    elements.append(Paragraph("EXAM RESULT CERTIFICATE", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student and Exam Information
    info_data = [
        ['Student Name:', session.student.username],
        ['Student Email:', session.student.email or 'N/A'],
        ['Exam Title:', session.exam.title],
        ['Exam Date:', session.started_at.strftime('%B %d, %Y at %I:%M %p')],
        ['Duration:', f"{session.exam.duration_minutes} minutes"],
        ['Status:', session.status],
    ]
    
    info_table = Table(info_data, colWidths=[2*inch, 4*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e5e7eb')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f2937')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#d1d5db')),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Score Summary
    elements.append(Paragraph("Score Summary", heading_style))
    
    total_questions = session.exam.questions.count()
    answered_questions = session.answers.count()
    total_possible_marks = sum(q.marks for q in session.exam.questions.all())
    percentage = (session.total_marks / total_possible_marks * 100) if total_possible_marks > 0 else 0
    
    # Determine grade
    if percentage >= 90:
        grade = 'A+'
        grade_color = colors.HexColor('#059669')
    elif percentage >= 80:
        grade = 'A'
        grade_color = colors.HexColor('#10b981')
    elif percentage >= 70:
        grade = 'B'
        grade_color = colors.HexColor('#3b82f6')
    elif percentage >= 60:
        grade = 'C'
        grade_color = colors.HexColor('#f59e0b')
    elif percentage >= 50:
        grade = 'D'
        grade_color = colors.HexColor('#f97316')
    else:
        grade = 'F'
        grade_color = colors.HexColor('#ef4444')
    
    score_data = [
        ['Total Questions:', str(total_questions)],
        ['Questions Answered:', str(answered_questions)],
        ['Total Marks Obtained:', f"{session.total_marks:.2f}"],
        ['Total Possible Marks:', f"{total_possible_marks:.2f}"],
        ['Percentage:', f"{percentage:.2f}%"],
        ['Grade:', grade],
    ]
    
    score_table = Table(score_data, colWidths=[2.5*inch, 3.5*inch])
    score_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1e40af')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
        ('BACKGROUND', (1, 5), (1, 5), grade_color),
        ('TEXTCOLOR', (1, 5), (1, 5), colors.white),
    ]))
    
    elements.append(score_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Violation Information
    if session.violation_count > 0:
        elements.append(Paragraph("Violation Report", heading_style))
        
        violation_data = [
            ['Total Violations:', str(session.violation_count)],
            ['Violation Limit:', str(session.exam.violation_limit)],
            ['Status:', 'Terminated' if session.status == 'TERMINATED' else 'Completed'],
        ]
        
        violation_table = Table(violation_data, colWidths=[2.5*inch, 3.5*inch])
        violation_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#fee2e2')),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#991b1b')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#fca5a5')),
        ]))
        
        elements.append(violation_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Questions and Answers
    elements.append(Paragraph("Question-wise Analysis", heading_style))
    elements.append(Spacer(1, 0.1*inch))
    
    answers = session.answers.select_related('question').all()
    
    for idx, answer in enumerate(answers, 1):
        question = answer.question
        
        # Question header
        q_text = f"Q{idx}. {question.text}"
        elements.append(Paragraph(q_text, ParagraphStyle(
            'Question',
            parent=normal_style,
            fontSize=11,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )))
        
        # Answer details
        answer_details = []
        
        if question.type == 'MCQ':
            answer_details.append(['Your Answer:', question.choices[answer.mcq_choice] if answer.mcq_choice is not None else 'Not Answered'])
            if question.correct_answer is not None:
                answer_details.append(['Correct Answer:', question.choices[int(question.correct_answer)]])
        else:
            answer_details.append(['Your Answer:', answer.short_text or 'Not Answered'])
        
        answer_details.append(['Marks Awarded:', f"{answer.marks_awarded}/{question.marks}"])
        
        # Color code based on correctness
        bg_color = colors.HexColor('#d1fae5') if answer.marks_awarded == question.marks else colors.HexColor('#fee2e2')
        
        answer_table = Table(answer_details, colWidths=[1.5*inch, 4.5*inch])
        answer_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ]))
        
        elements.append(answer_table)
        elements.append(Spacer(1, 0.15*inch))
    
    # Footer
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph(
        f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        ParagraphStyle(
            'Footer',
            parent=normal_style,
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
    ))
    
    elements.append(Paragraph(
        "This is a computer-generated document. No signature is required.",
        ParagraphStyle(
            'Footer2',
            parent=normal_style,
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=0
        )
    ))
    
    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    return buffer
