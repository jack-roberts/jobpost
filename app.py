from flask import Flask, request, render_template_string
from PIL import Image, ImageDraw, ImageFont
import io
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import os

app = Flask(__name__)

# Email settings
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')  # Environment variable for your email
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Environment variable for the app password

@app.route('/')
def index():
    return '''
        <form method="POST" action="/generate" enctype="multipart/form-data">
            Your Email: <input type="email" name="user_email" required><br><br>
            
            Job Type: <input type="radio" name="job_type" value="Permanent" required> Permanent
                      <input type="radio" name="job_type" value="Temporary" required> Temporary<br><br>

            Job Title: <input type="text" name="job_title" required><br><br>
            Job Location: <input type="text" name="job_location" required><br><br>
            Job Salary: <input type="text" name="job_salary" required><br><br>
            
            Published Client (Optional): <input type="text" name="published_client"><br><br>
            
            <input type="submit" value="Request Job Post Image">
        </form>
    '''

@app.route('/generate', methods=['POST'])
def generate_image():
    # Get the form data
    user_email = request.form['user_email']
    job_type = request.form['job_type']
    job_title = request.form['job_title']
    job_location = request.form['job_location']
    job_salary = request.form['job_salary']
    published_client = request.form.get('published_client', '')  # Optional field

    # If Published Client is provided, ask the user for the company URL
    if published_client:
        return render_template_string('''
            <p>Please provide the URL for {{ published_client }}:</p>
            <form method="POST" action="/confirm_url">
                <label>Company URL:</label>
                <input type="text" name="company_url" required><br><br>
                <input type="hidden" name="user_email" value="{{ user_email }}">
                <input type="hidden" name="job_type" value="{{ job_type }}">
                <input type="hidden" name="job_title" value="{{ job_title }}">
                <input type="hidden" name="job_location" value="{{ job_location }}">
                <input type="hidden" name="job_salary" value="{{ job_salary }}">
                <input type="hidden" name="published_client" value="{{ published_client }}">
                <input type="submit" value="Submit">
            </form>
        ''', published_client=published_client, user_email=user_email, job_type=job_type, job_title=job_title, job_location=job_location, job_salary=job_salary)

    # If no Published Client is provided, proceed with the regular image generation
    return create_and_send_image(user_email, job_type, job_title, job_location, job_salary)

@app.route('/confirm_url', methods=['POST'])
def confirm_url():
    # Get the submitted data
    company_url = request.form['company_url']
    user_email = request.form['user_email']
    job_type = request.form['job_type']
    job_title = request.form['job_title']
    job_location = request.form['job_location']
    job_salary = request.form['job_salary']
    published_client = request.form['published_client']

    # Send the email to the marketing team with all the fields and company URL
    send_email_to_marketing(user_email, job_type, job_title, job_location, job_salary, published_client, company_url)

    # Display the confirmation message to the user
    return '''
        <p>Thanks for submitting your post. As this is a client post, it has been sent to the marketing team. They will send you your post back soon.</p>
    '''

def send_email_to_marketing(user_email, job_type, job_title, job_location, job_salary, published_client, company_url):
    # Create email message for marketing team
    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_USERNAME
    msg['To'] = 'jack.roberts@jacksonhogg.com'
    msg['Subject'] = f'Client Post Request: {published_client}'

    # Create the body with job details and company URL
    body = MIMEMultipart('alternative')
    html_content = f"""
    <html>
    <body>
        <p>A new client post request has been submitted with the following details:</p>
        <ul>
            <li><strong>Your Email:</strong> {user_email}</li>
            <li><strong>Job Type:</strong> {job_type}</li>
            <li><strong>Job Title:</strong> {job_title}</li>
            <li><strong>Location:</strong> {job_location}</li>
            <li><strong>Salary:</strong> {job_salary}</li>
            <li><strong>Published Client:</strong> {published_client}</li>
            <li><strong>Company URL:</strong> <a href="{company_url}">{company_url}</a></li>
        </ul>
        <p>The job post image will need to be reviewed and sent back to the user.</p>
    </body>
    </html>
    """
    html_part = MIMEText(html_content, 'html')
    body.attach(html_part)

    # Attach the body to the main message
    msg.attach(body)

    # Send the email to the marketing team
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)  # Login to the SMTP server
        server.send_message(msg)

def create_and_send_image(user_email, job_type, job_title, job_location, job_salary):
    # Load the base image
    img = Image.open("input_image.png")  # Replace with your default image
    img = img.resize((1080, 1080))  # Resize to 1080x1080px
    
    draw = ImageDraw.Draw(img)

    # Load a font
    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"  # Path to a font file
    font = ImageFont.truetype(font_path, 40)

    # Text to insert
    job_title_text = f"Job Title: {job_title}"
    job_location_text = f"Location: {job_location}"
    job_salary_text = f"Salary: {job_salary}"

    # Define where to place the text on the image
    draw.text((50, 100), job_title_text, font=font, fill="black")
    draw.text((50, 200), job_location_text, font=font, fill="black")
    draw.text((50, 300), job_salary_text, font=font, fill="black")

    # Save the image to memory
    img_io = io.BytesIO()
    img.save(img_io, 'JPEG', dpi=(300, 300))
    img_io.seek(0)

    # Send the image to the user
    send_email_to_user(user_email, img_io, job_title)

    return f'Job post image generated and sent to {user_email}.'

def send_email_to_user(to_email, image_data, job_title):
    # Create email message
    msg = MIMEMultipart('related')
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to_email
    msg['Subject'] = f'LinkedIn Post: {job_title}'

    # Create the body with the text and an embedded image
    body = MIMEMultipart('alternative')
    
    # Plain text version
    text_part = MIMEText(f'Thank you for submitting your post for {job_title}. Your post image is attached.', 'plain')
    
    # HTML version
    html_content = f"""
    <html>
    <body>
        <p>Thank you for submitting your post for the job: <strong>{job_title}</strong>.</p>
        <p>Your post image is attached.</p>
    </body>
    </html>
    """
    html_part = MIMEText(html_content, 'html')

    # Attach plain text and HTML parts to the email
    body.attach(text_part)
    body.attach(html_part)
    
    # Attach the body to the main message
    msg.attach(body)

    # Attach the image as a file
    img_part = MIMEBase('application', 'octet-stream')
    img_part.set_payload(image_data.read())
    encoders.encode_base64(img_part)
    img_part.add_header('Content-Disposition', 'attachment', filename='job_post_image.jpg')
    msg.attach(img_part)

    # Send email via SMTP
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)  # Login to the SMTP server
        server.send_message(msg)

if __name__ == '__main__':
    app.run(debug=True)

   