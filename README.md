FixNBook – Service Booking Platform
FixNBook is a full-stack web application that connects service seekers with service providers, enabling users to browse, book, and pay for services securely.
Built with Flask, MongoDB Atlas, and Stripe, it supports provider management, booking scheduling, and secure payment processing.

Credentials for testing:

  Providers Credential
  1 vivek@gmail.com
    psd: ok
  2 chintu@gmail.com
    psd: ok
  
  Seeker credentials
  raj@gmail.com
  psd: ok

The best part about this Application is,if there are 2 providers Vivek and Chintu, here Vivek can only see the services he posted previosly but not the services Chintu or any others posted. And the seeker can see all the available serives SUCCESSFULLY. And I could plan, code, built, deploy, and hosted in single day in CODEGNAN Hackathon.


🚀 Features
For Service Seekers
Browse available services with details (price, date, time, location, description).

View service images uploaded by providers.

Book services with integrated Stripe payment gateway.

Secure card payments with error handling.

For Service Providers
Provider signup & login with authentication.

Create, update, and delete their own services.

Upload service images.

View bookings related to their services.

Services list is filtered — providers only see their own listings.

General
MongoDB Atlas cloud database.

CORS enabled for API access.

Responsive front-end using HTML/CSS.

Secure secret key management using environment variables.

Deployed on Render.

🛠 Tech Stack
Layer	Technology
Backend	Flask (Python)
Frontend	HTML, CSS, Vanilla JS
Database	MongoDB Atlas
Payment	Stripe
Deployment	Render
Dependencies	Flask, Flask-CORS, pymongo, gunicorn, stripe, dnspython

📂 Project Structure
bash
Copy
Edit
fixNbook/
│
├── app.py                     # Flask application entry point
├── requirements.txt           # Python dependencies
├── render.yaml                # Render deployment configuration
│
├── seeker.html                # Service seeker dashboard
├── seeker-login.html          # Seeker login page
├── seeker-signup.html         # Seeker signup page
├── seeker.css                 # Styles for seeker dashboard
│
├── provider-dashboard.html    # Provider dashboard
├── provider-login.html        # Provider login page
├── provider-signup.html       # Provider signup page
├── provider-dashboard.css     # Styles for provider dashboard
│
├── index.html                 # Landing page
├── styles.css                 # General styles
├── styles-login.css           # Login styles
├── styles-auth.css            # Auth styles
│
├── images/                    # Service images
└── dashboard.css              # Dashboard styles


⚙️ Environment Variables
Set these in your .env file locally or in Render’s Environment tab:

ini
Copy
Edit
MONGO_URI=your_mongodb_atlas_connection_string
FLASK_SECRET_KEY=your_flask_secret
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
📦 Installation & Setup
Local Development
Clone the repository

bash
Copy
Edit
git clone https://github.com/your-username/fixNbook.git
cd fixNbook
Create a virtual environment

bash
Copy
Edit
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
Install dependencies

bash
Copy
Edit
pip install -r requirements.txt
Set environment variables

bash
Copy
Edit
export MONGO_URI="your_mongodb_atlas_connection_string"
export FLASK_SECRET_KEY="your_flask_secret"
export STRIPE_SECRET_KEY="your_stripe_secret_key"
export STRIPE_PUBLISHABLE_KEY="your_stripe_publishable_key"
Run the application

bash
Copy
Edit
python app.py
App will be available at: http://127.0.0.1:5000

☁️ Deployment on Render
Push your code to GitHub.

Create a Web Service in Render.

Connect to your GitHub repository.

Set the Start Command:

bash
Copy
Edit
gunicorn app:app --preload --workers=2 --threads=4 --timeout=120
Add environment variables in Settings → Environment.

Deploy and access your live app.

💳 Payment Flow
Seeker clicks Book on a service.

App fetches service details and price.

Backend creates a Stripe PaymentIntent.

Frontend displays Stripe card input modal.

On success, user is redirected to /payment-success.

🔐 Security Notes
Never commit API keys to the repository.

All secrets are stored in environment variables.

CORS enabled with controlled origins.

MongoDB Atlas IP access list must include 0.0.0.0/0 or Render's outbound IPs for connectivity.

📌 Future Enhancements
Email notifications for bookings.

Search & filter services.

Multi-currency payment support.

Provider analytics dashboard.
