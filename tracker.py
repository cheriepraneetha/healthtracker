import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from fpdf import FPDF
import io
import tempfile

# Function to detect anomalies
def detect_anomalies(data):
    features = ['Steps', 'Heart Rate (bpm)', 'Calories Burned', 'Sleep Duration (hours)']
    
    # Standardize the data
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(data[features])
    
    # Apply Isolation Forest for anomaly detection
    model = IsolationForest(contamination=0.05)
    data['Anomaly'] = model.fit_predict(scaled_data)
    
    # -1 for anomaly, 1 for normal
    anomalies = data[data['Anomaly'] == -1]
    
    return anomalies

# Function to provide recommendations
def provide_recommendations(anomalies):
    recommendations = []
    
    if not anomalies.empty:
        avg_steps = anomalies['Steps'].mean()
        avg_heart_rate = anomalies['Heart Rate (bpm)'].mean()
        avg_calories = anomalies['Calories Burned'].mean()
        avg_sleep = anomalies['Sleep Duration (hours)'].mean()
        
        if avg_steps < 5000:
            recommendations.append("Consider increasing daily steps. Aim for at least 10,000 steps per day.")
        if avg_heart_rate < 60 or avg_heart_rate > 100:
            recommendations.append("Monitor your heart rate. Consult with a healthcare provider if you notice persistent abnormal values.")
        if avg_calories < 1800 or avg_calories > 2500:
            recommendations.append("Ensure you’re consuming an adequate amount of calories based on your activity level.")
        if avg_sleep < 7:
            recommendations.append("Aim for at least 7-9 hours of sleep per night.")
    
    if not recommendations:
        recommendations.append("No significant anomalies detected. Your activity seems normal.")
    
    return recommendations
# Function to visualize data
def plot_data(data):
    st.subheader("Data Visualizations")
    
    # Set up the figure and axes
    fig, ax = plt.subplots(2, 2, figsize=(18, 14))  # Increase figsize for better spacing
    
    # Apply Seaborn style for better aesthetics
    sns.set(style="whitegrid")
    
    # Plot Steps
    sns.lineplot(x='Date', y='Steps', data=data, ax=ax[0, 0], marker='o')
    ax[0, 0].set_title('Daily Steps')
    ax[0, 0].set_xlabel('Date')
    ax[0, 0].set_ylabel('Steps')
    ax[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot Heart Rate
    sns.lineplot(x='Date', y='Heart Rate (bpm)', data=data, ax=ax[0, 1], marker='o')
    ax[0, 1].set_title('Daily Heart Rate (bpm)')
    ax[0, 1].set_xlabel('Date')
    ax[0, 1].set_ylabel('Heart Rate (bpm)')
    ax[0, 1].tick_params(axis='x', rotation=45)
    
    # Plot Calories Burned
    sns.lineplot(x='Date', y='Calories Burned', data=data, ax=ax[1, 0], marker='o')
    ax[1, 0].set_title('Daily Calories Burned')
    ax[1, 0].set_xlabel('Date')
    ax[1, 0].set_ylabel('Calories Burned')
    ax[1, 0].tick_params(axis='x', rotation=45)
    
    # Plot Sleep Duration
    sns.lineplot(x='Date', y='Sleep Duration (hours)', data=data, ax=ax[1, 1], marker='o')
    ax[1, 1].set_title('Daily Sleep Duration (hours)')
    ax[1, 1].set_xlabel('Date')
    ax[1, 1].set_ylabel('Sleep Duration (hours)')
    ax[1, 1].tick_params(axis='x', rotation=45)
    
    # Adjust layout to prevent overlap
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    
    st.pyplot(fig)


# Function to visualize data
def plot_data(data):
    st.subheader("Data Visualizations")
    
    # Set up the figure and axes
    fig, ax = plt.subplots(2, 2, figsize=(18, 14))  # Increase figsize for better spacing
    
    # Apply Seaborn style for better aesthetics
    sns.set(style="whitegrid")
    
    # Plot Steps
    sns.lineplot(x='Date', y='Steps', data=data, ax=ax[0, 0], marker='o')
    ax[0, 0].set_title('Daily Steps')
    ax[0, 0].set_xlabel('Date')
    ax[0, 0].set_ylabel('Steps')
    ax[0, 0].tick_params(axis='x', rotation=45)
    
    # Plot Heart Rate
    sns.lineplot(x='Date', y='Heart Rate (bpm)', data=data, ax=ax[0, 1], marker='o')
    ax[0, 1].set_title('Daily Heart Rate (bpm)')
    ax[0, 1].set_xlabel('Date')
    ax[0, 1].set_ylabel('Heart Rate (bpm)')
    ax[0, 1].tick_params(axis='x', rotation=45)
    
    # Plot Calories Burned
    sns.lineplot(x='Date', y='Calories Burned', data=data, ax=ax[1, 0], marker='o')
    ax[1, 0].set_title('Daily Calories Burned')
    ax[1, 0].set_xlabel('Date')
    ax[1, 0].set_ylabel('Calories Burned')
    ax[1, 0].tick_params(axis='x', rotation=45)
    
    # Plot Sleep Duration
    sns.lineplot(x='Date', y='Sleep Duration (hours)', data=data, ax=ax[1, 1], marker='o')
    ax[1, 1].set_title('Daily Sleep Duration (hours)')
    ax[1, 1].set_xlabel('Date')
    ax[1, 1].set_ylabel('Sleep Duration (hours)')
    ax[1, 1].tick_params(axis='x', rotation=45)
    
    # Adjust layout to prevent overlap
    plt.subplots_adjust(wspace=0.3, hspace=0.3)
    
    # Save the plot to a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
    plt.savefig(temp_file.name, format='png')
    plt.close(fig)
    
    return temp_file.name

# Function to create a PDF report
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Image
from io import BytesIO

def create_pdf_report(name, age, data, anomalies, recommendations, plot_image_path):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title = Paragraph(f"Health Report for {name}, Age: {age}", styles['Title'])
    elements.append(title)
    elements.append(Paragraph('<br/>', styles['Normal']))
    
    # Data Summary
    elements.append(Paragraph("Data Summary:", styles['Heading2']))
    
    # Anomalies
    elements.append(Paragraph("Anomalies Detected:", styles['Heading3']))
    anomaly_data = [
        ["Date", "Steps", "Heart Rate (bpm)", "Calories Burned", "Sleep Duration (hours)"]
    ]
    for _, row in anomalies.iterrows():
        anomaly_data.append([
            row['Date'], row['Steps'], row['Heart Rate (bpm)'], row['Calories Burned'], row['Sleep Duration (hours)']
        ])
    
    anomaly_table = Table(anomaly_data)
    anomaly_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(anomaly_table)
    elements.append(Paragraph('<br/>', styles['Normal']))
    
    # Recommendations
    elements.append(Paragraph("Recommendations:", styles['Heading2']))
    recommendations_list = [f"- {rec}" for rec in recommendations]
    for rec in recommendations_list:
        elements.append(Paragraph(rec, styles['Normal']))
    elements.append(Paragraph('<br/>', styles['Normal']))
    
    # Plot image
    elements.append(Image(plot_image_path, width=400, height=300))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return buffer.read()


# Streamlit app
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
        plot_image_path = plot_data(data)
        
        # Create and display the downloadable report
        pdf_buf = create_pdf_report(name, age, data, anomalies, recommendations, plot_image_path)
        st.download_button(
            label="Download Report",
            data=pdf_buf,
            file_name="health_report.pdf",
            mime="application/pdf"
        )
