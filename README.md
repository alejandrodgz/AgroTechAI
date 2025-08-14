# AgroTech AI - Agricultural Monitoring System

An intelligent agricultural monitoring system powered by AI agents that analyze crop conditions, soil health, and environmental factors in real-time. The system uses multiple specialized AI agents to provide comprehensive agricultural insights and automated decision-making.

## 🌟 Features

- **Multi-Agent AI System**: Three specialized AI agents working together
  - **AgriVision**: Visual analysis of crop health and pest detection
  - **SoilSense**: Environmental conditions and soil analysis
  - **CropMaster**: Integrated decision-making and recommendations
- **Real-time Monitoring**: Live data processing and WebSocket communication
- **Interactive Dashboard**: React-based frontend with real-time visualizations
- **Scenario Simulation**: Pre-configured agricultural scenarios for demonstration

## 🏗️ Architecture

This project follows a client-server architecture:

```
AgroTech AI/
├── client/          # React frontend application
│   ├── app.jsx      # Main React component
│   ├── main.jsx     # React entry point
│   ├── index.html   # HTML template
│   ├── styles.css   # Tailwind CSS styles
│   └── package.json # Frontend dependencies
└── server/          # FastAPI backend application
    ├── main.py      # FastAPI server with AI agents
    └── requirements.txt # Python dependencies
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** v20.18.3 or higher
- **Python** 3.8 or higher
- **Ollama** (AI model server)

### 🤖 Ollama Setup

Ollama is a local AI model server that runs large language models on your machine. It provides the AI capabilities for our agricultural agents.

1. **Install Ollama**:
   ```bash
   # On macOS
   brew install ollama
   
   # On Linux
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # On Windows
   # Download from https://ollama.ai/download
   ```

2. **Start Ollama server**:
   ```bash
   ollama serve
   ```

3. **Install the required model**:
   ```bash
   ollama pull gemma2
   ```

   > **Note**: The system is configured to use the `gemma2` model. You can also use `llama2` or `codellama` by updating the `MODEL_NAME` variable in `server/main.py`.

### 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd reto2
   ```

2. **Install server dependencies**:
   ```bash
   cd server
   pip install -r requirements.txt
   ```

3. **Install client dependencies**:
   ```bash
   cd ../client
   npm install
   ```

### 🏃‍♂️ Running the Application

#### Start the Backend Server

1. **Navigate to server directory**:
   ```bash
   cd server
   ```

2. **Start the FastAPI server**:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

   The server will be available at: `http://localhost:8000`

#### Start the Frontend Client

1. **Navigate to client directory**:
   ```bash
   cd client
   ```

2. **Start the React development server**:
   ```bash
   npm start
   ```

   The client will be available at: `http://localhost:3000`

### 🔍 API Endpoints

- **GET** `/` - Health check and API information
- **GET** `/health` - Server and Ollama status check
- **WebSocket** `/ws` - Real-time communication for AI agent data

## 🧠 AI Agents Overview

### AgriVision Agent
- **Purpose**: Visual analysis of crop conditions
- **Capabilities**: 
  - Crop health assessment
  - Pest and disease detection
  - Leaf condition analysis
  - Visual symptom identification

### SoilSense Agent
- **Purpose**: Environmental and soil monitoring
- **Capabilities**:
  - Soil moisture analysis
  - pH level monitoring
  - Temperature and humidity tracking
  - Irrigation recommendations

### CropMaster Agent
- **Purpose**: Integrated decision-making
- **Capabilities**:
  - Data fusion from multiple agents
  - Risk assessment
  - Yield estimation
  - Priority action recommendations

## 📊 Demo Scenarios

The system includes four pre-configured scenarios for demonstration:

1. **🌱 Healthy Crop**: Optimal growing conditions
2. **🐛 Pest Detection**: Early pest identification
3. **💧 Water Stress**: Drought conditions monitoring
4. **🧪 Nutrient Deficiency**: Soil nutrition analysis

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern Python web framework
- **Uvicorn**: ASGI server
- **WebSockets**: Real-time communication
- **Requests**: HTTP client for Ollama integration
- **Ollama**: Local AI model server

### Frontend
- **React 18**: User interface framework
- **Vite**: Build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **Chart.js**: Data visualization
- **Socket.io**: Real-time communication

## 🔧 Development

### Server Development
```bash
cd server
# Install dependencies
pip install -r requirements.txt

# Run with auto-reload
uvicorn main:app --reload
```

### Client Development
```bash
cd client
# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

## 🧪 Testing the System

1. **Ensure Ollama is running** with the gemma2 model
2. **Start the backend server** on port 8000
3. **Start the frontend client** on port 3000
4. **Open your browser** to `http://localhost:3000`
5. **Watch the real-time analysis** as the system cycles through different agricultural scenarios

## 📝 Configuration

### Model Configuration
To change the AI model, edit `server/main.py`:
```python
MODEL_NAME = "gemma2"  # Change to "llama2" or "codellama"
```

### Port Configuration
- **Backend**: Change port in uvicorn command or `main.py`
- **Frontend**: Change port in `vite.config.js`

## 🚨 Troubleshooting

### Common Issues

1. **"Could not connect to Ollama"**:
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is installed: `ollama list`

2. **"Error loading ASGI app"**:
   - Run uvicorn from the server directory
   - Use: `uvicorn main:app --reload`

3. **Frontend connection issues**:
   - Ensure backend is running on port 8000
   - Check WebSocket connection in browser console

### Port Conflicts
- Backend default: `8000`
- Frontend default: `3000`
- Ollama default: `11434`

## 📄 License

This project is for educational purposes as part of EAFIT University coursework.

## 🤝 Contributing

This is an academic project. For improvements or suggestions, please create an issue or submit a pull request.

---

**Built with ❤️ for sustainable agriculture and AI innovation**
