# 🎓 USAR Ranklist

A web application to view and compare student results and rankings for **University School of Automation & Robotics (USAR)**, GGSIPU.

![Draft](https://img.shields.io/badge/Status-Draft%20v1.0-yellow)
![Python](https://img.shields.io/badge/Python-3.8+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)

---

## 📌 About

This project provides a simple, user-friendly interface for USAR students to:

- 📊 View **branch-wise ranklists** sorted by SGPA or Percentage
- 🔍 Filter results by **Branch**, **Semester**, and **Batch**
- 📈 See **statistics** like average SGPA, topper info, etc.
- 📥 **Export ranklist to CSV** for offline use
- 👤 View **individual student details**

---

## 🚀 Features

| Feature | Description |
|---------|-------------|
| **Branch Filter** | AIDS, AIML, IIOT, AR |
| **Semester Filter** | All available semesters |
| **Batch Filter** | 2024, 2023, etc. |
| **Sorting** | By SGPA or Percentage (Ascending/Descending) |
| **Statistics** | Total students, Average SGPA, Average %, Topper |
| **Export** | Download ranklist as CSV file |
| **Responsive** | Works on desktop and mobile |

---

## 🛠️ Tech Stack

- **Backend:** Python, FastAPI, Uvicorn
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5
- **Data:** JSON (parsed from IPU results)

---

## 📂 Project Structure

```
usar-ranklist/
├── data/
│   └── output/
│       └── parsed_results.json    # Student data
├── result-management/
│   ├── main.py                    # FastAPI server
│   ├── database_service.py        # Data handling
│   ├── models.py                  # Data models
│   ├── templates/
│   │   └── index.html             # Main page
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
└── README.md
```

---

## ⚡ Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Waqar080206/usar-ranklist.git
cd usar-ranklist
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn jinja2 python-multipart
```

### 3. Run the server

```bash
cd result-management
python main.py
```

### 4. Open in browser

```
http://localhost:8000
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main web interface |
| `/api/ranklist` | GET | Get ranked list with filters |
| `/api/filters` | GET | Get available filter options |
| `/api/student/{roll_no}` | GET | Get student details |
| `/api/stats` | GET | Get statistics |

### Query Parameters for `/api/ranklist`

| Parameter | Type | Description |
|-----------|------|-------------|
| `branch` | string | Branch code: AIDS, AIML, IIOT, AR |
| `semester` | string | Semester: 01, 02, 03... |
| `batch` | string | Batch year: 2024, 2023... |
| `sort_by` | string | Sort by: `sgpa` or `percentage` |
| `order` | string | Order: `asc` or `desc` |

**Example:**
```
/api/ranklist?branch=AIDS&semester=03&sort_by=sgpa&order=desc
```

---

## ⚠️ Disclaimer

> **IMPORTANT: Please read before using this application.**

1. **Unofficial Website**  
   This is **NOT** an official website of GGSIPU or USAR. It is an independent project created for the convenience of students.

2. **Purpose**  
   This tool is created solely to help USAR students view their results and compare rankings easily. It is meant for **educational and informational purposes only**.

3. **Data Source**  
   All data is sourced from **publicly available** IPU examination results. No private or confidential information is collected or stored.

4. **No Guarantee**  
   While efforts have been made to ensure accuracy, we do **not guarantee** the correctness of the data. Always verify results from the official IPU website.

5. **Draft Version**  
   This is **Draft v1.0** and is still under development. Features may change, and bugs may exist.

6. **No Liability**  
   The developer is not responsible for any decisions made based on the information provided by this application.

---

## 🙏 Credits & Inspiration

This project is inspired by [**IPU Ranklist**](https://www.ipuranklist.com) created by [**Ankush Garg**](https://github.com/ankushgarg1998/).

A huge thanks to Ankush for the original idea and inspiration! 🎉

---

## 👨‍💻 Developer

**Waqar Akhtar**

- 🌐 Website: [waqar.tech](https://waqar.tech)
- 💻 GitHub: [@Waqar080206](https://github.com/Waqar080206)

---

## 📄 License

This project is open source and available for educational purposes.

---

## 🔮 Future Updates

- [ ] Add more semesters data
- [ ] Search by student name or roll number
- [ ] Subject-wise analysis
- [ ] Historical comparison
- [ ] Dark mode
- [ ] Mobile app

---

<div align="center">

**Made with ❤️ for USAR Students**

*If you find this helpful, give it a ⭐ on GitHub!*

</div>