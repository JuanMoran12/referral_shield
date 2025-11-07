# API Testing Examples

This file contains examples for testing your referral fraud detection API.

## Current Database Contents

Your database now contains **25 referrals** from **9 different referrers**:

### Active Referrers:
1. **spammer@gmail.com** - 10 referrals (AT LIMIT ⚠️)
2. **sarah.johnson@techcorp.com** - 2 referrals
3. **john.martinez@business.org** - 2 referrals
4. **david.lee@enterprise.com** - 2 referrals
5. **robert.taylor@services.com** - 2 referrals
6. **anna.wilson@media.com** - 2 referrals
7. **jennifer.adams@finance.net** - 2 referrals
8. **maria.garcia@consulting.io** - 1 referral
9. **lisa.chen@global.net** - 1 referral
10. **carlos.rodriguez@tech.org** - 1 referral

---

## Test Scenarios

### ✅ Valid Referral (Should Succeed)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "new.user@company.com", "referee_email": "friend@example.net"}'
```
**Expected:** Success message

---

### ❌ Fraud Test 1: Same Person (Self-Referral)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "alice@test.com", "referee_email": "alice@test.com"}'
```
**Expected:** "Fraude: el referee no puede ser el mismo referrer."

---

### ❌ Fraud Test 2: Alias Bypass with + (Should be Blocked)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "alice@gmail.com", "referee_email": "alice+1@gmail.com"}'
```
**Expected:** "Fraude: el referee no puede ser el mismo referrer."

---

### ❌ Fraud Test 3: Gmail Dot Bypass (Should be Blocked)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "alice@gmail.com", "referee_email": "a.l.i.c.e@gmail.com"}'
```
**Expected:** "Fraude: el referee no puede ser el mismo referrer."

---

### ❌ Fraud Test 4: Duplicate Referee
Try to refer someone who's already in the database:
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "new@test.com", "referee_email": "mike.wilson@startup.io"}'
```
**Expected:** "Fraude: el referee ya está registrado."

---

### ❌ Fraud Test 5: Duplicate with Alias (Should be Blocked)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "new@test.com", "referee_email": "mike.wilson+test@startup.io"}'
```
**Expected:** "Fraude: el referee ya está registrado."

---

### ❌ Fraud Test 6: Suspicious Email Pattern
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "valid@real.com", "referee_email": "test@example.com"}'
```
**Expected:** "Fraude: el email del referee parece inválido o sospechoso."

---

### ❌ Fraud Test 7: Temporary Email Service
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "valid@real.com", "referee_email": "user@mailinator.com"}'
```
**Expected:** "Fraude: el email del referee parece inválido o sospechoso."

---

### ❌ Fraud Test 8: Referral Limit Exceeded
Try to make an 11th referral from spammer@gmail.com (already at 10):
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "spammer@gmail.com", "referee_email": "newvictim@email.com"}'
```
**Expected:** "Fraude: el referrer ha excedido el límite de 10 referrals."

---

### ❌ Fraud Test 9: Limit Bypass with Alias (Should be Blocked)
```bash
curl -X POST http://localhost:5000/referral \
  -H "Content-Type: application/json" \
  -d '{"referrer_email": "spammer+new@gmail.com", "referee_email": "newvictim@email.com"}'
```
**Expected:** "Fraude: el referrer ha excedido el límite de 10 referrals."

---

## Batch Testing Script

Create multiple test referrals at once:

```bash
# Add 5 more referrals from different users
for i in {1..5}; do
  curl -s -X POST http://localhost:5000/referral \
    -H "Content-Type: application/json" \
    -d "{\"referrer_email\": \"batch.user${i}@test.com\", \"referee_email\": \"batch.friend${i}@email.com\"}"
  echo ""
done
```

---

## View Database Contents

Check the current database:
```bash
cat referrals.csv
```

Or count referrals:
```bash
# Total referrals
wc -l referrals.csv

# Count unique referrers
tail -n +2 referrals.csv | cut -d',' -f1 | sort | uniq | wc -l

# Count unique referees
tail -n +2 referrals.csv | cut -d',' -f2 | sort | uniq | wc -l
```

---

## Configuration

To change the referral limit, edit `MAX_REFERRALS_PER_USER` in `main.py`:
```python
MAX_REFERRALS_PER_USER = 10  # Change this number
```
