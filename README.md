# Smart Todo List with AI Integration

A comprehensive full-stack web application for intelligent task management with AI-powered features including task prioritization, deadline suggestions, and context-aware recommendations.

## 📋 Features

### Core Functionality
- ✅ **Task Management**: Complete CRUD operations for tasks with priority scoring
- 📝 **Context Processing**: Analyze daily context (messages, emails, notes) for task insights
- 🤖 **AI Integration**: OpenAI/Claude/Gemini APIs or local LLM support via LM Studio
- 📊 **Smart Categorization**: Auto-suggest task categories and tags
- ⚡ **Priority Scoring**: AI-powered task prioritization (0-100 scale)
- 📅 **Deadline Suggestions**: Intelligent deadline recommendations
- 🎯 **Context-Aware**: Extract tasks from daily context automatically

### AI-Powered Features
- **Task Prioritization**: Use AI to rank tasks based on urgency and context
- **Deadline Suggestions**: Recommend realistic deadlines based on task complexity
- **Smart Categorization**: Auto-suggest task categories and tags
- **Task Enhancement**: Improve task descriptions with context-aware details
- **Context Analysis**: Process daily context to understand user's schedule and priorities

## 🏗️ Project Structure

```
/
├── backend/                    # Django REST Framework backend
│   ├── smart_todo/            # Main Django project
│   ├── tasks/                 # Tasks app
│   ├── context/               # Context processing app
│   ├── ai_integration/        # AI integration module
│   ├── requirements-simple.txt
│   └── manage.py
├── frontend/                  # NextJS frontend (To be implemented)
└── README.md
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: SQLite (development) / PostgreSQL (production)
- **AI Integration**: OpenAI API, Anthropic Claude, Google Gemini, or LM Studio
- **Authentication**: Django Session Authentication
- **API Documentation**: DRF built-in docs

### Frontend (Planned)
- **Framework**: Next.js with TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context/Redux Toolkit
- **UI Components**: Modern responsive design

### AI Integration Options
- **Option 1**: External APIs (OpenAI, Anthropic Claude, Google Gemini)
- **Option 2**: Local LLM via LM Studio (recommended for privacy)

## 🚀 Quick Start

### Backend Setup

1. **Clone and navigate to backend**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements-simple.txt
   ```

4. **Run migrations**:
   ```bash
   python manage.py migrate
   ```

5. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**:
   ```bash
   python manage.py runserver
   ```

The API will be available at `http://localhost:8000/`

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Django settings
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI Integration (choose one or more)
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
GEMINI_API_KEY=your-gemini-api-key

# LM Studio (for local LLM)
LM_STUDIO_URL=http://localhost:1234/v1
LM_STUDIO_MODEL=local-model
```

## 📡 API Endpoints

### Tasks API (`/api/v1/tasks/`)

#### Core Endpoints
- `GET /api/v1/tasks/` - List all tasks
- `POST /api/v1/tasks/` - Create a new task
- `GET /api/v1/tasks/{id}/` - Get task details
- `PUT /api/v1/tasks/{id}/` - Update task
- `DELETE /api/v1/tasks/{id}/` - Delete task

#### Special Endpoints
- `POST /api/v1/tasks/{id}/mark_completed/` - Mark task as completed
- `GET /api/v1/tasks/overdue/` - Get overdue tasks
- `GET /api/v1/tasks/high_priority/` - Get high priority tasks
- `GET /api/v1/tasks/by_status/` - Get tasks grouped by status
- `GET /api/v1/tasks/dashboard_stats/` - Get dashboard statistics

#### AI Features
- `POST /api/v1/tasks/{id}/ai_analysis/` - Request AI analysis for task
- `POST /api/v1/tasks/ai_prioritization/` - AI prioritization for multiple tasks
- `POST /api/v1/tasks/bulk_update/` - Bulk update multiple tasks

### Context API (`/context/api/v1/entries/`)

#### Core Endpoints
- `GET /context/api/v1/entries/` - List context entries
- `POST /context/api/v1/entries/` - Create context entry
- `GET /context/api/v1/entries/{id}/` - Get context details
- `PUT /context/api/v1/entries/{id}/` - Update context entry

#### AI Processing
- `POST /context/api/v1/entries/{id}/analyze/` - Analyze single context entry
- `POST /context/api/v1/entries/bulk_analyze/` - Bulk analyze multiple entries
- `GET /context/api/v1/entries/summary/` - Get context summary statistics

#### Filtered Views
- `GET /context/api/v1/entries/pending_processing/` - Pending AI processing
- `GET /context/api/v1/entries/high_relevance/` - High relevance entries
- `GET /context/api/v1/entries/with_extracted_tasks/` - Entries with extracted tasks

### Categories API (`/api/v1/categories/`)
- `GET /api/v1/categories/` - List categories
- `POST /api/v1/categories/` - Create category
- `GET /api/v1/categories/{id}/` - Get category details

## 🗄️ Database Schema

### Tasks App
- **Task**: Main task model with AI-enhanced fields
- **Category**: Task categories and tags
- **TaskComment**: Comments and updates on tasks

### Context App
- **ContextEntry**: Daily context data (messages, emails, notes)
- **ContextInsight**: AI-extracted insights from context
- **ContextProcessingLog**: Processing activity logs

### AI Integration App
- **AIProvider**: AI service provider configurations
- **AIRequest**: Track AI API requests and responses
- **UserAIPreferences**: User AI settings and preferences
- **TaskAIAnalysis**: AI analysis results for tasks

## 🤖 AI Integration

### Supported Providers
1. **OpenAI GPT** - Task analysis and prioritization
2. **Anthropic Claude** - Context understanding and insights
3. **Google Gemini** - Smart categorization
4. **LM Studio** - Local LLM hosting (recommended for privacy)

### AI Features Implementation
- **Context Processing**: Analyze daily context to understand user's schedule
- **Task Prioritization**: Generate priority scores based on context analysis
- **Deadline Suggestions**: Recommend optimal deadlines considering workload
- **Task Enhancement**: Provide enhanced task descriptions with relevant context
- **Smart Categorization**: Automatically recommend task categories and tags

## 📊 Sample API Responses

### Task List Response
```json
{
  "results": [
    {
      "id": 1,
      "title": "Complete project presentation",
      "status": "todo",
      "priority": "high",
      "priority_score": 85.0,
      "deadline": "2024-12-30T15:00:00Z",
      "category_name": "Work",
      "urgency_level": "high",
      "is_overdue": false,
      "created_at": "2024-12-27T10:00:00Z"
    }
  ]
}
```

### AI Analysis Response
```json
{
  "task_id": 1,
  "priority_analysis": {
    "suggested_priority_score": 75.0,
    "factors": ["Deadline proximity", "Task complexity", "Dependencies"],
    "confidence": 85.0
  },
  "deadline_suggestion": {
    "suggested_deadline": "2024-12-30T10:00:00Z",
    "reasoning": "Based on task complexity and current workload",
    "confidence": 80.0
  },
  "enhancement_suggestions": [
    "Break down into smaller subtasks",
    "Add specific deliverables"
  ]
}
```

## 🔧 Development Status

### ✅ Completed
- Django backend with REST API
- Database models and migrations
- Task management CRUD operations
- Context entry management
- AI integration framework (mock responses)
- API documentation
- Authentication system

### 🚧 In Progress
- Frontend implementation (Next.js)
- Real AI integration (OpenAI/Claude/Gemini)
- LM Studio integration

### 📋 Planned
- Advanced context analysis
- Task scheduling suggestions
- Calendar integration
- Export/import functionality
- Dark mode toggle
- Mobile responsiveness

## 🛡️ Security Considerations

- CORS properly configured for frontend
- Authentication required for all API endpoints
- Input validation and sanitization
- Rate limiting for AI API calls
- Environment variables for sensitive data

## 📝 Notes

- Currently using SQLite for development (easily switchable to PostgreSQL)
- AI responses are mocked for demonstration (real integration pending)
- Frontend development to begin next
- Supports both external AI APIs and local LLM via LM Studio

## 🤝 Contributing

This project is part of a technical assignment. The code demonstrates:
- Clean, readable, well-structured code
- Proper OOP implementation
- Comprehensive API design
- AI integration architecture
- Modern web development practices

## 📞 Support

For questions or issues, contact: devgods99@gmail.com

---

**Note**: This is a comprehensive full-stack application showcasing modern web development practices with AI integration. The backend is fully functional with mock AI responses, ready for frontend integration and real AI service connection.
