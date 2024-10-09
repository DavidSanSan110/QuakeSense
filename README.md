# 🌍🚀 Seismic Data Detection in Planetary Missions - NASA Space Apps Challenge 2024 🌋📡

Welcome to our project for the **NASA Space Apps Challenge 2024**! This project addresses the power limitations faced in planetary seismology missions by developing a system that filters out noise and detects seismic quakes in real-time, transmitting only the relevant data back to Earth. Our AI model achieves **97% accuracy** in detecting seismic quakes! 🌟

---

## 📜 Project Overview

In missions like Apollo and Mars InSight, transmitting continuous seismic data back to Earth is power-consuming and inefficient due to noise. Our solution? Analyze the data on the lander using AI to identify the relevant seismic events and send only that information back to Earth. 

Our approach:
- **Windowing technique** to detect seismic events.
- **Peak detection** to determine the start time of the seismic quake.
- Simulated satellites receiving real-time velocity data, processing it, and detecting seismic events.

During demonstrations, you can visualize the incoming data and seismic detection via **real-time graphs**! 📊

---

## 🏗️ Project Structure

The project is organized into four core modules, each with its own Dockerfile:

1. **🌐 Front-End (`front`)**: Built using **three.js** for real-time data visualization and seismic event detection.

2. **🔧 Back-End (`back`)**: A **microservices orchestrator** managing the data flow between the components.

3. **🛰️ Satellite Simulation (`satellite`)**: Simulates real-time data reception and signal processing from a satellite.

4. **🤖 Seismic Detector (`detector`)**: The **AI module** responsible for detecting seismic quakes, using machine learning models trained on real planetary data.

---

## ⚙️ Technical Details - Model Training

To achieve high accuracy in detecting seismic quakes, our model follows these steps:

1. **Feature Scaling**:
   ```python
   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)
   ```

2. **Data Splitting with Stratification**:
   ```python
   X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42, stratify=y)
   ```

3. **ADASYN for Data Balancing**:
   ```python
   adasyn = ADASYN(random_state=42)
   X_train_resampled, y_train_resampled = adasyn.fit_resample(X_train, y_train)
   ```

   - After ADASYN, the class distribution is balanced to improve model performance.

4. **Ensemble Model**:
   We used an ensemble of three models:
   - **LightGBM**
   - **XGBoost**
   - **Logistic Regression**

   Each model was optimized using a **VotingClassifier** for soft voting, ensuring robustness in seismic detection.

5. **LightGBM Hyperparameter Tuning**:
   ```python
   param_grid_lgbm = {
       'lgbm__n_estimators': [100, 200],
       'lgbm__max_depth': [5, 7, -1],
       'lgbm__learning_rate': [0.05, 0.1],
       'lgbm__subsample': [0.7, 0.8, 1.0],
       'lgbm__colsample_bytree': [0.7, 0.8, 1.0]
   }
   ```

   **Result**: Our final model achieved **97% accuracy** in detecting seismic events.

---

## 🚀 How to Run

This project is set up using **Docker Compose**, making it easy to deploy all modules at once.

### Steps:
1. **Clone the repository**:
   ```bash
   git clone https://github.com/DavidSanSan110/QuakeSense.git
   cd QuakeSense
   ```

2. **Run with Docker Compose**:
   - Start all services (front-end, back-end, satellite, detector):
   ```bash
   docker-compose up --build -d
   ```

3. **Access the Application**:
   - Go to `http://localhost` (or the port you configured) to visualize the real-time data and seismic detection process.

4. **Shutdown**:
   - Stop the services by running:
   ```bash
   docker-compose down
   ```

---

## 🌍 Conclusion

This project demonstrates an innovative approach to improving data efficiency in planetary missions by leveraging AI to detect seismic events in real-time. With a model accuracy of **97%** and a fully simulated satellite infrastructure, this solution has the potential to significantly impact future planetary seismology missions.

Thanks for checking out our submission for the **NASA Space Apps Challenge 2024**! 🚀

---

## 👥 Developers

- **Daniel Mulas Fajardo** - (https://github.com/danimulas)

- **Mario Prieta Sánchez** - (https://github.com/mariops03)

- **Diego Borrallo Herrero** - (https://github.com/diegoobh)

- **Tomás Pérez Vellarino** - (https://github.com/Tomypv)

- **Álvaro Sánchez Moro** - (https://github.com/smalvaro)

- **David Sánchez Sánchez** - (https://github.com/DavidSanSan110)

---
