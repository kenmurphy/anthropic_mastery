// MongoDB initialization script
db = db.getSiblingDB('claude_db');

// Create a user for the application
db.createUser({
  user: 'claude_user',
  pwd: 'claude_password',
  roles: [
    {
      role: 'readWrite',
      db: 'claude_db'
    }
  ]
});

// Create initial collections (optional)
db.createCollection('users');
db.createCollection('courses');
db.createCollection('threads');
db.createCollection('Thoughts');

print('Database initialized successfully');
