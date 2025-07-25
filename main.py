import re
import pdfplumber
import os
from dotenv import load_dotenv
from google import genai
import argparse

# Load .env for secure API key handling
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Gemini
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client()

# Define CLI arguments
parser = argparse.ArgumentParser(description="Crossword Solver using Gemini AI")
parser.add_argument(
    "--pdf",
    type=str,
    default="cw2.pdf",
    help="Path to the PDF file containing crossword clues (default: cw1.pdf)",
)
args = parser.parse_args()

# PDF file path
pdf_path = args.pdf


# Extract clues from PDF
def extract_clues(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() + "\n"

    lines = text.splitlines()
    clues = []
    cluesStart = False

    for i, line in enumerate(lines):
        line = line.strip()
        if line.lower().startswith("across"):
            cluesStart = True
        if cluesStart and line and line[0].isdigit():
            if line.count(".") > 2:
                clues.extend(re.findall(r"[^?]+[?]?", line))
            else:
                splits = line.split(".")

                if len(splits) > 2:
                    secondNumber = ""
                    while splits[1][-1].isdigit():
                        secondNumber = splits[1][-1] + secondNumber
                        splits[1] = splits[1][:-1].strip()

                    clues.append(splits[0].strip() + ". " + splits[1].strip())
                    clues.append(secondNumber + ". " + splits[2].strip())
                else:
                    clues.append(
                        splits[0].strip() + ". " + splits[1].split("?")[0] + "?"
                    )

    return clues


# Get answer from Gemini
def get_answer_from_gemini(clues):
    prompt = f"Answer this crossword clues list(only one word answers): {clues}\n\nPrint nothing else as output but the solutions line by line in the format of the question -> answer. Please give answers without any other decorations like bold, italics, etc."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        return response.text.strip()
    except Exception as e:
        return f"Error: {e}"


# Solve and display the crossword
def solve_crossword():
    clues = extract_clues(pdf_path)
    answer = get_answer_from_gemini(str(clues))

    print(answer)

    with open("crossword.md", "w", encoding="utf-8") as f:
        for line in answer.splitlines():
            f.write(line + "\n")


# Run it
solve_crossword()
