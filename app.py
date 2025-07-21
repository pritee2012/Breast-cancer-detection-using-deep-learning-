
import streamlit as st
from PIL import Image, ImageEnhance, ImageChops, ImageDraw
import numpy as np
from tensorflow.keras.models import load_model
import pyttsx3
import time
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
import random 
from datetime import date
import db  # Import the db.py file

# Load the trained model
model = load_model('breast_cancer_model.h5')

# Create a dictionary to store user details
user_details = {
    'Name': '',
    'surname': '',
    'Age': 0,
    'Gender': '',
    'Address': '',
    'Mobile Number': '',
    'Date of consultant ': '',
    'Referring Physician': '',
}

# Set the page configuration
st.set_page_config(
    page_title="Breast Cancer Detection",
    page_icon="⚕️",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Color palette
primary_color = "#E63946"
secondary_color = "#F1FAEE"
text_color = "#1D3557"
background_color = "#A8DADC"


# Logo image
#logo_image = Image.open("new.jpg")

# Styling the sidebar and background color
st.markdown(
    f"""
    <style>
        body {{
            background-color: {background_color};
        }}
        .sidebar .sidebar-content {{
            background-color: {primary_color};
            color: {secondary_color};
        }}
        .css-17eq0hr {{
            background-color: {background_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Display the logo image
#st.image(logo_image, use_column_width=False, width=150)

# first alert
# Page title
st.title("𝔹𝕣𝕖𝕒𝕤𝕥 ℂ𝕒𝕟𝕔𝕖𝕣 𝔻𝕖𝕥𝕖𝕔𝕥𝕚𝕠𝕟")

# Collect user details
st.sidebar.subheader("Patient Information")


# Patient Name (Compulsory)
user_details['Name'] = st.sidebar.text_input("Patient Name:")
user_details['surname'] = st.sidebar.text_input("Surname:")

if not user_details['Name'] and not user_details['surname']:
    st.warning("Please enter the patient's name.")
    st.stop()

# Patient Age (Compulsory)
user_details['Age'] = st.sidebar.number_input("Patient Age:", max_value=120)
if user_details['Age'] == 0:
    st.warning("Please enter a valid age.")
    st.stop()

# Patient Gender (Compulsory)
user_details['Gender'] = st.sidebar.radio("Patient Gender:", ['Female', 'Male'])
if not user_details['Gender']:
    st.warning("Please select the patient's gender.")
    st.stop()

user_details['Address'] = st.sidebar.text_input("Address:")
user_details['Mobile Number'] = st.sidebar.text_input("Mobile Number:")
user_details['Date of consultant'] = st.sidebar.date_input("Date of consultant:")
user_details['Referring Physician'] = st.sidebar.text_input("Referring Physician:")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

# After collecting sidebar inputs
submit = st.sidebar.button("Submit Patient Info")  # 🔥 Add this line

if submit:
    db.insert_patient(user_details)  # 🔄 Save to DB
    st.success("✅ Patient added successfully!")
    


def calculate_tumor_size(probability):
    # Placeholder function for tumor size calculation
    # Replace this with your actual calculation logic
    # For now, generate a random tumor size for demonstration
    if probability >= 0.5:
        tumor_size = random.uniform(0.5, 5.0)
        return "Malignant", tumor_size
    else:
        return "Benign", 0.0


if uploaded_file is not None:
    # Display the selected image
    image = Image.open(uploaded_file)
    
    # Ensure the image is in RGB format
    image = image.convert('RGB')  # Convert to RGB to ensure 3 channels

    # Preprocess the image for prediction
    img_array = np.array(image.resize((64, 64)))
    img_array = np.expand_dims(img_array, axis=0)  # Shape becomes (1, 64, 64, 3)
    img_array = img_array.astype('float32') / 255.0



    def is_colorful_image(img):
        color_enhancer = ImageEnhance.Color(img)
        color_enhanced = color_enhancer.enhance(1.0)
        difference = ImageChops.difference(img, color_enhanced)
        return difference.getbbox() is not None


    def is_valid_breast_image(img):
        return not is_colorful_image(img)


    img = Image.fromarray(img_array[0].astype('uint8'))  # Convert array back to Image object

    width, height = img.size
    width, height = image.size
    aspect_ratio = width / height

    if is_valid_breast_image(image):
        start_time = time.time()
        pred = model.predict(img_array)
        end_time = time.time()
        elapsed_time = end_time - start_time
        threshold = 0.5
        class_label = "No Cancer" if pred[0][0] >= threshold else "Cancer"

        # Display the modified image
        st.image(image, caption='Detected Image.', use_column_width=True)

        # Download report option
        if st.button("Check", key="generate_report_button", use_container_width=True):
            # Generate PDF report
            pdf_filename = f"{user_details['Name']}_{user_details['surname']}_breast_cancer_report.pdf"
            pdf_canvas = canvas.Canvas(BytesIO())

            # Add patient information to the PDF
            pdf_canvas.setFont("Helvetica-Bold", 16)
            pdf_canvas.drawString(30, 750,
"------------------------------------PATIENT REPORT-----------------------------")
            pdf_canvas.setFont("Helvetica", 12)
            pdf_canvas.drawString(30, 730, f"Patient Name: {user_details['Name']} {user_details['surname']}")
            pdf_canvas.drawString(30, 710, f"Age: {user_details['Age']}")
            pdf_canvas.drawString(30, 690, f"Gender: {user_details['Gender']}")
            pdf_canvas.drawString(30, 650, f"Mobile Number: {user_details['Mobile Number']}")
            pdf_canvas.drawString(30, 630, f"Date of consultant: {user_details['Date of consultant']}")
            pdf_canvas.drawString(30, 610, f"Referring Physician: {user_details['Referring Physician']}")

            # Add prediction details to the PDF

            pdf_canvas.drawString(30, 510, "Diagnostic Details:")
            pdf_canvas.drawString(30, 470, f"Prediction Probability: {pred[0][0]:.2f}")

            # Add tumor label and size to the PDF
            tumor_label, tumor_size = calculate_tumor_size(1 - pred[0][0])
            pdf_canvas.drawString(30, 450, f"Tumor Label: {tumor_label}")
            pdf_canvas.drawString(30, 430, f"Tumor Size: {tumor_size:.2f} cm")

            # Add risk probability to the PDF
            pdf_canvas.drawString(30, 490, f"Risk Probability: {100 * (1 - pred[0][0]):.2f}%")

            # Generate histogram for the input image
            histogram_data = np.array(image.convert('L')).ravel()
            hist, bins = np.histogram(histogram_data, bins=256, range=[0, 256])

            # Plot histogram
            hist_filename = f"{user_details['Name']}_{user_details['surname']}_histogram.png"
            plt.figure(figsize=(6, 4))
            plt.bar(bins[:-1], hist, width=0.1, color='skyblue', edgecolor='red')
            plt.title('Histogram')
            plt.xlabel('Pixel Value')
            plt.ylabel('Frequency')
            plt.savefig(hist_filename)
            plt.close()

            hist_pdf = Image.open(hist_filename)
            pdf_canvas.drawInlineImage(hist_pdf, 10, 20)  # Adjust position here

            # Save the PDF
            pdf_canvas.save()

            # Offer the PDF for download
            st.download_button(
                label="Download Report",
                data=BytesIO(pdf_canvas.getpdfdata()),
                file_name=pdf_filename,
                key="report_button", use_container_width=True
            )

            # Read the result using text-to-speech
            engine = pyttsx3.init()
            try:
                engine.say(
                    f"Breast cancer detected for {user_details['Name']} {user_details['surname']}." if class_label == "Cancer"
                    else f"No breast cancer detected for {user_details['Name']} {user_details['surname']}.")
                st.subheader(f"Result: {class_label}")
                st.text(f"Required Prediction Time: {elapsed_time:.2f} seconds")
                engine.runAndWait()
            finally:
                engine.stop()  # Stop the engine to avoid the "run loop already started" error

    else:
        st.error("Invalid image selected. Please choose a valid breast image.")




