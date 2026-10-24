# QUICK REFERENCE CARD

## START COMMANDS

### Web Dashboard (Recommended for Demo)
```powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher"
.\venv\Scripts\activate
python app.py
```
**? http://localhost:5000/dashboard**

### FastAPI Server (For Mobile App)
```powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/server"
.\venv\Scripts\activate
uvicorn app.main:app --reload
```
**? http://localhost:8000/docs**

### Mobile App (Browser)
```powershell
cd "E:/Kiro/Hackachusetts 2026/healthcare/clinical-trial-matcher/app"
npx expo start --web
```
**? http://localhost:19006**

---

## SYSTEM STATUS ?

- Flask: WORKING (3,131 trials, 5 patients)
- FastAPI: WORKING (7 tables, API ready)
- Mobile: READY (dependencies installed)
- Tests: 100% PASSING
- GitHub: ALL COMMITTED

---

## DOCUMENTATION

1. **FINAL_STATUS.md** - Complete verification report
2. **USAGE_GUIDE.md** - Flask vs FastAPI
3. **MOBILE_APP_GUIDE.md** - Mobile app instructions
4. **COMPLETE_SUMMARY.md** - Quick overview
5. **README.md** - Full project documentation

---

Ready for demo! ??
