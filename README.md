# Fake Logo Detection

A Flask-based web application that uses deep learning to detect fake logos from real ones.

## Features

- **Logo Classification**: Upload logo images and get instant predictions
- **User Authentication**: Secure registration and login system
- **Admin Dashboard**: Manage users and view classification history
- **Real-time Processing**: Fast logo verification with confidence scores
- **Classification History**: Track all logo classifications

## Tech Stack

- **Backend**: Flask, SQLAlchemy
- **ML Model**: TensorFlow/Keras
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite

## Installation

1. Clone the repository:
```bash
git clone https://github.com/imyashpatil/Fake-Logo-Detection.git
cd "Fake Logo Detection"
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv1
source venv1/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python3 site.py
```

The app will be available at `http://127.0.0.1:5000`

## Usage

### For Users:
1. Register a new account
2. Log in with your credentials
3. Upload a logo image (PNG, JPG, JPEG, GIF)
4. View the classification result (Real/Fake) with confidence score
5. Check your classification history

### For Admins:
1. Navigate to `/admin/login`
2. Use admin credentials to access the dashboard
3. View and manage all users

## Project Structure

```
├── site.py                 # Main Flask application
├── models.py              # Database models
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
├── static/                # CSS, JS, images
│   ├── css/              # Stylesheets
│   ├── js/               # JavaScript files
│   ├── uploads/          # User uploaded images
│   └── processed/        # Processed images
└── dataset/              # Training dataset
    ├── train/            # Training images
    └── validation/       # Validation images
```

## Model

The application uses a pre-trained Keras model (`fake_logo_detector (2).h5`) that classifies logos with high accuracy.

## Environment Variables

Create a `.env` file in the project root:
```
SECRET_KEY=your_secret_key_here
```

## License

This project is open source and available under the MIT License.

## Contact

For questions or support, please contact the project maintainer.
