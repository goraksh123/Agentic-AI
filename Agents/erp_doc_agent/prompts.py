# prompts.py
# All AI prompts for documentation generation

MODULE_DOC_PROMPT = """
You are an expert technical documentation writer
for PHP ERP systems.

Analyze this PHP ERP module code and generate
COMPLETE professional documentation.

MODULE: {module_name}
FILES: {file_list}

CODE:
{code_content}

Generate documentation with these sections:

# {module_name} Module Documentation

## 1. Overview
- What this module does
- Business purpose
- Key features

## 2. Files Structure
- List all files with purpose

## 3. Functions Reference
For each function:
- Function name
- Purpose
- Parameters (name, type, description)
- Return value
- Example usage

## 4. Database Tables Used
- Table names
- Key columns used
- Relationships

## 5. UI Flow
- What user sees
- Form fields
- Actions available

## 6. Process Flow (Mermaid Diagram)
```mermaid
flowchart TD
    [generate actual flow from code]
```

## 7. Data Flow (Mermaid Diagram)
```mermaid
sequenceDiagram
    [UI to PHP to MySQL flow]
```

## 8. Error Handling
- What errors are handled
- Error messages shown to user

## 9. Dependencies
- Files included
- External libraries used

Be specific and accurate based on actual code.
"""

DATABASE_DOC_PROMPT = """
You are expert MySQL database documentation writer.

Analyze these database tables from PHP ERP system
and generate complete database documentation.

TABLES INFO:
{tables_info}

Generate:

# Database Documentation

## 1. Overview
- Total tables
- Database purpose
- Key relationships

## 2. ERD Diagram (Mermaid)
```mermaid
erDiagram
    [generate actual ERD from tables]
```

## 3. Table Reference
For each table:
### table_name
| Column | Type | Null | Key | Description |
|--------|------|------|-----|-------------|
[fill from actual columns]

**Purpose:** what this table stores
**Key Relationships:** foreign keys

## 4. Key Queries
Common queries used in the system

## 5. Indexes
Important indexes for performance
"""

FLOW_DOC_PROMPT = """
Analyze this PHP ERP code and generate
complete flow documentation.

CODE: {code_content}
MODULE: {module_name}

Generate ALL these diagrams:

## 1. User Journey Flow
```mermaid
flowchart TD
    [user actions from login to task completion]
```

## 2. PHP Processing Flow
```mermaid
flowchart TD
    [PHP code execution flow]
```

## 3. Database Interaction Flow
```mermaid
sequenceDiagram
    participant U as User Browser
    participant P as PHP Script
    participant D as MySQL Database
    [actual sequence from code]
```

## 4. Error Flow
```mermaid
flowchart TD
    [error handling flow]
```
"""

SYSTEM_PROMPT = """
You are an expert technical documentation writer
specializing in PHP ERP accounting systems.

You are documenting Font Accounting Framework
which is a PHP (version < 6) ERP system
with MySQL database.

Rules:
- Be specific and accurate
- Use actual function/table names from code
- Generate working Mermaid diagrams
- Write for both technical and business readers
- Follow professional documentation standards
"""