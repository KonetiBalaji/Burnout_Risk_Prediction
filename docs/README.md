# Burnout Risk Prediction System

**Created by Balaji Koneti**

A comprehensive AI-powered system for predicting burnout risk in hybrid and remote teams using machine learning, real-time data analysis, and personalized recommendations.

## 🚀 Features

### Core Functionality
- **Real-time Burnout Risk Assessment**: AI-powered prediction using multiple data sources
- **Personalized Recommendations**: Tailored suggestions based on individual risk factors
- **Comprehensive Dashboard**: Interactive visualization of risk trends and insights
- **Multi-source Data Integration**: Calendar events, email patterns, and survey responses
- **Advanced Analytics**: Detailed reports and trend analysis

### Technical Features
- **Modern Tech Stack**: React, TypeScript, Node.js, MongoDB, Python, TensorFlow
- **Scalable Architecture**: Microservices with Docker containerization
- **Real-time Processing**: Low-latency prediction API
- **Secure Authentication**: JWT-based user management
- **Responsive Design**: Mobile-first UI with Tailwind CSS

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │    │   ML Service    │
│   (React/TS)    │◄──►│   (Node.js)     │◄──►│   (Python)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx         │    │   MongoDB       │    │   Redis Cache   │
│   (Reverse      │    │   (Database)    │    │   (Sessions)    │
│    Proxy)       │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
burnout-risk-prediction/
├── backend/                 # Node.js/TypeScript API
│   ├── src/
│   │   ├── api/            # API routes and controllers
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── utils/          # Utility functions
│   │   └── config/         # Configuration
│   ├── tests/              # Unit and integration tests
│   └── Dockerfile
├── frontend/               # React/TypeScript UI
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   └── hooks/          # Custom hooks
│   └── Dockerfile
├── ml/                     # Python ML pipeline
│   ├── src/
│   │   ├── preprocess.py   # Data preprocessing
│   │   ├── train.py        # Model training
│   │   ├── evaluate.py     # Model evaluation
│   │   └── predict.py      # Prediction service
│   ├── notebooks/          # Jupyter notebooks
│   └── Dockerfile
├── docs/                   # Documentation
├── nginx/                  # Nginx configuration
└── docker-compose.yml      # Docker orchestration
```

## 🛠️ Installation & Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for ML development)
- MongoDB 7.0+

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd burnout-risk-prediction
   ```

2. **Set up environment variables**
   ```bash
   cp backend/env.example backend/.env
   # Edit backend/.env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3000
   - ML Service: http://localhost:8000
   - MongoDB: localhost:27017

### Local Development Setup

#### Backend Setup
```bash
cd backend
npm install
npm run dev
```

#### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

#### ML Service Setup
```bash
cd ml
pip install -r requirements.txt
python src/train.py
```

## 🔧 Configuration

### Environment Variables

#### Backend (.env)
```env
PORT=3000
NODE_ENV=development
MONGODB_URI=mongodb://localhost:27017/burnout-risk-prediction
JWT_SECRET=your-super-secret-jwt-key
JWT_EXPIRES_IN=24h
CORS_ORIGIN=http://localhost:5173
```

#### Frontend (.env)
```env
VITE_API_URL=http://localhost:3000/api
```

### Database Configuration
The system uses MongoDB for data storage. Key collections:
- `users`: User accounts and profiles
- `calendarEvents`: Calendar event data
- `emailMessages`: Email analysis data
- `predictionResults`: ML prediction results

## 📊 API Documentation

### Authentication Endpoints
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/profile` - Get user profile
- `PUT /api/auth/profile` - Update user profile

### Prediction Endpoints
- `POST /api/predictions` - Generate new prediction
- `GET /api/predictions/latest` - Get latest prediction
- `GET /api/predictions/history` - Get prediction history
- `GET /api/predictions/stats` - Get prediction statistics

### Metadata Endpoints
- `GET /api/health` - Health check
- `GET /api/info` - API information
- `GET /api/models` - Model information

## 🤖 Machine Learning Pipeline

### Data Sources
1. **Calendar Events**: Work hours, meetings, breaks
2. **Email Patterns**: Sentiment analysis, frequency
3. **Survey Responses**: Self-reported stress levels
4. **Biometric Data**: Sleep, exercise, nutrition

### Feature Engineering
- Time-based features (work hours, overtime)
- Meeting patterns (frequency, duration)
- Email sentiment analysis
- Work-life balance indicators
- Health and lifestyle factors

### Models
- **Random Forest**: Baseline ensemble model
- **Gradient Boosting**: Advanced ensemble model
- **Neural Networks**: Deep learning approach
- **Ensemble Methods**: Combined model predictions

### Evaluation Metrics
- Accuracy, Precision, Recall, F1-Score
- ROC-AUC, Precision-Recall AUC
- Confusion Matrix Analysis
- Feature Importance Analysis

## 🎨 User Interface

### Dashboard Features
- **Risk Overview**: Current burnout risk level and score
- **Trend Analysis**: Historical risk patterns
- **Factor Breakdown**: Individual risk factor analysis
- **Recommendations**: Personalized action items
- **Interactive Charts**: Data visualization

### Key Components
- `RiskCard`: Main risk assessment display
- `Chart`: Interactive data visualization
- `RecommendationList`: Personalized suggestions
- `Dashboard`: Comprehensive overview

## 🔒 Security Features

- **JWT Authentication**: Secure token-based auth
- **Password Hashing**: bcrypt encryption
- **Rate Limiting**: API request throttling
- **CORS Protection**: Cross-origin security
- **Input Validation**: Data sanitization
- **Helmet Security**: HTTP security headers

## 📈 Performance Optimization

- **Caching**: Redis for session management
- **Database Indexing**: Optimized MongoDB queries
- **CDN**: Static asset delivery
- **Compression**: Gzip response compression
- **Lazy Loading**: Frontend code splitting

## 🧪 Testing

### Backend Tests
```bash
cd backend
npm test
npm run test:watch
```

### Frontend Tests
```bash
cd frontend
npm test
```

### ML Tests
```bash
cd ml
pytest tests/
```

## 📝 Development Guidelines

### Code Style
- **TypeScript**: Strict type checking
- **ESLint**: Code linting and formatting
- **Prettier**: Code formatting
- **Black**: Python code formatting

### Git Workflow
1. Create feature branch
2. Make changes with tests
3. Run linting and tests
4. Create pull request
5. Code review and merge

### Documentation
- **API Docs**: OpenAPI/Swagger
- **Code Comments**: Inline documentation
- **README**: Setup and usage guides
- **Architecture**: System design docs

## 🚀 Deployment

### Production Deployment
1. **Environment Setup**: Configure production variables
2. **Database Migration**: Run database migrations
3. **Model Training**: Train and deploy ML models
4. **Container Build**: Build Docker images
5. **Service Deployment**: Deploy with Docker Compose

### Monitoring
- **Health Checks**: Service health monitoring
- **Logging**: Centralized log management
- **Metrics**: Performance monitoring
- **Alerts**: Automated alerting

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and documentation
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Balaji Koneti**
- Email: [your-email@example.com]
- LinkedIn: [your-linkedin-profile]
- GitHub: [your-github-profile]

## 🙏 Acknowledgments

- Machine learning community for open-source libraries
- React and Node.js communities for excellent frameworks
- MongoDB team for robust database solutions
- All contributors and testers

---

**Note**: This system is designed for educational and research purposes. For production use, ensure proper security measures, data privacy compliance, and professional medical consultation for health-related recommendations.
