# Admin Dashboard Implementation TODO

## Completed ✅
- [x] Update admin_dashboard.html with full UI (Monitor Users, Add Discussion, Generate Summary, Get Word Cloud)
- [x] Create static/css/admin_dashboard.css with gradient styling (#a5a58d, #b7b7a4)
- [x] Add Flask routes in app.py:
  - [x] /admin/monitor_users (GET: list users JSON, POST: delete user)
  - [x] /admin/add_discussion (POST: handle CSV upload to comments table)
  - [x] /admin/generate_summary (POST: placeholder for sentiment analysis)
  - [x] /admin/get_word_cloud (GET: placeholder for word cloud generation)
- [x] Implement Monitor Users feature (list users with delete functionality)
- [x] Implement Add Discussion feature (CSV upload with username, comment, discussion_topic columns)

## Pending ⏳
- [ ] Integrate sentiments.py for sentiment analysis
- [ ] Integrate summary.py for summary generation
- [ ] Implement Generate Summary feature (run sentiment analysis + store in sentiment_score table + generate summaries)
- [ ] Implement Get Word Cloud feature (generate word cloud from summaries table)
- [ ] Add word cloud generation dependencies (wordcloud, matplotlib, pillow)
- [ ] Test CSV upload functionality
- [ ] Test user deletion functionality
- [ ] Add proper error handling for database operations
- [ ] Add file validation for CSV uploads
- [ ] Implement word cloud image generation and serving
- [ ] Add progress indicators for long-running operations (sentiment analysis, summary generation)

## Notes
- Sentiments.py and summary.py need to be provided by user
- Word cloud will likely require additional Python libraries
- Database operations are implemented but need testing
- UI uses AJAX for dynamic user loading
- Gradients match the cool colors from register/login pages
