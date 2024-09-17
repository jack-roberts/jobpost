import os
from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
from dotenv import load_dotenv
import msal
from PIL import Image, ImageDraw, ImageFont
import smtplib
from email.message import EmailMessage
import io
import imaplib
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your_flask_secret_key')
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

# Azure AD configuration
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID')
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
REDIRECT_PATH = "/getAToken"
SCOPE = ["User.Read"]

# Email configuration
EMAIL_USERNAME = os.getenv('EMAIL_USERNAME')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
MARKETING_EMAIL = os.getenv('MARKETING_EMAIL')

# IMAP configuration
IMAP_SERVER = "outlook.office365.com"
IMAP_PORT = 993

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

def build_msal_app(cache=None, authority=None):
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=authority or AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache)

def build_auth_url():
    return build_msal_app().get_authorization_request_url(
        SCOPE, redirect_uri=url_for('authorized', _external=True))

@app.route('/')
def index():
    if not session.get('user'):
        return redirect(url_for('login'))
    return redirect(url_for('form'))

@app.route('/login')
def login():
    auth_url = build_auth_url()
    return redirect(auth_url)

@app.route('/getAToken')
def authorized():
    if request.args.get('error'):
        return f"Login error: {request.args['error']}"
    if 'code' in request.args:
        result = build_msal_app().acquire_token_by_authorization_code(
            request.args['code'],
            scopes=SCOPE,
            redirect_uri=url_for('authorized', _external=True))
        if "error" in result:
            return f"Token acquisition error: {result['error']}"
        session['user'] = result.get('id_token_claims')
        email_address = session['user'].get('preferred_username', '')
        if not email_address.endswith('@jacksonhogg.com'):
            session.clear()
            return "Access denied: Unauthorized email domain."
    return redirect(url_for('form'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect('https://login.microsoftonline.com/common/oauth2/v2.0/logout' +
                    f'?post_logout_redirect_uri={url_for("index", _external=True)}')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if not session.get('user'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        wants_branded_ad = request.form.get('wants_branded_ad') == 'yes'
        if wants_branded_ad:
            selected_template = request.form.get('template_selection')
            if selected_template == 'New Brand':
                # Send details to marketing team
                send_email_to_marketing(request.form.to_dict())
                return "Your request for a new branded ad has been submitted. The marketing team has been informed and will design a new branded ad for you."
            else:
                # Use selected template to generate image
                template_path = os.path.join('static', 'BrandedAds', selected_template + '.jpg')
                image = generate_image_with_template(request.form.to_dict(), template_path)
                send_email(request.form.get('email'), request.form.get('job_title'), image, request.form.to_dict())
                return "Email with your branded ad has been sent successfully!"
        else:
            # Regular image generation
            image = generate_image(request.form.to_dict())
            send_email(request.form.get('email'), request.form.get('job_title'), image, request.form.to_dict())
            return "Email sent successfully!"

    # Pre-fill data if available
    data = request.args.to_dict()
    email_address = session['user'].get('preferred_username', '')
    data.setdefault('email', email_address)
    
    # Get list of templates with display names
    templates = sorted([
        {
            'filename': f[:-4],
            'display_name': f[:-4].replace("_", " ")
        }
        for f in os.listdir(os.path.join('static', 'BrandedAds')) if f.endswith('.jpg')
    ], key=lambda x: x['display_name'])
    
    return render_template('index.html', data=data, templates=templates)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    wants_branded_ad = data.get('wants_branded_ad', False)
    if wants_branded_ad:
        selected_template = data.get('template_selection')
        if selected_template == 'New Brand':
            # Send details to marketing team
            send_email_to_marketing(data)
            return 'New brand request submitted', 200
        else:
            # Use selected template to generate image
            template_path = os.path.join('static', 'BrandedAds', selected_template + '.jpg')
            image = generate_image_with_template(data, template_path)
            send_email(data.get('email'), data.get('job_title'), image, data)
            return 'Branded ad email sent', 200
    else:
        # Regular image generation
        image = generate_image(data)
        send_email(data.get('email'), data.get('job_title'), image, data)
        return 'Email sent successfully', 200

def generate_image(data):
    # Create a blank image
    img = Image.new('RGB', (1080, 1080), color='white')
    draw = ImageDraw.Draw(img)

    # Load font
    font_path = os.path.join('static', 'fonts', 'PTSans-Regular.ttf')
    font_size = 100  # Starting font size
    font = ImageFont.truetype(font_path, font_size)

    # Define text and bounding box
    text = f"{data.get('job_title', '')}\n{data.get('job_location', '')}\n{data.get('job_salary', '')}"
    max_width = 1000
    max_height = 1000

    # Adjust font size to fit within bounding box
    while True:
        w, h = draw.multiline_textsize(text, font=font)
        if w <= max_width and h <= max_height:
            break
        font_size -= 1
        if font_size < 10:
            break  # Prevent font size from becoming too small
        font = ImageFont.truetype(font_path, font_size)

    # Calculate position
    x = (1080 - w) / 2
    y = (1080 - h) / 2

    # Draw text
    draw.multiline_text((x, y), text, fill='black', font=font, align='center')

    # Save image to a BytesIO object
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', dpi=(300, 300))
    img_bytes.seek(0)
    return img_bytes

def generate_image_with_template(data, template_path):
    # Open the template image
    img = Image.open(template_path).convert('RGB')
    draw = ImageDraw.Draw(img)

    # Load font
    font_path = os.path.join('static', 'fonts', 'PTSans-Regular.ttf')
    font_size = 50  # Starting font size
    font = ImageFont.truetype(font_path, font_size)

    # Define text and bounding box
    text = f"{data.get('job_title', '')}\n{data.get('job_location', '')}\n{data.get('job_salary', '')}"
    max_width = img.width - 100
    max_height = img.height - 100

    # Adjust font size to fit within bounding box
    while True:
        w, h = draw.multiline_textsize(text, font=font)
        if w <= max_width and h <= max_height:
            break
        font_size -= 1
        if font_size < 10:
            break  # Prevent font size from becoming too small
        font = ImageFont.truetype(font_path, font_size)

    # Calculate position
    x = (img.width - w) / 2
    y = (img.height - h) / 2

    # Draw text
    draw.multiline_text((x, y), text, fill='black', font=font, align='center')

    # Save image to a BytesIO object
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG', dpi=(300, 300))
    img_bytes.seek(0)
    return img_bytes

def send_email(to_email, job_title, image_bytes, form_data):
    msg = EmailMessage()
    msg['Subject'] = f"LinkedIn Post: {job_title}"
    msg['From'] = EMAIL_USERNAME
    msg['To'] = to_email

    # Construct the pre-filled form link with query parameters
    link = url_for('form', _external=True, **form_data)

    # Email content with the pre-filled form link
    msg.set_content(f'This is an auto-generated image. If you\'d like to make any changes, please [click here]({link}).')

    # Add the image as an attachment
    msg.add_attachment(image_bytes.read(), maintype='image', subtype='jpeg', filename='job_post.jpeg')

    # Send email using Office 365 SMTP
    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.send_message(msg)

def send_email_to_marketing(data):
    msg = EmailMessage()
    msg['Subject'] = f"New Branded Ad Request: {data.get('job_title', '')}"
    msg['From'] = EMAIL_USERNAME
    msg['To'] = MARKETING_EMAIL

    # Email content with submission details
    content = (
        f"A new branded ad request has been submitted with the following details:\n\n"
        f"Email: {data.get('email', '')}\n"
        f"Job Type: {data.get('job_type', '')}\n"
        f"Job Title: {data.get('job_title', '')}\n"
        f"Job Location: {data.get('job_location', '')}\n"
        f"Job Salary: {data.get('job_salary', '')}\n"
        f"Published Client: {data.get('published_client', '')}\n"
    )
    msg.set_content(content)

    # Send email using Office 365 SMTP
    with smtplib.SMTP('smtp.office365.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        smtp.send_message(msg)

def check_incoming_emails():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        mail.select('inbox')

        # Search for unseen emails from marketing team with attachments
        status, messages = mail.search(None, f'(UNSEEN FROM "{MARKETING_EMAIL}")')
        if status != 'OK':
            print("No new emails found.")
            mail.logout()
            return

        email_ids = messages[0].split()
        for email_id in email_ids:
            status, msg_data = mail.fetch(email_id, '(RFC822)')
            if status != 'OK':
                print(f"Failed to fetch email ID {email_id}")
                continue

            msg = email.message_from_bytes(msg_data[0][1])
            subject = msg['Subject']
            from_email = msg['From']

            # Process only if it's a reply to the branded ad request
            if "New Branded Ad Request" in subject:
                for part in msg.walk():
                    if part.get_content_maintype() == 'multipart':
                        continue
                    if part.get('Content-Disposition') is None:
                        continue
                    filename = part.get_filename()
                    if filename and filename.lower().endswith(('.jpg', '.jpeg')):
                        brand_name = os.path.splitext(filename)[0]
                        # Replace spaces with underscores for filenames
                        sanitized_brand_name = brand_name.replace(" ", "_")
                        # Check if the brand already exists to prevent overwriting
                        save_filename = f"{sanitized_brand_name}.jpg"
                        save_path = os.path.join('static', 'BrandedAds', save_filename)
                        if os.path.exists(save_path):
                            print(f"Template for brand '{sanitized_brand_name}' already exists. Skipping.")
                            continue
                        # Save the attachment
                        with open(save_path, 'wb') as f:
                            f.write(part.get_payload(decode=True))
                        print(f"Saved new branded ad template: {save_filename}")
                # Mark email as seen
                mail.store(email_id, '+FLAGS', '\\Seen')

        mail.logout()
    except Exception as e:
        print(f"Error checking emails: {e}")

# Schedule the email checker to run every 5 minutes
scheduler.add_job(func=check_incoming_emails, trigger="interval", minutes=5)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5858)