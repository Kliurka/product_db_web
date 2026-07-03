# Stone Factory ERP UI System

Version: 1.0

---

# General Rules

Every ERP page follows the same layout.

List Pages

Subtitle

↓

Title

↓

Toolbar

↓

Table

↓

Pagination (future)

---------------------------------------

Form Pages

Subtitle

↓

Title

↓

Top Actions

↓

Panels

↓

Audit

↓

Bottom Actions

---------------------------------------

# Page Header

Contains:

- Subtitle
- Title

---------------------------------------

# Toolbar

Contains:

- Search
- Filters (optional)
- Add button

---------------------------------------

# ERP Panels

Every form is divided into numbered panels.

Example:

01 — Identity

02 — Contact

03 — Financial

04 — Audit

---------------------------------------

# Buttons

Top:

Cancel
Reset
Save

Bottom:

Cancel
Save

---------------------------------------

# Tables

Every table should support:

Search

Sorting

Filters (if applicable)

Add button

---------------------------------------

# Mobile

Sidebar collapses.

Toolbar becomes vertical.

Table keeps readability.

---------------------------------------

# Naming

Master Data

Products

Customers

Storage Locations

Textures

System

Users

Operations

Orders

Reservations

Reports (future)

---------------------------------------

## Components Policy

Reusable components should represent complete UI blocks.

Good examples:

- Page Header
- Search Toolbar
- Audit Panel
- Form Actions

Avoid creating components for small HTML fragments such as:

- Panels
- Labels
- Form rows
- Individual fields

Readability is more important than reducing a few lines of HTML.


This document defines the UI standard for the entire Stone Factory ERP project.