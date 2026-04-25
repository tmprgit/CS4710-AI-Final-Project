# Course Data Extraction

## Setup

1. In a private window, go to <https://sisuva.admin.virginia.edu/psp/ihprd/UVSS/SA/s/WEBLIB_HCX_CM.H_COURSE_CATALOG.FieldFormula.IScript_Main?cmd=uninav&Rnode=LOCAL_NODE&uninavpath=Root%7BPORTAL_ROOT_OBJECT%7D.HighPoint%7BHIGHPOINT%7D.Campus+Experience%7BHPT_CAMPUS_EXPERIENCE%7D.Find+Classes%7BHPT_CX_CLASS_INFORMATION%7D>
2. Inspect element, go to Storage, and then Cookie Storage
3. Create a cookies.csv file with the following structure, of all cookies in your browser:

```
Name,Value,Domain,Path
```

## Running

In your terminal, run:

```bash
python3 course_service.py --db course_catalog.sqlite3
```
