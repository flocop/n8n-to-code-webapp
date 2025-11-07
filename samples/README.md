# Sample n8n Workflows

This directory contains sample n8n workflow JSON files for testing the converter.

## Available Samples

### 1. simple-http.json
A basic workflow that makes a single HTTP GET request to the GitHub API.

**Nodes:**
- Start trigger
- HTTP Request (GET GitHub repo info)

**Usage:**
```bash
python -m backend.cli convert samples/simple-http.json -o output/simple.py
```

### 2. http-with-condition.json
A workflow that fetches user data and uses conditional logic to process it differently based on repo count.

**Nodes:**
- Start trigger
- HTTP Request (Fetch GitHub user)
- IF condition (Check repo count)
- Set variables (Different messages for each branch)

**Usage:**
```bash
python -m backend.cli convert samples/http-with-condition.json -d output/conditional/
```

### 3. webhook-workflow.json
A webhook-triggered workflow that processes incoming data and forwards it to an external API.

**Nodes:**
- Webhook trigger
- Code node (Process data)
- HTTP Request (Send to external API)

**Usage:**
```bash
python -m backend.cli convert samples/webhook-workflow.json -d output/webhook/
```

## Testing the Converter

1. **Convert a workflow:**
   ```bash
   python -m backend.cli convert samples/simple-http.json -o test.py
   ```

2. **Validate a workflow:**
   ```bash
   python -m backend.cli validate samples/simple-http.json
   ```

3. **Generate full project:**
   ```bash
   python -m backend.cli convert samples/http-with-condition.json -d output/
   cd output/
   pip install -r requirements.txt
   python workflow.py
   ```

## Creating Your Own Samples

Export your n8n workflow as JSON:
1. Open your workflow in n8n
2. Click the menu (three dots)
3. Select "Download"
4. Save the JSON file to this directory

Then test the conversion:
```bash
python -m backend.cli convert samples/your-workflow.json -d output/your-workflow/
```
