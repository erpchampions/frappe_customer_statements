# Testing Checklist

## Multi-Party Type Statement of Accounts - Comprehensive Testing Guide

---

## Pre-Testing Setup

### Environment Preparation
- [ ] ERPNext v15 instance running
- [ ] App installed successfully
- [ ] Database migrated (custom fields created)
- [ ] Cache cleared
- [ ] Bench restarted
- [ ] Test data available (Customers, Suppliers, Employees)

### Verification Steps
- [ ] Process Statement of Accounts Party doctype exists
- [ ] Custom fields visible in Process Statement of Accounts
- [ ] JS file loading without errors (check browser console)
- [ ] Python controller override active (no import errors)

---

## Test Suite 1: Backward Compatibility (Default Mode)

### Test 1.1: Standard Customer Workflow
**Objective:** Verify 100% backward compatibility with ERPNext core

**Steps:**
1. [ ] Open Process Statement of Accounts
2. [ ] Create new document
3. [ ] Verify `enable_multi_party_type` is **unchecked** by default
4. [ ] Verify standard customer fields are visible:
   - [ ] Customer Collection
   - [ ] Collection Name
   - [ ] Customers table
   - [ ] Fetch Customers button
5. [ ] Select Customer Collection: "Customer Group"
6. [ ] Select a Customer Group (e.g., "Commercial")
7. [ ] Click "Fetch Customers"
8. [ ] Verify customers populate in table
9. [ ] Set From Date / To Date
10. [ ] Select Report: "General Ledger"
11. [ ] Click "Download"
12. [ ] Verify PDF generates successfully
13. [ ] Open PDF and verify:
   - [ ] Shows "For: [Customer Name]" (not "Customer:")
   - [ ] Transactions display correctly
   - [ ] Aging summary present
   - [ ] Company letterhead shows

**Expected Result:** Works exactly like standard ERPNext (no regression)

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Notes:**
```
[Add any observations or issues here]
```

---

### Test 1.2: Accounts Receivable - Default Mode
**Objective:** Verify AR report works in default mode

**Steps:**
1. [ ] Create new Process Statement of Accounts
2. [ ] Leave multi-party flag **unchecked**
3. [ ] Fetch customers by Territory
4. [ ] Select Report: "Accounts Receivable"
5. [ ] Set Report Date
6. [ ] Enable "Show Future Payments"
7. [ ] Click "Download"
8. [ ] Verify PDF shows:
   - [ ] Aging buckets (0-30, 30-60, etc.)
   - [ ] Customer LPO column (if applicable)
   - [ ] Outstanding amounts
   - [ ] Future payments section

**Expected Result:** Standard AR report functionality

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 2: Customer Mode (Enhanced)

### Test 2.1: Multi-Party Mode with Customer
**Objective:** Verify multi-party mode produces identical output for Customers

**Steps:**
1. [ ] Create new Process Statement of Accounts
2. [ ] **Check** "Enable Multi-Party Type Statements"
3. [ ] Verify field visibility changes:
   - [ ] Old customer fields **hidden**
   - [ ] New party fields **visible**
4. [ ] Verify Party Type defaults to "Customer"
5. [ ] Select Fetch Parties By: "Customer Group"
6. [ ] Verify Party Collection options show:
   - [ ] Customer Group
   - [ ] Territory
   - [ ] Sales Partner
   - [ ] Sales Person
7. [ ] Select Collection Name: [same group as Test 1.1]
8. [ ] Click "Fetch Parties"
9. [ ] Verify parties table populates with same customers
10. [ ] Verify party_type = "Customer" for all rows
11. [ ] Download General Ledger report
12. [ ] Compare PDF with Test 1.1 output
13. [ ] Verify identical content (except "Customer:" label)

**Expected Result:** Same data, enhanced mode works for Customers

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Notes:**
```

```

---

### Test 2.2: Customer - Territory Based Fetch
**Objective:** Verify territory-based hierarchical fetching

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Customer
3. [ ] Fetch Parties By: "Territory"
4. [ ] Select a parent territory with child territories
5. [ ] Click "Fetch Parties"
6. [ ] Verify all customers from parent and child territories are fetched
7. [ ] Download statements
8. [ ] Verify all fetched customers have statements

**Expected Result:** Hierarchical territory fetching works

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 2.3: Customer - Sales Person Based Fetch
**Objective:** Verify sales person based fetching

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Customer
3. [ ] Fetch Parties By: "Sales Person"
4. [ ] Select a Sales Person with assigned customers
5. [ ] Click "Fetch Parties"
6. [ ] Verify only customers with that sales person appear
7. [ ] Download statements

**Expected Result:** Sales person filtering works correctly

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 3: Supplier Mode (Primary Requirement)

### Test 3.1: Supplier - General Ledger
**Objective:** Verify supplier statement generation (core requirement)

**Steps:**
1. [ ] Create new Process Statement of Accounts
2. [ ] Enable multi-party type
3. [ ] Select Party Type: "Supplier"
4. [ ] Verify Fetch Parties By options show:
   - [ ] Supplier Group
   - [ ] Supplier Type
5. [ ] Select "Supplier Group"
6. [ ] Select a Supplier Group with suppliers
7. [ ] Click "Fetch Parties"
8. [ ] Verify suppliers populate in parties table
9. [ ] Verify party_type = "Supplier" for all rows
10. [ ] Set From Date / To Date
11. [ ] Select Report: "General Ledger"
12. [ ] Click "Download"
13. [ ] Open PDF and verify:
   - [ ] Header shows "Supplier:" not "Customer:"
   - [ ] Supplier name displays correctly
   - [ ] Purchase invoices show in transactions
   - [ ] Payment entries show
   - [ ] Debit/Credit columns correct (reversed from customer)
   - [ ] Balance calculation correct
   - [ ] Aging summary shows
   - [ ] No "Customer LPO" field

**Expected Result:** Supplier statement generates correctly

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Notes:**
```

```

---

### Test 3.2: Supplier - Supplier Type Based Fetch
**Objective:** Verify supplier type filtering

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Supplier
3. [ ] Fetch Parties By: "Supplier Type"
4. [ ] Select "Raw Material" supplier type (or similar)
5. [ ] Click "Fetch Parties"
6. [ ] Verify only suppliers of that type are fetched
7. [ ] Download statements
8. [ ] Verify correct supplier data

**Expected Result:** Supplier type filtering works

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 3.3: Supplier - Aging Calculation
**Objective:** Verify supplier aging is calculated correctly

**Steps:**
1. [ ] Fetch suppliers
2. [ ] Enable "Include Ageing"
3. [ ] Set Ageing Based On: "Posting Date"
4. [ ] Download statements
5. [ ] Verify aging summary shows in PDF
6. [ ] Verify aging buckets calculated based on posting date
7. [ ] Cross-check with Accounts Payable report in ERPNext
8. [ ] Verify amounts match

**Expected Result:** Supplier aging matches AP report

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 3.4: Supplier - Multiple Suppliers
**Objective:** Verify batch processing for multiple suppliers

**Steps:**
1. [ ] Fetch 5+ suppliers from a supplier group
2. [ ] Download statements
3. [ ] Verify:
   - [ ] PDF contains separate statements for each supplier
   - [ ] Page breaks between suppliers
   - [ ] Each supplier's data is isolated (no mixing)
   - [ ] All 5+ statements generated

**Expected Result:** Multiple supplier statements in single PDF

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 4: Employee Mode

### Test 4.1: Employee - Department Based
**Objective:** Verify employee statement generation

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Employee
3. [ ] Verify Fetch Parties By options:
   - [ ] Department
   - [ ] Branch
   - [ ] Employment Type
4. [ ] Select "Department"
5. [ ] Choose a department (e.g., "Accounts")
6. [ ] Fetch parties
7. [ ] Verify employees from that department populate
8. [ ] Download General Ledger
9. [ ] Verify:
   - [ ] Header shows "Employee:"
   - [ ] Employee name displays
   - [ ] Transactions show (if any GL entries exist)

**Expected Result:** Employee statements work

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Notes:**
```

```

---

### Test 4.2: Employee - Branch Based
**Objective:** Verify branch-based employee fetching

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Employee
3. [ ] Fetch Parties By: "Branch"
4. [ ] Select a branch
5. [ ] Fetch parties
6. [ ] Verify only employees from that branch appear
7. [ ] Download statements

**Expected Result:** Branch filtering works

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 5: Field Visibility & UI Behavior

### Test 5.1: Field Show/Hide Logic
**Objective:** Verify fields show/hide correctly based on flag

**Steps:**
1. [ ] Create new document
2. [ ] Verify multi-party flag is unchecked
3. [ ] Verify customer fields visible, party fields hidden
4. [ ] Check the multi-party flag
5. [ ] Verify immediate changes:
   - [ ] Customer fields hide
   - [ ] Party fields show
6. [ ] Uncheck the flag
7. [ ] Verify fields revert to original state

**Expected Result:** Field visibility toggles correctly

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 5.2: Party Type Change Behavior
**Objective:** Verify UI updates when party type changes

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Select Party Type: Customer
3. [ ] Note the Fetch Parties By options
4. [ ] Change to Party Type: Supplier
5. [ ] Verify Fetch Parties By options change to Supplier options
6. [ ] Verify parties table clears
7. [ ] Verify collection name clears
8. [ ] Change to Employee
9. [ ] Verify options update again

**Expected Result:** Dynamic options update per party type

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 5.3: Manual Party Addition
**Objective:** Verify manual row addition in parties table

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Set Party Type: Supplier
3. [ ] Manually add a row in parties table
4. [ ] Verify party_type auto-fills as "Supplier"
5. [ ] Select a supplier in the party field
6. [ ] Verify party_name auto-fills
7. [ ] Verify primary_email auto-fills (if exists)
8. [ ] Download statement for that one supplier

**Expected Result:** Manual party addition works

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 6: Email Functionality

### Test 6.1: Email - Customer (Default Mode)
**Objective:** Verify email works in default mode

**Steps:**
1. [ ] Create statement in default mode
2. [ ] Fetch customers
3. [ ] Enable "Enable Auto Email"
4. [ ] Configure sender email
5. [ ] Set subject and body
6. [ ] Click "Send Emails"
7. [ ] Verify emails sent to customers
8. [ ] Check email content (PDF attached, correct recipient)

**Expected Result:** Emails send correctly in default mode

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 6.2: Email - Supplier (Enhanced Mode)
**Objective:** Verify email works for suppliers

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Party Type = Supplier
3. [ ] Fetch suppliers
4. [ ] Enable auto email
5. [ ] Configure email settings
6. [ ] Send emails
7. [ ] Verify suppliers receive their statements
8. [ ] Verify email addresses pulled from supplier records

**Expected Result:** Supplier emails work

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 7: Edge Cases & Error Handling

### Test 7.1: Empty Party List
**Objective:** Handle case with no parties fetched

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Select a collection with no parties
3. [ ] Click "Fetch Parties"
4. [ ] Verify appropriate message shown
5. [ ] Verify no error occurs
6. [ ] Try to download (should error or warn)

**Expected Result:** Graceful handling of empty results

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 7.2: Party with No Transactions
**Objective:** Handle parties with no GL entries

**Steps:**
1. [ ] Fetch a supplier with no purchase history
2. [ ] Download statement
3. [ ] Verify:
   - [ ] PDF generates
   - [ ] Shows party name
   - [ ] Shows "No transactions" or empty table
   - [ ] No Python errors

**Expected Result:** Handles no-transaction case gracefully

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 7.3: Mixed Data Validation
**Objective:** Ensure data isolation between party types

**Steps:**
1. [ ] Create statement with Customer party type
2. [ ] Fetch customers
3. [ ] Save document
4. [ ] Reopen document
5. [ ] Change party type to Supplier (without refetching)
6. [ ] Verify warning or error
7. [ ] OR verify parties table clears

**Expected Result:** Prevents data inconsistency

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

### Test 7.4: Missing Required Fields
**Objective:** Verify validation of required fields

**Steps:**
1. [ ] Enable multi-party mode
2. [ ] Leave party type blank
3. [ ] Try to fetch parties
4. [ ] Verify error: "Please select Party Type"
5. [ ] Set party type but leave collection blank
6. [ ] Try to fetch
7. [ ] Verify error: "Please select Fetch Parties By"

**Expected Result:** Proper validation messages

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 8: Performance & Scalability

### Test 8.1: Large Party List
**Objective:** Test with 100+ parties

**Steps:**
1. [ ] Fetch a large supplier group (100+ suppliers)
2. [ ] Note time to fetch
3. [ ] Note time to download PDF
4. [ ] Verify PDF size reasonable
5. [ ] Verify all suppliers included
6. [ ] Check for memory issues

**Expected Result:** Handles large lists without issues

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Performance Notes:**
```
Fetch time: ___ seconds
Download time: ___ seconds
PDF size: ___ MB
```

---

### Test 8.2: Date Range Performance
**Objective:** Test with large date ranges

**Steps:**
1. [ ] Fetch suppliers
2. [ ] Set From Date: 3 years ago
3. [ ] Set To Date: Today
4. [ ] Download statements
5. [ ] Verify reasonable performance
6. [ ] Verify data completeness

**Expected Result:** Large date range handled

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 9: Upgrade & Migration

### Test 9.1: Backward Compatibility After Upgrade
**Objective:** Ensure old documents still work

**Steps:**
1. [ ] Create document in default mode (pre-upgrade simulation)
2. [ ] Save document
3. [ ] Simulate app update (bench restart)
4. [ ] Reopen old document
5. [ ] Verify still works
6. [ ] Download statement
7. [ ] Verify output unchanged

**Expected Result:** Old documents unaffected

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Test Suite 10: Cross-Validation

### Test 10.1: GL Report Comparison
**Objective:** Verify statement matches ERPNext GL report

**Steps:**
1. [ ] Generate supplier statement for specific supplier
2. [ ] Note date range and filters
3. [ ] Open ERPNext > Reports > General Ledger
4. [ ] Apply same filters (supplier, dates, account)
5. [ ] Compare:
   - [ ] Transaction list matches
   - [ ] Amounts match
   - [ ] Balance matches
   - [ ] Debit/Credit totals match

**Expected Result:** 100% match with GL report

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

**Variance (if any):**
```

```

---

### Test 10.2: Aging Report Comparison
**Objective:** Verify aging matches ERPNext AR/AP

**Steps:**
1. [ ] Generate customer statement with aging
2. [ ] Open Accounts Receivable report
3. [ ] Filter for same customer and date
4. [ ] Compare aging buckets:
   - [ ] 0-30 days
   - [ ] 30-60 days
   - [ ] 60-90 days
   - [ ] 90-120 days
   - [ ] 120+ days
5. [ ] Repeat for supplier (Accounts Payable)

**Expected Result:** Aging matches core reports

**Status:** ⬜ Pass | ⬜ Fail | ⬜ Not Tested

---

## Summary Report

### Test Results Overview

| Test Suite | Tests Passed | Tests Failed | Not Tested | Pass Rate |
|-----------|--------------|--------------|------------|-----------|
| Suite 1: Backward Compatibility | | | | |
| Suite 2: Customer Mode | | | | |
| Suite 3: Supplier Mode | | | | |
| Suite 4: Employee Mode | | | | |
| Suite 5: Field Visibility | | | | |
| Suite 6: Email | | | | |
| Suite 7: Edge Cases | | | | |
| Suite 8: Performance | | | | |
| Suite 9: Upgrade | | | | |
| Suite 10: Cross-Validation | | | | |
| **TOTAL** | | | | |

### Critical Issues Found
```
[List any blocking issues here]
```

### Non-Critical Issues Found
```
[List minor issues here]
```

### Recommendations
```
[Testing recommendations and next steps]
```

### Sign-Off

**Tester Name:** _______________
**Date:** _______________
**Status:** ⬜ Approved for Production | ⬜ Needs Fixes | ⬜ Blocked

---

## Notes

- Mark each checkbox as you complete the test
- Document any deviations from expected results
- Capture screenshots for visual issues
- Log Python errors with full stack trace
- Test in both development and staging environments before production
