# Admissions Prediction API - BentoML Exam

This repository contains a complete machine learning workflow for predicting the chance of admission of a student to a university, containerized and served using BentoML.

---

## 📁 Project Structure

```plaintext
examen_bentoml/
├── data/
│   ├── processed/          # Processed train/test splits
│   └── raw/                # Raw dataset (admission.csv)
├── models/                 # Saved models (if any)
├── src/
│   ├── prepare_data.py     # Data preparation script
│   ├── train_model.py      # Model training and saving script
│   └── service.py          # BentoML service (API)
├── tests/
│   └── test_service.py     # Pytest unit tests for the API
├── bentofile.yaml          # BentoML build configuration
├── Dockerfile.template     # Custom Dockerfile for BentoML containerization
├── requirements.txt        # Python dependencies
├── README.md               # This file
└── bento_image.tar         # Exported Docker image (for submission)
```

---

## 🚀 Quickstart

### 1. **Setup**

Clone the repository and move into the project directory:

```bash
git clone <your-fork-url>
cd examen_bentoml
```

### 2. **(Optional) Create and Activate a Virtual Environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. **Prepare Data**

Download the dataset and place it in `data/raw/admission.csv` (already included if you see the file).

Run the data preparation script:

```bash
python src/prepare_data.py
```

### 4. **Train the Model**

```bash
python src/train_model.py
```

This will save the trained model to the BentoML model store.

### 5. **Build the Bento**

```bash
bentoml build
```

### 6. **Containerize the Bento**

```bash
bentoml containerize admissions_prediction_service:latest -t christopherguth_christopherguthbentoml
```

### 7. **Export the Docker Image**

```bash
docker save -o bento_image.tar christopherguth_christopherguthbentoml
```

---

## 🐳 Running the API with Docker

Load the Docker image (if starting from `bento_image.tar`):

```bash
docker load -i bento_image.tar
```

Run the container:

```bash
docker run --rm -p 3000:3000 christopherguth_christopherguthbentoml
```

The API will be available at [http://localhost:3000](http://localhost:3000).

---

## 🔐 API Endpoints

### 1. **Login**

- **POST** `/login`
- **Body:**  
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
  ```
- **Returns:** JWT token

### 2. **Predict**

- **POST** `/predict`
- **Headers:**  
  `Authorization: Bearer <JWT_TOKEN>`
- **Body:**  
  ```json
  {
    "GRE Score": 320,
    "TOEFL Score": 110,
    "University Rating": 4,
    "SOP": 4.5,
    "LOR": 4.0,
    "CGPA": 9.2,
    "Research": 1
  }
  ```
- **Returns:**  
  ```json
  {
    "admission_chance": 0.85
  }
  ```

---

## 🧪 Running Unit Tests

With the API running (see above), in a new terminal:

```bash
pytest tests/test_service.py -v
```

All tests should pass, covering:
- JWT authentication (valid/invalid/expired tokens)
- Login endpoint (valid/invalid credentials)
- Prediction endpoint (valid/invalid input, authentication)

---

## 📝 Submission Checklist

- [x] `README.md` (this file)
- [x] `bento_image.tar` (Docker image)
- [x] `tests/test_service.py` (unit tests)

**To validate:**
1. Unpack your archive.
2. Load and run the Docker image.
3. Run the tests with `pytest tests/test_service.py -v` (all should pass).

---