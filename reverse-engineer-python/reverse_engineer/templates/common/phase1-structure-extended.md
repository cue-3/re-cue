{% extends "base.md" %}

{% block title %}Phase 1: Project Structure Analysis - {{ PROJECT_NAME }}{% endblock %}

{% block overview_content %}
This document contains the results of Phase 1 analysis: discovering the basic
structure of the project including endpoints, models, views, services, and features.
{% endblock %}

{% block overview_stats %}
- **API Endpoints**: {{ ENDPOINT_COUNT | default(0) }}
- **Data Models**: {{ MODEL_COUNT | default(0) }}
- **UI Views**: {{ VIEW_COUNT | default(0) }}
- **Backend Services**: {{ SERVICE_COUNT | default(0) }}
- **Features**: {{ FEATURE_COUNT | default(0) }}
{% endblock %}

{% block main_content %}
## API Endpoints

{% if ENDPOINT_COUNT and ENDPOINT_COUNT > 0 %}
| Method | Endpoint | Controller |
|--------|----------|------------|
{% for endpoint in endpoints %}
| {{ endpoint.method }} | {{ endpoint.path }} | {{ endpoint.controller }} |
{% endfor %}
{% else %}
*No API endpoints detected.*
{% endif %}

---

## Data Models

{% if MODEL_COUNT and MODEL_COUNT > 0 %}
| Model | Fields | Location |
|-------|--------|----------|
{% for model in models %}
| {{ model.name }} | {{ model.fields | length }} | {{ model.location }} |
{% endfor %}
{% else %}
*No data models detected.*
{% endif %}

---

## UI Views

{% if VIEW_COUNT and VIEW_COUNT > 0 %}
| View Name | Component File |
|-----------|----------------|
{% for view in views %}
| {{ view.name }} | {{ view.file }} |
{% endfor %}
{% else %}
*No UI views detected.*
{% endif %}

---

## Backend Services

{% if services %}
{% for service in services %}
### {{ service.name }}

- **Type**: {{ service.type }}
- **Location**: {{ service.location }}
{% if service.methods %}
- **Methods**: {{ service.methods | length }}
{% endif %}

{% endfor %}
{% else %}
*No backend services detected.*
{% endif %}

---

## Features

{% if features %}
The following features were identified:

{% for feature in features %}
- **{{ feature.name }}**: {{ feature.description | default('No description') }}
{% endfor %}
{% else %}
*No features detected.*
{% endif %}
{% endblock %}

{% block next_steps_details %}
- Identify actors who interact with the system
- Discover user roles and permissions
- Map external systems and integrations
{% endblock %}
