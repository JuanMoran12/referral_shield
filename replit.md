# Referral Fraud Detection API

## Overview

This is a FastAPI-based referral system that validates referrals and detects fraudulent submissions. Users can submit a referrer email and referee email, and the system checks for various fraud patterns before storing the referral in a CSV database. The application includes basic anti-fraud measures such as duplicate detection, suspicious email pattern matching, and same-person validation.

**Last Updated**: November 6, 2025

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture

**Framework: FastAPI**
- **Rationale**: FastAPI provides automatic API documentation, built-in request validation, and async support
- **Pros**: Fast performance, automatic OpenAPI schema generation, type hints for better code quality
- **Cons**: CSV storage has limitations for concurrent access and scalability

**Data Validation**
- **Solution**: Pydantic models with EmailStr validation
- **Problem Addressed**: Ensures email format correctness before processing
- **Implementation**: `ReferralRequest` model validates both referrer and referee emails at the request level
- **Normalization**: All emails are converted to lowercase and trimmed before processing

### Fraud Detection System

**Anti-Fraud Measures Implemented:**

1. **Email Normalization (Anti-Bypass Protection)**
   - Prevents alias bypasses using + suffix (e.g., `user+1@gmail.com` → `user@gmail.com`)
   - Removes dots from Gmail addresses (e.g., `u.ser@gmail.com` → `user@gmail.com`)
   - Applied to both referrer and referee emails before all fraud checks
   - **Protects against**: Self-referral bypasses, duplicate detection bypasses, referral limit bypasses

2. **Same Person Detection**
   - Prevents users from referring themselves
   - Compares normalized emails: `normalize(referrer) == normalize(referee)`
   - **Blocks**: `user@gmail.com` referring `user+1@gmail.com`

3. **Referral Limit Enforcement**
   - Maximum of 10 referrals per person (configurable via `MAX_REFERRALS_PER_USER`)
   - Counts referrals using normalized referrer email
   - **Prevents**: Spam abuse using alias rotation (`spammer+1@gmail.com`, `spammer+2@gmail.com`, etc.)

4. **Suspicious Email Pattern Detection**
   - Blocks common test/temporary email patterns
   - Current patterns: `test@`, `fake@`, `temp@`, `mailinator`, `example.com`
   - Simple substring matching

5. **Duplicate Referee Detection**
   - Prevents the same referee from being registered multiple times
   - Uses normalized email comparison
   - **Blocks**: `bob@gmail.com` and `bob+1@gmail.com` as duplicates

**Fraud Detection Flow:**
1. Normalize both referrer and referee emails (remove +suffix, remove dots for Gmail)
2. Check if normalized referrer == normalized referee (same person)
3. Check if referrer has exceeded referral limit (using normalized email count)
4. Validate email pattern for suspicious domains
5. Check if normalized referee already exists in database
6. If all checks pass, store normalized emails in CSV

### Data Storage

**CSV-Based Storage**
- **File**: `referrals.csv`
- **Format**: Two columns - `referrer_email`, `referee_email`
- **Auto-creation**: File is created automatically with headers if not exists
- **Persistence**: Data persists across server restarts

**Trade-offs:**
- **Pros**: Simple, human-readable, easy to inspect and export
- **Cons**: 
  - No file locking (concurrent writes may corrupt data)
  - O(n) lookup performance (slows down as data grows)
  - No indexing for fast duplicate detection
  - Not suitable for high-traffic production use

### API Design

**RESTful Endpoints**
- `/referral` (POST): Submit referrer and referee emails with fraud checking

**Request Format:**
```json
{
  "referrer_email": "user@example.com",
  "referee_email": "friend@example.com"
}
```

**Response Structure:**
- Success (200): `{"message": "Referral registrado exitosamente."}`
- Fraud detected (400): `{"detail": "Fraude: [specific fraud reason]"}`

**Fraud Error Messages:**
- "Fraude: el referee no puede ser el mismo referrer." - Same person
- "Fraude: el email del referee parece inválido o sospechoso." - Suspicious pattern
- "Fraude: el referee ya está registrado." - Duplicate referee

## Known Limitations & Improvement Opportunities

### Critical Issues (Identified by Code Review)

1. **Concurrency Safety** ⚠️ UNRESOLVED
   - CSV writes lack file locking
   - Multiple simultaneous requests can corrupt the database
   - **Recommendation**: Add file locking or migrate to SQLite

2. **Performance** ⚠️ UNRESOLVED
   - Duplicate checking scans entire CSV file (O(n) complexity)
   - Referral counting also scans entire CSV (O(n) per request)
   - Will become slow as referral count grows
   - **Recommendation**: Use indexed database or in-memory cache

3. **Email Alias Bypasses** ✅ FIXED
   - ~~No protection against email aliases (user+1@gmail.com, user+2@gmail.com)~~
   - **Fixed**: Email normalization now removes + suffixes and dots in Gmail addresses
   - **Prevents**: Self-referral bypasses, duplicate bypasses, referral limit bypasses

4. **Referral Limits** ✅ FIXED
   - ~~Same referrer can submit unlimited referrals~~
   - **Fixed**: Max 10 referrals per person (configurable via `MAX_REFERRALS_PER_USER`)
   - **Prevents**: Spam abuse and incentive program exploitation

5. **Disposable Email Detection** ⚠️ LIMITED
   - Static pattern list only blocks a few common patterns
   - No detection for hundreds of disposable email services (10minutemail, guerrillamail, etc.)
   - **Recommendation**: Use comprehensive disposable email blocklist or paid API service

### Suggested Enhancements

- ✅ **COMPLETED**: Email normalization to prevent alias bypasses
- ✅ **COMPLETED**: Referral limits per user
- Add database migration to PostgreSQL or SQLite for better performance and concurrency
- Add file locking for CSV writes to prevent corruption
- Implement rate limiting per IP address
- Add logging for fraud attempts and analytics
- Create admin dashboard to review flagged referrals
- Implement email verification (send confirmation emails)
- Add referral tracking codes/links instead of raw email collection
- Expand disposable email detection with comprehensive blocklist

## External Dependencies

### Core Dependencies

**FastAPI**
- Purpose: Web framework and API routing
- Features Used: Request validation, automatic documentation, exception handling

**Pydantic**
- Purpose: Data validation and serialization
- Features Used: `BaseModel` for request schemas, `EmailStr` for email validation

**email-validator**
- Purpose: Email validation for Pydantic's EmailStr type
- Features Used: Email format validation

**Uvicorn**
- Purpose: ASGI server for running FastAPI application
- Usage: Development server with auto-reload

**Python csv module**
- Purpose: CSV file reading and writing
- Features Used: CSV DictReader for checking duplicates, CSV writer for storing referrals

## Test Data

**test_emails.csv**
- Contains sample test cases for validating the fraud detection system
- Includes valid referrals, fraud cases, and edge cases
- Use this file to manually test various scenarios

## Future Integration Opportunities

- **Database**: PostgreSQL or SQLite for production-grade persistence
- **Email Service**: SendGrid, Mailgun, or AWS SES for verification emails
- **Fraud Detection**: Third-party email validation API (NeverBounce, ZeroBounce)
- **Analytics**: Track referral conversion rates and fraud patterns
- **Authentication**: Add API keys or OAuth for secure access
