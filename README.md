# ContriTrack — Phase 3

Django + SQLite Ajo/Esusu rotating contribution management. This phase adds database-backed payout rounds and administrator payout completion actions.

## Requirements
- Python 3.10+
- pip

## Run on Windows
Open a terminal in the folder containing `manage.py`, then run:

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations savings
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/ and sign in with your administrator account. The Django admin is at http://127.0.0.1:8000/admin/.

## Included
- Four main application pages: Dashboard, Members & Contributions, Ajo Rotation & Payouts, History/Reports/Settings. Login and registration are supporting screens.
- Admin can add members, record contributions, add payout rounds, and mark a payout completed.
- Members can see their own dashboard/history and payout rounds assigned to them.
- The contribution form contains only member selection, amount, and contribution date.
- Payout rounds store round number, recipient, scheduled date, amount, status, payout date and optional note.

## Important
Marking a payout completed records the event; it does not transfer money or connect to a bank. The administrator should verify that the member received the money before marking it complete. Payout amount is entered manually and is not automatically calculated from contribution records.


## Phase 4 additions
- Dashboard totals and recent contributions now come from the database.
- History page includes date filtering for contribution and payout records.
- Export report downloads a CSV file that can be opened in Excel.
- Administrator group settings are stored in the database; members can view but cannot change them.
- Role-based visibility limits members to their own contribution and payout records.

After replacing your project with this phase, run these commands in the project folder:

```bash
python manage.py makemigrations savings
python manage.py migrate
python manage.py runserver
```

Keep your existing `db.sqlite3` file if you want to preserve your existing data. Back it up before running migrations. The report export currently exports all dates; the on-screen report can be filtered by date.
