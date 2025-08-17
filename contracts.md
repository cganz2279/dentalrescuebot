# Backend Development Contracts

## API Endpoints Required

### 1. Dental Specialties
- `GET /api/specialties` - Get all dental specialties with procedure counts
- `GET /api/specialties/:id` - Get specific specialty with its procedures

### 2. Procedures
- `GET /api/procedures` - Get all procedures (with optional specialty filter)
- `GET /api/procedures/:id` - Get specific procedure with full details
- `GET /api/procedures/search?q={query}` - Search procedures by name or specialty

### 3. Admin Routes (Future Enhancement)
- `POST /api/procedures` - Add new procedure
- `PUT /api/procedures/:id` - Update procedure
- `DELETE /api/procedures/:id` - Delete procedure

## MongoDB Data Models

### Specialty Schema
```javascript
{
  _id: ObjectId,
  id: String (unique identifier),
  name: String,
  description: String,
  icon: String,
  color: String,
  createdAt: Date,
  updatedAt: Date
}
```

### Procedure Schema
```javascript
{
  _id: ObjectId,
  id: String (unique identifier),
  name: String,
  specialty: String (references Specialty.id),
  specialtyName: String,
  duration: String,
  overview: String,
  immediateAftercare: Array[String],
  dietRestrictions: Array[String],
  warningSignsToCallDoctor: Array[String],
  recoveryTimeline: Array[{
    day: String,
    activity: String
  }],
  medications: Array[String],
  createdAt: Date,
  updatedAt: Date
}
```

## Mock Data Migration Plan

### Current Mock Data in `/frontend/src/data/mock.js`:

1. **dentalSpecialties** - Will be stored in MongoDB `specialties` collection
2. **procedureDetails** - Will be stored in MongoDB `procedures` collection
3. **searchProcedures function** - Will be replaced with backend search API

### Frontend Integration Changes:

1. **Replace mock.js imports** with API calls in:
   - `HomePage.jsx` - Search functionality and specialty listing
   - `SpecialtyPage.jsx` - Specialty details and procedure listing
   - `ProcedurePage.jsx` - Individual procedure details

2. **Add loading states** for all API calls
3. **Add error handling** for failed requests
4. **Implement data caching** for better performance

## Backend Implementation Plan

### Phase 1: Database Setup
- Create MongoDB models using Mongoose
- Seed database with current mock data
- Add database connection and error handling

### Phase 2: API Endpoints
- Implement all CRUD operations
- Add search functionality with text indexing
- Add validation and error handling
- Add request/response logging

### Phase 3: Frontend Integration
- Replace all mock data usage with API calls
- Add loading spinners and error states
- Test all user flows end-to-end
- Optimize performance and caching

## API Response Formats

### GET /api/specialties
```json
{
  "success": true,
  "data": [
    {
      "id": "endodontics",
      "name": "Endodontics",
      "description": "Root canal treatments and related procedures",
      "icon": "Activity",
      "color": "bg-blue-50 border-blue-200",
      "procedureCount": 2
    }
  ]
}
```

### GET /api/procedures/:id
```json
{
  "success": true,
  "data": {
    "id": "root-canal",
    "name": "Root Canal Treatment",
    "specialty": "endodontics",
    "specialtyName": "Endodontics",
    "duration": "7-14 days recovery",
    "overview": "Root canal treatment removes infected...",
    "immediateAftercare": [...],
    "dietRestrictions": [...],
    "warningSignsToCallDoctor": [...],
    "recoveryTimeline": [...],
    "medications": [...]
  }
}
```

### GET /api/procedures/search?q=root
```json
{
  "success": true,
  "data": [
    {
      "id": "root-canal",
      "name": "Root Canal Treatment",
      "specialty": "endodontics",
      "specialtyName": "Endodontics",
      "duration": "7-14 days recovery"
    }
  ]
}
```

## Error Handling

### Standard Error Response
```json
{
  "success": false,
  "error": {
    "message": "Resource not found",
    "code": "NOT_FOUND"
  }
}
```

## Frontend Service Layer

Create `src/services/api.js` to centralize all API calls:
- Axios configuration with base URL
- Request/response interceptors
- Error handling utilities
- Loading state management

## Testing Strategy

1. **Backend Testing**: Test all API endpoints with proper data validation
2. **Frontend Integration**: Test all user flows with real backend data
3. **Error Scenarios**: Test network failures and invalid data handling
4. **Performance**: Test with large datasets and concurrent users

## Database Seeding

Migration script to populate MongoDB with current mock data:
- Convert mock.js data to proper MongoDB documents
- Add timestamps and validation
- Create indexes for search optimization
- Ensure data consistency and relationships