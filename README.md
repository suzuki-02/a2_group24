# Event Management Progress Update

## Current Routes
- **User Authentication**
  - `/register` → Register a new user (first name, surname, email, password, contact number, street address)
  - `/login` → Login with email + password
  - `/logout` → Logout the current user

- **Events**
  - `/events/{id}` → Show individual event page with details and comments
  - `/events/create` → Form to create a new event (supports image upload)
  - `/events/{id}/comment` → Post a new comment for a specific event

---

## Database Notes
- The database file is stored at:  
  `instance/sitedata.sqlite`

- **Important:**  
  Whenever you modify `models.py` (add or change classes/fields), you need to:
  1. Delete the existing DB file  
     ```
     instance/sitedata.sqlite
     ```
  2. Recreate the database by running:  
     ```
     python create_at.py
     ```

- ⚠️ **Warning:**  
  Doing this will **erase all existing data**  
  (users, events, comments, etc.).

---
