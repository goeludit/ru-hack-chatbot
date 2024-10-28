# ru-hack-chatbot (SangOne Chatbot)

## Overview

The SangOne Patch is an innovative biomaterial-based sticker that reacts with HPV biomarkers and hormone metabolites in menstrual blood, causing a visible color change. This tool enables non-invasive monitoring and point-of-care screening for gynecological diseases. To complement this technology, the SangONE Chatbot integrates advanced AI for patient education and appointment management.

## Technical Architecture

### Backend
- **Flask:** Serves as the web framework to handle business logic and API integrations.
- **Gunicorn:** Manages high traffic efficiently as a WSGI HTTP server.

### Frontend
- **Technologies:** Uses CSS, HTML5, and Bootstrap for a responsive and user-friendly interface.

### AI & Machine Learning
- **GPT-3.5:** Powers the conversational AI capabilities of the chatbot.
- **Random Forest Classifier:** Analyzes medical data to identify crucial biomarkers for HPV.

### Cloud Infrastructure
- **AWS EC2:** Hosts the application ensuring scalable and secure computing environments.
- **AWS S3:** Provides secure storage for user documents like PDFs.
- **AWS Redis (Planned):** To enhance data handling and caching for user information and appointments.

## Key Features

- **AI-Powered Chat:** Handles user queries dynamically, supported by GPT-3.5.
- **Appointment Booking:** Simplifies scheduling and managing medical appointments.
- **Document Processing:** Securely uploads, stores, and processes medical documents, facilitating efficient information retrieval.

## Challenges Overcome

- Achieved seamless integration of multiple technologies including Flask, OCR, and AI modules.
- Ensured scalability in document handling and processing across diverse network conditions.
- Developed an intuitive and cohesive user interface.

## Future Enhancements

- Integration with EHR systems.
- Expansion of AI to include predictive analytics.
- Support for multiple languages to serve a diverse demographic.

## Deployment Instructions

```bash
# Clone the Git Repository
git clone https://github.com/goeludit/ru-hack-chatbot

# Navigate to the Project Folder
cd ru-hack-chatbot

# Install Required Dependencies
pip install -r requirements.txt

# Run the Application
python app.py  # OR python3 app.py
```

**Note:** This application requires an OpenAI API secret key for chatbot functionality, which may need renewal over time.


##AWS Deployment

```bash

http://44.210.140.103:8000/

```



