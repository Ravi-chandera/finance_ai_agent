from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from finance_agent import anlyse_user_question
import os
import uuid
from datetime import datetime
import asyncio
import markdown  # <-- Add this import

app = FastAPI()
templates = Jinja2Templates(directory="templates_dir")

# Store for tracking processing status
processing_status = {}

async def func1(text: str) -> str:
    return await anlyse_user_question(text)

def generate_pdf(processed_text: str, filename: str):
    """Generate PDF from processed text"""
    doc = SimpleDocTemplate(filename, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    content_style = ParagraphStyle(
        'CustomContent',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=12,
        leftIndent=20,
        rightIndent=20
    )
    
    # Build PDF content
    story = []
    
    # Title
    title = Paragraph("Analysis Report", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Timestamp
    timestamp = Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal'])
    story.append(timestamp)
    story.append(Spacer(1, 20))
    
    # Processed content
    # content_title = Paragraph("Processed Content:", styles['Heading2'])
    # story.append(content_title)
    # story.append(Spacer(1, 12))
    
    # Split text into paragraphs and add to PDF
    paragraphs = processed_text.split('\n')
    for para in paragraphs:
        if para.strip():
            # Convert markdown to HTML
            html_para = markdown.markdown(para.strip())
            # Remove <p> tags added by markdown for compatibility with ReportLab
            if html_para.startswith('<p>') and html_para.endswith('</p>'):
                html_para = html_para[3:-4]
            p = Paragraph(html_para, content_style)
            story.append(p)
            story.append(Spacer(1, 6))
    
    # Build PDF
    doc.build(story)

async def process_text_async(text: str, task_id: str):
    """Process text asynchronously and generate PDF"""
    try:
        # Update status to processing
        processing_status[task_id] = {"status": "processing", "filename": None}
        
        # Process the text
        processed_text = await func1(text)
        
        # Generate unique filename
        filename = f"reports/report_{task_id}.pdf"
        
        # Ensure reports directory exists
        os.makedirs("reports", exist_ok=True)
        
        # Generate PDF
        generate_pdf(processed_text, filename)
        
        # Update status to completed
        processing_status[task_id] = {"status": "completed", "filename": filename}
        
    except Exception as e:
        processing_status[task_id] = {"status": "error", "error": str(e)}

@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "task_id": None})

@app.post("/", response_class=HTMLResponse)
async def post_form(request: Request, background_tasks: BackgroundTasks, text: str = Form(...)):
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Process the text synchronously to get markdown (for preview)
    processed_markdown = await func1(text)
    
    # Start background processing for PDF
    background_tasks.add_task(process_text_async, text, task_id)
    
    # Return template with task ID and processed markdown
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "task_id": task_id,
            "processed_markdown": processed_markdown
        }
    )

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    """Check processing status"""
    if task_id in processing_status:
        return processing_status[task_id]
    else:
        return {"status": "not_found"}

@app.get("/download/{task_id}")
async def download_pdf(task_id: str):
    """Download the generated PDF"""
    if task_id in processing_status and processing_status[task_id]["status"] == "completed":
        filename = processing_status[task_id]["filename"]
        if os.path.exists(filename):
            return FileResponse(
                filename, 
                filename=f"report_{task_id}.pdf",
                media_type="application/pdf"
            )
    
    return {"error": "File not found"}

# Cleanup function (optional - run periodically to clean old files)
def cleanup_old_files():
    """Clean up old PDF files and status entries"""
    # Implementation for cleaning up old files
    pass