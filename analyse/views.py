import os
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from groq import Groq
from PyPDF2 import PdfReader

groq_api_key = "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"
# Initialize Groq client with the API key
client = Groq(
    api_key=  groq_api_key
)

def index(request):
    """
    Render the main HTML page for the resume analysis.
    """
    return render(request, "index.html")

def extract_text_from_pdf(pdf_file):
    """
    Extract text content from a PDF file.
    """
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception:
        return None

@csrf_exempt
def analyze_resume(request):
    """
    Analyze the uploaded resume using Groq API.
    """
    if request.method == "POST" and request.FILES.get("resume"):
        try:
            # Extract job role and company from request
            job_role = request.POST.get("job_role", "")
            company = request.POST.get("company", "")

            # Read uploaded PDF and extract text
            pdf_file = request.FILES["resume"]
            resume_text = extract_text_from_pdf(pdf_file)
            
            if not resume_text:
                return JsonResponse({"success": False, "error": "Unable to extract text from the uploaded resume."})

            # Prepare Groq request
            prompt = (
                f"Analyze the following resume for the job role '{job_role}' at the company '{company}'. "
                f"Provide a score out of 100, a brief description, and suggestions for improvement.\n\n"
                f"Resume Text:\n{resume_text}"
            )

            chat_completion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an AI resume analysis assistant."},
                    {"role": "user", "content": prompt},
                ],
                model="llama-3.3-70b-versatile",
            )

            response_text = chat_completion.choices[0].message.content

            # Simulate parsed Groq response (if Groq response is structured, adjust accordingly)
            # Example: Parse response_text into score, description, and suggestions
            return JsonResponse(
                {
                    "success": True,
                    "data": response_text
                }
            )
        except Exception:
            return JsonResponse({"success": False, "error": "An error occurred during analysis."})

    return JsonResponse({"success": False, "error": "Invalid request"})
