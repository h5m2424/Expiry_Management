# Expiry_Management
Help you manage the expiration time of various documents.

## Project Setup

1. Prepare before running the project:
   - Modify the database server IP (`expiry/expiry_api/config/config.ini`).
   - Modify the frontend and backend API server IP (`nginx/config/conf.d/default.conf`).

2. Run the project using the following command:
   
```bash
docker-compose up -d
```
3. Access the project at the following URL:   
http://nginxIP/expiry

4. Project Features:
- Manage (add, delete, and view) document names and expiration dates on the web page. The list is sorted in descending order based on the expiration date.
- Receive email alerts when the expiration date is approaching (under development).

5. Project Screenshots
