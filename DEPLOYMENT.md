# Deployment Guide

This guide covers deploying the Anthropic Mastery platform using:

- **Vercel** for the React frontend
- **Render** for the Flask backend
- **MongoDB Atlas** for the database

## Prerequisites

Before deploying, ensure you have:

- GitHub repository with your code
- Vercel account
- Render account
- MongoDB Atlas account
- Anthropic API key

## 1. MongoDB Atlas Setup

### Create Database Cluster

1. Log into [MongoDB Atlas](https://cloud.mongodb.com/)
2. Create a new cluster (M0 Sandbox tier is free)
3. Choose your preferred cloud provider and region
4. Wait for cluster creation (5-10 minutes)

### Configure Database Access

1. Go to **Database Access** → **Add New Database User**
2. Create a user with **Read and write to any database** permissions
3. Note down the username and password

### Configure Network Access

1. Go to **Network Access** → **Add IP Address**
2. Add `0.0.0.0/0` to allow access from anywhere (for Render deployment)
3. Or add specific Render IP ranges for better security

### Get Connection String

1. Click **Connect** on your cluster
2. Choose **Connect your application**
3. Copy the connection string (it will look like: `mongodb+srv://username:password@cluster.mongodb.net/`)

## 2. Backend Deployment (Render)

### Deploy to Render

1. Log into [Render](https://render.com/)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `anthropic-mastery-backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --bind 0.0.0.0:$PORT app:app`
   - **Instance Type**: Free tier is sufficient for testing

### Set Environment Variables

In Render dashboard, go to **Environment** and add:

```
FLASK_ENV=production
FLASK_DEBUG=false
SECRET_KEY=your-production-secret-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here
MONGODB_URI=mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/claude_db?retryWrites=true&w=majority
MONGODB_DB=claude_db
APP_HOST=0.0.0.0
APP_PORT=10000
BACKGROUND_CLUSTERING_ENABLED=true
CLUSTERING_MESSAGE_THRESHOLD=1
CLUSTERING_TIME_THRESHOLD_MINUTES=5
```

### Deploy

1. Click **Create Web Service**
2. Wait for deployment to complete
3. Note the service URL (e.g., `https://anthropic-mastery-backend.onrender.com`)

## 3. Frontend Deployment (Vercel)

### Deploy to Vercel

1. Log into [Vercel](https://vercel.com/)
2. Click **New Project**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### Set Environment Variables

In Vercel dashboard, go to **Settings** → **Environment Variables** and add:

```
VITE_API_BASE_URL=https://your-render-backend-url.onrender.com
```

Replace `your-render-backend-url` with your actual Render service URL.

### Deploy

1. Click **Deploy**
2. Wait for deployment to complete
3. Note the deployment URL (e.g., `https://your-project.vercel.app`)

## 4. Update Backend CORS Settings

After deploying the frontend, update your backend's CORS configuration:

1. In Render dashboard, go to **Environment Variables**
2. Add a new variable:
   ```
   VERCEL_DOMAIN=your-project.vercel.app
   ```
3. Redeploy the backend service

## 5. Testing the Deployment

### Backend Health Check

Visit your backend URL + `/health`:

```
https://your-backend.onrender.com/health
```

Should return:

```json
{
  "status": "healthy",
  "service": "claude_backend",
  "version": "1.0.0"
}
```

### Frontend Test

1. Visit your Vercel deployment URL
2. Try creating a new conversation
3. Verify that messages are being sent and received
4. Check browser developer tools for any API errors

## 6. Common Issues and Solutions

### Backend Issues

**MongoDB Connection Errors**

- Verify connection string format
- Check username/password
- Ensure network access is configured for `0.0.0.0/0`

**CORS Errors**

- Verify `VERCEL_DOMAIN` environment variable is set
- Check that frontend URL matches the CORS configuration

**Anthropic API Errors**

- Verify API key is correct
- Check API key has sufficient credits

### Frontend Issues

**API Connection Errors**

- Verify `VITE_API_BASE_URL` points to correct backend URL
- Check backend is running and accessible

**Build Errors**

- Ensure all dependencies are in `package.json`
- Check TypeScript compilation errors

## 7. Environment Variables Reference

### Backend (Render)

| Variable            | Description               | Example                                                                   |
| ------------------- | ------------------------- | ------------------------------------------------------------------------- |
| `FLASK_ENV`         | Flask environment         | `production`                                                              |
| `SECRET_KEY`        | Flask secret key          | `your-secret-key`                                                         |
| `ANTHROPIC_API_KEY` | Anthropic API key         | `sk-ant-...`                                                              |
| `MONGODB_URI`       | MongoDB connection string | `mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/claude_db...` |
| `MONGODB_DB`        | Database name             | `claude_db`                                                               |
| `VERCEL_DOMAIN`     | Frontend domain           | `your-project.vercel.app`                                                 |

### Frontend (Vercel)

| Variable            | Description     | Example                             |
| ------------------- | --------------- | ----------------------------------- |
| `VITE_API_BASE_URL` | Backend API URL | `https://your-backend.onrender.com` |

## 8. Monitoring and Maintenance

### Render Monitoring

- Check service logs in Render dashboard
- Monitor service health and uptime
- Set up alerts for service failures

### Vercel Monitoring

- Monitor deployment status
- Check function logs for errors
- Review analytics and performance metrics

### MongoDB Atlas Monitoring

- Monitor database performance
- Check connection limits
- Review query performance

## 9. Scaling Considerations

### Backend Scaling

- Upgrade Render instance type for better performance
- Consider using Redis for session storage
- Implement database connection pooling

### Frontend Scaling

- Vercel automatically handles CDN and scaling
- Consider implementing caching strategies
- Optimize bundle size for better performance

### Database Scaling

- Monitor MongoDB Atlas metrics
- Upgrade cluster tier as needed
- Implement proper indexing for better query performance

## 10. Security Best Practices

### Environment Variables

- Never commit secrets to version control
- Use strong, unique passwords
- Rotate API keys regularly

### Network Security

- Restrict MongoDB network access to specific IPs when possible
- Use HTTPS for all communications
- Implement proper CORS policies

### Application Security

- Keep dependencies updated
- Implement proper input validation
- Use secure session management

## Support

If you encounter issues during deployment:

1. Check the service logs in respective dashboards
2. Verify all environment variables are set correctly
3. Test each service independently
4. Review the common issues section above

For additional help, consult the documentation for:

- [Render Documentation](https://render.com/docs)
- [Vercel Documentation](https://vercel.com/docs)
- [MongoDB Atlas Documentation](https://docs.atlas.mongodb.com/)
