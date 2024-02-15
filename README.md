# IVF Clinic Management API

A Django REST API for an **IVF (In Vitro Fertilization) clinic** mobile app, featuring patient health tracking, DASS psychological assessments, and a staff CRM dashboard.

## Tech Stack

- **Django** + **Django REST Framework**
- **PostgreSQL** - Patient data storage
- **AWS S3** - Presigned URLs for profile image uploads
- **DASS-21** - Depression Anxiety Stress Scale scoring algorithm
- **Expo Push Notifications** - Mobile push notifications
- **Multi-language** - English, Serbian, Russian, Chinese

## Features

- **Patient Portal** - Registration, login, health profile management
- **DASS Psychological Tests** - Automated scoring with severity classification
- **Menstrual Cycle Tracking** - Period dates with ordinal tracking
- **Push Notifications** - Cycle reminders, test reminders via Expo
- **S3 Image Upload** - Presigned URLs for secure profile photo uploads
- **Staff CRM** - Dashboard for clinic admins to manage patients and notes
- **4-Language Support** - Full i18n with translation management

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/login` | Patient authentication |
| POST | `/api/logout` | End session |
| GET | `/api/user_data?token=` | Get patient profile |
| PUT | `/api/edit_client` | Update patient info |
| POST | `/api/dass_test_results` | Submit DASS test |
| POST | `/api/generate_signed_url` | Get S3 upload URL |
| GET | `/api/translations` | Multi-language strings |
| POST | `/api/crm/login` | Staff authentication |
| GET | `/api/crm/dashboard` | Staff dashboard |
| GET | `/api/crm/client/<id>/` | Patient detail view |
