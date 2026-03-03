INSERT INTO users (name, email) VALUES
    ('Alice Johnson', 'alice@example.com'),
    ('Bob Smith', 'bob@example.com'),
    ('Carol White', 'carol@example.com');

INSERT INTO projects (name, description) VALUES
    ('Website Redesign', 'Redesigning the corporate website.'),
    ('Mobile App Launch', 'Launching the new iOS and Android mobile app.');

INSERT INTO tickets (title, description, status, priority, type, project_id, assignee_id) VALUES
    ('Update homepage UI', 'Make the homepage more modern.', 'DONE', 'HIGH', 'FEATURE', 1, 1),
    ('Fix login bug', 'Users cannot log in using Safari.', 'IN_REVIEW', 'CRITICAL', 'BUG', 1, 2),
    ('Setup Push Notifications', 'Integrate APNs and FCM.', 'IN_PROGRESS', 'MEDIUM', 'IMPROVEMENT', 2, 3),
    ('Draft Privacy Policy', 'Write the initial draft for privacy policy.', 'TODO', 'LOW', 'TASK', 2, 1),
    ('Optimize images', 'Compress all assets to improve load time.', 'TODO', 'MEDIUM', 'TASK', 1, NULL);
