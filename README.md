# 🌿 LeafGuard AI - Plant Disease Classification System

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.x-red.svg)
![Firebase](https://img.shields.io/badge/Firebase-Firestore-yellow.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

**An AI-powered plant disease detection system using Deep Learning**

[Demo](#demo) • [Features](#features) • [Installation](#installation) • [Usage](#usage) • [Team](#team)

</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Model Performance](#model-performance)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Dataset](#dataset)
- [Team](#team)

---

## 🎯 Overview

**LeafGuard AI** is a deep learning-based system that automatically identifies and classifies plant diseases from leaf images. The system uses **MobileNetV2** with **Transfer Learning** to achieve high accuracy while maintaining a lightweight architecture suitable for mobile deployment.

### Key Objectives:
- Build a multi-class classification model (15 classes) achieving **F1-Score > 90%**
- Provide an intuitive web interface for farmers and agricultural workers
- Enable early disease detection to improve crop yields and reduce losses

---

## 🔬 Problem Statement

Plant diseases cause significant crop yield reduction, especially in small-scale farming areas. Traditional disease detection relies on manual observation, which is:
- Time-consuming and error-prone
- Dependent on individual expertise
- Often results in delayed diagnosis

**Our Solution:** An AI-powered system that provides instant, accurate disease diagnosis from leaf images, helping farmers detect diseases early and take appropriate action.

### Research Questions:
1. How to efficiently collect and preprocess diverse leaf image data?
2. Which deep learning model is best suited for leaf disease classification?
3. What evaluation metrics should be prioritized for imbalanced datasets?
4. How to optimize the model for mobile deployment?
5. What ethical considerations arise when deploying AI in agriculture?

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔍 **Disease Detection** | Upload or capture leaf images for instant diagnosis |
| 📊 **Confidence Scores** | View prediction confidence and top-3 alternatives |
| 💊 **Treatment Recommendations** | Get detailed treatment, prevention, and care information |
| 👤 **User Authentication** | Secure login/registration via Firebase |
| 📈 **Diagnosis History** | Track past diagnoses and view statistics |
| 🎨 **Modern UI** | Bio-digital themed interface with smooth animations |

---

## 📈 Model Performance

Our trained model achieves excellent performance on the test dataset:

| Metric | Score |
|--------|-------|
| **Accuracy** | 91.07% |
| **Macro F1-Score** | 90.09% |
| **Macro Precision** | 90.59% |
| **Macro Recall** | 89.95% |

### Supported Classes (15):

| Plant | Diseases |
|-------|----------|
| **Pepper Bell** | Bacterial Spot, Healthy |
| **Potato** | Early Blight, Late Blight, Healthy |
| **Tomato** | Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy |

---

## 🛠️ Technologies

| Category | Technologies | Purpose |
|----------|-------------|---------|
| **Deep Learning** | TensorFlow, Keras, MobileNetV2 | Model development and training |
| **Web Framework** | Streamlit | Web application interface |
| **Backend** | Firebase Auth, Firestore | Authentication & database |
| **Data Processing** | NumPy, Pandas, Pillow | Image preprocessing |
| **Visualization** | Matplotlib, Plotly | Charts and graphs |
| **Version Control** | Git, GitHub | Collaboration and code management |

---

## 📁 Project Structure

```
AI_LeafGuard_Team/
├── 📂 config/                  # Configuration files
│   └── firebase_config.py      # Firebase settings
├── 📂 database/                # Database operations
│   └── firestore_manager.py    # Firestore CRUD operations
├── 📂 dataset/                 # Dataset files
│   ├── solutions.json          # Treatment information
│   └── class_weights.json      # Class balancing weights
├── 📂 figures/                 # Generated visualizations
│   ├── model_architecture.png
│   ├── confusion_matrix.png
│   └── f1_score_by_class.png
├── 📂 models/                  # Trained models
│   ├── MobileNetV2_best.h5     # Best trained model
│   ├── class_indices.json      # Class name mapping
│   └── evaluation_report.json  # Performance metrics
├── 📂 pages/                   # Streamlit pages
│   ├── Login.py
│   ├── Register.py
│   ├── Profile.py
│   └── History.py
├── 📂 src/                     # Source code
│   ├── auth_manager.py         # Authentication logic
│   ├── balance_data.py         # Class balancing
│   ├── data_loader.py          # Data generators
│   ├── model_trainer.py        # Model building & training
│   ├── ui_components.py        # UI styling
│   └── utils.py                # Utility functions
├── 📄 app.py                   # Main Streamlit application
├── 📄 train.py                 # Training script
├── 📄 requirements.txt         # Python dependencies
└── 📄 README.md                # This file
```

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Git
- (Optional) CUDA-enabled GPU for faster training

### Step 1: Clone the Repository

```bash
git clone https://github.com/Tbaonhi/AI_LeafGuard_Team.git
cd AI_LeafGuard_Team
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Firebase Setup (Optional - for full features)

1. Create a Firebase project at [Firebase Console](https://console.firebase.google.com/)
2. Enable Authentication (Email/Password)
3. Create a Firestore database
4. Download service account credentials
5. Create `.env` file:

```env
FIREBASE_CREDENTIALS_PATH=path/to/your/firebase-credentials.json
```

---

## 💻 Usage

### Run the Web Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

### Train the Model (Optional)

If you want to retrain the model:

1. Download the PlantVillage dataset from [Kaggle](https://www.kaggle.com/datasets/emmarex/plantdisease)
2. Extract to `dataset/` folder with structure:
   ```
   dataset/
   ├── train/
   ├── val/
   └── test/
   ```
3. Run training:
   ```bash
   python train.py
   ```

---

## � Dataset

| Attribute | Value |
|-----------|-------|
| **Source** | PlantVillage Dataset (Kaggle) |
| **Total Classes** | 15 |
| **Plants Covered** | Pepper Bell, Potato, Tomato |
| **Image Size** | 224 × 224 pixels |
| **Split Ratio** | 70% Train / 15% Val / 15% Test |
| **Preprocessing** | Resize, Normalize, Augmentation |
| **Class Balancing** | Class Weights Applied |

### Data Augmentation:
- Rotation: ±20°
- Width/Height Shift: 20%
- Zoom: 20%
- Horizontal Flip: Yes

---

## 👥 Team

| Member | Responsibilities |
|--------|------|------------------|
| **Trương Tuyết Trinh**  | Dataset Setup, Model Training, Database Operations |
| **Trần Bảo Nhi**  | Data Cleaning, Firebase Integration, Authentication |
| **Phan Thị Thùy Nhung**  | Class Balancing, Streamlit Development |
| **Nguyễn Hoàng Thanh Trâm**  | Data Preprocessing, UI/UX Design |

---

## 📄 License

This project is developed for educational purposes as part of the Artificial Intelligence course at VNUK.

---

## 🙏 Acknowledgments

- [PlantVillage Dataset](https://www.kaggle.com/datasets/emmarex/plantdisease) for providing the training data
- [TensorFlow](https://www.tensorflow.org/) and [Keras](https://keras.io/) for the deep learning framework
- [Streamlit](https://streamlit.io/) for the web application framework
- [Firebase](https://firebase.google.com/) for authentication and database services

---

<div align="center">

**Made with ❤️ by LeafGuard Team**

⭐ Star this repository if you find it helpful!

</div>
