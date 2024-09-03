import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
import matplotlib.pyplot as plt

def detect_anomalies(data):
    # Anomaly detection logic (simple thresholding for demonstration)
    anomalies = data[
        (data['Heart Rate (bpm)'] > 100) | 
        (data['Steps'] < 1000) |
        (data['Sleep Duration (hours)'] < 5)
    ]
    return anomalies

def provide_recommendations(anomalies):
    # Simple recommendation generation based on anomalies
    recommendations = []
    if not anomalies.empty:
        if (anomalies['Heart Rate (bpm)'] > 100).any():
            recommendations.append("Consider consulting a doctor about high heart rate readings.")
        if (anomalies['Steps'] < 1000).any():
            recommendations.append("Increase daily steps to at least 1000 for better health.")
        if (anomalies['Sleep Duration (hours)'] < 5).any():
            recommendations.append("Ensure to get at least 5-7 hours of sleep daily.")
    else:
        recommendations.append("No anomalies detected. Keep up the good work!")
    return recommendations

def plot_data(data):
    # Create plots
    plt.figure(figsize=(10, 6))
    plt.subplot(2, 2, 1)
    plt.plot(data['Date'], data['Steps'], marker='o')
    plt.title('Steps Over Time')
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 2)
    plt.plot(data['Date'], data['Heart Rate (bpm)'], marker='o', color='red')
    plt.title('Heart Rate Over Time')
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 3)
    plt.plot(data['Date'], data['Calories Burned'], marker='o', color='green')
    plt.title('Calories Burned Over Time')
    plt.xticks(rotation=45)

    plt.subplot(2, 2, 4)
    plt.plot(data['Date'], data['Sleep Duration (hours)'], marker='o', color='purple')
    plt.title('Sleep Duration Over Time')
    plt.xticks(rotation=45)

    plt.tight_layout()
    
    # Save plot to a file-like object
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf

def create_pdf_report(name, age, data, anomalies, recommendations, plot_image_buf):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph(f"Health Report for {name}, Age: {age}", styles['Title'])
    elements.append(title)

    # Data Summary
    elements.append(Paragraph("Data Summary:", styles['Heading2']))

    # Anomalies
    elements.append(Paragraph("Anomalies Detected:", styles['Heading3']))
    anomaly_data = [["Date", "Steps", "Heart Rate (bpm)", "Calories Burned", "Sleep Duration (hours)"]]
    for _, row in anomalies.iterrows():
        anomaly_data.append([row['Date'], row['Steps'], row['Heart Rate (bpm)'], row['Calories Burned'], row['Sleep Duration (hours)']])
    
    anomaly_table = Table(anomaly_data)
    anomaly_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(anomaly_table)

    # Recommendations
    elements.append(Paragraph("Recommendations:", styles['Heading2']))
    for rec in recommendations:
        elements.append(Paragraph(f"- {rec}", styles['Normal']))

    # Add plot image
    elements.append(Image(plot_image_buf))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()

# Streamlit App
st.title('Smartwatch Health Tracker')

# Input fields for user details
name = st.text_input("Enter your name:")
age = st.number_input("Enter your age:", min_value=0, max_value=120, value=30)

st.write(f"Hello, {name}! You are {age} years old.")

st.write("Upload your CSV file containing smartwatch activity data.")

# File uploader
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    # Read the CSV file
    data = pd.read_csv(uploaded_file)

    # Display the first few rows of the dataset
    st.write("Data Preview:")
    st.write(data.head())

    # Check for necessary columns
    required_columns = ['Date', 'Steps', 'Heart Rate (bpm)', 'Calories Burned', 'Sleep Duration (hours)']
    if not all(col in data.columns for col in required_columns):
        st.error("CSV file must contain the following columns: 'Date', 'Steps', 'Heart Rate (bpm)', 'Calories Burned', 'Sleep Duration (hours)'.")
    else:
        # Detect anomalies
        anomalies = detect_anomalies(data)

        st.write("Anomalies Detected:")
        st.write(anomalies)

        # Provide recommendations
        recommendations = provide_recommendations(anomalies)
        st.write("Recommendations:")
        for rec in recommendations:
            st.write(f"- {rec}")

        # Visualize the data
        plot_image_buf = plot_data(data)

        # Create and display the downloadable report
        pdf_buf = create_pdf_report(name, age, data, anomalies, recommendations, plot_image_buf)
        st.download_button(
            label="Download Report",
            data=pdf_buf,
            file_name="health_report.pdf",
            mime="application/pdf"
        )
