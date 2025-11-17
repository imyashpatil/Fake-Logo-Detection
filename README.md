Fake Logo Detection 🛡️

A deep learning–powered Flask web application that detects fake logos using a CNN model.

This project allows users to upload an image, and the system predicts whether the logo is real or fake.
The backend is built using Flask, and the machine learning pipeline is powered by a Convolutional Neural Network (CNN) trained on a custom dataset.

🚀 Features

Upload an image and get instant prediction (Real / Fake)
Custom-trained CNN model (Keras/TensorFlow)
Clean Flask web interface
Modular code structure (easy to extend)
Lightweight and easy to deploy
🧠 Model Details (Custom CNN)

Custom-built CNN architecture
Trained using Keras on a custom dataset
Uses convolutional, pooling, dropout and dense layers
Saved in .h5 format (not included in repo due to size)
You can download or place the model manually inside the model/ folder
🛠️ Installation & Setup

1️⃣ Clone the repository

git clone https://github.com/imyashpatil/Fake-Logo-Detection.git
cd Fake-Logo-Detection

python3 -m venv venv
source venv/bin/activate   # macOS / Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
Add the model file

Place your .h5 model inside:

model/


(Example: fake_logo_detector_advanced.h5)

Run the Flask App
python site.py

Author

Yash Patil
GitHub: [@imyashpatil](https://github.com/imyashpatil)
