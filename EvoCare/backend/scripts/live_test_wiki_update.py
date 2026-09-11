import requests, json

BASE = 'http://127.0.0.1:8000/api'

# Step 1: Login as caregiver
r = requests.post(f'{BASE}/auth/login', json={'username': 'caregiver.demo', 'password': 'CaregiverPass123!'})
token = r.json()['access_token']
headers = {'Authorization': f'Bearer {token}'}
print('[1] Logged in as caregiver.demo')

# Step 2: Start observation with an unambiguous mobility note that has enough detail
note = 'She was unsteady and needed help walking to the bathroom.'
body = {'patient_code': 'P001', 'text': note, 'caregiver_id': 'CG001', 'processing_mode': 'AUTO'}
r2 = requests.post(f'{BASE}/observations/start', json=body, headers=headers)
d = r2.json()
session_id = d.get('session_id')
category = d.get('category', 'unknown')
questions = d.get('questions', [])
print(f'[2] Session {session_id} | category={category} | {len(questions)} clarification questions')
for q in questions:
    print(f'    Q: {q.get("question")} | options: {q.get("options", [])}')

# Step 3: Answer each question with first available option
for q in questions:
    opts = q.get('options') or ['Not sure / Unknown']
    answer = opts[0]
    ans_body = {'question_id': q['id'], 'field_name': q['field_name'], 'answer': answer}
    ra = requests.post(f'{BASE}/clarification/{session_id}/answer', json=ans_body, headers=headers)
    print(f'[3] Answered {q["field_name"]} = "{answer}" -> HTTP {ra.status_code}')

# Step 4: Complete session (triggers wiki update)
rc = requests.post(f'{BASE}/clarification/{session_id}/complete', headers=headers)
cd = rc.json()
print(f'\n[4] Complete HTTP {rc.status_code}')
print(f'    evidence_code : {cd.get("evidence_code")}')
print(f'    category      : {cd.get("category")}')
print(f'    wiki_updated  : {cd.get("wiki_updated")}')
print(f'    wiki_files    : {cd.get("wiki_files")}')

# Step 5: Read the Mobility.md file to confirm new row was appended
if cd.get('wiki_files'):
    for wf in cd['wiki_files']:
        print(f'\n[5] Checking wiki file: {wf}')
        try:
            with open(wf, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            # Print last 8 lines of the file
            print('    ... (last 8 lines of file) ...')
            for line in lines[-8:]:
                print('   ', line.rstrip())
        except FileNotFoundError:
            print(f'    File not found: {wf}')
else:
    # Try to find Mobility.md directly
    import pathlib
    search = pathlib.Path(r'c:\Users\lokan\Downloads\journey\sve')
    for md in search.rglob('Mobility.md'):
        print(f'\n[5] Found {md}')
        lines = md.read_text(encoding='utf-8').splitlines()
        print('    ... (last 8 lines) ...')
        for line in lines[-8:]:
            print('   ', line)
        break
