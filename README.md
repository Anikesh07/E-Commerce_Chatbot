Comprehensive Project Report: E-commerce Chatbot Setup and Progress
Project Objective
Develop a machine learning–based e-commerce chatbot capable of comparing product prices, quality, and quantity across platforms, providing users with the best buying recommendations through natural language conversations.

Timeline and Key Actions
1. Environment Setup
Installed Python 3.10 to ensure compatibility with Rasa and other ML libraries, avoiding issues found with Python 3.13.

Created a virtual environment (.venv) for dependency isolation and project manageability.

2. Dependency Management
Installed essential packages:

Rasa (chatbot framework)

spaCy with English model (for NLP and entity recognition)

requests (to interact with APIs)

pandas and numpy (for data processing)

beautifulsoup4 and scrapy (optional, for web scraping if API lacks)

Addressed dependency conflicts by aligning package versions compatible with Rasa (numpy, pydantic, attrs).

3. Development Tools and Dependency Fixes
Resolved environment issues: pip missing, access denied errors, compatibility warnings.

Learned to create, activate, and manage the virtual environment effectively.

Set up version control basics and generated .gitignore for clean GitHub repositories.

4. Additional Enhancements
Investigated and prepared for speech capabilities:

Planning added SpeechRecognition, pyttsx3, and PyAudio for voice input/output features.

Advised installation method for PyAudio on Windows using prebuilt wheels to avoid build errors.

5. Awareness and Planning on Tools Not Used Yet
Understood usefulness of Git for version control — recommended immediate usage.

Learned about Docker containerization and why it is optional as a beginner.

Clarified database options: starting with SQLite (no external install) and scaling possibilities.

Recognized warnings related to SQLAlchemy 2.0 and pinned versions for stability.

Summary of Learnings
Set up a stable, compatible Python environment specialized for ML and chatbot development.

Managed package dependencies carefully to prevent conflicts.

Gained knowledge in using NLP tools and chatbot frameworks effectively.

Explored expanding chatbot capabilities with speech input/output.

Balanced beginner needs with professional standards, recommending gradual introduction of advanced tools like Git and Docker.

