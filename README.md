# GitHub Release Tag Fetcher

A lightweight Python utility to fetch the **latest GitHub release tag** from a repository, with optional filtering to **exclude releases that contain specific file types** (e.g., `.apk`, `.aab`).  
Ideal for deployment pipelines or automation scripts where only clean releases are required.

---

## ✅ Features

- Fetch the latest release from any GitHub repository.
- Skip releases that include disallowed asset types.
- Write the valid release tag to a file.
- Configurable via environment variables.
- Clean logging with [loguru](https://github.com/Delgan/loguru).

---

## 🧱 Project Setup (Poetry)

### 1. Clone the Repository

```bash
  git clone https://github.com/your-org/your-repo.git
```
```bash
  cd your-repo
```

### 2. Activate the Virtual Environment

```bash
  poetry shell
```

### 3. Install Dependencies
```bash
  poetry install
```


### 4. Run
```bash
  poetry run fetch-tag
```

