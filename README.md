# django_proj
Application for enrolling students in college in Django and PostgreSQL


### Prerequisites
Please refer to the requirements.txt file.

### Setup
1. Step-by-step instructions on how to install your project.
   - Clone the repository.
   - Navigate to the project directory.
   - Create and activate a virtual environment.
   - Install project dependencies using `pip install -r requirements.txt`.
2. Instructions on how to configure the .env file.
   - Create a .env file in the root directory of the project.
   - Add the SECRET_KEY and DATABASE_PASSWORD to the .env file.
3. Instructions on running create_courses.py.
   - Navigate to the `django_proj/proj/app` directory.
   - Run the `create_courses.py` script using Python.
   - **Note**: If running `create_courses.py` multiple times, ensure the script is adapted to prevent duplicate entries in the database.

## Usage Scenarios
### Student Registration:
- **Endpoint:** `POST /student/register/`
- **Data to Send:**
  - Name
  - Surname
  - Email
  - Password
- **Response:** Returns the user ID number upon successful registration.

### Professor Registration:
- **Endpoint:** `POST /professor/register/`
- **Data to Send:**
  - Name
  - Surname
  - Email
  - Password
- **Response:** Returns the user ID number upon successful registration.

### Login for Both Students and Professors:
- **Endpoint:** `POST /login/`
- **Data to Send:**
  - Email
  - Password
- **Response:** Returns the user id, refresh and access tokens upon successful login.

### Access Student Profile:
- **Endpoint:** `GET /student/<int:id>/profile/`
- **Authorization:** Include the JWT access token in the request headers.
- **Response:** Retrieves the student profile based on the provided ID.

### Update Student Profile:
- **Endpoint:** `POST /student/<int:id>/profile/`
- **Authorization:** Include the JWT access token in the request headers.
- **Data to Send:** Updated student profile data.
- **Response:** Updates the student profile with the provided data.

### Access Courses and Subjects for Student:
- **Endpoint:** `GET /student/<int:id>/courses/`
- **Authorization:** Include the JWT access token in the request headers.
- **Response:** Retrieves information about the courses and subjects available for the student based on their ID.

### Enroll in a Course for Student:
- **Endpoint:** `POST /student/<int:student_id>/course_enrollment/`
- **Authorization:** Include the JWT access token in the request headers.
- **Data to Send:**
  - Course ID
- **Response:** Enrolls the student in the specified course. If there is available space, enrollment is immediate. Otherwise, enrollment requires admin approval.

### Admin Approval for Course Enrollment:
- **Endpoint:** Admin Dashboard (/admin)
- **Authorization:** Accessible only by users with admin privileges.
- **Functionality:** Admin can review pending course enrollments and update their status to approved or rejected.

### Access Professor Profile:
- **Endpoint:** `GET /professor/<int:user_id>/profile/`
- **Authorization:** Include the JWT access token in the request headers.
- **Response:** Retrieves the professor profile based on the provided user ID.

### Update Professor Profile:
- **Endpoint:** `POST /professor/<int:user_id>/profile/`
- **Authorization:** Include the JWT access token in the request headers.
- **Data to Send:** Updated professor profile data.
- **Response:** Updates the professor profile with the provided data.

### Additional Notes:
- **Incomplete Functionalities:** Some functionalities such as creating a new admin or professor, viewing student data, and allowing students to select more than one course have not been fully implemented or tested!

## Token Refreshing

To refresh a token, you have two options:

1. **Using the Refresh Token Endpoint**:
   - Send your refresh token to the `/refresh/` endpoint.
   - The server will respond with a new access token if the refresh token is valid.
   - This is the recommended method as it allows you to refresh your token without logging in again.

2. **Logging in Again**:
   - You can also refresh your token by logging in again with your credentials.
   - This will generate a new access token and refresh token pair.
   - However, this method requires sending your credentials again and is less efficient than using the refresh token endpoint.
