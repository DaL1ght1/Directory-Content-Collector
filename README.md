# Directory Content Collector

A small CLI utility that walks a project directory, generates an ASCII **tree view**, and concatenates the **contents of relevant source files** into a single text output — inserting a clear ASCII separator between files. It’s tuned to **ignore common build artifacts, binaries, lockfiles, IDE folders, and large generated directories** typically found in Spring Boot + Angular repositories.

---

## ✨ Features

* Generates an ASCII **directory tree**
* Exports **source file contents** into one consolidated text output
* Inserts a clear ASCII **file separator** between files
* Skips noisy folders like:

  * `node_modules`, `target`, `dist`, `.git`, `.idea`, `.vscode`, `build`, `.angular`, `.gradle`, `.mvn`, etc.
* Skips many non-code/binary formats (images, archives, jars, pdfs, docs, etc.) and common lock/config artifacts
* Prints progress logs (what it’s processing / skipping)

---

## ✅ Use cases

* Sharing project context with an LLM (e.g., paste one export instead of hundreds of files)
* Quick code reviews / audits
* Generating a lightweight “project snapshot” for documentation

---

## 🧰 Requirements

* Python **3.8+**
* No external dependencies

---

## 🚀 Installation

Clone or copy the script into your project, e.g.:

* `parser.py`

---

## ▶️ Usage

Run the script from anywhere and point it at the directory you want to export.

```bash
python parser.py /path/to/project
```

By default, it writes a consolidated output file (see `OUTPUT_FILE` in the script). If your script version accepts an output argument, use:

```bash
python parser.py /path/to/project /path/to/output.txt
```

---

## 📄 Output format

The generated file has two main sections:

1. **DIRECTORY STRUCTURE**

   * An ASCII tree of the scanned directory

2. **FILE CONTENTS**

   * For each included file:

     * a header with the file path
     * the raw file contents
     * an ASCII separator block between files

---

## 🔍 Filtering rules

The script is designed to export “useful source” while avoiding large or irrelevant content.

### Ignored directories (examples)

* `.git`, `.idea`, `.vscode`
* `node_modules`, `dist`, `build`, `.angular`
* `target`, `.gradle`, `.mvn`

### Ignored file types (examples)

* Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.svg`, `.ico`
* Archives/Binaries: `.zip`, `.tar`, `.gz`, `.jar`, `.war`, `.class`, `.exe`
* Documents: `.pdf`, `.docx`, `.pptx`

> You can customize these lists in the script to match your repo layout.

---

## 🛠️ Customization

Common edits you might want:

* Add/remove ignored directories in `EXCLUDED_DIRS`
* Add/remove ignored extensions in `EXCLUDED_EXTS`
* Change the output filename/path (e.g., `OUTPUT_FILE`)

---

## ⚠️ Notes

* Very large repositories can still produce large outputs.
* If your repo contains secret keys, `.env` files, or credentials, ensure they’re excluded before exporting.


