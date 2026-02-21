from fasthtml.common import *
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from io import BytesIO
import base64

app, rt = fast_app()

def pdf_to_download(pdf_bytes, filename):
    b64 = base64.b64encode(pdf_bytes).decode()
    return A(
        f"⬇ Download {filename}",
        href=f"data:application/pdf;base64,{b64}",
        download=filename,
        cls="button"
    )

@rt('/')
def get():
    return Titled("📄 PDF Toolkit",
        Card(
            H2("Choose Operation:"),
            Div(
                A("Merge PDFs", href="/merge", cls="button"),
                A("Split PDF", href="/split", cls="button"),
                A("Extract Pages", href="/extract", cls="button"),
                A("Rotate Pages", href="/rotate", cls="button"),
                A("Compress PDF", href="/compress", cls="button"),
                style="display: grid; gap: 1rem;"
            )
        )
    )

@rt('/merge')
def get():
    return Titled("Merge PDFs",
        Card(
            Form(
                Label("Upload PDF files to merge:"),
                Input(type="file", name="files", multiple=True, accept=".pdf", required=True),
                Button("Merge PDFs", type="submit"),
                method="post",
                enctype="multipart/form-data"
            )
        ),
        A("← Back to Home", href="/", cls="button secondary")
    )

@rt('/merge')
async def post(files: list[UploadFile]):
    if not files or len(files) == 0:
        return Card(P("No files uploaded"), A("← Try Again", href="/merge", cls="button"))
    
    merger = PdfMerger()
    total_pages = 0
    file_list = []
    
    for file in files:
        content = await file.read()
        pdf_file = BytesIO(content)
        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)
        total_pages += page_count
        file_list.append(f"✓ {file.filename} ({page_count} pages)")
        pdf_file.seek(0)
        merger.append(pdf_file)
    
    output = BytesIO()
    merger.write(output)
    merger.close()
    
    return Titled("Merge Result",
        Card(
            H3("Uploaded Files:"),
            Ul(*[Li(f) for f in file_list]),
            P(Strong(f"✅ Successfully merged {len(files)} PDFs ({total_pages} total pages)")),
            pdf_to_download(output.getvalue(), "merged_document.pdf"),
        ),
        A("← Merge More", href="/merge", cls="button secondary")
    )

@rt('/split')
def get():
    return Titled("Split PDF",
        Card(
            Form(
                Label("Upload PDF file:"),
                Input(type="file", name="file", accept=".pdf", required=True),
                Button("Split into Pages", type="submit"),
                method="post",
                enctype="multipart/form-data"
            )
        ),
        A("← Back to Home", href="/", cls="button secondary")
    )

@rt('/split')
async def post(file: UploadFile):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    
    links = []
    for page_num in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[page_num])
        
        output = BytesIO()
        writer.write(output)
        
        filename = f"page_{page_num + 1:03d}.pdf"
        links.append(Li(pdf_to_download(output.getvalue(), filename)))
    
    return Titled("Split Result",
        Card(
            P(Strong(f"✅ Split into {len(reader.pages)} pages")),
            H3("Download Pages:"),
            Ul(*links)
        ),
        A("← Split Another", href="/split", cls="button secondary")
    )

@rt('/extract')
def get():
    return Titled("Extract Pages",
        Card(
            Form(
                Label("Upload PDF file:"),
                Input(type="file", name="file", accept=".pdf", required=True),
                Div(
                    Label("Start page:", Input(type="number", name="start", value="1", min="1", required=True)),
                    Label("End page:", Input(type="number", name="end", value="5", min="1", required=True)),
                    style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;"
                ),
                Button("Extract Pages", type="submit"),
                method="post",
                enctype="multipart/form-data"
            )
        ),
        A("← Back to Home", href="/", cls="button secondary")
    )

@rt('/extract')
async def post(file: UploadFile, start: int, end: int):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    for page_num in range(start - 1, end):
        if page_num < len(reader.pages):
            writer.add_page(reader.pages[page_num])
    
    output = BytesIO()
    writer.write(output)
    
    pages_extracted = min(end, len(reader.pages)) - start + 1
    
    return Titled("Extract Result",
        Card(
            P(Strong(f"✅ Extracted pages {start}-{end} ({pages_extracted} pages)")),
            pdf_to_download(output.getvalue(), "extracted_pages.pdf")
        ),
        A("← Extract More", href="/extract", cls="button secondary")
    )

@rt('/rotate')
def get():
    return Titled("Rotate Pages",
        Card(
            Form(
                Label("Upload PDF file:"),
                Input(type="file", name="file", accept=".pdf", required=True),
                Label("Rotation angle:",
                    Select(
                        Option("90°", value="90"),
                        Option("180°", value="180"),
                        Option("270°", value="270"),
                        name="angle"
                    )
                ),
                Button("Rotate All Pages", type="submit"),
                method="post",
                enctype="multipart/form-data"
            )
        ),
        A("← Back to Home", href="/", cls="button secondary")
    )

@rt('/rotate')
async def post(file: UploadFile, angle: int):
    content = await file.read()
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    for page in reader.pages:
        page.rotate(angle)
        writer.add_page(page)
    
    output = BytesIO()
    writer.write(output)
    
    return Titled("Rotate Result",
        Card(
            P(Strong(f"✅ Rotated {len(reader.pages)} pages by {angle} degrees")),
            pdf_to_download(output.getvalue(), "rotated_document.pdf")
        ),
        A("← Rotate More", href="/rotate", cls="button secondary")
    )

@rt('/compress')
def get():
    return Titled("Compress PDF",
        Card(
            Form(
                Label("Upload PDF file:"),
                Input(type="file", name="file", accept=".pdf", required=True),
                Button("Compress PDF", type="submit"),
                method="post",
                enctype="multipart/form-data"
            )
        ),
        A("← Back to Home", href="/", cls="button secondary")
    )

@rt('/compress')
async def post(file: UploadFile):
    content = await file.read()
    original_size = len(content)
    
    reader = PdfReader(BytesIO(content))
    writer = PdfWriter()
    
    for page in reader.pages:
        page.compress_content_streams()
        writer.add_page(page)
    
    output = BytesIO()
    writer.write(output)
    
    compressed_size = len(output.getvalue())
    reduction = ((original_size - compressed_size) / original_size) * 100
    
    return Titled("Compress Result",
        Card(
            P(f"Original size: {original_size / 1024 / 1024:.2f} MB"),
            P(f"Compressed size: {compressed_size / 1024 / 1024:.2f} MB"),
            P(Strong(f"✅ Reduced by {reduction:.0f}%")),
            pdf_to_download(output.getvalue(), "compressed_document.pdf")
        ),
        A("← Compress More", href="/compress", cls="button secondary")
    )

serve()