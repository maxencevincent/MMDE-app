# 🧬 Mother Machine Data Explorer

This app allows users to interactively visualize and analyze data from mother machine experiments, especially CSV outputs from the BACMMAN plugin (FIJI).

---

## 🚀 Features
- ✅ Upload or select multiple BACMMAN `.csv` datasets
- ✅ Filter cells by: trench, position, mother-only, or outlier threshold
- ✅ Visualize biological features:
  - time-series (mean ± std or single-cell)
  - position-based boxplots
- ✅ Add experimental treatment periods as shaded regions
- ✅ Customize plot style: font, colors, size, palette, axes limits
- ✅ Export plots in `.png`, `.pdf`, `.svg` + plot data as `.csv`

---

## 📁 How to Use

### 1. Clone this repository
```bash
git clone https://github.com/your-username/mothermachine-explorer.git
cd mothermachine-explorer
```

### 2. Install dependencies
Create a virtual environment and install required packages:
```bash
pip install -r requirements.txt
```

### 3. Run the app locally
```bash
streamlit run app.py
```

---

## 📂 Input Format
CSV files must come from BACMMAN (FIJI plugin). Each row corresponds to a single bacterium at a specific frame. Example columns:
- `PositionIdx`, `Indices`, `BacteriaLineage`
- `PreviousDivisionFrame`, `NextDivisionFrame`
- `Size`, `GrowthRate`, `MeanGFP`, `MeanRFP`, `Length`, `Division time`, etc.

---

## 🧪 Example
A sample dataset can be placed in the `data/` folder or uploaded via the interface.

---

## 📬 Contact
Created by Maxence VINCENT (with a massive help of ChatGPT)
📧  mvincent@imm.cnrs.fr

For questions or suggestions, feel free to reach out :).

---

## 📜 License
This project is licensed under the [MIT License](LICENSE).
