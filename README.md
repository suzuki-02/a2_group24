# Event Management Progress Update

## Current Routes
- **View Event**  
  `/events/{id}` → Show individual event page with details and comments

- **Create Event**  
  `/events/create` → Form to create a new event (supports image upload)

- **Add Comment**  
  `/events/{id}/comment` → Post a new comment for a specific event

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
