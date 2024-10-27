from flask import Flask, render_template, request, jsonify
import pandas as pd
from datetime import datetime
from chatbot.rag_chatbot import get_chatgpt_response  # Custom response module
import os
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pytesseract
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Needed for session management
app.config["UPLOAD_FOLDER"] = "./uploads"  # Directory to store uploaded PDFs
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)  # Ensure upload folder exists
user_states = {}  # Dictionary to store user states for conversational flow

@app.route("/")
def home():
    return render_template("index.html")

# Chat endpoint for handling both document-based and regular chat
@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json.get("message").strip().lower()
    user_id = request.remote_addr  # Use IP as user identifier (adjust if needed)
    extracted_text = app.config.get("EXTRACTED_TEXT", "")
    
    # Document-related keywords
    document_keywords = ["report", "document", "file", "data", "analysis", "summary", "findings"]
    is_document_query = any(keyword in user_input for keyword in document_keywords)

    # Initialize user state if not present
    if user_id not in user_states:
        user_states[user_id] = {"state": "initial", "doctor": None, "time": None}

    user_state = user_states[user_id]

    # Appointment booking flow
    if user_state["state"] == "initial" and "appointment" in user_input:
        user_state["state"] = "awaiting_doctor"
        return jsonify({"response": "Sure, let's book an appointment. Which doctor would you like to see? We have Dr. Smith and Dr. Lee."})
    
    elif user_state["state"] == "awaiting_doctor":
        if "smith" in user_input:
            user_state["doctor"] = "Dr. Smith"
            user_state["state"] = "awaiting_time"
            return jsonify({"response": "You've chosen Dr. Smith. Please specify a date and time for your appointment."})
        elif "lee" in user_input:
            user_state["doctor"] = "Dr. Lee"
            user_state["state"] = "awaiting_time"
            return jsonify({"response": "You've chosen Dr. Lee. Please specify a date and time for your appointment."})
        else:
            return jsonify({"response": "I'm sorry, I didn't understand. Please choose either Dr. Smith or Dr. Lee."})

    elif user_state["state"] == "awaiting_time":
        user_state["time"] = user_input
        user_state["state"] = "confirming"
        return jsonify({
            "response": f"Great! You've chosen {user_state['doctor']} at {user_input}. Please confirm your appointment by saying 'confirm' or cancel by saying 'cancel'."
        })

    elif user_state["state"] == "confirming":
        if "confirm" in user_input:
            # Save appointment to Excel
            appointment = {
                "Doctor": user_state["doctor"],
                "Time": user_state["time"],
                "Booked At": datetime.now()
            }
            try:
                appointments = pd.read_excel("appointments.xlsx")
            except FileNotFoundError:
                appointments = pd.DataFrame(columns=["Doctor", "Time", "Booked At"])
            appointments = pd.concat([appointments, pd.DataFrame([appointment])], ignore_index=True)
            appointments.to_excel("appointments.xlsx", index=False)

            # Reset user state
            user_states[user_id] = {"state": "initial", "doctor": None, "time": None}
            return jsonify({"response": "Your appointment has been confirmed. Thank you!"})

        elif "cancel" in user_input:
            user_states[user_id] = {"state": "initial", "doctor": None, "time": None}
            return jsonify({"response": "Your appointment has been canceled. Let me know if I can assist you with anything else."})

        else:
            return jsonify({"response": "Please type 'confirm' to finalize the appointment or 'cancel' to cancel it."})

    # Document-specific chat for relevant queries
    elif extracted_text and is_document_query:
        prompt = f"Based on the following document, answer the user's question:\n\n{extracted_text}\n\nUser question: {user_input}"
        #print("GPT Prompt with Document Context:\n", prompt)
        try:
            
            bot_response = get_chatgpt_response(prompt)
            return jsonify({"response": bot_response})
        except Exception as e:
            print(f"Error in document-based response: {e}")
            return jsonify({"response": "I'm sorry, there was an error processing your document-based request."})

    # General chatbot response for non-appointment-related and non-document-specific queries
    else:
        try:
            bot_response = get_chatgpt_response(user_input)
            return jsonify({"response": bot_response})
        except Exception as e:
            print(f"Error in chatbot response: {e}")
            return jsonify({"response": "I'm sorry, there was an error processing your request."})


# Function to extract text from PDF
def extract_text_from_pdf(file_path):
    """Extracts text from a PDF. Uses OCR if the PDF is image-based."""
    extracted_text = ""
    doc = fitz.open(file_path)
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()  # Try to extract text directly
        if text.strip():  # If text is found, add it to extracted_text
            extracted_text += text
        else:
            # If no text is found, convert to image and apply OCR
            images = convert_from_path(file_path, first_page=page_num + 1, last_page=page_num + 1)
            for image in images:
                extracted_text += pytesseract.image_to_string(image)

    doc.close()
    return extracted_text

# Endpoint to handle PDF upload
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "file" not in request.files:
        return jsonify({"message": "No file uploaded."}), 400

    file = request.files["file"]

    if file.filename == "" or not file.filename.lower().endswith(".pdf"):
        return jsonify({"message": "Please upload a valid PDF file."}), 400

    # Save the PDF securely
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(file_path)

    # Extract text from the PDF
    extracted_text = extract_text_from_pdf(file_path)

    # Save extracted text for question-answering
    app.config["EXTRACTED_TEXT"] = extracted_text
    #print("Extracted Text:\n", extracted_text)
    return jsonify({"message": f"File '{filename}' uploaded and processed successfully.", "file_path": file_path}), 200

if __name__ == "__main__":
    app.run(debug=True)
