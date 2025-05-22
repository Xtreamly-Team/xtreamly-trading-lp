# 🌐 AI & Policy API

This is a FastAPI application named **xtreamly-trading-lp**, designed for sending actionable signals for on-chain trading activities such as Uniswap LP position management.

## 📋 Requirements

1. **Python Version**: Python 3.11.3
2. **Dependencies**: All necessary dependencies are listed in the `requirements.txt` file.

## 🛠 Installation

1. Clone this repository:

   ```bash
   git clone https://github.com/Xtreamly-Team/xtreamly-trading-lp.git
   ```

   ```bash
   cd <repository-folder>
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Optional: Configure environment variables in a `.env` file (if needed for additional customizations).

## ⚙️ Configuration

- **CORS Middleware:** Configured to allow specific origins (e.g., `localhost` on common development ports).
- **Environment Variables:** You need to set the `.env` variables to run data fetching:
  - GMAIL_KEY

## 💻 Set Up Environment with Anaconda

Follow these steps to set up your development environment using Anaconda:

1. **Check Existing Environments**

   ```bash
   conda env list
   ```

2. **Create a New Environment**

   Create a new environment named `py311_xtreamly_v1` with Python 3.11.3:

   ```bash
   conda create -n py311_xtreamly_v1 python=3.11.3
   ```

3. **Activate the Environment**

   ```bash
   conda activate py311_xtreamly_v1
   ```

4. **Install Dependencies**

   Use `pip` to install the dependencies listed in the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

5. **Install Spyder Kernels (Optional)**

   If you are using Spyder IDE, install the required version of Spyder kernels:

   ```bash
   conda install spyder-kernels==2.4.4
   ```

6. (OPTIONAL FOR APP) **Build Docker Image**

   Build a Docker image for the application:

   ```bash
   docker build -t fastapi .
   ```

Your Anaconda environment is now set up, and you can proceed to run or develop the application.


## 🚀 Usage

Access the API in your browser or API testing tool at:

   ```
   http://localhost:8080
   ```

## 🚀 Execute tests

   ```bash
   python -m tests.position_management 
   ```
