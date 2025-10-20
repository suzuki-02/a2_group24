# Progress Update

## Current Routes
- **User Authentication**
  - `/register` → Register a new user (first name, surname, email, password, contact number, street address)
  - `/login` → Login with email + password
  - `/logout` → Logout the current user

- **Events**
  - `/events/{id}` → Show individual event page with details and comments
  - `/events/create` → Form to create a new event (supports image upload)
  - `/events/{id}/comment` → Post a new comment for a specific event
  - `/events/<id>/purchase` → Purchase tickets for an event
  - `/events/books` → Displays the logged-in user’s booking history
  - `/events/my_events` → Displays all events created by the logged-in user with **Update** and **Cancel** options
  - `/events/<id>/update` → Update event details (only accessible by the event creator)
  - `/events/<id>/cancel` → Cancel an event (only accessible by the event creator; action cannot be undone)

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
