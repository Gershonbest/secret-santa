# Secret Santa Web Application

A simple, secure web application for organizing Secret Santa events for church members. Built with FastAPI (Python backend) and server-side rendered HTML templates.

## Features

- **User Registration & Login**: Users can register with first name, last name, email, phone number, and password
- **User Dashboard**: View all registered users and see your assigned Secret Santa recipient
- **Admin Controls**: 
  - Open/close registration
  - Create random Secret Santa pairings
- **Secure Authentication**: Session-based authentication using JWT tokens
- **One-to-One Pairing**: Ensures each user is assigned to exactly one other user (no duplicates, no self-assignments)

## Tech Stack

- **Backend**: FastAPI
- **Frontend**: Jinja2 templates with Tailwind CSS
- **Database**: Remote database (PostgreSQL/MySQL/etc.) with SQLAlchemy ORM
- **Authentication**: JWT-based session authentication

## Installation

1. **Set up environment variables**:
   ```bash
   export DATABASE_URL="your_remote_database_url_here"
   ```
   Or create a `.env` file with:
   ```
   DATABASE_URL=your_remote_database_url_here
   ```
   
   **Note**: Make sure you have the appropriate database driver installed:
   - For PostgreSQL: `pip install psycopg2-binary`
   - For MySQL: `pip install pymysql` or `pip install mysql-connector-python`

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Create the first admin user**:
   ```bash
   python create_admin.py
   ```
   Follow the prompts to create your admin account.

4. **Run the application**:
   ```bash
   uvicorn main:app --reload
   ```

5. **Access the application**:
   Open your browser and navigate to `http://localhost:8000`

## Usage

### For Administrators

1. **Log in** with your admin credentials
2. **Manage Registration**:
   - Click "Lock Registration" to prevent new users from registering
   - Click "Open Registration" to allow new registrations
3. **Create Pairings**:
   - Once all users have registered, click "Create Pairings"
   - This will randomly assign each user to gift someone else
   - Pairings are permanent and cannot be undone

### For Regular Users

1. **Register** with your information (if registration is open)
2. **Log in** to access your dashboard
3. **View your assignment**: Once pairings are created, you'll see who you're gifting to
4. **View all users**: See the list of all registered participants

## Project Structure

```
santa-app/
├── main.py              # FastAPI application and routes
├── database.py          # Database models and setup
├── auth.py              # Authentication utilities
├── pairing.py           # Secret Santa pairing logic
├── create_admin.py      # Script to create admin user
├── templates/
│   ├── index.html       # Login/Registration page
│   └── dashboard.html   # User dashboard
├── pyproject.toml       # Project dependencies
└── README.md           # This file
```

## Database

The application uses a remote database configured via the `DATABASE_URL` environment variable. The database URL should be in the format:
- PostgreSQL: `postgresql://user:password@host:port/database`
- MySQL: `mysql+pymysql://user:password@host:port/database`

The database contains:
- **users**: User accounts with authentication info
- **pairings**: Secret Santa assignments (gifter_id → receiver_id)
- **settings**: Application settings (e.g., registration status)

## Security Notes

- Passwords are hashed using bcrypt
- JWT tokens are used for session management
- Admin-only endpoints are protected
- **Important**: Change the `SECRET_KEY` in `auth.py` before deploying to production!

## Development

To run in development mode with auto-reload:

```bash
uvicorn main:app --reload
```

The application will automatically reload when you make changes to the code.

