# Bronze Tier Testing Instructions

## Test 1: Filesystem Watcher

### Start the watcher:
```bash
python watchers/filesystem_watcher.py
```

### What you'll see:
```
[WATCHER] Monitoring: C:\Users\Pc\hackathon-0\AI_Employee_Vault\Inbox
[WATCHER] Output to: C:\Users\Pc\hackathon-0\AI_Employee_Vault\Needs_Action
------------------------------------------------------------
[STARTED] Filesystem watcher is running...
[INFO] Press Ctrl+C to stop
```

### Test it:
1. Keep the watcher running
2. Open another terminal/file explorer
3. Create a new file in `/Inbox` folder (any file: .txt, .md, .pdf, etc.)
4. Watch the console output:
   ```
   [COPIED] yourfile.txt -> File_yourfile.txt
   [METADATA] Created File_yourfile.txt.md
   ```

### Verify:
- Check `/Needs_Action` folder
- You should see:
  - `File_yourfile.txt` (the copied file)
  - `File_yourfile.txt.md` (metadata with YAML front matter)

### Stop the watcher:
Press `Ctrl+C`

---

## Test 2: Basic File Handler

### Run the skill:
```bash
python basic_file_handler.py
```

### What it does:
1. Lists all .md files in `/Needs_Action`
2. Processes the first file found
3. Creates a Plan.md in `/Plans`
4. Moves the file to `/Done`

### Expected output:
```
============================================================
BASIC FILE HANDLER - Starting Process
============================================================

📖 Checking Company Handbook rules...
✓ Rules loaded

📄 Reading file: [path]
✓ File summarized (X words, Y lines)

📝 Creating action plan...
✓ Plan created: [path]

📦 Moving file to Done...
✓ File moved: [path]

============================================================
✅ SUCCESS - Process Complete
============================================================
```

### Verify:
- Check `/Plans/Plan.md` - should contain action steps
- Check `/Done` - file should be moved there
- Original file removed from `/Needs_Action`

---

## Test 3: Task Analyzer (Advanced)

### Run the skill:
```bash
python task_analyzer.py
```

### What it does:
1. Analyzes file type (payment, communication, report, file_drop)
2. Checks for sensitive keywords
3. Extracts payment amounts
4. Determines if approval needed
5. Creates detailed action plan
6. Routes to `/Pending_Approval` if needed

### Expected output:
```
============================================================
TASK ANALYZER - Starting Analysis
============================================================

📄 Step 1: Reading file: [path]
✓ File read (X words)

🔍 Step 2: Identifying file type...
✓ Type identified: Payment Request

⚖️ Step 3: Checking if approval needed...
⚠️ APPROVAL REQUIRED
  - Contains sensitive keyword: 'payment'
  - Payment amount $750.00 exceeds threshold of $500

📋 Step 4: Creating multi-step action plan...
✓ 4 steps identified

📝 Step 5: Writing action plan...
✓ Plan created: [path]

⚠️ Step 6: Routing to Pending_Approval...
✓ Approval file created: [path]

============================================================
✅ SUCCESS - Analysis Complete
============================================================
```

### Verify:
- Check `/Plans/Plan.md` - detailed analysis with checkboxes
- Check `/Pending_Approval` - approval file if payment > $500
- File stays in `/Needs_Action` for human review

---

## Test 4: Complete End-to-End Workflow

### Step-by-step test:

1. **Start the watcher:**
   ```bash
   python watchers/filesystem_watcher.py
   ```

2. **Drop a test file in Inbox:**
   Create `Inbox/payment_request.md`:
   ```markdown
   # Payment Request

   Please process payment of $850 to vendor ABC Corp.
   Invoice #12345
   ```

3. **Watch the watcher process it:**
   - Should copy to `/Needs_Action/File_payment_request.md`
   - Should create `/Needs_Action/File_payment_request.md.md`

4. **Stop the watcher** (Ctrl+C)

5. **Run Task Analyzer:**
   ```bash
   python task_analyzer.py
   ```
   - Should detect payment type
   - Should flag for approval ($850 > $500)
   - Should create plan
   - Should route to Pending_Approval

6. **Verify results:**
   - `/Plans/Plan.md` exists with analysis
   - `/Pending_Approval/APPROVAL_NEEDED_File_payment_request.md` exists
   - Original file still in `/Needs_Action` awaiting approval

---

## Quick Test Commands

### Test watcher only:
```bash
python watchers/filesystem_watcher.py
# Drop file in Inbox, then Ctrl+C
```

### Test file handler:
```bash
echo "# Test" > Needs_Action/test.md
python basic_file_handler.py
```

### Test analyzer:
```bash
echo "# Payment Request\nPay $600 to vendor" > Needs_Action/payment.md
python task_analyzer.py
```

---

## Troubleshooting

### Watcher not detecting files:
- Make sure you're dropping files in `/Inbox` not `/Needs_Action`
- Wait 1-2 seconds after creating file
- Check console for error messages

### Skills not finding files:
- Make sure .md files exist in `/Needs_Action`
- Check file permissions
- Verify you're in the project root directory

### Import errors:
- Install watchdog: `pip install watchdog`
- Make sure Python 3.7+ is installed

---

## Success Criteria

✅ Watcher detects new files in Inbox
✅ Metadata files created automatically
✅ Basic File Handler processes and moves files
✅ Task Analyzer identifies types and routes correctly
✅ Plans created with action steps
✅ Approval routing works for payments > $500
✅ All files tracked through workflow

**Bronze Tier Status: COMPLETE ✅**
