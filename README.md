# Fashanize  
CITS3403 - Agile Web Development Project

---

## Description

**Fashanize** is an intuitive wardrobe management and outfit-sharing web application designed to help users digitize their clothing, curate outfits, analyze their style habits, and share looks with others. Built using the Agile methodology, this full-stack Flask application supports:

### Key Features

- **Wardrobe Management**: Upload and tag clothing items with categories like color, condition, size, and more.
- **Outfit Creation**: Mix and match your uploaded items into styled outfits.
- **Wardrobe Analysis**: Gain insights into your fashion usage, most-used items, and outfit frequency through data visualizations.
- **Social Sharing**: Publish outfits and browse those shared by others.
- **Smart Image Processing**: Auto-remove backgrounds using `rembg` libraries for cleaner visuals.

---

## 👥 Group Members

| UWA ID   | Student Name         | GitHub Username     |
|----------|----------------------|---------------------|
| 24058503 | Ralisha Woodhouse    | RalishaW            |
| 23856399 | Duc Minh Nguyen      | aminpepezethun      |
| 23775211 | Prem Patel           | Premithy            |
| 24346916 | Lithasa Munasinghe   | lithasa4            |

---

## Instructions: How to Launch the Application

### 1. Clone the repository

```bash
git clone https://github.com/RalishaW/WebWardrobe.git
cd WebWardrobe
```

### 2. Set up a virtual environment

**Note**: This app needs the python to be 3.9.6 to work.

#### macOS/Linux

```bash
python -m venv venv
source venv/bin/activate
```

#### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```


### 4 .env structure
- Create .env file (This is an example)
```bash
SECRET_KEY=SECRET_KEY 
FLASK_APP=fashanise.py
MAIL_USERNAME=somemail@gmail.com
MAIL_PASSWORD=sixteen-character-smtp-pwd
```
- Then run the command
```bash
pip install python-dotenv
```

### 5. Initialise a clean database
```bash
python3 db.init.py
```

### 6. Launch the application

```bash
flask run
```

> For development mode (auto-reloads on changes), you can use:
```bash
flask run --debug
```

---

## Instructions: How to Run Tests

### Unit Tests

Run the following to test basic backend functionality:

#### macOS/Linux

```bash
python3 -m unittest tests/test_app.py
```

#### Windows

```bash
python.exe -m unittest tests/test_app.py
```

---

### Selenium System Tests

These simulate user actions like login and upload:

#### macOS/Linux

```bash
python3 -m unittest tests/Sele_tests.py
```

#### Windows

```bash
python.exe -m unittest tests/Sele_tests.py
```

> Ensure **ChromeDriver** is installed and available in your system `PATH`.

---

## How to Use the Application

### 1. Sign Up

- Go to the **Sign Up** page.
- Create a new account with your username, email, and password.
- After logging in, you’ll be redirected to your wardrobe.

### 2. Upload Clothing Items

- Navigate to the **My Wardrobe** page.
- Click the **"+ Add Item"** button.
- Upload an image of your clothing item and fill in the tags (e.g., category, color, size, condition, etc.).
- Click **Upload** to save the item to your wardrobe.

> **Note**: Only `.png` images are supported for upload and background removal. Make sure your image is in `.png` format.

### 3. Create and Save Outfits

- Go to the **Outfits** page.
- Click **Create Outfit** and select items from your wardrobe.
- Name your outfit and choose to make it **public** or **private**.
- Save the outfit to view it in your collection.

### 4. Analyse Your Wardrobe

- Visit the **Analysis** page to view insights.
- See graphs showing your most used item, number of outfits, total clothing items, and more.

### 5. Explore Other Users' Outfits

- Head to the **Social** page to browse outfits shared by other users to you.
- Get inspiration and see how they’re styling their wardrobes.
