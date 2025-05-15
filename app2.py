import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np
from streamlit_option_menu import option_menu
import re
import base64
from fpdf import FPDF
import mysql.connector

# Connect to the MySQL database
try:
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="admin123",
        database="alzheimer"
    )
    print("Database connection successful")
except mysql.connector.Error as err:
    print("Error connecting to database:", err)
    exit(1)

# Get a cursor object to execute SQL queries
mycursor = mydb.cursor()

# Set the background image for the page
def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-position: center;
    background-size: cover;
    color: teal;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)

# Function to get base64 encoding of an image
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Set background
set_background('E:\projects\Projects\workspace\Alzheimers-disease-detection-main\Alzheimers-disease-detection-main\images\\bg3.png')

# Load the saved model
model = tf.keras.models.load_model('E:\projects\Projects\workspace\Alzheimers-disease-detection-main\Alzheimers-disease-detection-main\my_model.h5')

# Define the class labels
class_labels = ['Mild Demented', 'Moderate Demented', 'Non Demented', 'Very Mild Demented']

# Function to preprocess the image
def preprocess_image(image):
    image = image.convert('RGB')
    image = image.resize((176, 176))
    image = np.array(image)
    image = image / 255.0
    image = np.expand_dims(image, axis=0)
    return image

# Validation functions
def validate_phone_number(phone_number):
    pattern = r'^\d{10}$'
    contact = re.match(pattern, str(phone_number))
    if not contact:
        st.error('Please enter a 10 digit number!')
        return False
    return True

def validate_name(name):
    if not all(char.isalpha() or char.isspace() for char in name):
        st.error("Name should not contain numbers or special characters.")
        return False
    return True

def validate_input(name, age, contact, file):
    if not name:
        st.error('Please enter the patient\'s name!')
        return False
    if not age:
        st.error('Please enter your age!')
        return False
    if not contact:
        st.error('Please enter your contact number!')
        return False
    if not file:
        st.error('Please upload the MRI scan!')
        return False
    return True

# Define the Streamlit app's pages and navigation
def home_page():
    st.markdown('<h1 style="color:rgb(19, 190, 148);">AI Brain-Watch</h1>', unsafe_allow_html=True)
    st.markdown('<p style="color:white; font-size: 24px;">Alzheimer disease is the most common type of dementia...</p>', unsafe_allow_html=True)
    #st.write("Alzheimer disease is the most common type of dementia. It is a progressive disease beginning with mild memory loss and possibly leading to loss of the ability to carry on a conversation and respond to the environment. Alzheimer disease involves parts of the brain that control thought, memory, and language.")
    st.write("Using this website, you can find out if your MRI scan shows Alzheimer's disease. It is classified according to four different stages of Alzheimer's disease.")
    st.write('1. Mild Demented')
    st.write("2. Very Mild Demented")
    st.write("3. Moderate Demented")
    st.write("4. Non Demented")

def about_us_page():
    st.title('Welcome!')
    st.write('This web app uses a CNN model to recognize the presence of Alzheimer\'s disease in any age group. Leaving behind the traditional method of MRI Scans, you can now get yourself checked through our portable web app and receive your report within no time.')
    st.write('This web app is a project made by Abhinav K, Pranav S, and Vignesh B')

def alzheimer_detection_page():
    st.title('Alzheimer Detection Web App')
    st.write('Please enter your personal details along with MRI scan.')

    # Create a form for user inputs
    with st.form(key='myform', clear_on_submit=True):
        # Name input
        # Using st.markdown to change the label color of the Name field to black
        st.markdown('<p style="color:black;">Name</p>', unsafe_allow_html=True)
        name = st.text_input('',key='name')  # Empty string as the label, as we handled it above



       # name = st.text_input('Name')
        

        # Age input
        st.markdown('<p style="color:black;">Age</p>', unsafe_allow_html=True)
        age = st.number_input('', min_value=1, max_value=150, value=40)

        # Gender radio button
    # Using st.markdown to change the label color of the Gender radio button to black
        #st.markdown('<p style="color:black;">Gender</p>', unsafe_allow_html=True)
        #gender = st.radio('', ('Male', 'Female', 'Other'))  # Empty string as the label, handled above

        # Change the label color and also the individual radio button options' colors using CSS
        st.markdown("""
        <style>
        .radio-text {
        color: black;
        font-size: 18px;
        font-family: Arial;
    }
        .radio-label {
        font-size: 18px;
        color: black;
        font-family: Arial;
    }
    </style> """, unsafe_allow_html=True)
       

# Apply custom style for the label "Gender"
        st.markdown('<p class="radio-label">Gender</p>', unsafe_allow_html=True)

        st.markdown("""
        <style>
        .radio-text {
        color: black;
        font-size: 18px;
        font-family: Arial;
    }
        .radio-label {
        font-size: 18px;
        color: black;
        font-family: Arial;
    }
    </style> """, unsafe_allow_html=True)








# Then create the radio button with custom styles
        gender = st.radio('', ('Male', 'Female', 'Other'), key="gender")






        #gender = st.radio('Gender', ('Male', 'Female', 'Other'))

        # Contact number input
        contact = st.text_input('Contact Number', value='', key='contact')

        # File uploader for MRI scan
        file = st.file_uploader('Upload an image', type=['jpg', 'jpeg', 'png'])

        # Submit button
        submit = st.form_submit_button("Submit")

        # Insert form data into the database
        def insert_data(name, age, gender, contact, prediction):
            try:
                sql = "INSERT INTO predictions (Patient_Name, Age, Gender, Contact, Prediction) VALUES (%s, %s, %s, %s, %s)"
                val = (name, age, gender, contact, prediction)
                mycursor.execute(sql, val)
                mydb.commit()
                print(mycursor.rowcount, "record inserted")
            except mysql.connector.Error as err:
                print("Error inserting record:", err)

        if submit:
            if file is not None and validate_input(name, age, contact, file) and validate_phone_number(contact) and validate_name(name):
                st.success('Your personal information has been recorded.', icon="✅")
                image = Image.open(file)
                png_image = image.convert('RGBA')
                st.image(image, caption='Uploaded Image', width=200)
                
                # Display entered details
                st.write('Name:', name)
                st.write('Age:', age)
                st.write('Gender:', gender)
                st.write('Contact:', contact)
                
                # Preprocess the image for prediction
                image = preprocess_image(image)
                prediction = model.predict(image)
                prediction = np.argmax(prediction, axis=1)

                # Display the prediction result
                st.success('The predicted class is: ' + class_labels[prediction[0]])

                # Format the result string for the PDF report
                result_str = 'Name: {}\nAge: {}\nGender: {}\nContact: {}\nPrediction for Alzheimer: {}'.format(
                    name, age, gender, contact, class_labels[prediction[0]])

                # Insert data into the database
                insert_data(name, age, gender, contact, class_labels[prediction[0]])

                # Generate and provide the download link for the PDF report
                export_as_pdf = st.button("Export Report")

                def create_download_link(val, filename):
                    b64 = base64.b64encode(val)
                    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{filename}.pdf">Download file</a>'

                if export_as_pdf:
                    pdf = FPDF()
                    pdf.add_page()
                    pdf.set_font('Times', 'B', 24)
                    pdf.cell(200, 20, 'Alzheimer Detection Report', 0, 1, 'C')
                    pdf.set_font('Arial', 'B', 16)
                    pdf.cell(200, 10, 'Patient Details', 0, 1)
                    pdf.set_font('Arial', '', 12)
                    pdf.cell(200, 10, f'Name: {name}', 0, 1)
                    pdf.cell(200, 10, f'Age: {age}', 0, 1)
                    pdf.cell(200, 10, f'Gender: {gender}', 0, 1)
                    pdf.cell(200, 10, f'Contact: {contact}', 0, 1)
                    pdf.ln(10)

                    # Save and add the image to the PDF
                    png_file = "image.png"
                    png_image.save(png_file, "PNG")
                    pdf.cell(200, 10, 'MRI scan:', 0, 1)
                    pdf.image(png_file, x=40, y=80, w=50, h=50)

                    # Add prediction details to the PDF
                    pdf.ln(10)
                    pdf.set_font('Arial', 'B', 16)
                    pdf.cell(200, 10, f'Prediction for Alzheimer: {class_labels[prediction[0]]}', 0, 1)

                    # Create the download link for the PDF
                    html = create_download_link(pdf.output(dest="S").encode("latin-1"), "test")
                    st.markdown(html, unsafe_allow_html=True)

# Define the main page
def app():
    selected = option_menu(
        menu_title=None,  # required
        options=["Home", "Alzheimer Detection", "About Us"],  # required
        icons=["house", "book", "envelope"],  # optional
        menu_icon="cast",  # optional
        default_index=0,  # optional
        orientation="horizontal",
    )

    if selected == "Home":
        home_page()
    elif selected == "Alzheimer Detection":
        alzheimer_detection_page()
    elif selected == "About Us":
        about_us_page()

# Run the app
if __name__ == '__main__':
    app()
