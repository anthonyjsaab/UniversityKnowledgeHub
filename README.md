# UniversityKnowledgeHub

# Video Demo: https://youtu.be/_HNXV63ucSk

## Description:

### About me

1. Anthony J. Saab
    
2. Final year engineering student at the American University of Beirut in Lebanon
    
3. Interested in Cybersecurity, Software, and Computer Networks
    
4. Loves CS50x :)
    

### About my project

1. Web Application developed with Python Framework Django
    
2. Meant to be used by university students for sharing learning resources (PDFs, Powerpoints, etc.)
    
3. Designed to centralize resource sharing between students. Instead of creating small, short-lived Whatsapp groups to share resources and deleting those groups at the end of the semester, students are invited to use this web app instead
    
4. Shared resources are organized, triaged, and democratized
    

### Django Details

* The authentication app takes care of logging in users using Microsoft. It makes use of the Microsoft Graph API described in the Microsoft docs.
    
* The storage\_conn app has some code to download files from AWS S3. Uploading is taken care of by Boto3.
    
* The uni\_data app has all the views and models that matter to the user.
    

### Deployment Details

* The website has the following CNAME: cs50x.anthonyjsaab.com
    
* Django running on Heroku Dynos
    
* Postgres database hosted on AWS RDS
    
* User files are uploaded/downloaded from an AWS S3 bucket
    

### Security by Design

* All secrets are fetched from environment variables. No secret is hardcoded.
    
* The authentication process is outsourced to Microsoft. The website is effectively passwordless since users can only sign in using their Microsoft accounts.
    
* The data minimization principle is followed.
    
* Names and emails are not revealed to the public.
    
* Admins can restrict which Fully-qualified domain names can be registered. For example, I can allow only people with a @mail.aub.edu email to register on my website. This setting is controlled by an environment variable.
    

### Improvements to be made

* Files should be sent to an antivirus API for checking before storing them. That way the website won't empower any watering hole attack.
    
* A system for voting files up and down should be implemented
    
* A system for voting users up and down should be implemented
    
* A chat system should be implemented
    
* A reporting system should be made available.
    
* An easy setup process should be developed to let the different universities deploy their own instances quickly and seamlessly. For example, course names should be customized.
